# Build Report — v0.6

Date: 2026-10-07

## Result
- CMake configure: PASS
- C++20 build: PASS
- Compiler warning check: PASS after correcting two misleading-indentation warnings in the Unicode escape path
- CTest: **22/22 PASS**
- Native recursive descent: not used by JSON-0 parser
- Existing 5,000-level nested-array test: PASS

## New validated CPU behavior
- Matrix cell → generation-aware route/recovery-route binding.
- Route PREPARE → COMMIT sequencing.
- Recovery-route commit denied without matching explicit authorization.
- Recovery checkpoint selection by recursion identity/generation/validation state.
- Multi-edge validated frame mapping-chain execution.
- Generic lexical fragment templates with JSON `true` / `null` matching.
- JSON structural form recognition.
- JSON Unicode surrogate-pair acceptance and malformed/lone surrogate rejection.
- Complete JSON member spans and explicit MemberKey / MemberValue relations.

## Explicitly unvalidated
- AMD HIP kernels / rocPRIM integration.
- RX 7700 XT execution/performance characteristics.
- Windows Job Object supervisor and worker fault/reset behavior.
- GPU sparse-brick physical layout and performance.
- CPU/GPU crossover and transfer-overlap measurements.
