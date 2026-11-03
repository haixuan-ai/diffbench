"""MuJoCo CPU / MJX(JAX, CPU) / MuJoCo-Warp(CPU device) 共用一份 MJCF。

状态读取统一为：先 forward（mj_step 之后 xpos 是上一步的），再取 xpos/xquat/物体质心速度。
默认配置（Protocol A 原生默认）：Euler 积分器、pyramidal 摩擦锥、默认 solref/solimp；摩擦只设滑动 mu，扭转/滚动摩擦为 0。
"""
from __future__ import annotations
import time
import numpy as np
from .base import Adapter, empty_states
from ..spec import sample_every
from ..truth import rotm


def build_xml(sc: dict, dt: float) -> str:
    g = sc["gravity"]; mu = sc["friction"]
    def geom(b):
        s = b["shape"]; fr = f'friction="{mu} 0 0" condim="3"'
        if s["type"] == "box":
            return f'<geom type="box" size="{s["half"][0]} {s["half"][1]} {s["half"][2]}" mass="{b["mass"]}" {fr}/>'
        return f'<geom type="sphere" size="{s["radius"]}" mass="{b["mass"]}" {fr}/>'
    bodies = ""
    for b in sc["bodies"]:
        p = b["pos"]; q = b.get("quat", [1, 0, 0, 0])
        if sc.get("hinge") and sc["hinge"]["body"] == b["id"]:
            pv = sc["hinge"]["pivot"]; ax = sc["hinge"]["axis"]
            joint = f'<joint name="hj" type="hinge" axis="{ax[0]} {ax[1]} {ax[2]}" pos="{pv[0]-p[0]} {pv[1]-p[1]} {pv[2]-p[2]}" damping="0"/>'
        else:
            joint = "<freejoint/>"
        bodies += f'<body name="{b["id"]}" pos="{p[0]} {p[1]} {p[2]}" quat="{q[0]} {q[1]} {q[2]} {q[3]}">{joint}{geom(b)}</body>'
    ground = f'<geom type="plane" size="50 50 1" friction="{sc["ground"]["friction"]} 0 0" condim="3"/>' if sc.get("ground") else ""
    return f'<mujoco><option timestep="{dt}" gravity="{g[0]} {g[1]} {g[2]}"/><worldbody>{ground}{bodies}</worldbody></mujoco>'


def init_velocities(m, d, sc):
    import mujoco
    for b in sc["bodies"]:
        if sc.get("hinge") and sc["hinge"]["body"] == b["id"]:
            continue
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, b["id"]); adr = m.body_dofadr[bid]
        d.qvel[adr:adr + 3] = b.get("vel", [0, 0, 0])
        R = rotm(b.get("quat", [1, 0, 0, 0])); d.qvel[adr + 3:adr + 6] = R.T @ np.array(b.get("angvel", [0, 0, 0]), float)  # 自由关节角速度在体坐标系


def read_state(m, d, sc):
    import mujoco
    pos, quat, vel, ang = [], [], [], []; res = np.zeros(6)
    for b in sc["bodies"]:
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, b["id"])
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, bid, res, 0)  # 世界系, 物体质心: [ω, v]
        pos.append(d.xipos[bid].tolist()); quat.append(d.xquat[bid].tolist()); ang.append(res[:3].tolist()); vel.append(res[3:].tolist())
    return pos, quat, vel, ang


class MuJoCoCPU(Adapter):
    name = "mujoco"
    def version(self):
        import mujoco; return f"mujoco {mujoco.__version__}"
    def run(self, sc, dt):
        import mujoco
        m = mujoco.MjModel.from_xml_string(build_xml(sc, dt)); d = mujoco.MjData(m)
        init_velocities(m, d, sc); mujoco.mj_forward(m, d)
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0
        def rec(k):
            mujoco.mj_forward(m, d); p, q, v, a = read_state(m, d, sc)
            out["t"].append(k * dt); out["pos"].append(p); out["quat"].append(q); out["vel"].append(v); out["angvel"].append(a)
        rec(0)
        for k in range(1, steps + 1):
            t0 = time.perf_counter(); mujoco.mj_step(m, d); wall += time.perf_counter() - t0
            if k % se == 0 or k == steps: rec(k)
        out["steps_per_sec"] = steps / wall; out["config"] = {"integrator": "Euler(default)", "cone": "pyramidal(default)", "solref": "default"}
        return out


class MJX(Adapter):
    name = "mjx"
    def version(self):
        import mujoco, jax; from mujoco import mjx
        return f"mujoco-mjx {mujoco.__version__}, jax {jax.__version__} (CPU)"
    def available(self):
        try:
            from mujoco import mjx  # noqa
            return True, ""
        except Exception as e:
            return False, str(e)[:120]
    def run(self, sc, dt):
        import mujoco, jax
        from mujoco import mjx
        jax.config.update("jax_enable_x64", False)
        m = mujoco.MjModel.from_xml_string(build_xml(sc, dt)); d = mujoco.MjData(m)
        init_velocities(m, d, sc); mujoco.mj_forward(m, d)
        mx = mjx.put_model(m); dx = mjx.put_data(m, d)
        step = jax.jit(mjx.step); fwd = jax.jit(mjx.forward)
        dx = step(mx, dx); jax.block_until_ready(dx.qpos)  # 预热编译（不计时）
        dx = mjx.put_data(m, d)
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0
        def rec(k):
            dd = mjx.get_data(m, fwd(mx, dx)); mujoco.mj_forward(m, dd)  # 速度/位置读取沿用 CPU 侧同一读取函数
            p, q, v, a = read_state(m, dd, sc)
            out["t"].append(k * dt); out["pos"].append(p); out["quat"].append(q); out["vel"].append(v); out["angvel"].append(a)
        rec(0)
        for k in range(1, steps + 1):
            t0 = time.perf_counter(); dx = step(mx, dx); jax.block_until_ready(dx.qpos); wall += time.perf_counter() - t0
            if k % se == 0 or k == steps: rec(k)
        out["steps_per_sec"] = steps / wall; out["config"] = {"float": "float32(jax default)", "note": "MJX CPU 单环境，非其设计的批量 GPU 场景"}
        return out


class MuJoCoWarp(Adapter):
    name = "mujoco_warp"
    def version(self):
        import mujoco, warp as wp, mujoco_warp as mjw
        return f"mujoco_warp {getattr(mjw, '__version__', '?')}, mujoco {mujoco.__version__}, warp {wp.__version__} (CPU device)"
    def run(self, sc, dt):
        import mujoco, warp as wp, mujoco_warp as mjw
        wp.config.quiet = True; wp.set_device("cpu")
        m = mujoco.MjModel.from_xml_string(build_xml(sc, dt)); d = mujoco.MjData(m)
        init_velocities(m, d, sc); mujoco.mj_forward(m, d)
        mw = mjw.put_model(m); dw = mjw.put_data(m, d, nworld=1, nconmax=256, njmax=1024)
        mjw.step(mw, dw)  # 预热/内核编译（不计时）
        dw = mjw.put_data(m, d, nworld=1, nconmax=256, njmax=1024)
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0; tmp = mujoco.MjData(m)
        def rec(k):
            mjw.get_data_into(tmp, m, dw); mujoco.mj_forward(m, tmp); p, q, v, a = read_state(m, tmp, sc)
            out["t"].append(k * dt); out["pos"].append(p); out["quat"].append(q); out["vel"].append(v); out["angvel"].append(a)
        rec(0)
        for k in range(1, steps + 1):
            t0 = time.perf_counter(); mjw.step(mw, dw); wp.synchronize(); wall += time.perf_counter() - t0
            if k % se == 0 or k == steps: rec(k)
        out["steps_per_sec"] = steps / wall; out["config"] = {"device": "cpu", "note": "MuJoCo-Warp 为 GPU 并行设计，此处 CPU 单环境"}
        return out
