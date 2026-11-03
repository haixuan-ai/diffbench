# Production verification (2026-11-02)

Target: https://www.openaethos.com (hosted API), engine build `nexus-f2ca9e94428b90e2`, key `ed25519:d2081026064d4cd3`.

* Re-ran both Nexus entrants (nexus_pgs, nexus_diffrigid) over the full public accuracy set against the production API: **28 runs, 28 identical** to the metrics in the published bundles (`68b2f0ee1892c987`, `722f72444e42aad1`), 0 errors.
* The 28 raw responses were verified offline with `python -m diffbench.attest --pubkey c60e18be…cefc3`: **28 / 28 valid**.
* Rate limit: documented as 6 requests/min/IP. Observed: the development server returns HTTP 429 from the 7th request; the production endpoint returned no 429 in 25 consecutive requests (400 for an empty body). **The documented limit is not reliably enforced in production** (likely per-instance counters under autoscale, or a proxy-address issue); it must be fixed or the documentation changed before launch. The platform applied its own limit of 1000 requests/min.
* Availability: no uptime commitment has been measured or decided; docs say "best effort".
