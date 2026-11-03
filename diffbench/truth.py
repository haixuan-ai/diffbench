"""解析/高精度数值真值与指标计算。

只读取引擎返回的统一状态（t, pos, quat, vel, angvel），参赛引擎无法影响评分口径。
状态数组形状：pos[T][B][3], quat[T][B][4] (wxyz), vel[T][B][3] (质心线速度, 世界系), angvel[T][B][3] (世界系)。
"""
from __future__ import annotations
import math
import numpy as np

G = 9.81


def inertia_body(b: dict) -> np.ndarray:
    m = b["mass"]; s = b["shape"]
    if s["type"] == "box":
        x, y, z = (2 * h for h in s["half"])
        return np.diag([m * (y * y + z * z) / 12, m * (x * x + z * z) / 12, m * (x * x + y * y) / 12])
    i = 0.4 * m * s["radius"] ** 2
    return np.diag([i, i, i])


def rotm(q) -> np.ndarray:
    w, x, y, z = np.asarray(q, float) / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def qmul(a, b):
    return np.array([a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                     a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                     a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                     a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]])


def quat_angle_deg(qa, qb) -> float:
    qa = np.asarray(qa, float) / np.linalg.norm(qa); qb = np.asarray(qb, float) / np.linalg.norm(qb)
    d = abs(float(np.dot(qa, qb)))
    return math.degrees(2 * math.acos(min(1.0, d)))


def _arr(st):
    return (np.asarray(st["t"], float), np.asarray(st["pos"], float), np.asarray(st["quat"], float),
            np.asarray(st["vel"], float), np.asarray(st["angvel"], float))


def torque_free_truth(b: dict, w0_world, times):
    """Euler 方程 + 四元数积分，RK4 h=1e-4（作为高精度数值真值）。初始姿态=单位。"""
    I = np.diag(inertia_body(b)); w = np.array(w0_world, float); q = np.array([1.0, 0, 0, 0]); t = 0.0
    def f(w, q):
        dw = np.array([(I[1] - I[2]) * w[1] * w[2] / I[0], (I[2] - I[0]) * w[2] * w[0] / I[1], (I[0] - I[1]) * w[0] * w[1] / I[2]])
        return dw, 0.5 * qmul(q, np.array([0, *w]))
    out = []
    for T in times:
        while t < T - 1e-12:
            h = min(1e-4, T - t)
            k1 = f(w, q); k2 = f(w + h / 2 * k1[0], q + h / 2 * k1[1]); k3 = f(w + h / 2 * k2[0], q + h / 2 * k2[1]); k4 = f(w + h * k3[0], q + h * k3[1])
            w = w + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); q = q + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); q /= np.linalg.norm(q); t += h
        out.append(q.copy())
    return out


def pendulum_truth(b: dict, times):
    """复摆（绕 y 轴、从水平静止释放）：θ'' = m g d cosθ / I，θ 为水平线下方角度。RK4 h=1e-5。"""
    m = b["mass"]; hx, hy, hz = b["shape"]["half"]; d = hx
    I = m * ((2 * hx) ** 2 + (2 * hz) ** 2) / 12 + m * d * d
    th, om, t = 0.0, 0.0, 0.0; out = []
    f = lambda th, om: (om, m * G * d * math.cos(th) / I)
    for T in times:
        while t < T - 1e-12:
            h = min(1e-5, T - t)
            k1 = f(th, om); k2 = f(th + h / 2 * k1[0], om + h / 2 * k1[1]); k3 = f(th + h / 2 * k2[0], om + h / 2 * k2[1]); k4 = f(th + h * k3[0], om + h * k3[1])
            th += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); om += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); t += h
        out.append((th, om))
    return out, I, d


def total_energy(sc, st, bi: int) -> np.ndarray:
    t, pos, quat, vel, angvel = _arr(st); b = sc["bodies"][bi]; m = b["mass"]; I = inertia_body(b); g = np.array(sc["gravity"], float)
    e = []
    for k in range(len(t)):
        R = rotm(quat[k, bi]); wb = R.T @ angvel[k, bi]
        e.append(0.5 * m * float(vel[k, bi] @ vel[k, bi]) + 0.5 * float(wb @ I @ wb) - m * float(g @ pos[k, bi]))
    return np.array(e)


def evaluate(sc: dict, st: dict) -> dict:
    t, pos, quat, vel, angvel = _arr(st)
    if not all(np.all(np.isfinite(a)) for a in (pos, quat, vel, angvel)):
        return {"error": "NaN/Inf in states", "metrics": {}}
    kind = sc["kind"]; b0 = sc["bodies"][0]; g = np.array(sc["gravity"], float)
    p0 = np.array(b0["pos"], float); v0 = np.array(b0.get("vel", [0, 0, 0]), float); w0 = np.array(b0.get("angvel", [0, 0, 0]), float)
    m: dict[str, float] = {}
    if kind == "ballistic":
        tt = t[:, None]
        m["pos_err_max_m"] = float(np.abs(pos[:, 0] - (p0 + v0 * tt + 0.5 * g * tt ** 2)).max())
        m["vel_err_max_mps"] = float(np.abs(vel[:, 0] - (v0 + g * tt)).max())
        if np.any(w0):
            m["angvel_err_max_rps"] = float(np.abs(angvel[:, 0] - w0).max())
    elif kind == "torque_free":
        qt = torque_free_truth(b0, w0, t)
        m["orient_err_deg_max"] = max(quat_angle_deg(quat[k, 0], qt[k]) for k in range(len(t)))
        e = total_energy(sc, st, 0); m["energy_drift_rel"] = float(np.abs(e - e[0]).max() / abs(e[0]))
        I = inertia_body(b0); L = np.array([rotm(quat[k, 0]) @ I @ rotm(quat[k, 0]).T @ angvel[k, 0] for k in range(len(t))])
        m["angmom_drift_rel"] = float(np.linalg.norm(L - L[0], axis=1).max() / np.linalg.norm(L[0]))
        m["com_drift_m"] = float(np.abs(pos[:, 0] - p0).max())
    elif kind == "slide":
        mu = sc["friction"]; v = float(np.linalg.norm(v0)); d_true = v * v / (2 * mu * G)
        m["stop_dist_rel_err"] = abs(float(pos[-1, 0, 0] - p0[0]) - d_true) / d_true
        m["residual_speed_mps"] = float(np.linalg.norm(vel[-1, 0])); m["z_err_max_m"] = float(np.abs(pos[:, 0, 2] - p0[2]).max())
    elif kind == "incline":
        mu = sc["friction"]; a = abs(g[0]) - mu * abs(g[2]); s_true = 0.5 * a * t[-1] ** 2
        m["slope_pos_rel_err"] = abs(float(pos[-1, 0, 0] - p0[0]) - s_true) / s_true; m["z_err_max_m"] = float(np.abs(pos[:, 0, 2] - p0[2]).max())
    elif kind == "rest":
        m["z_err_max_m"] = float(np.abs(pos[:, 0, 2] - p0[2]).max()); m["lateral_drift_m"] = float(np.abs(pos[:, 0, :2] - p0[:2]).max())
        m["speed_max_mps"] = float(np.linalg.norm(vel[len(t) // 2:, 0], axis=1).max())
    elif kind == "drop":
        hz = b0["shape"]["half"][2]
        m["final_z_err_m"] = float(abs(pos[-1, 0, 2] - hz)); m["final_speed_mps"] = float(np.linalg.norm(vel[-1, 0]))
        hit = np.where(pos[:, 0, 2] <= hz + 5e-3)[0]
        m["max_rebound_m"] = float(max(0.0, pos[hit[0]:, 0, 2].max() - hz)) if len(hit) else float("nan")
    elif kind == "roll":
        v = float(v0[0]); r = b0["shape"]["radius"]; mu = sc["friction"]
        t_roll = 2 * v / (7 * mu * G); v_end = 5.0 / 7.0 * v
        x_true = v * t_roll - 0.5 * mu * G * t_roll ** 2 + v_end * (t[-1] - t_roll)
        m["final_v_rel_err"] = abs(float(vel[-1, 0, 0]) - v_end) / v_end
        m["roll_resid_rel"] = abs(float(vel[-1, 0, 0]) - float(angvel[-1, 0, 1]) * r) / v_end
        m["x_end_rel_err"] = abs(float(pos[-1, 0, 0]) - x_true) / x_true
    elif kind == "stack":
        top = np.array(sc["bodies"][-1]["pos"], float)
        m["top_z_err_m"] = float(np.abs(pos[:, -1, 2] - top[2]).max()); m["lateral_drift_m"] = float(np.abs(pos[:, :, :2]).max())
        m["speed_max_mps"] = float(np.linalg.norm(vel[len(t) // 2:], axis=2).max())
    elif kind == "pendulum":
        tru, I, d = pendulum_truth(b0, t)
        com_true = np.array([[d * math.cos(th), 0.0, sc["hinge"]["pivot"][2] - d * math.sin(th)] for th, _ in tru])
        m["com_pos_err_max_m"] = float(np.linalg.norm(pos[:, 0] - com_true, axis=1).max())
        e = total_energy(sc, st, 0); m["energy_drift_rel"] = float(np.abs(e - e[0]).max() / (b0["mass"] * G * d))
    else:
        raise ValueError(kind)
    return {"metrics": m}


def convergence_order(dts, errs):
    pts = [(math.log(d), math.log(e)) for d, e in zip(dts, errs) if e and e > 0 and math.isfinite(e)]
    if len(pts) < 3:
        return None
    return float(np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)[0])
