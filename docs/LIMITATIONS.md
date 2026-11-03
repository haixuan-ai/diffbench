# Limitations (read before citing any number)

1. **Organizer is an entrant.** See GOVERNANCE.md. Nexus entries are vendor-configured; others are defaults run by us and not yet maintainer-reviewed.
2. **Nexus is closed source.** Its numbers are reproducible through the hosted API but cannot be audited at code level. The Ed25519 attestation (see HOSTED_API.md) can be verified offline, but it is signed by the operator's own key: it proves integrity of the returned states, not that the engine is unmodified.
3. **Engine changes after benchmark exposure** — listed in NEXUS_DISCLOSURE.md.
4. **Hidden set not yet a formal commit–reveal result** (HIDDEN_SET.md).
5. **Narrow scope.** 10 single-body or simple-stack scenarios, one body class (boxes/spheres), no restitution, no rolling/torsional friction, no articulated chains beyond one hinge, no soft or deformable bodies, no robots, no sensor models, short horizons (≤ 3 s).
6. **Tolerances are our choice.** Strict tolerances on no-contact scenarios effectively test integrator order. A different tolerance set would change pass counts. Raw values are always published so readers can apply their own.
7. **Default-config policy** favors no engine in principle, but "default" is a judgement call per engine; adapter choices (e.g. effective-μ alignment) can matter.
8. **CPU track only.** GPU throughput, batch simulation and gradient accuracy are not covered. GPU-designed engines (MJX, MuJoCo-Warp, Newton) were run on CPU, which is not their intended regime.
9. **Speed numbers** are single-environment, include binding overhead, and in some runs were taken while other engines ran in parallel; they are not comparable.
10. **Raw trajectories** are published in `site/raw/` for the 9 accuracy bundles (re-issued 2026-11-02); the hidden-set demo bundle `5450c5078fed8275` and the superseded bundles in `site/history/pre-raw-*` have none, so `verify --rescore` does not apply to them.
11. **Hosted API limits**: ≤ 12 bodies, ≤ 5 s, dt ≥ 0.5 ms; the intended rate limit is 6 requests/min/IP but it was not observed to be enforced on the production deployment (2026-11-02), so do not rely on it; availability is best effort with no uptime commitment.
12. **No composite score** by design; any ranking built from this table is not endorsed by the maintainers.
