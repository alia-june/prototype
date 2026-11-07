# Dev Notes

- Substrate implemented before ELR/Voxel specialization.
- CPU reference code is authoritative for early correctness comparisons.
- HIP integration remains isolated until Windows target validation.
- Persistent references are typed logical identities; native pointers remain runtime-local.
- `observed_depth` exists for telemetry/debugging only, not as a universal recursion cap.
- `Plane<T>` is currently sparse for simplicity; dense/brick implementations remain separate backing realizations.
- JSON-0 lexical pass is intentionally incomplete and should remain testable before adding grammar complexity.
