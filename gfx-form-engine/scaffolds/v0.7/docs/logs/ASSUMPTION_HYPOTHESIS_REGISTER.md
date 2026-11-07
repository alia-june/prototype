# Assumption / Hypothesis Register — v0.7

- HYP-001 — IDENTITY/CODE/VALUE/MASK are sufficient as initial logical atomic families. STATUS: PROVISIONAL
- HYP-002 — Logical polymorphism + homogeneous physical pools will suit GPU access better than pointer-oriented object polymorphism. STATUS: UNTESTED ON GPU
- HYP-003 — Plane 3 dynamic recursion governance can replace arbitrary universal depth caps. STATUS: CPU DESIGN VALIDATED / GPU UNTESTED
- HYP-004 — Sparse/tiled voxel backing will outperform dense volume representation for expected workloads. STATUS: UNTESTED
- HYP-005 — ELR dense-to-sparse transition will be useful for JSON and later form workloads. STATUS: CPU FUNCTIONALLY VALIDATED / UNBENCHMARKED
- HYP-006 — Shared coordinate/frame mechanics can support multiple semantic structures without contaminating the core with axis-specific meaning. STATUS: CPU DESIGN VALIDATED
- HYP-007 — Explicit activation/continuation graphs can permit practical deep recursion while supporting spill/recovery better than native GPU stacks. STATUS: CPU STRUCTURE VALIDATED / SPILL UNTESTED
- HYP-008 — Semantic heartbeat plus bounded breadcrumbs will materially improve worker fault reconstruction. STATUS: STRUCTURE VALIDATED / WINDOWS EMPIRICAL TEST PENDING
