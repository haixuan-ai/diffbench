"""Build the data file and copy artifacts for the public leaderboard page.

Usage (from the release directory):  python3 site/build_site_page.py <target_dir>
Reads site/bundles/*.json (the signed result bundles, source of truth); writes <target>/data.json and copies
bundles/raw/history/KEYS.md/PROD_VERIFICATION.md/report*.md next to it. index.html is hand-written (site/page/index.html).
"""
import glob, json, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
target = sys.argv[1]
os.makedirs(target, exist_ok=True)

TITLES_EN = {
    "free_fall": "Free fall", "projectile_spin": "Projectile + constant-spin sphere",
    "torque_free_asym": "Torque-free asymmetric body (intermediate-axis flip)", "coulomb_slide": "Coulomb sliding stop distance",
    "incline_slide": "Incline slide (gravity decomposition, μ<tanθ)", "box_rest": "Box at rest (contact equilibrium)",
    "box_drop": "Box drop (rest height, inelastic)", "sphere_slide_to_roll": "Sphere slide → pure rolling (friction-torque coupling)",
    "stack5": "Five-box stack at rest", "pendulum_hinge": "Hinged compound pendulum (horizontal release, large swing)",
}
METRICS = {  # id: (en, zh, unit)
    "pos_err_max_m": ("Max position error", "最大位置误差", "m"), "vel_err_max_mps": ("Max velocity error", "最大速度误差", "m/s"),
    "angvel_err_max_rps": ("Max angular-velocity error", "最大角速度误差", "rad/s"), "orient_err_deg_max": ("Max orientation error", "最大姿态误差", "deg"),
    "energy_drift_rel": ("Relative energy drift", "能量相对漂移", ""), "angmom_drift_rel": ("Relative angular-momentum drift", "角动量相对漂移", ""),
    "com_drift_m": ("CoM drift", "质心漂移", "m"), "stop_dist_rel_err": ("Stop-distance relative error", "停距相对误差", ""),
    "residual_speed_mps": ("Residual speed", "残余速度", "m/s"), "z_err_max_m": ("Max height error", "最大高度误差", "m"),
    "slope_pos_rel_err": ("Along-slope position rel. error", "沿斜面位置相对误差", ""), "lateral_drift_m": ("Lateral drift", "横向漂移", "m"),
    "speed_max_mps": ("Max speed", "最大速度", "m/s"), "final_z_err_m": ("Final height error", "末端高度误差", "m"),
    "final_speed_mps": ("Final speed", "末端速度", "m/s"), "max_rebound_m": ("Max rebound", "最大反弹", "m"),
    "final_v_rel_err": ("Final velocity rel. error", "末速度相对误差", ""), "roll_resid_rel": ("Rolling residual (rel.)", "纯滚动残差(相对)", ""),
    "x_end_rel_err": ("End position rel. error", "终点位置相对误差", ""), "top_z_err_m": ("Top-box height error", "顶层盒高度误差", "m"),
    "com_pos_err_max_m": ("Max CoM position error", "质心最大位置误差", "m"),
}
ENGINES = {  # id: (label, organizer-entrant?)
    "brax_generalized": ("Brax (generalized)", False), "drake": ("Drake", False), "mjx": ("MJX", False), "mujoco": ("MuJoCo", False),
    "mujoco_warp": ("MuJoCo-Warp", False), "newton_mujoco": ("Newton (MuJoCo solver)", False), "newton_xpbd": ("Newton (XPBD)", False),
    "nexus_diffrigid": ("Nexus DiffRigid", True), "nexus_pgs": ("Nexus PGS", True),
}

out = {"scenarios": [], "engines": [], "results": {}, "convergence": [], "spec_sha256": None, "date_utc": None, "host": None, "diffbench_version": None, "hidden": None}
scen = {}
for p in sorted(glob.glob(os.path.join(ROOT, "bundles", "*.json"))):
    b = json.load(open(p)); fid = os.path.basename(p)[:-5]
    if b["track"] == "accuracy_hidden":
        out["hidden"] = {"bundle": fid, "commitment": b["hidden_seed_commitment"], "engines": list(b["engine_versions"]), "date_utc": b["date_utc"]}
        continue
    out["spec_sha256"] = b["spec_sha256"]; out["host"] = b["host"]; out["diffbench_version"] = b["diffbench_version"]
    out["date_utc"] = max(filter(None, [out["date_utc"], b["date_utc"]]))
    for sid, m in b["scenario_meta"].items():
        scen[sid] = {"id": sid, "title_zh": m["title"], "title_en": TITLES_EN[sid], "tol": m["tol"]}
    for eng, ver in b["engine_versions"].items():
        sha = b["signature"]["sha256"]
        out["engines"].append({"id": eng, "label": ENGINES[eng][0], "organizer_entrant": ENGINES[eng][1], "version": ver, "bundle": fid, "sha256": sha, "date_utc": b["date_utc"]})
    for r in b["results"]:
        slot = out["results"].setdefault(r["engine"], {}).setdefault(r["scenario"], {})
        if "metrics" not in r:
            slot[str(round(1 / r["dt"]))] = {"error": r.get("error", "error")[-120:]}
            continue
        slot[str(round(1 / r["dt"]))] = {"metrics": r["metrics"], "pass": r["pass"], "steps_per_sec": r.get("steps_per_sec"), "wall_s": r.get("wall_s")}
    out["convergence"] += b.get("convergence", [])
out["scenarios"] = [scen[k] for k in TITLES_EN if k in scen]
out["metrics"] = {k: {"en": v[0], "zh": v[1], "unit": v[2]} for k, v in METRICS.items()}
# Display version for Haixuan's own engine: signed bundles keep the raw build id (unchanged); the page shows the release version.
NEXUS_DISPLAY_VERSION = "nexus 1.1.0"
for e in out["engines"]:
    if e["id"].startswith("nexus_"):
        e["build"] = e["version"]; e["version"] = NEXUS_DISPLAY_VERSION
out["engines"].sort(key=lambda e: e["id"])
json.dump(out, open(os.path.join(target, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))

for d in ("bundles", "raw", "history"):
    dst = os.path.join(target, d)
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(os.path.join(ROOT, d), dst)
for f in ("KEYS.md", "PROD_VERIFICATION.md", "report.md", "report.en.md", "leaderboard.json"):
    shutil.copy(os.path.join(ROOT, f), os.path.join(target, f))
shutil.copy(os.path.join(ROOT, "page", "index.html"), os.path.join(target, "index.html"))
shutil.copy(os.path.join(ROOT, "page", "logo.png"), os.path.join(target, "logo.png"))
print("built", target, len(out["engines"]), "engine rows,", len(out["scenarios"]), "scenarios")
