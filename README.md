# Haixuan DiffBench (v0.1, accuracy track)

[简体中文](README.zh-CN.md) · [Leaderboard](site/index.en.html) · [Scenarios](docs/SCENARIOS.md) · [Protocol](docs/PROTOCOL.md) · [Limitations](docs/LIMITATIONS.md)

An open, reproducible **accuracy benchmark for rigid-body physics engines**. Every scenario has an analytic or high-precision numerical truth; the scoring code is fully public; engines only return state trajectories and **cannot influence how they are scored**. There is **no composite score and no ranking**: raw per-metric, per-scenario values are published next to fixed public tolerances, including results that are unfavorable to the maintainers.

> **Conflict of interest.** DiffBench is maintained by Hangzhou Haixuan Yunzhi Technology Co., Ltd., which also develops one entrant (Nexus). Read [GOVERNANCE.md](GOVERNANCE.md) and [docs/LIMITATIONS.md](docs/LIMITATIONS.md) before drawing conclusions. We invite independent audits and re-runs.

## What is and is not in this repository
| Open | Not open |
|---|---|
| Benchmark spec, 10 scenarios, tolerances | Nexus engine source code |
| Truth + scoring code, hidden-set generator | The hosted Nexus API implementation |
| Adapters for MuJoCo, MJX, MuJoCo-Warp, Newton (XPBD / MuJoCo), Brax, Drake, and the Nexus **HTTP** client | |
| Signed result bundles, history, leaderboard site, report generator | |

Nexus participates **only through a hosted API that returns states**; it is scored locally by the same public scorer as every other engine.

## Quick start
```bash
pip install -e .                      # numpy only
pip install mujoco                    # other engines on demand: mujoco-mjx jax brax drake newton mujoco-warp warp-lang
python -m unittest discover -s tests  # engine-free self-tests of the scorer

python -m diffbench.runner --engines mujoco,drake --out results/run1 --raw
python -m diffbench.report  --bundles 'results/*/bundle.json' --out report/ --lang en
python -m diffbench.verify  results/run1/bundle.json --rescore results/run1   # recompute every metric from raw states

# Nexus (hosted API; no source needed)
export DIFFBENCH_NEXUS_URL=https://www.openaethos.com
python -m diffbench.runner --engines nexus_pgs,nexus_diffrigid --nexus http --out results/nexus
```

## Reading the first results
Public set, dt = 1/240 s, CPU track, number of the 10 scenarios whose **every** metric is within the public tolerance (details and caveats in [docs/RESULTS.md](docs/RESULTS.md)):

| Engine (default config) | pass |
|---|---|
| Nexus PGS (vendor-configured entrant) | 10/10 |
| Nexus DiffRigid (vendor-configured entrant) | 9/10 |
| MuJoCo 3.17.0 / MJX / MuJoCo-Warp / Newton-XPBD / Newton-MuJoCo | 5/10 each |
| Brax (generalized) | 4/10 |
| Drake | 3/10 |

This table is a convenience summary, **not a ranking**. Tolerances are tight on purpose (e.g. 1 mm free-fall position error), so first-order integrators in their default mode fail some scenarios by design; this reflects accuracy against closed-form truth, not general engine quality, speed, robustness, features, or suitability for any task. Nexus is slower than MuJoCo (0.04–0.94× in our single-environment CPU measurement) and the gradient and GPU tracks do not exist yet.

## Layout
`diffbench/` spec, truth, runner, verify, report, publish, adapters · `site/` signed bundles, history, static leaderboard · `docs/` · `tests/`

## License
Code: Apache-2.0 ([LICENSE](LICENSE)). Specification text, documentation, data and result bundles: CC-BY-4.0 ([LICENSE-DOCS](LICENSE-DOCS)); please credit "Haixuan DiffBench". Third-party names are trademarks of their owners ([TRADEMARKS.md](TRADEMARKS.md)). Cite via [CITATION.cff](CITATION.cff).
