"""CLI：python -m diffbench.runner --engines mujoco,newton_xpbd,nexus_pgs --out results/run1 [--nexus http] [--only free_fall,...]

对每个 (引擎, 场景, dt) 运行 → 用 truth.evaluate 对解析真值打分 → 写结果包 bundle.json（含环境、版本、规格哈希、签名）。
不产生综合分；报告按维度逐项列出。引擎运行失败/不支持如实记录为 error，不填默认值。
"""
from __future__ import annotations
import argparse, datetime, gzip, hashlib, hmac, json, os, platform, subprocess, sys, time, traceback
from . import __version__, spec, truth
from .adapters import REGISTRY, HTTP_NEXUS


def host_info() -> dict:
    cpu = ""
    try:
        cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
    except Exception:
        cpu = platform.processor()
    return {"cpu": cpu, "cores": os.cpu_count(), "os": platform.platform(), "python": platform.python_version(), "gpu": "none (CPU track)"}


def sign(bundle_core: dict) -> dict:
    payload = json.dumps(bundle_core, sort_keys=True, separators=(",", ":")).encode()
    sig = {"sha256": hashlib.sha256(payload).hexdigest()}
    key = os.environ.get("DIFFBENCH_SIGN_KEY")
    if key:
        sig["hmac_sha256"] = hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()
    return sig


def _jsonable(o):
    """numpy scalars/arrays (e.g. float32 in adapter `config`) -> plain JSON types."""
    if hasattr(o, "tolist"): return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o).__name__}")


def resolve(names, nexus_mode):
    out = []
    for n in names:
        if n in REGISTRY: out.append(REGISTRY[n]())
        elif n in HTTP_NEXUS and nexus_mode == "http": out.append(HTTP_NEXUS[n]())
        else: raise SystemExit(f"unknown engine/mode: {n} (nexus mode={nexus_mode})")
    return out


def run_all(engines, only, out_dir, keep_raw=False, scenarios=None, sweep=True, hidden_seed=""):
    scs = scenarios if scenarios is not None else spec.scenarios()
    scs = [s for s in scs if not only or s["id"] in only]
    results = []; versions = {}
    os.makedirs(out_dir, exist_ok=True)
    for eng in engines:
        ok, why = eng.available()
        versions[eng.name] = eng.version() if ok else f"unavailable: {why}"
        if not ok:
            for sc in scs: results.append({"engine": eng.name, "scenario": sc["id"], "dt": spec.DEFAULT_DT, "error": f"engine unavailable: {why}"})
            continue
        for sc in scs:
            for dt in (sc.get("dts") if sweep and sc.get("dts") else [spec.DEFAULT_DT]):
                rec = {"engine": eng.name, "scenario": sc["id"], "dt": dt}
                try:
                    t0 = time.time(); st = eng.run(sc, dt); rec["wall_s"] = round(time.time() - t0, 2)
                    ev = truth.evaluate(sc, st)
                    if "error" in ev: rec["error"] = ev["error"]
                    else:
                        rec["metrics"] = {k: (float(v) if v == v else None) for k, v in ev["metrics"].items()}
                        rec["pass"] = {k: (bool(v <= sc["tol"][k]) if (k in sc["tol"] and v is not None) else None) for k, v in rec["metrics"].items()}
                    rec["steps_per_sec"] = st.get("steps_per_sec"); rec["config"] = st.get("config", {})
                    if keep_raw:
                        with gzip.open(os.path.join(out_dir, f"raw-{eng.name}-{sc['id']}-{round(1/dt)}.json.gz"), "wt") as f: json.dump(st, f, default=_jsonable)
                except Exception:
                    rec["error"] = traceback.format_exc()[-500:]
                results.append(rec)
                m = rec.get("metrics"); print(f"[{eng.name}] {sc['id']} dt=1/{round(1/dt)}: " + (json.dumps({k: (None if v is None else float(f'{v:.3g}')) for k, v in m.items()}) if m else "ERROR " + rec["error"].splitlines()[-1][:100]), file=sys.stderr, flush=True)
    # 收敛阶（只对有 dts 扫描的场景、且误差指标）
    conv = []
    for sc in scs:
        if not (sweep and sc.get("dts")): continue
        key = {"free_fall": "pos_err_max_m", "pendulum_hinge": "com_pos_err_max_m"}.get(sc["id"])
        for eng in engines:
            rs = [r for r in results if r["engine"] == eng.name and r["scenario"] == sc["id"] and r.get("metrics")]
            if key and len(rs) >= 3:
                conv.append({"engine": eng.name, "scenario": sc["id"], "metric": key, "order": truth.convergence_order([r["dt"] for r in rs], [r["metrics"][key] for r in rs])})
    core = {"track": "accuracy_hidden" if hidden_seed else "accuracy", "hidden_seed_commitment": spec.seed_commitment(hidden_seed) if hidden_seed else None, "diffbench_version": __version__, "spec_version": spec.SPEC_VERSION, "spec_sha256": spec.spec_hash(),
            "date_utc": datetime.datetime.utcnow().isoformat() + "Z", "host": host_info(), "engine_versions": versions, "scenario_meta": {sc["id"]: {"title": sc["title"], "tol": sc["tol"]} for sc in scs}, "results": results, "convergence": conv}
    bundle = {**core, "signature": sign(core)}
    with open(os.path.join(out_dir, "bundle.json"), "w") as f: json.dump(bundle, f, indent=1)
    return bundle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engines", default="mujoco"); ap.add_argument("--only", default=""); ap.add_argument("--out", required=True)
    ap.add_argument("--hidden-seed", default="", help="revealed hidden-set seed; evaluates hidden variants instead of the public scenarios")
    ap.add_argument("--nexus", default="http", choices=["http"]); ap.add_argument("--raw", action="store_true"); ap.add_argument("--no-sweep", action="store_true")
    a = ap.parse_args()
    scs = spec.hidden_variants(a.hidden_seed) if a.hidden_seed else None
    run_all(resolve(a.engines.split(","), a.nexus), [s for s in a.only.split(",") if s], a.out, a.raw, scenarios=scs, sweep=not a.no_sweep and not a.hidden_seed, hidden_seed=a.hidden_seed)


if __name__ == "__main__":
    main()
