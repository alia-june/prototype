# Build Report — v0.5

## Environment used for scaffold validation
- CMake-generated native C++20 build in the current execution container.
- HIP disabled; no claim of target AMD GPU execution.
- Windows supervisor not executed.

## Result
- Configure: PASS
- Compile: PASS
- CPU tests: **16/16 PASS**
- Native recursive JSON descent: not used
- 5,000-level nesting regression: PASS

## New v0.5 tests
- typed homogeneous backing pool + route chain validation
- frame-graph multi-edge path discovery
- ELR plane descriptor alignment
- JSON Relation + sequence cross-validation
- recovery-route lookup from Plane 3 candidate

## Unvalidated
HIP kernels, rocPRIM integration, Windows Job Objects, pinned-memory tuning, RX 7700 XT capability values, GPU recovery/reset, GPU sparse backing layout and all performance claims.
