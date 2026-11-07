# Decision Ledger — v0.8

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

v0.8 additions:
- DEC-047 — Durable/adoptable state must be distinguishable from merely completed work through explicit commit evidence. LOCKED
- DEC-048 — Commit certificates form an explicit predecessor chain over committed generations; current implementation is structural continuity evidence, not cryptographic integrity. LOCKED
- DEC-049 — Checkpoint restoration is a planned candidate transition and cannot self-authorize restoration or execution. LOCKED
- DEC-050 — Aligned plane lookup may be indexed/cached only when frame, generation and validation epoch are explicit. LOCKED
- DEC-051 — ELR processing stages retain explicit generation ancestry rather than relying on implicit mutation history. LOCKED
- DEC-052 — JSON source reconstruction is exact-source reconstruction from the retained authoritative source; it is distinct from canonical reserialization. LOCKED
