"""把一个或多个结果包合并成 Markdown + 静态 HTML 报告。

规则：按场景、按指标逐项列出各引擎原始数值；达标/未达标仅与场景公开容差比较；
不产生综合分、不做排名；失败/不可用如实显示；包含环境、版本、规格哈希与签名摘要。
用法：python -m diffbench.report --bundles /tmp/db/*/bundle.json --out report_dir [--title ...]
"""
from __future__ import annotations
import argparse, glob, html, json, os
from . import spec

METRIC_LABEL = {
    "pos_err_max_m": "位置最大误差 (m)", "vel_err_max_mps": "速度最大误差 (m/s)", "angvel_err_max_rps": "角速度最大误差 (rad/s)",
    "orient_err_deg_max": "姿态最大误差 (°)", "energy_drift_rel": "能量漂移(相对)", "angmom_drift_rel": "角动量漂移(相对)", "com_drift_m": "质心漂移 (m)",
    "stop_dist_rel_err": "停距相对误差", "residual_speed_mps": "残余速度 (m/s)", "z_err_max_m": "高度最大误差 (m)", "slope_pos_rel_err": "沿斜面位移相对误差",
    "lateral_drift_m": "横向漂移 (m)", "speed_max_mps": "静置最大速度 (m/s)", "final_z_err_m": "终态高度误差 (m)", "final_speed_mps": "终态速度 (m/s)",
    "max_rebound_m": "最大回弹 (m)", "final_v_rel_err": "末速度相对误差", "roll_resid_rel": "滚动约束残差(相对)", "x_end_rel_err": "末位置相对误差",
    "top_z_err_m": "顶层高度最大误差 (m)", "com_pos_err_max_m": "质心位置最大误差 (m)",
}


METRIC_LABEL_EN = {
    "pos_err_max_m": "max position error (m)", "vel_err_max_mps": "max velocity error (m/s)", "angvel_err_max_rps": "max angular-velocity error (rad/s)",
    "orient_err_deg_max": "max orientation error (deg)", "energy_drift_rel": "energy drift (relative)", "angmom_drift_rel": "angular-momentum drift (relative)", "com_drift_m": "COM drift (m)",
    "stop_dist_rel_err": "stopping-distance rel. error", "residual_speed_mps": "residual speed (m/s)", "z_err_max_m": "max height error (m)", "slope_pos_rel_err": "along-slope displacement rel. error",
    "lateral_drift_m": "lateral drift (m)", "speed_max_mps": "max speed at rest (m/s)", "final_z_err_m": "final height error (m)", "final_speed_mps": "final speed (m/s)",
    "max_rebound_m": "max rebound (m)", "final_v_rel_err": "final velocity rel. error", "roll_resid_rel": "rolling-constraint residual (rel.)", "x_end_rel_err": "final position rel. error",
    "top_z_err_m": "top-layer max height error (m)", "com_pos_err_max_m": "max COM position error (m)",
}
SCENARIO_TITLE_EN = {}  # filled from docs/SCENARIOS.md; spec.py titles stay Chinese because they are part of spec_sha256
LANG = "zh"


def tr(zh, en):
    return en if LANG == "en" else zh


def lab(k):
    return (METRIC_LABEL_EN if LANG == "en" else METRIC_LABEL).get(k, k)


def load(paths):
    merged = {"results": [], "engine_versions": {}, "convergence": [], "bundles": [], "scenario_meta": {}}
    for p in paths:
        b = json.load(open(p)); merged["results"] += b["results"]; merged["engine_versions"].update(b["engine_versions"]); merged["convergence"] += b.get("convergence", []); merged["scenario_meta"].update(b.get("scenario_meta", {}))
        merged["bundles"].append({"path": p, "date_utc": b["date_utc"], "sha256": b["signature"]["sha256"], "spec_sha256": b["spec_sha256"], "host": b["host"]})
    return merged


def fmt(v):
    if v is None: return "—"
    if v == 0: return "0"
    return f"{v:.2e}" if abs(v) < 1e-3 or abs(v) >= 1e3 else f"{v:.4g}"


def build(merged, title):
    scs = {k: v for k, v in merged["scenario_meta"].items()} or {s["id"]: s for s in spec.scenarios()}
    engines = sorted({r["engine"] for r in merged["results"]})
    md = [f"# {title}", "", tr(f"规格版本 {spec.SPEC_VERSION}（sha256 `{spec.spec_hash()[:16]}…`）。CPU 赛道；无综合分、无排名，逐指标列出原始数值。", f"Spec version {spec.SPEC_VERSION} (sha256 `{spec.spec_hash()[:16]}…`). CPU track; no composite score, no ranking; raw per-metric values."), "",
          tr("## 环境与版本","## Environment and versions"), ""]
    for e in engines: md.append(f"- **{e}**：{merged['engine_versions'].get(e, '?')}")
    for b in merged["bundles"]: md.append(f"- " + tr("结果包","bundle") + f" `{os.path.basename(os.path.dirname(b['path']))}` {b['date_utc']} · CPU {b['host']['cpu']} ×{b['host']['cores']} · sha256 `{b['sha256'][:16]}…`")
    html_rows = []
    for sid, sc in scs.items():
        rows = [r for r in merged["results"] if r["scenario"] == sid and abs(r["dt"] - spec.DEFAULT_DT) < 1e-9]
        if not rows: continue
        keys = list(sc["tol"].keys())
        md += ["", f"## {sc['title']}（`{sid}`，dt=1/240）", "", tr("| 引擎 | ","| Engine | ") + " | ".join(lab(k) for k in keys) + " |", "|---|" + "---|" * len(keys)]
        md.append(tr("| *公开容差* | ","| *public tolerance* | ") + " | ".join(fmt(sc["tol"][k]) for k in keys) + " |")
        html_rows.append((sc["title"], sid, keys, sc["tol"], []))
        for e in engines:
            r = next((x for x in rows if x["engine"] == e), None)
            if r is None: continue
            if r.get("error") or not r.get("metrics"):
                md.append(f"| {e} | " + " | ".join([tr("失败/不可用","failed / unavailable")] + [""] * (len(keys) - 1)) + " |"); html_rows[-1][4].append((e, None, r.get("error", "")[-120:])); continue
            cells = []
            for k in keys:
                v = r["metrics"].get(k); ok = r["pass"].get(k)
                cells.append(fmt(v) + ("" if ok is None else (" ✓" if ok else " ✗")))
            md.append(f"| {e} | " + " | ".join(cells) + " |"); html_rows[-1][4].append((e, r, ""))
    if merged["convergence"]:
        md += ["", tr("## 时间步收敛阶（dt = 1/60, 1/240, 1/1000 的误差对数斜率；越大收敛越快）","## Time-step convergence order (log-log slope of error at dt = 1/60, 1/240, 1/1000; larger = faster convergence)"), "", tr("| 引擎 | 场景 | 指标 | 阶 |","| Engine | Scenario | Metric | Order |"), "|---|---|---|---|"]
        for c in merged["convergence"]:
            order = "—" if c["order"] is None else format(c["order"], ".2f"); md.append(f"| {c['engine']} | {c['scenario']} | {c['metric']} | {order} |")
    md += ["", tr("## 单环境 CPU 步进速度（仅供参考，不属于精度赛道结论；若结果包由多个引擎并行跑出，受 CPU 争用影响，不可比较）","## Single-environment CPU stepping speed (informational only, not an accuracy-track result; not comparable if engines ran in parallel and contended for CPU)"), "", tr("| 引擎 | ","| Engine | ") + " | ".join(scs.keys()) + " |", "|---|" + "---|" * len(scs)]
    for e in engines:
        cells = []
        for sid in scs:
            r = next((x for x in merged["results"] if x["engine"] == e and x["scenario"] == sid and abs(x["dt"] - spec.DEFAULT_DT) < 1e-9), None)
            cells.append("—" if not r or not r.get("steps_per_sec") else f"{r['steps_per_sec']:.0f}")
        md.append(f"| {e} | " + " | ".join(cells) + " |")
    md += ["", tr("> 速度含各引擎 Python/Node 绑定开销，且 GPU 引擎（MJX/MuJoCo-Warp/Newton）在 CPU 单环境下不处于其设计工况；速度对比需另设性能赛道（分 CPU/GPU）。","> Speed includes each engine's Python/Node binding overhead, and GPU engines (MJX / MuJoCo-Warp / Newton) are outside their design regime on a single CPU environment; a speed comparison needs a separate performance track (CPU/GPU).")]
    return "\n".join(md), html_rows


def to_html(title, md_text, html_rows):
    css = "body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#1d2330}table{border-collapse:collapse;margin:.5rem 0 1.5rem;width:100%}th,td{border:1px solid #d6dae3;padding:.35rem .6rem;font-size:.9rem;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#f2f4f8}.ok{background:#e8f6ec}.bad{background:#fdeceb}.na{background:#f5f5f5;color:#888}.tol td{font-style:italic;background:#fffbe6}pre{white-space:pre-wrap;background:#f6f7f9;padding:1rem;border-radius:6px;font-size:.85rem}"
    out = [f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title><style>{css}</style><h1>{html.escape(title)}</h1>",
           tr("<p>无综合分、无排名；每个单元格为该指标相对解析/高精度数值真值的原始误差，✓/✗ 仅表示是否满足场景公开容差。</p>","<p>No composite score, no ranking. Each cell is the raw error of that metric against the analytic / high-precision numerical truth; green/red only indicates whether the public scenario tolerance is met.</p>")]
    for ttl, sid, keys, tol, rows in html_rows:
        out.append(f"<h2>{html.escape(ttl)} <small>({sid})</small></h2><table><tr><th>" + tr("引擎","Engine") + "</th>" + "".join(f"<th>{html.escape(lab(k))}</th>" for k in keys) + "</tr>")
        out.append("<tr class=tol><td>" + tr("公开容差","public tolerance") + "</td>" + "".join(f"<td>{fmt(tol[k])}</td>" for k in keys) + "</tr>")
        for e, r, err in rows:
            if r is None: out.append(f"<tr><td>{e}</td><td class=na colspan={len(keys)}>{tr('失败/不可用','failed / unavailable')} {html.escape(err)}</td></tr>"); continue
            tds = []
            for k in keys:
                v = r["metrics"].get(k); ok = r["pass"].get(k)
                tds.append(f"<td class={'na' if ok is None else ('ok' if ok else 'bad')}>{fmt(v)}</td>")
            out.append(f"<tr><td>{e}</td>{''.join(tds)}</tr>")
        out.append("</table>")
    out.append("<details><summary>" + tr("完整 Markdown 报告","Full Markdown report") + f"</summary><pre>{html.escape(md_text)}</pre></details>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bundles", nargs="+", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=""); ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    global LANG
    a = ap.parse_args(); LANG = a.lang; a.title = a.title or tr("Haixuan DiffBench 精度赛道报告（v0.1）", "Haixuan DiffBench Accuracy Track Report (v0.1)"); paths = [p for g in a.bundles for p in glob.glob(g)]
    merged = load(paths); md, rows = build(merged, a.title); os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "report.md"), "w").write(md); open(os.path.join(a.out, "index.html"), "w").write(to_html(a.title, md, rows))
    json.dump(merged, open(os.path.join(a.out, "merged.json"), "w"), indent=1); print(md)


if __name__ == "__main__":
    main()
