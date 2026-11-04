# GPU backend barrier

CPU modeling is the behavioral reference. GPU representation and execution are deferred.

A later GPU scope must specify:

- the canonical CPU-to-GPU representation mapping;
- memory ownership and lifetime;
- stream and fragment addressing;
- ordering and synchronization;
- deterministic and nondeterministic operations;
- mutation versus immutable successor creation;
- rendering and inspection semantics;
- resource limits and fallback behavior;
- parity tests against the CPU reference; and
- receipts proving which backend produced each result.

Keeping streams in GPU memory may improve later rendering or transformation throughput, but memory placement does not define document semantics and does not replace the CPU authority model.

This repository installs no CUDA, ROCm, driver, framework, kernel or GPU model.

