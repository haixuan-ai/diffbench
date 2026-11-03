# Changelog

## 0.1.0 (initial public release)
* Result bundles re-issued on 2026-11-02 with raw trajectories (`site/raw/`); the previous 9 accuracy bundles are kept in `site/history/pre-raw-*`. All metrics reproduced the earlier bundles to <1e-6 relative, **except Brax(generalized) `pendulum_hinge` `energy_drift_rel`**: the earlier bundle (0.748) was produced before an adapter fix (hinge COM-velocity conversion) and was never regenerated; the corrected values are 2.9e-2 / 7.0e-3 / 1.7e-3 at dt = 1/60, 1/240, 1/1000. Pass/fail counts are unchanged (Brax still 4/10; pendulum COM error 5.6 mm still exceeds 5 mm).
* Nexus bundles now record the hosted-API engine build (`nexus-f2ca9e94428b90e2`) instead of "local build".
* Hosted API: responses carry an Ed25519 signature (offline-verifiable with `diffbench.attest`); the public key is published at `/info`.
* Fixed: `runner --raw` crashed on numpy float32 values in an adapter's `config` (Newton adapters); Nexus HTTP adapter backs off on HTTP 429.
* Spec 0.1.0: 10 scenarios, `spec_sha256 = 3d6ecebe82b2ba79…`.
* 9 entrants in the first bundles: MuJoCo, MJX, MuJoCo-Warp, Newton(XPBD), Newton(MuJoCo), Brax(generalized), Drake, Nexus(PGS), Nexus(DiffRigid).
* Added: `--lang en|zh` for report/publish, engine-free self-tests, HTTP-only Nexus adapter.
* Removed from the public copy: the internal local Nexus bridge (not applicable to a source-closed engine).
