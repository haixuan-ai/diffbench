"""发布静态榜单：python -m diffbench.publish --bundles dirs... --out site/
追加式（append-only）：每个结果包按 sha256 命名拷贝，历史包永不删除（含对我方不利的结果）；index.html 汇总最新包。"""
from __future__ import annotations
import argparse, glob, json, os, shutil
from . import report


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bundles", nargs="+", required=True); ap.add_argument("--out", required=True); ap.add_argument("--title", default=""); ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    a = ap.parse_args(); report.LANG = a.lang; a.title = a.title or report.tr("Haixuan DiffBench 榜单（精度赛道）", "Haixuan DiffBench Leaderboard (accuracy track)"); paths = [p for g in a.bundles for p in glob.glob(g)]
    os.makedirs(os.path.join(a.out, "bundles"), exist_ok=True)
    for p in paths:
        sha = json.load(open(p))["signature"]["sha256"][:16]; dst = os.path.join(a.out, "bundles", f"{sha}.json"); (None if os.path.abspath(p) == os.path.abspath(dst) else shutil.copy(p, dst))
    allp = sorted(glob.glob(os.path.join(a.out, "bundles", "*.json")))
    merged = report.load(allp); md, rows = report.build(merged, a.title)
    open(os.path.join(a.out, "index.html" if a.lang == "zh" else "index.en.html"), "w").write(report.to_html(a.title, md, rows)); open(os.path.join(a.out, "report.md" if a.lang == "zh" else "report.en.md"), "w").write(md)
    json.dump([{"file": os.path.basename(p), **{k: v for k, v in json.load(open(p)).items() if k in ("date_utc", "track", "spec_sha256", "engine_versions", "signature")}} for p in allp], open(os.path.join(a.out, "leaderboard.json"), "w"), indent=1, ensure_ascii=False)
    print("published", len(allp), "bundles")


if __name__ == "__main__":
    main()
