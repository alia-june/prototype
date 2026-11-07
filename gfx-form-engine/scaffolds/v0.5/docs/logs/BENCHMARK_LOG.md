# Benchmark Log — v0.5

No target-performance results yet. CPU tests are correctness tests, not performance claims.

Required measurements:
- Atomic/reference overhead.
- Recursion activation/continuation/checkpoint overhead.
- Plane lookup and aligned tri-plane read cost.
- Homogeneous backing pool access cost.
- Sparse brick lookup and hierarchy cost.
- Route traversal cost.
- ELR classification/bitplane throughput.
- Structural compaction throughput.
- JSON CPU/GPU crossover.
- Pinned transfer aperture throughput and overlap.
- Segment size and VRAM headroom.
- 2 GB valid-set lookup payoff.
- Worker fault/reset/recovery behavior.
