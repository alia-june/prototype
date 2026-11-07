# Dev Notes — v0.6

Implemented and CPU-tested:
- Atomic/Binding/Relation/Reference/Validation/Provenance.
- Activation/Continuation/Progress/Recursion with dynamic Plane-3 governance and no universal depth cap.
- Coordinate/Frame/FrameMapping/FrameGraph plus validated multi-edge mapping-chain execution.
- Composition/decomposition round-trip validation.
- Dense/sparse/brick backing plus homogeneous typed backing pools.
- `Plane<T>` descriptors/backing bindings and aligned tri-plane reads.
- Cast resolution, prioritized recovery candidates and CastTrace.
- Route/RouteStep molecules and RecoveryRouteRegistry.
- MatrixRouteBinding/Registry connecting matrix cells to normal/recovery routes without embedding route semantics in MatrixCell.
- Transaction-ledger route PREPARE/COMMIT and explicit recovery authorization gate.
- RecoveryCheckpoint/CheckpointStore.
- Generic FormFragment plus JSON lexical literal fragments.
- ELR lexical planes and plane descriptors.
- JSON-0 iterative parser with strict UTF-8, number grammar, Unicode escape surrogate validation, spans/data/nodes/Relations/sequencing.
- JSON Member→Key / Member→Value relations, complete member spans and form recognition.
- 5,000-level nesting test without native recursive descent.

Unvalidated boundaries:
- HIP kernels / rocPRIM integration and RX 7700 XT behavior.
- Windows Job Object worker supervision and reset/recovery behavior.
- Pinned-transfer sizing / overlap.
- GPU sparse-brick layout and target performance/crossover measurements.
