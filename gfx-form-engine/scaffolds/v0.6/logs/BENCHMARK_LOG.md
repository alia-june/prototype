# Benchmark Log — v0.6

No target-performance results yet. CPU tests are correctness tests, not performance claims.

Required measurements:
- Atomic/reference and relation lookup overhead.
- Recursion activation/continuation/checkpoint overhead.
- Plane lookup and aligned tri-plane read cost.
- Matrix→route binding and route commit overhead.
- Frame mapping-chain cost.
- Homogeneous backing pool access cost.
- Sparse brick lookup/hierarchy cost.
- ELR classification/bitplane/fragment-match throughput.
- Structural compaction and JSON CPU/GPU crossover.
- Pinned transfer aperture throughput/overlap and segment size.
- VRAM headroom and 2 GB valid-set lookup payoff.
- Worker fault/reset/recovery behavior.
