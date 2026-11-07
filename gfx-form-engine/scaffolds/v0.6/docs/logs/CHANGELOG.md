# Change Log

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
