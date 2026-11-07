# Build Report

## Validation performed

- CMake configure: PASS
- C++20 compile: PASS
- CTest: **6/6 PASS**
- smoke executable: PASS

Smoke output:

```text
structural_positions=10
strings_balanced=1 structure_balanced=1
```

Test coverage currently includes:
1. Atomic type smoke
2. Reference generation/authority validation
3. Recursion governor: continue vs Plane-3 recovery diversion
4. Tri-plane cast acceptance
5. JSON-0 ELR structural masking/balance smoke
6. Identity/generation/ledger/brick/DDA runtime primitives

## Explicitly not validated here

- AMD HIP runtime/API behavior
- RX 7700 XT device behavior
- GPU kernels
- pinned-memory throughput
- Windows Job Object worker lifecycle
- Win32 shared-mapping/event coordination
- reset/recovery behavior
- performance characteristics
- stable bitcode assignments
- frozen binary/wire layouts

Those remain behind interfaces or TODOs rather than being represented as completed behavior.
