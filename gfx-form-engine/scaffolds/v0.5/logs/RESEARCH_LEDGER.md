# Research Ledger — v0.5

Verified/grounded directions retained:
- Structural-index JSON parsing and bitmask/bitmap lexical classification are established high-performance techniques.
- Compute-based voxel traversal does not require hardware ray-tracing acceleration.
- DDA-style exact voxel traversal remains the preferred discrete-grid candidate over arbitrary tiny-step marching.
- Sparse/tiled/bricked physical backing remains preferred for large logical 3D spaces pending benchmark.
- Logical polymorphism should not require pointer-oriented heterogeneous allocation; homogeneous backing pools preserve a GPU-friendly path.

No v0.5 GPU/Windows empirical result has been promoted. Target-specific claims remain unvalidated until run on the RX 7700 XT / Windows HIP machine.
