# Dev Notes — v0.9

Implemented and CPU-tested:
- All v0.7 substrate/runtime/ELR/JSON behavior.
- Structural CommitChain over transaction-ledger COMMIT evidence.
- Recovery checkpoint → RestorePlan generation with AuthorizationRequired state.
- Generation/epoch-scoped AlignedPlaneIndex.
- ELR stage/generation lineage with parent-generation validation.
- Exact JSON source retention, reconstruction and parse/reparse round-trip validation.
- 5,000-level nesting without native recursive descent.

Important boundaries:
- CommitChain currently proves structural predecessor/ledger continuity, not cryptographic tamper resistance.
- RestorePlan identifies a candidate restore target only; CPU recovery authority remains required.
- Exact JSON reconstruction returns authoritative original source, including whitespace; canonical JSON serialization is not implemented.

Unvalidated boundaries:
- HIP kernels / rocPRIM integration and RX 7700 XT behavior.
- Windows Job Object worker supervision and reset/recovery behavior.
- Durable crash-consistent commit/fault persistence.
- Continuation spill/reload across GPU/CPU backing.
- Pinned-transfer sizing / overlap.
- GPU sparse-brick layout and target performance/crossover measurements.


v0.9 implemented and CPU-tested:
- Pure C++ SHA-256 with known-vector validation.
- IntegrityCommitChain binding payload digest + predecessor digest + committed ledger evidence.
- RecoveryPlan validation across checkpoint, route, RecoveryDomain, transaction, generation, frame and activation membership.
- Explicit RecoveryAuthorization promotion from AuthorizationRequired to Authorized.
- Cross-frame cast mapping through FrameGraph + FrameMappingRegistry before tri-plane resolution.
- Immutable JSON SourceMutationPlan with bounds/overlap/stale-generation rejection and reparse into a new generation.
- ELR rebuild request after source-generation mutation; no in-place derived-plane mutation.

Important boundaries:
- SHA-256 integrity is not authenticity, signature, trusted timestamp or durable-storage proof.
- Recovery-plan authorization is still an object-level CPU authority contract; Win32 worker enforcement is unvalidated.
