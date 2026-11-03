"""Drake MultibodyPlant（离散时间步=dt，点接触模型，默认离散求解器）。"""
from __future__ import annotations
import time
import numpy as np
from .base import Adapter, empty_states
from ..spec import sample_every


class Drake(Adapter):
    name = "drake"
    def version(self):
        from importlib.metadata import version
        return f"drake {version('drake')} (point contact, discrete)"
    def available(self):
        try:
            import pydrake.all  # noqa
            return True, ""
        except Exception as e:
            return False, str(e)[:120]
    def run(self, sc, dt):
        from pydrake.all import (DiagramBuilder, AddMultibodyPlantSceneGraph, RigidTransform, SpatialInertia, UnitInertia, Box, Sphere, HalfSpace,
                                 CoulombFriction, Simulator, RevoluteJoint, FixedOffsetFrame, SpatialVelocity, RotationMatrix, ContactModel, Quaternion)
        builder = DiagramBuilder(); plant, sg = AddMultibodyPlantSceneGraph(builder, time_step=dt)
        plant.set_contact_model(ContactModel.kPoint)
        plant.mutable_gravity_field().set_gravity_vector(np.array(sc["gravity"], float))
        mu = sc["friction"]; bodies = []
        if sc.get("ground"):
            plant.RegisterCollisionGeometry(plant.world_body(), RigidTransform(), HalfSpace(), "ground", CoulombFriction(sc["ground"]["friction"], sc["ground"]["friction"]))
        for b in sc["bodies"]:
            s = b["shape"]; m = b["mass"]
            if s["type"] == "box":
                h = s["half"]; L = [2 * x for x in h]
                I = SpatialInertia.SolidBoxWithDensity if False else SpatialInertia(m, np.zeros(3), UnitInertia.SolidBox(*L))
                geom = Box(*L)
            else:
                I = SpatialInertia(m, np.zeros(3), UnitInertia.SolidSphere(s["radius"])); geom = Sphere(s["radius"])
            body = plant.AddRigidBody(b["id"], I)
            plant.RegisterCollisionGeometry(body, RigidTransform(), geom, b["id"] + "_col", CoulombFriction(mu, mu))
            if sc.get("hinge") and sc["hinge"]["body"] == b["id"]:
                pv = np.array(sc["hinge"]["pivot"], float); com = np.array(b["pos"], float)
                fp = plant.AddFrame(FixedOffsetFrame("hp", plant.world_frame(), RigidTransform(pv)))
                fc = plant.AddFrame(FixedOffsetFrame("hc", body.body_frame(), RigidTransform(pv - com)))
                plant.AddJoint(RevoluteJoint("hj", fp, fc, np.array(sc["hinge"]["axis"], float), -1e9, 1e9, 0.0))
            bodies.append(body)
        plant.Finalize(); diagram = builder.Build(); sim = Simulator(diagram); ctx = sim.get_mutable_context(); pctx = plant.GetMyMutableContextFromRoot(ctx)
        for b, body in zip(sc["bodies"], bodies):
            if sc.get("hinge") and sc["hinge"]["body"] == b["id"]:
                continue
            q = b.get("quat", [1, 0, 0, 0]); X = RigidTransform(RotationMatrix(Quaternion(q[0], q[1], q[2], q[3])), np.array(b["pos"], float))
            plant.SetFreeBodyPose(pctx, body, X)
            plant.SetFreeBodySpatialVelocity(body, SpatialVelocity(np.array(b.get("angvel", [0, 0, 0]), float), np.array(b.get("vel", [0, 0, 0]), float)), pctx)
        steps = round(sc["duration"] / dt); se = sample_every(dt); out = empty_states(); wall = 0.0
        def rec(k):
            P, Q, V, W = [], [], [], []
            for body in bodies:
                X = plant.EvalBodyPoseInWorld(pctx, body); sv = plant.EvalBodySpatialVelocityInWorld(pctx, body)
                P.append(X.translation().tolist()); Q.append(X.rotation().ToQuaternion().wxyz().tolist())
                W.append(sv.rotational().tolist()); V.append(sv.translational().tolist())
            out["t"].append(k * dt); out["pos"].append(P); out["quat"].append(Q); out["vel"].append(V); out["angvel"].append(W)
        rec(0)
        for k in range(1, steps + 1):
            t0 = time.perf_counter(); sim.AdvanceTo(k * dt); wall += time.perf_counter() - t0
            if k % se == 0 or k == steps: rec(k)
        out["steps_per_sec"] = steps / wall; out["config"] = {"contact_model": "point", "discrete_solver": "default(SAP)", "note": "Drake 点接触对 box 几何每对只给单个接触点，未按文献常用做法改用角点小球；这是默认能力的真实表现"}
        return out
