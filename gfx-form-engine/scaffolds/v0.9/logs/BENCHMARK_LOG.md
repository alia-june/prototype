# Benchmark Log — v0.9

No target performance benchmark results yet.

Required later:
- Atomic/reference overhead
- Recursive continuation overhead
- Plane lookup vs AlignedPlaneIndex lookup
- Three-plane aligned-read cost
- Sparse brick lookup
- ELR byte-plane vs bit-packed throughput
- Structural compaction throughput
- CPU versus GPU crossover
- Pinned transfer aperture throughput
- Segment size
- 2 GB valid-set payoff
- Worker fault/reset behavior
- Commit/checkpoint persistence overhead


v0.9 benchmark TODO additions:
- SHA-256 commit-certificate throughput/latency on intended CPU
- integrity hashing cost per ledger commit and per payload size
- cross-frame cast mapping-path overhead
- full ELR rebuild vs future localized regeneration after mutation
