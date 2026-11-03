# Results summary — public set, dt = 1/240 s, CPU track

✓ = every metric within the public tolerance; ✗ = at least one metric outside; error = run failed. **Not a ranking.** Raw numbers: `site/report.en.md`. Source of truth is `site/bundles/*.json`; this table was generated from them and re-checked against the re-issued bundles (2026-11-02, with raw trajectories in `site/raw/`).

| engine | free_fall | projectile_spin | torque_free_asym | coulomb_slide | incline_slide | box_rest | box_drop | sphere_slide_to_roll | stack5 | pendulum_hinge | all-pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nexus_pgs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 10/10 |
| nexus_diffrigid | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 9/10 |
| mujoco | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5/10 |
| mjx | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5/10 |
| mujoco_warp | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5/10 |
| newton_xpbd | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | 5/10 |
| newton_mujoco | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5/10 |
| brax_generalized | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | 4/10 |
| drake | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | 3/10 |

## Reading notes
- Nexus entries are vendor-configured and were improved after the first benchmark run (see `docs/NEXUS_DISCLOSURE.md`); other engines are default configurations run by the benchmark organizers and not reviewed by their maintainers.
- Several ✗ for first-order integrators come from the strict 1 mm / 2 % tolerances (e.g. MuJoCo free_fall position error 2.0e-2 m, first-order in dt). This is accuracy against closed-form truth, not a judgement of any engine's usefulness.
- Hidden-set bundle (`accuracy_hidden`, MuJoCo + Nexus only, demo seed): PGS 10/10, DiffRigid 9/10, MuJoCo 5/10 — not a formal commit–reveal result.
- Speed (steps/s) is in the raw report and is informational; Nexus was 0.04–0.94× of MuJoCo in our single-environment CPU measurement.
- Not covered: GPU throughput, gradients, contact-rich manipulation, soft bodies, long-horizon stability, robustness to bad inputs.