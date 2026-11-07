# Decision Ledger — v0.6

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

v0.6 additions:
- DEC-033 — Matrix-to-route selection is an explicit generation-aware binding, not hidden inside MatrixCell. LOCKED
- DEC-034 — Normal route commitment requires durable PREPARE before COMMIT; recovery-route commitment additionally requires explicit recovery authorization. LOCKED
- DEC-035 — Recovery checkpoints are first-class stored recovery state and may preserve recursion activation/location/progress without imposing a depth cap. LOCKED
- DEC-036 — Reusable form fragments are generic molecular templates; workload-specific lexical fragments specialize them without changing core coordinate mechanics. LOCKED
- DEC-037 — JSON `\\uXXXX` validation includes surrogate-pair/scalar correctness; lone or malformed surrogates are rejected. LOCKED
- DEC-038 — JSON members expose explicit Member→Key and Member→Value relations and complete member source spans. LOCKED
- DEC-039 — Multi-edge frame paths may execute only through validated explicit coordinate mappings; semantic projections are not silently treated as reversible coordinate transforms. LOCKED
