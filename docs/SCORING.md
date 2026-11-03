# Scoring

For each (engine, scenario, dt) the runner stores the metrics computed by `diffbench.truth.evaluate` and a per-metric pass flag `metric ≤ tolerance`. A scenario is "all-pass" only if every metric passes. We publish counts of all-pass scenarios as a convenience, never as a score. NaN/Inf in the trajectory is an error.

Time-step convergence order is the least-squares slope of log(error) vs log(dt) at dt = 1/60, 1/240, 1/1000 for `free_fall` (position) and `pendulum_hinge` (COM position).

**Bundle integrity.** `bundle.json` has `signature.sha256` over canonical JSON (sorted keys, compact separators). `verify` checks (1) the hash, (2) the spec hash against the local spec, (3) with `--rescore <dir>` recomputes all metrics from raw trajectories (`--raw` runs write `raw-<engine>-<scenario>-<rate>.json.gz`). An optional HMAC is only meaningful to whoever holds the key; it is not a public proof.
