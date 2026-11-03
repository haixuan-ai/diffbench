"""校验结果包：python -m diffbench.verify bundle.json [--key KEY] [--rescore raw_dir]
1) 重算 sha256（内容未被改动）；2) 若提供密钥，校验 HMAC（组织方签发的包）；
3) --rescore：用原始状态（--raw 产生的 raw-*.json.gz）按公开真值重新计算指标并与包内数值比对。"""
from __future__ import annotations
import argparse, glob, gzip, hashlib, hmac, json, os, sys
from . import spec, truth


def check(path, key=None, raw_dir=None, hidden_seed=""):
    b = json.load(open(path)); sig = b.pop("signature"); payload = json.dumps(b, sort_keys=True, separators=(",", ":")).encode()
    res = {"sha256_ok": hashlib.sha256(payload).hexdigest() == sig["sha256"]}
    if key and "hmac_sha256" in sig: res["hmac_ok"] = hmac.compare_digest(hmac.new(key.encode(), payload, hashlib.sha256).hexdigest(), sig["hmac_sha256"])
    res["spec_hash_matches_local"] = b["spec_sha256"] == spec.spec_hash()
    if raw_dir:
        scs = {s["id"]: s for s in (spec.hidden_variants(hidden_seed) if hidden_seed else spec.scenarios())}; bad = []; n = 0
        for r in b["results"]:
            f = os.path.join(raw_dir, f"raw-{r['engine']}-{r['scenario']}-{round(1 / r['dt'])}.json.gz")
            if not os.path.exists(f) or not r.get("metrics"): continue
            m = truth.evaluate(scs[r["scenario"]], json.load(gzip.open(f, "rt")))["metrics"]; n += 1
            if any(abs((m[k] or 0) - (r["metrics"][k] or 0)) > 1e-9 + 1e-6 * abs(m[k] or 0) for k in m if m[k] == m[k]): bad.append((r["engine"], r["scenario"]))
        res["rescored_runs"] = n; res["rescore_mismatches"] = bad
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bundle"); ap.add_argument("--key", default=os.environ.get("DIFFBENCH_SIGN_KEY")); ap.add_argument("--rescore"); ap.add_argument("--hidden-seed", default="")
    a = ap.parse_args(); r = check(a.bundle, a.key, a.rescore, a.hidden_seed); print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(0 if r["sha256_ok"] and r.get("hmac_ok", True) and not r.get("rescore_mismatches") else 1)
