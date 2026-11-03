"""Newton（CPU device）：XPBD 与 MuJoCo(Warp 后端) 两个求解器分别参赛。z-up，body_q=(p, q_xyzw)，body_qd 约定见 _state()。"""
from __future__ import annotations
import time
import numpy as np
from .base import Adapter, empty_states
from ..spec import sample_every


def _vol(s):
    if s["type"] == "box":
        h = s["half"]; return 8 * h[0] * h[1] * h[2]
    return 4 / 3 * np.pi * s["radius"] ** 3


class _Newton(Adapter):
    solver = ""
    def version(self):
        import newton, warp as wp
        return f"newton {newton.__version__}, warp {wp.__version__} (CPU)"
    def run(self, sc, dt):
        import newton, warp as wp
        wp.config.quiet = True; wp.set_device("cpu")
        bld = newton.ModelBuilder(up_axis=newton.Axis.Z, gravity=tuple(sc["gravity"]))
        mu = sc["friction"]
        if sc.get("ground"):
            bld.add_ground_plane(cfg=newton.ModelBuilder.ShapeConfig(mu=sc["ground"]["friction"]))
        hinge = sc.get("hinge"); bodies = []; joints = []
        for b in sc["bodies"]:
            cfg = newton.ModelBuilder.ShapeConfig(mu=mu, density=b["mass"] / _vol(b["shape"]))
            q = b.get("quat", [1, 0, 0, 0]); xf = wp.transform(wp.vec3(*b["pos"]), wp.quat(q[1], q[2], q[3], q[0]))
            if hinge and hinge["body"] == b["id"]:
                body = bld.add_link(xform=xf)
            else:
                body = bld.add_body(xform=xf)
            if b["shape"]["type"] == "box":
                h = b["shape"]["half"]; bld.add_shape_box(body, hx=h[0], hy=h[1], hz=h[2], cfg=cfg)
            else:
                bld.add_shape_sphere(body, radius=b["shape"]["radius"], cfg=cfg)
            if hinge and hinge["body"] == b["id"]:
                pv = hinge["pivot"]; loc = [pv[i] - b["pos"][i] for i in range(3)]
                joints.append(bld.add_joint_revolute(parent=-1, child=body, axis=wp.vec3(*hinge["axis"]),
                              parent_xform=wp.transform(wp.vec3(*pv), wp.quat_identity()), child_xform=wp.transform(wp.vec3(*loc), wp.quat_identity())))
            bodies.append(body)
        if hinge: bld.add_articulation(joints)
        model = bld.finalize(device="cpu")
        if self.solver == "xpbd": sv = newton.solvers.SolverXPBD(model, iterations=10)
        else: sv = newton.solvers.SolverMuJoCo(model, njmax=400, nconmax=200)
        s0, s1, ctl = model.state(), model.state(), model.control()
        if not hinge:
            jqd = s0.joint_qd.numpy()
            for i, b in enumerate(sc["bodies"]):
                jqd[6 * i:6 * i + 6] = [*b.get("vel", [0, 0, 0]), *b.get("angvel", [0, 0, 0])]
            s0.joint_qd.assign(jqd); newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0
        def rec(k, st):
            q = st.body_q.numpy(); qd = st.body_qd.numpy(); P, Q, V, W = [], [], [], []
            for bi in bodies:
                P.append(q[bi][:3].tolist()); x, y, z, w = q[bi][3:7]; Q.append([w, x, y, z])
                V.append(qd[bi][:3].tolist()); W.append(qd[bi][3:6].tolist())   # Newton: (线速度, 角速度) 世界系
            out["t"].append(k * dt); out["pos"].append(P); out["quat"].append(Q); out["vel"].append(V); out["angvel"].append(W)
        rec(0, s0)
        for k in range(1, steps + 1):
            s0.clear_forces(); t0 = time.perf_counter()
            contacts = model.collide(s0) if sc.get("ground") or len(bodies) > 1 else None
            sv.step(s0, s1, ctl, contacts, dt); wall += time.perf_counter() - t0
            s0, s1 = s1, s0
            if k % se == 0 or k == steps: rec(k, s0)
        out["steps_per_sec"] = steps / wall; out["config"] = {"solver": self.solver, "xpbd_iterations": 10 if self.solver == "xpbd" else None}
        return out


class NewtonXPBD(_Newton):
    name = "newton_xpbd"; solver = "xpbd"


class NewtonMuJoCo(_Newton):
    name = "newton_mujoco"; solver = "mujoco"
