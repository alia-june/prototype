# Dev Notes — v0.3

Implemented: Atomic/Binding/Relation/Reference/Validation/Provenance; Activation/Continuation/Progress/Recursion; Coordinate/Frame/FrameRelation; dense/sparse/brick backing; Plane<T>; aligned tri-plane read; Cast and CastTrace; DDA step; ELR lexical planes; JSON-0 iterative parser; identity/generation/ledger/recovery interfaces.

Unvalidated boundaries: HIP kernels, Windows Job Object worker supervision, pinned transfer aperture sizing, GPU reset/recovery behavior, sparse-brick GPU layout, performance tuning.

- DEV-011 — Added `ReindexTransform` as a generic coordinate representation transform independent of axis semantics.
- DEV-012 — Added explicit `SemanticProjection`; no projection is treated as reversible coordinate mapping.
- DEV-013 — Added `RecursionMonitor` with regime-defined progress, resource and revisit policy; observed depth remains non-governing.
- DEV-014 — Cast resolution now preserves Plane 3's highest-priority recovery candidate for CPU-authority review.
- DEV-015 — JSON ELR now tracks container type stack so `{]` and `[}` fail lexical structural balance.
- DEV-016 — Fixed parser close-object lifetime bug found by compiler warning after iterative-stack conversion.
