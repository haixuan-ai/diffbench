"""Engine-free self-tests for the public scorer. Run: python -m unittest discover -s tests -v

No physics engine is needed: a "perfect" trajectory is generated from the closed-form truth and
must score ~0 error; a deliberately wrong trajectory must fail the public tolerance.
"""
import gzip, hashlib, json, os, tempfile, unittest
import numpy as np
from diffbench import spec, truth, verify, report, attest

EXPECTED_SPEC_SHA256_PREFIX = "3d6ecebe82b2ba79"  # v0.1.0; changing any scenario changes this on purpose


def ballistic_states(sc, dt, bias=0.0):
    b = sc["bodies"][0]; g = np.array(sc["gravity"]); p0 = np.array(b["pos"]); v0 = np.array(b.get("vel", [0, 0, 0])); w0 = list(b.get("angvel", [0, 0, 0]))
    ts = np.arange(0, sc["duration"] + 1e-12, dt * spec.sample_every(dt))
    return {"t": ts.tolist(), "pos": [[(p0 + v0 * t + 0.5 * g * t * t + bias).tolist()] for t in ts], "quat": [[[1, 0, 0, 0]]] * len(ts),
            "vel": [[(v0 + g * t).tolist()] for t in ts], "angvel": [[w0]] * len(ts), "steps_per_sec": 1.0, "config": {}}


class SpecTests(unittest.TestCase):
    def test_spec_hash_stable(self):
        self.assertTrue(spec.spec_hash().startswith(EXPECTED_SPEC_SHA256_PREFIX))

    def test_ten_scenarios_have_tolerances(self):
        scs = spec.scenarios(); self.assertEqual(len(scs), 10)
        for s in scs: self.assertTrue(s["tol"], s["id"])

    def test_seed_commitment(self):
        self.assertEqual(spec.seed_commitment("abc"), hashlib.sha256(b"abc").hexdigest())

    def test_hidden_variants_deterministic_and_seed_dependent(self):
        a = spec.hidden_variants("seed-1"); b = spec.hidden_variants("seed-1"); c = spec.hidden_variants("seed-2")
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertNotEqual(json.dumps(a, sort_keys=True), json.dumps(c, sort_keys=True))
        self.assertTrue(all(s["id"].endswith("~h") for s in a))


class TruthTests(unittest.TestCase):
    def test_perfect_ballistic_scores_zero(self):
        for sid in ("free_fall", "projectile_spin"):
            sc = next(s for s in spec.scenarios() if s["id"] == sid)
            m = truth.evaluate(sc, ballistic_states(sc, spec.DEFAULT_DT))["metrics"]
            for k, v in m.items(): self.assertLess(v, 1e-9, (sid, k))

    def test_biased_trajectory_fails_tolerance(self):
        sc = next(s for s in spec.scenarios() if s["id"] == "free_fall")
        m = truth.evaluate(sc, ballistic_states(sc, spec.DEFAULT_DT, bias=0.05))["metrics"]
        self.assertGreater(m["pos_err_max_m"], sc["tol"]["pos_err_max_m"])

    def test_nan_is_error_not_score(self):
        sc = next(s for s in spec.scenarios() if s["id"] == "free_fall"); st = ballistic_states(sc, spec.DEFAULT_DT); st["pos"][3][0][0] = float("nan")
        self.assertIn("error", truth.evaluate(sc, st))

    def test_convergence_order_first_order_and_second_order(self):
        dts = [1 / 60, 1 / 240, 1 / 1000]
        self.assertAlmostEqual(truth.convergence_order(dts, [d for d in dts]), 1.0, places=2)
        self.assertAlmostEqual(truth.convergence_order(dts, [d * d for d in dts]), 2.0, places=2)


class BundleTests(unittest.TestCase):
    def _bundle(self, d):
        from diffbench.runner import sign
        sc = next(s for s in spec.scenarios() if s["id"] == "free_fall"); st = ballistic_states(sc, spec.DEFAULT_DT)
        ev = truth.evaluate(sc, st)
        core = {"spec_sha256": spec.spec_hash(), "results": [{"engine": "perfect", "scenario": "free_fall", "dt": spec.DEFAULT_DT, "metrics": ev["metrics"]}]}
        with gzip.open(os.path.join(d, f"raw-perfect-free_fall-{round(1 / spec.DEFAULT_DT)}.json.gz"), "wt") as f: json.dump(st, f)
        p = os.path.join(d, "bundle.json"); json.dump({**core, "signature": sign(core)}, open(p, "w")); return p, core

    def test_verify_roundtrip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as d:
            p, core = self._bundle(d); r = verify.check(p, raw_dir=d)
            self.assertTrue(r["sha256_ok"]); self.assertEqual(r["rescored_runs"], 1); self.assertEqual(r["rescore_mismatches"], [])
            b = json.load(open(p)); b["results"][0]["metrics"]["pos_err_max_m"] = 123.0; json.dump(b, open(p, "w"))
            self.assertFalse(verify.check(p)["sha256_ok"])

    def test_rescore_detects_edited_metrics_with_recomputed_hash(self):
        from diffbench.runner import sign
        with tempfile.TemporaryDirectory() as d:
            p, core = self._bundle(d); core["results"][0]["metrics"]["pos_err_max_m"] = 0.5
            json.dump({**core, "signature": sign(core)}, open(p, "w"))
            r = verify.check(p, raw_dir=d); self.assertTrue(r["sha256_ok"]); self.assertEqual(len(r["rescore_mismatches"]), 1)


class ReportTests(unittest.TestCase):
    def test_every_metric_has_both_labels(self):
        keys = {k for s in spec.scenarios() for k in s["tol"]}
        self.assertFalse(keys - set(report.METRIC_LABEL)); self.assertFalse(keys - set(report.METRIC_LABEL_EN))


class AttestTests(unittest.TestCase):
    def test_rfc8032_vector1(self):
        pub = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
        sig = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
        self.assertTrue(attest.ed25519_verify(pub, b"", sig))
        self.assertFalse(attest.ed25519_verify(pub, b"x", sig))

    def test_js_number_formatting(self):
        for x, e in ((1e-7, "1e-7"), (1.5e-7, "1.5e-7"), (1e21, "1e+21"), (0.000001, "0.000001"), (100.0, "100"), (1.2345e-5, "0.000012345"), (-2.5, "-2.5")):
            self.assertEqual(attest.js_num(x), e)

    def test_canonical_sorted_compact(self):
        self.assertEqual(attest.canonical({"b": 1, "a": [1, {"d": "x", "c": None}]}), '{"a":[1,{"c":null,"d":"x"}],"b":1}')


class NoClosedCodeTests(unittest.TestCase):
    def test_repo_ships_no_engine_bridge(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for dp, _, fs in os.walk(root):
            if ".git" in dp: continue
            for f in fs:
                self.assertNotIn("nexus_bridge", f)
                if f.endswith(".py") and "tests" not in dp:
                    self.assertNotIn("nexus_bridge", open(os.path.join(dp, f)).read(), f)


if __name__ == "__main__":
    unittest.main()
