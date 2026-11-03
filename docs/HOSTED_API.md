# Hosted API (Nexus entrant)

Base URL: https://www.openaethos.com (production). No account is needed for the public tier.

| Endpoint | Purpose |
|---|---|
| `GET /api/public/diffbench/info` | engine build fingerprint, limits |
| `POST /api/public/diffbench/run` | body `{entrant, scenario, dt}` → states `{t,pos,quat,vel,angvel,steps_per_sec,config}` + `attestation` |
| `POST /api/public/diffbench/verify` | body `{attestation}` → whether the attestation was issued by the service |

Limits: ≤ 12 bodies, duration ≤ 5 s, dt ≥ 0.5 ms, 6 requests/min/IP. The API returns **states only**; scoring happens on your machine.

**Attestation (Ed25519, offline-verifiable).** Each response carries `attestation = {engine_build, spec_version, request_sha256, states_sha256, issued_at, key_id, signature, hmac}`. `signature` is an Ed25519 signature over the canonical JSON (sorted keys, compact) of the attestation without `signature`/`hmac`; the public key and `key_id` are published at `/info` (`attestation_public_key`). Verify with no server and no dependencies:
```bash
python -m diffbench.attest --url https://www.openaethos.com response.json     # or --pubkey <hex>
```
This also re-hashes the states in the file against `states_sha256`. Raw files written by `runner --raw` contain the full response, so published raw trajectories can be checked the same way. The legacy `hmac` field is kept for compatibility and is verifiable only through `/verify`.

**What it proves and does not.** It proves that the holder of the signing key issued this attestation for exactly these states and this engine-build fingerprint, and that the states were not altered afterwards. It does **not** prove the engine ran unmodified, nor that the operator did not choose which runs to publish; the key is held by the operator (derived from a server secret), and rotating that secret changes the public key (old key ids will be listed in `site/KEYS.md`). Reproducibility comes from re-running: re-runs of the published Nexus bundles against the API reproduced the metrics bit-identically.
