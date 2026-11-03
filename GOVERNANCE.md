# Governance and conflict-of-interest statement

## Who runs this
DiffBench was created and is currently maintained by Hangzhou Haixuan Yunzhi Technology Co., Ltd. ("Haixuan"), **which also develops one of the entrants (Nexus)**. This is a conflict of interest. We handle it as follows:

1. **Public scorer.** All truth and scoring code is in this repository. Engines return states only.
2. **No composite score, no ranking.** Per-scenario, per-metric raw values only, compared with fixed public tolerances.
3. **Append-only results.** Unfavorable results (including ours) stay published. Pre-fix Nexus results are kept in `site/history/`.
4. **Engines run as shipped, defaults only.** For third-party engines we do not tune parameters. Disclosure: Nexus entries were run by its developers, with entry-level defaults they chose; third-party engines were run by us with default configurations and have not been reviewed by their maintainers.
5. **Reproduction path.** Nexus runs through a hosted API. The source is not open, so Nexus-side numbers are reproducible (the API returns the same trajectories) but not auditable at code level. This is a real limitation and is stated in `docs/LIMITATIONS.md`.
6. **Hidden set.** Commit–reveal (`docs/HIDDEN_SET.md`).
7. **Independent stewardship (goal).** Within 12 months we intend to move the spec, scorer and leaderboard to a neutral steering committee with at most one seat for Haixuan. Until then Haixuan holds merge rights; any maintainer may be added by invitation of the existing ones.

## Decision process
* Spec/tolerance changes: public RFC issue, ≥14 days comment period, engine maintainers pinged explicitly.
* Adapter disputes: owner of the engine gets the final say on "what is the default way to configure my engine", subject to the no-score-tuning rule.
* Third-party audit: anyone is invited to audit the scorer and to re-run any bundle; we will link audits from the README.
