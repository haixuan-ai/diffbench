# Reproducing published results

1. `pip install -e . mujoco` (add the engines you want; versions are in each bundle's `engine_versions`).
2. Check the spec: `python -c "from diffbench import spec; print(spec.spec_hash())"` must equal `spec_sha256` in the bundle.
3. Run: `python -m diffbench.runner --engines mujoco --out results/mine --raw`.
4. Compare with `site/bundles/*.json`. Same engine version on a different CPU can differ in the last digits; Python-only engines typically match to ~1e-12 relative.
7. Nexus: `export DIFFBENCH_NEXUS_URL=https://www.openaethos.com` and run with `--nexus http`.
6. Raw trajectories of the published accuracy bundles are in `site/raw/<bundle-id>/`: `python -m diffbench.verify site/bundles/<id>.json --rescore site/raw/<id>` recomputes every metric. For Nexus, each raw file is the full API response, so `python -m diffbench.attest <(zcat site/raw/<id>/raw-nexus_pgs-free_fall-240.json.gz) --pubkey <hex from site/KEYS.md>` checks the Ed25519 attestation offline.
7. Nexus: set `DIFFBENCH_NEXUS_URL` and run with `--nexus http`.
8. Hidden set: `--hidden-seed <revealed seed>`.
Bundles disagree with your re-run? Open an issue with both bundles; we will publish the discrepancy.

Note: two Nexus bundles list `nexus (local build, entrant=…)` as engine version. That means the vendor produced them through an internal runner before the hosted API existed; the hosted API was later checked to reproduce those metrics (see HOSTED_API.md). New Nexus bundles record the API `engine_build` fingerprint instead.
