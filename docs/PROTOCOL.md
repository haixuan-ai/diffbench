# Protocol B — parameter-aligned, each engine at its own defaults

1. **Scenario spec**: `diffbench/spec.py` (z-up, SI, quaternion wxyz). Its SHA-256 is written into every result bundle.
2. **Aligned**: geometry, mass, (symmetric) inertia derived from geometry, sliding friction coefficient μ, gravity, time step dt. No restitution; no rolling/torsional friction. If an engine combines friction coefficients differently, the adapter aligns the *effective* μ to the scenario μ and says so in the adapter source.
3. **Deliberately not aligned**: integrator, contact model and solver parameters are each engine's defaults, not tuned per scenario; the configuration is recorded in each result's `config` field.
4. **State readout**: COM position, body orientation, COM linear velocity, world-frame angular velocity; forward kinematics first. Adapter convention errors are exposed and fixed using the two no-contact scenarios (`free_fall`, `projectile_spin`); tuning an adapter by looking at scores is prohibited.
5. **Truth**: closed form for free fall / projectile / sliding / incline / rolling; RK4 (h ≤ 1e-4) high-precision numerical solution for torque-free rigid body and compound pendulum.
6. **Metrics** are reported individually against public per-scenario tolerances; there is no composite score. Failures, NaN and unsupported features are recorded as errors, never as defaults.
7. **Speed** (steps/s) is informational: single-environment CPU, includes binding overhead; GPU engines are outside their design regime.
8. **Known limitations** of an engine (e.g. first-order position error of MuJoCo's default Euler integrator) show up as real error and are not hidden. The two Nexus solvers enter separately.
