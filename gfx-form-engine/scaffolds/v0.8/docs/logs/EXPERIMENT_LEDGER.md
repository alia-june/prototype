# Experiment Ledger — v0.8

Validated CPU experiments:
- EXP-001 — Atomic encode/decode round trip — PASS
- EXP-002 — Reference resolution + stale-generation rejection — PASS
- EXP-003 — Recursive activation/continuation without native recursion — PASS
- EXP-004 — Cycle detection with legal repeated-state recursion — PASS
- EXP-005 — Progress-governed recursion beyond arbitrary conventional depths — PASS (5,000 JSON levels)
- EXP-006 — One cast + three aligned plane reads — PASS
- EXP-008 — JSON source → ELR → compacted structure — PASS
- EXP-011 — Plane-alignment generation mismatch rejection — PASS
- EXP-012 — Frame transform vs semantic projection validation — PASS
- EXP-013 — Activation graph context validation — PASS
- EXP-014 — Continuation chain generation validation — PASS
- EXP-015 — Recovery-domain state transitions — PASS
- EXP-016 — Bounded breadcrumb overwrite/order behavior — PASS
- EXP-017 — Execution-envelope legal/illegal phase transitions — PASS
- EXP-018 — JSON Reference/Provenance source-generation lineage — PASS
- EXP-022 — Commit-certificate predecessor/ledger continuity — PASS
- EXP-023 — Checkpoint restore-plan generation/rejection — PASS
- EXP-024 — Generation/epoch aligned-plane indexing — PASS
- EXP-025 — ELR generation-lineage continuity/rejection — PASS
- EXP-026 — Exact JSON source reconstruction + parse/reparse round trip — PASS

Pending empirical experiments:
- EXP-007 — Sparse versus dense plane backing — PLANNED
- EXP-009 — Dense lexical raster vs packed bitplanes — PLANNED
- EXP-010 — Sparse voxel brick sizes — PLANNED
- EXP-019 — Durable fault-capsule persistence across worker/process loss — PLANNED
- EXP-020 — Continuation spill to CPU backing and resume — PLANNED
- EXP-021 — Semantic-heartbeat stale/hung worker detection on Windows — PLANNED
- EXP-027 — Crash-consistent durable PREPARE/COMMIT ordering — PLANNED
- EXP-028 — Cryptographic commit-certificate chaining, if required by attestation design — PLANNED
