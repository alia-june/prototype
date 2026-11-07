# Change Log

## v0.8 — Commit / Restore / Lineage / Round-Trip Layer
- added structural CommitCertificate / CommitChain over committed transaction-ledger evidence
- added explicit RestorePlan generation from validated recovery checkpoints without granting recovery authority
- added generation/validation-epoch scoped AlignedPlaneIndex
- added explicit ELR stage/generation lineage
- JsonDocument now retains authoritative source text
- added exact-source reconstruction and parse/reparse round-trip validation
- documented that commit chain is structural continuity evidence, not yet cryptographic chaining
- corrected one test-only assert/braced-initializer macro error before release
- expanded clean CPU suite from 28 to 33 tests

## v0.7 — Activation / Continuation / Recovery Evidence Layer
- added explicit ActivationGraph
- added generation-scoped ContinuationChain
- added RecoveryDomain / RecoveryDomainRegistry
- added canonical ExecutionEnvelope: INTENT→PRECHECK→EFFECT→COMPLETE→COMMIT plus FAULT diversion
- added bounded BreadcrumbRing
- added SemanticHeartbeat contract
- added FaultCapsule contract
- added JSON Reference/Provenance emission for authoritative source and derived parse products
- retained iterative 5,000-level JSON nesting behavior
- corrected one test narrowing warning before packaging
- expanded clean CPU suite from 22 to 28 tests

## v0.6 — Execution Binding / Checkpoint / Form Layer
- added generation-aware MatrixRouteBinding / MatrixRouteRegistry
- added route PREPARE→COMMIT contract and explicit RecoveryAuthorization gate
- added RecoveryCheckpoint / CheckpointStore
- added generic FormFragment<T> and JSON lexical literal fragments
- added JSON form recognition over structural nodes
- added validated multi-edge frame mapping-chain execution
- added JSON Unicode escape surrogate-pair/scalar validation
- added complete JSON Member spans and explicit MemberKey / MemberValue relations
- extended transaction ledger with generic phase queries
- fixed compiler warnings in Unicode escape path before packaging
- expanded clean CPU suite from 16 to 22 tests

## v0.5 — Backing / Route / Relation Layer
- added homogeneous typed backing pool
- added explicit PlaneDescriptor and backing binding exposure
- added Route and RouteStep molecular forms with chain validation
- added RecoveryRouteRegistry that resolves prebuilt Plane-3 recovery routes without granting execution authority
- added FrameGraph multi-edge path discovery
- added ELR plane descriptors with generation/storage/element metadata
- added explicit generic Relation records to JSON output
- added JSON relationship and sequence cross-validation
- corrected CMake generation duplication error
- expanded CPU suite from 11 to 16 tests

## v0.4 — Composition / Mapping / Recovery Hardening
- added composition/decomposition round-trip validation
- added reversible generic coordinate reindex transform
- added explicit semantic-projection structure with loss/provenance fields
- added stateful recursion monitor for progress, resource and cycle policy
- preserved no universal recursion-depth limit
- tri-plane cast resolution carries prioritized recovery candidate without self-authorizing recovery
- ELR structural balance validates matching object/array container types
- fixed iterative parser context lifetime bug
- expanded suite from 8 to 11 tests

## v0.3
- added strict UTF-8 validator and JSON number grammar validator
- added explicit iterative JSON parser with spans, data, nodes and sequencing
- added 5,000-level nesting test
- added aligned tri-plane reader and cast trace
- added frame-relation graph scaffold and recursion-governor reason codes
- expanded suite to 8 tests

## v0.2
- initial CPU-compilable scaffold and 6 tests


## v0.9 — Integrity / Recovery Plan / Cross-Frame Cast / Mutation Layer
- added portable tested SHA-256 `Digest256` service
- added SHA-256-backed `IntegrityCommitCertificate` / `IntegrityCommitChain`
- retained structural CommitChain as a distinct lightweight continuity contract
- added composed recovery-plan validation across checkpoint, route and RecoveryDomain
- added explicit RecoveryAuthorization promotion; recovery plans cannot self-authorize
- added cross-frame cast resolution through explicit FrameGraph/FrameMapping paths
- added generation-bound immutable JSON source mutation plans
- added overlap/out-of-bounds/stale-generation mutation rejection
- added ELR rebuild request after source-generation mutation
- expanded clean CPU suite from 33 to 38 tests
