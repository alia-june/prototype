# Build Report — v0.4

Date: 2026-10-07

## Build
- CMake configure: PASS
- C++20 build: PASS
- Compiler warnings after correction: none observed
- CTest: 11/11 PASS

## Newly validated
- Composition/decomposition round-trip equivalence
- Generic reversible coordinate reindex transform and inverse
- Explicit semantic-projection representation
- Stateful recursion monitoring for progress/resource/cycle conditions without fixed depth limiting
- Tri-plane recovery-candidate preservation
- ELR mismatched container-type detection
- Existing 5,000-level iterative JSON nesting test continues to pass

## Explicitly unvalidated
- HIP kernel behavior
- RX 7700 XT / gfx1101 runtime behavior
- Windows worker/supervisor process control
- GPU recovery/reset behavior
- Throughput/performance assumptions
- Sparse brick size tuning
