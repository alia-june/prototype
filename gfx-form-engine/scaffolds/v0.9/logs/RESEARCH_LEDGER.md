# Research Ledger — v0.9

- RES-001 — Sparse/tiled physical backing remains preferred for large logical 3D spaces.
- RES-002 — Exact voxel traversal remains candidate baseline for discrete 3D traversal.
- RES-003 — Dense lexical discovery → sparse structural compaction remains the primary ELR strategy.
- RES-004 — Physical representation of polymorphic backing remains an empirical performance question.
- RES-005 — No new external research finding was promoted during v0.8; this increment is architecture/implementation hardening.
- RES-006 — Structural commit continuity and crash consistency remain separate problems; durable ordering is still untested.


v0.9:
- RES-007 — SHA-256 is now implemented/tested as a portable integrity primitive; this does not answer key management/authentication/attestation.
- RES-008 — Cross-frame casting can remain generic by composing existing frame-path/mapping contracts; no axis-specific semantics are required.
- RES-009 — Mutation safety is cleaner as immutable source-generation replacement + derived-state rebuild than partial in-place ELR patching at this stage.
