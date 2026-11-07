# Build Report — v0.8

Date: 2026-10-07

## Result
- CMake configure: PASS
- C++20 build: PASS
- Compiler warning check: PASS after correcting one test-only `assert` macro construction error
- CTest: **33/33 PASS**
- Native recursive descent: not used by JSON-0 parser
- Existing 5,000-level nested-array test: PASS

## New validated CPU behavior
- `CommitChain` accepts only ledger-committed generations and enforces structural predecessor continuity.
- Commit certificates are explicit continuity evidence; the current implementation is not a cryptographic hash chain.
- `RestorePlan` derives a candidate restoration target from a validated checkpoint but remains `AuthorizationRequired`.
- `AlignedPlaneIndex` binds one frame/generation/validation epoch to cached aligned Plane 1/2/3 entries.
- `ElrLineage` explicitly records stage-to-stage generation ancestry and rejects broken ancestry.
- `JsonDocument` retains the authoritative source text for exact reconstruction.
- JSON exact-source reconstruction preserves whitespace/escaping and round-trip reparsing reproduces structural/data/relation/sequence counts.
- All previous v0.7 tests remain passing.

## Explicitly unvalidated
- AMD HIP kernels / rocPRIM integration.
- RX 7700 XT execution/performance characteristics.
- Windows Job Object supervisor and worker fault/reset behavior.
- Durable on-disk commit/fault-capsule persistence and crash-consistency ordering.
- Cryptographic commit-certificate chaining.
- GPU continuation spill/reload behavior.
- GPU sparse-brick physical layout and performance.
- CPU/GPU crossover and transfer-overlap measurements.
