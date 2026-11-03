# Scenarios (spec v0.1.0)

All scenarios: z-up, SI units, quaternion wxyz. Tolerances are public and fixed per spec version. `spec_sha256` = SHA-256 of the canonical JSON of `spec.scenarios()` (including the Chinese `title` strings, which is why titles are not translated in code; English titles live here).

Current `spec_sha256`: `3d6ecebe82b2ba7953652e762cbdaf9ca1c4147e43700b2fc42c49fa54575142`

## `free_fall` — Free fall

- Truth: Closed form: p=p0+½gt², v=gt. No contact; isolates integrator/frame conventions.
- Tests: Pure integrator + adapter-convention check
- Duration: 1.0 s; sweep dts: 1/60, 1/240, 1/1000
- Public tolerances: `pos_err_max_m` ≤ 0.001 (max position error (m)), `vel_err_max_mps` ≤ 0.01 (max velocity error (m/s))

## `projectile_spin` — Projectile with constant spin (sphere)

- Truth: Closed-form ballistic; angular velocity must stay constant.
- Tests: Frame/angular-velocity convention check
- Duration: 1.0 s; sweep dts: default 1/240 only
- Public tolerances: `pos_err_max_m` ≤ 0.001 (max position error (m)), `vel_err_max_mps` ≤ 0.01 (max velocity error (m/s)), `angvel_err_max_rps` ≤ 0.001 (max angular-velocity error (rad/s))

## `torque_free_asym` — Torque-free asymmetric body (intermediate-axis tumbling)

- Truth: Euler equations integrated with RK4 (h ≤ 1e-4) as high-precision numerical truth.
- Tests: Gyroscopic term accuracy, energy and angular-momentum conservation
- Duration: 2.0 s; sweep dts: default 1/240 only
- Public tolerances: `orient_err_deg_max` ≤ 2 (max orientation error (deg)), `energy_drift_rel` ≤ 0.001 (energy drift (relative)), `angmom_drift_rel` ≤ 0.001 (angular-momentum drift (relative)), `com_drift_m` ≤ 1e-06 (COM drift (m))

## `coulomb_slide` — Coulomb sliding stop distance

- Truth: d = v²/(2μg).
- Tests: Friction model, stopping behaviour
- Duration: 1.0 s; sweep dts: default 1/240 only
- Public tolerances: `stop_dist_rel_err` ≤ 0.02 (stopping-distance rel. error), `residual_speed_mps` ≤ 0.01 (residual speed (m/s)), `z_err_max_m` ≤ 0.002 (max height error (m))

## `incline_slide` — Incline sliding (gravity decomposition, μ < tanθ)

- Truth: x = ½·g(sinθ − μcosθ)·t².
- Tests: Friction under sustained load; contact force build-up
- Duration: 1.0 s; sweep dts: default 1/240 only
- Public tolerances: `slope_pos_rel_err` ≤ 0.02 (along-slope displacement rel. error), `z_err_max_m` ≤ 0.002 (max height error (m))

## `box_rest` — Box resting on ground (contact equilibrium)

- Truth: Rest height = half-extent, zero velocity.
- Tests: Contact stability / jitter / creep
- Duration: 2.0 s; sweep dts: default 1/240 only
- Public tolerances: `z_err_max_m` ≤ 0.001 (max height error (m)), `lateral_drift_m` ≤ 0.001 (lateral drift (m)), `speed_max_mps` ≤ 0.01 (max speed at rest (m/s))

## `box_drop` — Box drop (rest height, inelastic)

- Truth: Final rest height = half-extent; rebound ≈ 0 (no restitution).
- Tests: Contact dissipation, rebound
- Duration: 2.0 s; sweep dts: default 1/240 only
- Public tolerances: `final_z_err_m` ≤ 0.002 (final height error (m)), `final_speed_mps` ≤ 0.01 (final speed (m/s)), `max_rebound_m` ≤ 0.02 (max rebound (m))

## `sphere_slide_to_roll` — Sphere slide → pure rolling (friction-torque coupling)

- Truth: Closed form: v_final = 5/7·v0; rolling constraint v=ωr.
- Tests: Friction force/torque coupling
- Duration: 1.0 s; sweep dts: default 1/240 only
- Public tolerances: `final_v_rel_err` ≤ 0.03 (final velocity rel. error), `roll_resid_rel` ≤ 0.03 (rolling-constraint residual (rel.)), `x_end_rel_err` ≤ 0.03 (final position rel. error)

## `stack5` — Five-box stack at rest

- Truth: Each box stays at its initial height.
- Tests: Multi-body contact stability
- Duration: 2.0 s; sweep dts: default 1/240 only
- Public tolerances: `top_z_err_m` ≤ 0.005 (top-layer max height error (m)), `lateral_drift_m` ≤ 0.005 (lateral drift (m)), `speed_max_mps` ≤ 0.05 (max speed at rest (m/s))

## `pendulum_hinge` — Hinged compound pendulum (horizontal release, large swing)

- Truth: RK4 (h ≤ 1e-4) of the exact pendulum ODE.
- Tests: Joint constraint accuracy, step-size convergence
- Duration: 3.0 s; sweep dts: 1/60, 1/240, 1/1000
- Public tolerances: `com_pos_err_max_m` ≤ 0.005 (max COM position error (m)), `energy_drift_rel` ≤ 0.01 (energy drift (relative))
