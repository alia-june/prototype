# Dev Notes — v0.5

Implemented and CPU-tested:
- Atomic/Binding/Relation/Reference/Validation/Provenance.
- Activation/Continuation/Progress/Recursion.
- Coordinate/Frame/FrameMapping/FrameGraph.
- Composition/decomposition round-trip validation.
- Dense/sparse/brick backing plus homogeneous typed backing pool.
- `Plane<T>` with explicit descriptor/backing binding.
- Aligned tri-plane read, Cast, prioritized recovery candidate, CastTrace.
- Route/RouteStep molecular chain validation.
- RecoveryRouteRegistry lookup without autonomous recovery execution.
- DDA step primitive.
- ELR lexical planes and ELR plane descriptors.
- JSON-0 iterative parser with spans/data/nodes/Relations/sequencing.
- Relationship and sequence cross-validation.
- Runtime identity/generation/transaction ledger/sentinel/recovery interfaces.

Unvalidated boundaries:
- HIP kernels and rocPRIM integration.
- RX 7700 XT capability measurements.
- Windows Job Object worker supervision.
- Pinned-transfer sizing and H2D/D2H overlap.
- GPU reset/recovery behavior.
- GPU sparse-brick physical layout.
- Performance/crossover measurements.
