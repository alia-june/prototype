# Dev Notes — v0.7

Implemented and CPU-tested:
- Atomic/Binding/Relation/Reference/Validation/Provenance.
- Activation/Continuation/Progress/Recursion with dynamic Plane-3 governance and no universal depth cap.
- ActivationGraph and generation-scoped ContinuationChain.
- RecoveryDomain registry for shared recovery fate.
- Coordinate/Frame/FrameMapping/FrameGraph plus validated multi-edge mapping-chain execution.
- Composition/decomposition round-trip validation.
- Dense/sparse/brick backing plus homogeneous typed backing pools.
- `Plane<T>` descriptors/backing bindings and aligned tri-plane reads.
- Cast resolution, prioritized recovery candidates and CastTrace.
- INTENT→PRECHECK→EFFECT→COMPLETE→COMMIT ExecutionEnvelope.
- Bounded BreadcrumbRing, SemanticHeartbeat and FaultCapsule contract.
- Route/RouteStep molecules, MatrixRouteBinding and RecoveryRouteRegistry.
- Transaction-ledger route PREPARE/COMMIT and explicit recovery authorization gate.
- RecoveryCheckpoint/CheckpointStore.
- Generic FormFragment plus JSON lexical literal fragments.
- ELR lexical planes and plane descriptors.
- JSON-0 iterative parser with strict UTF-8, number grammar, Unicode escape surrogate validation, spans/data/nodes/Relations/sequencing.
- JSON Member→Key / Member→Value relations, complete member spans and form recognition.
- JSON first-class Reference/Provenance emission for source and derived products.
- 5,000-level nesting test without native recursive descent.

Unvalidated boundaries:
- HIP kernels / rocPRIM integration and RX 7700 XT behavior.
- Windows Job Object worker supervision and reset/recovery behavior.
- Durable fault-capsule persistence.
- Continuation spill/reload across GPU/CPU backing.
- Pinned-transfer sizing / overlap.
- GPU sparse-brick layout and target performance/crossover measurements.
