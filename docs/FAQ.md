# FAQ

**Why open the benchmark but not the engine?** The benchmark is only credible if anyone can inspect the scoring. An engine does not need to be open for its outputs to be scored: it returns states, the scorer is public.

**Can a closed engine game a public benchmark?** Yes, partly; hence the hidden set, the rule that adapters can't be tuned from scores, append-only history, and the invitation for independent re-runs. None of this removes the conflict of interest.

**Is Nexus "the best" engine?** No such claim is made. On this narrow accuracy track, with these tolerances, Nexus PGS meets all 10 public tolerances and the default configurations of the other engines meet 3–5. Nexus is slower than MuJoCo, has no GPU path or gradient track results here, and its entries were configured by its developers.

**Why do MuJoCo/Newton etc. fail free fall?** Default first-order (semi-implicit Euler) integration has O(dt) position error; the 1 mm tolerance at dt=1/240 exposes it. Most users never need that accuracy, and other settings (e.g. RK4 in MuJoCo) are available. We do not tune.

**Will you add my engine / fix my adapter?** Yes, see CONTRIBUTING.md. Maintainers are contacted before publication of new results about their engines.

**Commercial use?** Code is Apache-2.0; spec text, docs, data and result bundles are CC-BY-4.0 (attribution required). Please do not imply endorsement by engine vendors.
