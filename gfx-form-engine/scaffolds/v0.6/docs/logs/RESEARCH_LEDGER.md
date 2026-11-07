# Research Ledger — v0.6

Grounded directions retained:
- Structural-index JSON parsing and bitmap/bitplane lexical classification are established high-performance patterns.
- Compute voxel traversal does not require hardware ray-tracing acceleration; DDA-style traversal remains the discrete-grid baseline candidate.
- Sparse/tiled/bricked physical backing remains preferred for large sparse logical volumes pending benchmark.
- Logical polymorphism should not require pointer-oriented heterogeneous allocation; homogeneous backing pools preserve a GPU-friendly path.

v0.6 is a construction/correctness pass. No new GPU/Windows empirical result has been promoted. Unicode escape, member relation, frame-chain, route-commit and checkpoint results are CPU reference results only.
