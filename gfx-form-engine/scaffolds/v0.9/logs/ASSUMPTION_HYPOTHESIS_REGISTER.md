# Assumption / Hypothesis Register — v0.9

- HYP-001 — IDENTITY/CODE/VALUE/MASK remain sufficient as the initial logical atomic families. STATUS: PROVISIONAL
- HYP-002 — Logical polymorphism + homogeneous physical pools will suit GPU access better than pointer-oriented object polymorphism. STATUS: UNTESTED
- HYP-003 — Plane 3 dynamic recursion governance can replace arbitrary universal depth caps. STATUS: DESIGN ACCEPTED / CPU TESTED / GPU UNTESTED
- HYP-004 — Sparse/tiled voxel backing will outperform dense volume representation for expected workloads. STATUS: UNTESTED
- HYP-005 — ELR dense-to-sparse transition will be useful for JSON and later form workloads. STATUS: CPU FUNCTIONAL / UNBENCHMARKED
- HYP-006 — Shared coordinate/frame mechanics can support multiple semantic structures without contaminating the core with axis-specific meaning. STATUS: CPU TESTED
- HYP-007 — Structural commit certificates will be sufficient for runtime continuity; cryptographic chaining may only be needed for external attestation. STATUS: PROVISIONAL


- HYP-007 — Structural-only commit certificates are sufficient for all integrity needs. STATUS: SUPERSEDED; SHA-256 integrity chain now available, while external authenticity/attestation remains unresolved.
- HYP-008 — Immutable source-generation replacement plus ELR rebuild is safer/simpler than in-place derived-plane patching for the baseline. STATUS: CPU DESIGN TESTED / GPU PERFORMANCE UNTESTED
