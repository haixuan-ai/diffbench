"""Brax generalized（球/盒/平面碰撞，MJCF 载入）。不支持的场景如实报错，不降级。"""
from __future__ import annotations
import time
import numpy as np
from .base import Adapter, empty_states
from .mujoco_family import build_xml
from ..spec import sample_every
from ..truth import rotm


class BraxGeneralized(Adapter):
    name = "brax_generalized"
    def version(self):
        import brax, jax
        return f"brax {brax.__version__}, jax {jax.__version__} (CPU, generalized pipeline)"
    def available(self):
        try:
            import brax  # noqa
            return True, ""
        except Exception as e:
            return False, str(e)[:120]
    def run(self, sc, dt):
        import jax, jax.numpy as jnp
        from brax.io import mjcf
        from brax.generalized import pipeline
        sys_ = mjcf.loads(build_xml(sc, dt))
        nb = len(sc["bodies"]); q = np.zeros(sys_.q_size()); qd = np.zeros(sys_.qd_size())
        hinge = sc.get("hinge")
        if not hinge:
            for i, b in enumerate(sc["bodies"]):
                q[7 * i:7 * i + 3] = b["pos"]; q[7 * i + 3:7 * i + 7] = b.get("quat", [1, 0, 0, 0])
                qd[6 * i:6 * i + 3] = b.get("vel", [0, 0, 0]); qd[6 * i + 3:6 * i + 6] = b.get("angvel", [0, 0, 0])
        state = pipeline.init(sys_, jnp.array(q), jnp.array(qd))
        step = jax.jit(pipeline.step); state = step(sys_, state, jnp.zeros(sys_.act_size())); jax.block_until_ready(state.q)
        state = pipeline.init(sys_, jnp.array(q), jnp.array(qd))
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0
        def rec(k):
            x, xd = state.x, state.xd
            out["t"].append(k * dt); out["pos"].append(np.asarray(x.pos).tolist()); out["quat"].append(np.asarray(x.rot).tolist())
            v = np.asarray(xd.vel); w = np.asarray(xd.ang)
            if hinge:  # 实测 Brax 对铰链连杆给出的 xd.vel 恒为 0（以关节枢轴为参考点）；换算为质心线速度 v = v_ref + ω × (r_com − r_pivot)
                v = v + np.cross(w, np.asarray(x.pos) - np.asarray(hinge["pivot"]))
            out["vel"].append(v.tolist()); out["angvel"].append(w.tolist())
        rec(0); act = jnp.zeros(sys_.act_size())
        for k in range(1, steps + 1):
            t0 = time.perf_counter(); state = step(sys_, state, act); jax.block_until_ready(state.q); wall += time.perf_counter() - t0
            if k % se == 0 or k == steps: rec(k)
        out["steps_per_sec"] = steps / wall; out["config"] = {"pipeline": "generalized", "note": "x.pos 为质心；铰链场景线速度由 xd.ang 与枢轴换算（见适配器注释）"}
        return out
