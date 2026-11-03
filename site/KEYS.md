# Attestation public keys

Nexus responses are signed with Ed25519 (see docs/HOSTED_API.md). Verify offline: `python -m diffbench.attest <response.json> --pubkey <hex>`.

| key_id | public key (hex) | environment | first used | status |
|---|---|---|---|---|
| ed25519:d2081026064d4cd3 | c60e18becbce2b6e6f47778b8c291261526474d76d361b56714cc542114cefc3 | development server (used to produce the bundles in `site/bundles` dated 2026-11-02) | 2026-11-02 | active for those bundles |
| ed25519:d2081026064d4cd3 | c60e18becbce2b6e6f47778b8c291261526474d76d361b56714cc542114cefc3 | production, https://www.openaethos.com/ (identical to the development key: same server secret) | 2026-11-02 | active; confirmed from `GET /api/public/diffbench/info` after the production deployment |

Production check (2026-11-02): `/info` returns the same key and engine build (`nexus-f2ca9e94428b90e2`) as the bundles; `nexus_pgs` free_fall (3 dt) and box_rest re-run against production reproduced the published metrics exactly, and the 4 raw responses verified offline. A full production re-run of both entrants (28 runs) matched the published bundles exactly and all 28 raw responses verified; see PROD_VERIFICATION.md. If the server secret is rotated the key changes; add the new key as a new row and keep this one.
