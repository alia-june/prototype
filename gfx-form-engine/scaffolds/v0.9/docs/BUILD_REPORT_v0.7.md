# Build Report — v0.7

Date: 2026-10-07

## Result
- CMake configure: PASS
- C++20 build: PASS
- Compiler warning check: PASS after correcting one test narrowing conversion
- CTest: **28/28 PASS**
- Native recursive descent: not used by JSON-0 parser
- Existing 5,000-level nested-array test: PASS

## New validated CPU behavior
- Explicit `ActivationGraph` with parent existence checks and transaction/generation context matching.
- Explicit `ContinuationChain` with generation consistency and duplicate-continuation rejection.
- `RecoveryDomain` / registry for grouping activations, routes and backing objects under shared recovery fate.
- `ExecutionEnvelope` enforcing INTENT → PRECHECK → EFFECT → COMPLETE → COMMIT, with FAULT diversion.
- Bounded `BreadcrumbRing` retaining ordered recent execution evidence.
- `SemanticHeartbeat` sanity checks over worker identity, active generation and transaction progress.
- `FaultCapsule` data contract for binding execution evidence to recovery-domain context.
- JSON-0 now emits first-class `Reference` and `Provenance` records for source and derived parse products.
- All new JSON provenance records retain source generation and source-reference lineage.

## Explicitly unvalidated
- AMD HIP kernels / rocPRIM integration.
- RX 7700 XT execution/performance characteristics.
- Windows Job Object supervisor and worker fault/reset behavior.
- Durable on-disk fault-capsule persistence.
- GPU continuation spill/reload behavior.
- GPU sparse-brick physical layout and performance.
- CPU/GPU crossover and transfer-overlap measurements.
