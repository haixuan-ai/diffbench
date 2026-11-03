# Nexus entry: what was changed after seeing the benchmark

The Nexus developers ran this benchmark on their own engine first, found failures, and changed the engine (the public scorer and tolerances were not changed). We list this so readers can judge how much the Nexus numbers say about generalization. Engine source remains closed.

| Round | Observed problem (default config) | Change in Nexus (engine-level, not per-scenario parameters) | Effect |
|---|---|---|---|
| 1 | DiffRigid 5-box stack collapsed | box–box contact generation rewritten (minimum-overlap axis, grid contact points) | top-layer error → 6.8e-4 m |
| 1 | DiffRigid box drop rebounded 0.247 m | symmetric Hunt–Crossley damping, default damping raised | 0.0112 m (tol 0.02) |
| 1 | DiffRigid hinge pendulum NaN at dt = 1/60 | automatic sub-stepping from a stability bound | stable at 60/240/1000 Hz |
| 1 | PGS torque-free body 3.95° error | principal-axis RK4 for unconstrained bodies | 0.0496° |
| 2 | DiffRigid incline slide 7.5 % error | critical normal damping, smaller friction regularization | 1.4 % (tol 2 %) |
| 2 | Pendulum COM error (DiffRigid 6.4 mm, PGS 5.6 mm) | stiffer hinge penalty; 2 internal sub-steps per output step (PGS, disclosed in `config`) | 0.57 mm / 2.8 mm |
| 2 | Free-fall / projectile error (PGS 2.0e-2 m, DiffRigid 2e-3 m) | trapezoidal position update for bodies with no contact, joint or external force in that step | ~1e-13 m |

Things to keep in mind:
* The last row is a legitimate improvement for free-flight steps, but it exists because the benchmark exposed first-order error; the same first-order error is still present for constrained/contacting bodies in Nexus, as in the other engines.
* Hidden-variant re-runs after each round (demo seed) showed the same improvement, but that seed was known to the developers (see `HIDDEN_SET.md`).
* Still failing: DiffRigid `torque_free_asym` (energy drift 2.3e-3 and angular-momentum drift 1.3e-3 vs 1e-3 tolerance); PGS pendulum at dt = 1/60 (11 mm vs 5 mm); two unit tests in the Nexus codebase failed before and after (hinge-pendulum gradient check, asymmetric free rotation).
* Cost: DiffRigid pendulum needs many sub-steps; throughput is lower.
* Before the fixes, results are kept in `site/history/` and not removed.
* Third-party engines were not tuned, and their maintainers may know better default setups. We will update adapters on evidence (see CONTRIBUTING.md).
