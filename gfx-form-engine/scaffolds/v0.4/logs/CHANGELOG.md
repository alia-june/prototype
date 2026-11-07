# Change Log

## v0.3
- Added strict UTF-8 validator.
- Added JSON number grammar validator.
- Added explicit iterative JSON parser with spans, data, nodes and sequencing.
- Added 5000-level nesting test to prove parser is not dependent on native recursive descent.
- Added aligned tri-plane reader with frame/generation validation.
- Added cast trace record.
- Added frame-relation graph scaffold.
- Added recursion-governor reason codes.
- Expanded CPU test suite to 8 tests.

## v0.2
- Initial CPU-compilable scaffold and 6 tests.

## v0.4 — Composition / Mapping / Recovery Hardening
- added composition/decomposition round-trip validation
- added reversible generic coordinate reindex transform
- added explicit semantic-projection structure with loss/provenance fields
- added stateful recursion monitor for progress, resource and cycle policy
- preserved no universal recursion-depth limit
- tri-plane cast resolution now carries a prioritized recovery candidate without self-authorizing recovery
- ELR structural balance now validates matching object/array container types
- fixed iterative parser context lifetime bug discovered by compiler warning
- expanded test suite from 8 to 11 tests
