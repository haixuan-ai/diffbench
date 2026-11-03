"""场景规格（引擎无关，z-up，SI 单位，四元数 wxyz）。

设计原则：
- 每个场景都有解析/高精度数值真值（见 truth.py），不存在"以某个引擎输出作为参考"的场景。
- 所有参赛引擎使用同一份场景：几何、质量、摩擦系数、重力、时间步长相同（Protocol B 参数对齐）。
- 摩擦：地面与物体取相同 mu，组合规则下有效 mu 即该值；无滚动/扭转摩擦、无恢复系数（接触为非弹性）。
"""
from __future__ import annotations
import hashlib, json, math

G = 9.81
SPEC_VERSION = "0.1.0"
DEFAULT_DT = 1.0 / 240.0


def _box(i, half, mass, pos, **kw):
    return {"id": i, "shape": {"type": "box", "half": list(half)}, "mass": mass, "pos": list(pos), **kw}


def _sphere(i, r, mass, pos, **kw):
    return {"id": i, "shape": {"type": "sphere", "radius": r}, "mass": mass, "pos": list(pos), **kw}


def scenarios() -> list[dict]:
    th = math.radians(20.0)
    return [
        {"id": "free_fall", "title": "自由落体", "kind": "ballistic", "duration": 1.0, "gravity": [0, 0, -G], "ground": None, "friction": 0.0,
         "bodies": [_box("b", (0.1, 0.1, 0.1), 1.0, (0, 0, 5.0))], "hinge": None,
         "tol": {"pos_err_max_m": 1e-3, "vel_err_max_mps": 1e-2}, "dts": [1 / 60, DEFAULT_DT, 1 / 1000]},
        {"id": "projectile_spin", "title": "抛射+匀速自旋球", "kind": "ballistic", "duration": 1.0, "gravity": [0, 0, -G], "ground": None, "friction": 0.0,
         "bodies": [_sphere("b", 0.1, 1.0, (0, 0, 10.0), vel=[3, 1, 4], angvel=[2, -3, 5])], "hinge": None,
         "tol": {"pos_err_max_m": 1e-3, "vel_err_max_mps": 1e-2, "angvel_err_max_rps": 1e-3}},
        {"id": "torque_free_asym", "title": "无力矩非对称刚体（中间轴翻转）", "kind": "torque_free", "duration": 2.0, "gravity": [0, 0, 0], "ground": None, "friction": 0.0,
         "bodies": [_box("b", (0.5, 0.2, 0.1), 2.0, (0, 0, 3.0), angvel=[0.2, 6.0, 0.3])], "hinge": None,
         "tol": {"orient_err_deg_max": 2.0, "energy_drift_rel": 1e-3, "angmom_drift_rel": 1e-3, "com_drift_m": 1e-6}},
        {"id": "coulomb_slide", "title": "库仑滑行停距", "kind": "slide", "duration": 1.0, "gravity": [0, 0, -G], "ground": {"friction": 0.5}, "friction": 0.5,
         "bodies": [_box("b", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.1), vel=[2.0, 0, 0])], "hinge": None,
         "tol": {"stop_dist_rel_err": 0.02, "residual_speed_mps": 1e-2, "z_err_max_m": 2e-3}},
        {"id": "incline_slide", "title": "斜面滑动（重力分解，μ<tanθ）", "kind": "incline", "duration": 1.0,
         "gravity": [G * math.sin(th), 0, -G * math.cos(th)], "ground": {"friction": 0.3}, "friction": 0.3,
         "bodies": [_box("b", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.1))], "hinge": None,
         "tol": {"slope_pos_rel_err": 0.02, "z_err_max_m": 2e-3}},
        {"id": "box_rest", "title": "静置盒体（接触平衡）", "kind": "rest", "duration": 2.0, "gravity": [0, 0, -G], "ground": {"friction": 0.5}, "friction": 0.5,
         "bodies": [_box("b", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.1))], "hinge": None,
         "tol": {"z_err_max_m": 1e-3, "lateral_drift_m": 1e-3, "speed_max_mps": 1e-2}},
        {"id": "box_drop", "title": "盒体下落（静止高度，非弹性）", "kind": "drop", "duration": 2.0, "gravity": [0, 0, -G], "ground": {"friction": 0.5}, "friction": 0.5,
         "bodies": [_box("b", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.6))], "hinge": None,
         "tol": {"final_z_err_m": 2e-3, "final_speed_mps": 1e-2, "max_rebound_m": 0.02}},
        {"id": "sphere_slide_to_roll", "title": "球体滑动→纯滚动（摩擦力矩耦合）", "kind": "roll", "duration": 1.0, "gravity": [0, 0, -G], "ground": {"friction": 0.5}, "friction": 0.5,
         "bodies": [_sphere("b", 0.1, 1.0, (0, 0, 0.1), vel=[2.0, 0, 0])], "hinge": None,
         "tol": {"final_v_rel_err": 0.03, "roll_resid_rel": 0.03, "x_end_rel_err": 0.03}},
        {"id": "stack5", "title": "五层盒体堆叠静置", "kind": "stack", "duration": 2.0, "gravity": [0, 0, -G], "ground": {"friction": 0.5}, "friction": 0.5,
         "bodies": [_box(f"b{k}", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.1 + 0.2 * k)) for k in range(5)], "hinge": None,
         "tol": {"top_z_err_m": 5e-3, "lateral_drift_m": 5e-3, "speed_max_mps": 5e-2}},
        {"id": "pendulum_hinge", "title": "铰链复摆（水平释放，大摆幅）", "kind": "pendulum", "duration": 3.0, "gravity": [0, 0, -G], "ground": None, "friction": 0.0,
         "bodies": [_box("rod", (0.5, 0.05, 0.05), 1.0, (0.5, 0, 2.0))], "hinge": {"body": "rod", "pivot": [0, 0, 2.0], "axis": [0, 1, 0]},
         "tol": {"com_pos_err_max_m": 5e-3, "energy_drift_rel": 1e-2}, "dts": [1 / 60, DEFAULT_DT, 1 / 1000]},
    ]


def spec_hash() -> str:
    return hashlib.sha256(json.dumps(scenarios(), sort_keys=True).encode()).hexdigest()


def sample_every(dt: float) -> int:
    return max(1, round(0.01 / dt))


# ───────── Phase 3：隐藏测试集（承诺-揭示） ─────────
def seed_commitment(seed: str) -> str:
    """组织方先公布 sha256(seed)；评测窗口结束后公布 seed，任何人可核对承诺并本地复现全部隐藏变体。"""
    return hashlib.sha256(seed.encode()).hexdigest()


def hidden_variants(seed: str) -> list[dict]:
    """由 seed 确定性生成的公开场景变体（质量/摩擦/初速/高度/杆长/斜面角度被扰动）。
    变体场景 id 以 ~h 结尾，复用同一套解析真值（truth.py 对场景参数是通用的）。无扰动的场景不进入隐藏集。"""
    import random
    rnd = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
    u = lambda a, b: round(rnd.uniform(a, b), 4)
    out = []
    for sc in scenarios():
        s = json.loads(json.dumps(sc)); s["id"] += "~h"; s["title"] += "（隐藏变体）"; s.pop("dts", None)
        b0 = s["bodies"][0]; sid = sc["id"]
        if sid == "free_fall":
            b0["pos"][2] = u(3, 8); b0["mass"] = u(0.5, 3)
        elif sid == "projectile_spin":
            b0["vel"] = [u(-4, 4), u(-4, 4), u(0, 6)]; b0["angvel"] = [u(-5, 5), u(-5, 5), u(-5, 5)]
        elif sid == "torque_free_asym":
            b0["angvel"] = [u(0.1, 0.5), u(4, 8), u(0.1, 0.5)]
        elif sid == "coulomb_slide":
            mu = u(0.25, 0.8); s["friction"] = mu; s["ground"]["friction"] = mu; b0["vel"] = [u(1.2, 2.5), 0, 0]
        elif sid == "incline_slide":
            th = math.radians(u(18, 30)); mu = u(0.15, 0.3); s["gravity"] = [G * math.sin(th), 0, -G * math.cos(th)]; s["friction"] = mu; s["ground"]["friction"] = mu
        elif sid == "box_drop":
            b0["pos"][2] = u(0.3, 1.0)
        elif sid == "sphere_slide_to_roll":
            mu = u(0.3, 0.7); s["friction"] = mu; s["ground"]["friction"] = mu; b0["vel"] = [u(1.5, 3.0), 0, 0]
        elif sid == "stack5":
            n = rnd.choice([3, 4, 6]); s["bodies"] = [_box(f"b{k}", (0.1, 0.1, 0.1), 1.0, (0, 0, 0.1 + 0.2 * k)) for k in range(n)]
        elif sid == "pendulum_hinge":
            hx = u(0.3, 0.7); s["bodies"] = [_box("rod", (hx, 0.05, 0.05), u(0.5, 2.0), (hx, 0, 2.0))]
        elif sid in ("box_rest",):
            mu = u(0.3, 0.9); s["friction"] = mu; s["ground"]["friction"] = mu; b0["mass"] = u(0.5, 5)
        out.append(s)
    return out
