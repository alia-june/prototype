# Dev Notes

- DEV-001 — Begin implementation at substrate level, not Voxel/ELR level.
- DEV-002 — First executable kernel: Atomic, Binding, Relation, Reference, Validation, Provenance.
- DEV-003 — Second executable kernel: Activation, Continuation, Progress, Recursion.
- DEV-004 — Only after these pass tests: Coordinate, Frame, Plane, Tri-plane Cast, ELR, JSON-0.
- DEV-005 — All persistent references remain logical/typed. Native CPU/GPU pointers stay inside runtime implementations.
- DEV-006 — No exact bitcodes until distinctions stabilize.
- DEV-007 — Keep source bytes immutable; derived planes are generation-scoped.
- DEV-008 — Prefer logical polymorphism with physically homogeneous backing pools.
- DEV-009 — Prefer sparse/tiled/bricked volume backing over dense cubes unless measurement proves otherwise.
- DEV-010 — One cast may resolve a 3D location; aligned planes are then read at that location.
