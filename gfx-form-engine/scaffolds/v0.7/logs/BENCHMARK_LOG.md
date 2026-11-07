# Benchmark Log — v0.7

No target-hardware performance results yet.

CPU correctness suite currently completes 28 tests in under one second on the build host; this is not a performance benchmark.

Required later:
- Atomic/reference overhead
- ActivationGraph / ContinuationChain overhead
- BreadcrumbRing / heartbeat overhead
- Recursive continuation spill/reload cost
- Plane lookup cost
- Three-plane aligned-read cost
- Sparse brick lookup
- ELR bytes/sec
- Structural compaction throughput
- CPU versus GPU crossover
- Pinned transfer aperture throughput
- Segment size
- 2 GB valid-set payoff
- Worker fault/reset/recovery behavior
