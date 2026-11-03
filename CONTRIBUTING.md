# Contributing

DiffBench is only useful if people who build engines trust it. Contributions are welcome, especially from engine maintainers.

## What you can contribute
1. **A new engine adapter** (`diffbench/adapters/`). See `docs/ADDING_AN_ENGINE.md`. Adapters return state trajectories only; they never compute scores.
2. **A correction to an existing adapter.** If you maintain an engine and believe your engine is mis-configured (wrong friction combination, wrong frame convention, a better *default* usage), open an issue with the minimal evidence. Adapter fixes must be justified by the unscored no-contact scenarios (`free_fall`, `projectile_spin`) or by documentation of the engine, never by "the score goes up".
3. **New scenarios / tracks** (GPU throughput, gradient accuracy, contact-rich scenes). Every scenario needs an analytic or documented high-precision truth and public tolerances proposed *before* anyone runs it.
4. **Result bundles.** Run on your hardware, submit `bundle.json` (+ raw trajectories) via PR to `site/bundles/`. Bundles are append-only: nobody's results are deleted, including unfavorable ones.
5. **Bug reports** in the scorer, truth, or docs.

## Ground rules
* No hard-coded numbers for any engine anywhere in the repository.
* Changing any scenario or tolerance changes `spec_sha256` and requires a spec version bump (`SPEC_VERSION`), a changelog entry and re-running all engines.
* `python -m unittest discover -s tests` must pass. English is the primary documentation language; Chinese translations are welcome.
* Sign off commits (DCO: `git commit -s`). Code contributions are licensed Apache-2.0; documentation contributions CC-BY-4.0.
