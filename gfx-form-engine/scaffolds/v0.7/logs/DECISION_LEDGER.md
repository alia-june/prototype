# Decision Ledger — v0.7

Existing locked decisions remain in force:
- JSON-0 is the first canonical workload.
- `Encoded Lexical Raster` is the canonical lexical-raster representation.
- Source bytes remain authoritative and immutable.
- Reference and Recursion are first-class molecular forms.
- No universal fixed recursion-depth limit; Plane 3 governs recursion safety/recovery.
- X/Y/Z semantics are frame-scoped and structure-defined.
- One 3D cast followed by aligned tri-plane reads is canonical.
- Plane 1 proposes direction/form intent; Plane 2 constrains admissibility; Plane 3 carries fallback/recovery and recursion governance.
- CPU retains recovery/reauthorization authority.
- Exact bitcodes and binary layouts remain unfrozen.
- Large structures remain compositions over atomics/molecules rather than primitive roots.

v0.7 additions:
- DEC-040 — Activations form an explicit graph; parent/child relationships are data, not native call-stack state. LOCKED
- DEC-041 — Continuations form explicit generation-scoped chains and may be validated/spilled independently of native stack depth. LOCKED
- DEC-042 — Recovery fate may be scoped through explicit RecoveryDomains spanning activations, routes and backing objects. LOCKED
- DEC-043 — The canonical execution phase envelope is INTENT → PRECHECK → EFFECT → COMPLETE → COMMIT; FAULT is an explicit diversion. LOCKED
- DEC-044 — Breadcrumbs are bounded forensic evidence and never authority. LOCKED
- DEC-045 — Semantic heartbeat records execution meaning/state rather than only liveness timing. LOCKED
- DEC-046 — JSON-derived objects carry first-class Reference + Provenance lineage back to the authoritative source generation. LOCKED
