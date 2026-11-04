# Hardening Status and Current Development Wall — MATH.SC-0 v0.8.0

## Hardening completed

- dual JavaScript/Python operation-contract validation;
- deterministic-local / web / LLM authority separation;
- terminal local failure for known contracted operations;
- exact arithmetic and exact rational interval arithmetic;
- directed-rounding transcendental interval backend;
- native C/C++ scalar/vector/matrix and LU kernels;
- heterogeneous reference checks and residual verification;
- numerical condition/backward-error diagnostics;
- request/result replay fingerprints;
- resource ceilings for shape, work, precision, numeric-string length, exact powers, and interval endpoint materialization;
- seeded native differential tests;
- seeded interval containment tests;
- exact metamorphic identity tests;
- AddressSanitizer and UndefinedBehaviorSanitizer native self-tests.

## Environment wall reached

### Independent transcendental interval oracle

The system runtime contains:

```text
/lib/x86_64-linux-gnu/libmpfr.so.6
```

but no `mpfr.h` development header is present. SC-0 therefore cannot compile and certify an independent MPFR-based outward-rounding oracle on this host without importing or installing additional development material. Manually recreating MPFR ABI structures would weaken rather than strengthen assurance, so it is intentionally not done.

### Open compute

`libOpenCL.so.1` is present, but OpenCL development headers are absent and no operator-provided OpenCL/SYCL/ROCm/HIP provider is attached. The open-compute adapter remains available as an integration boundary but cannot be certified here.

### GPU

Installed Torch is CPU-only. Runtime probes report:

```text
CUDA: unavailable
MPS:  unavailable
XPU:  unavailable
```

The accelerator adapter therefore remains correctly unavailable on this host.

## Consequence

Further ordinary CPU numerical work is possible, but the next planned assurance step—independent directed-rounding validation plus real heterogeneous accelerator certification—cannot be honestly completed in this environment. This is the current development wall for this pass.
