# xOSG-0 MATH.SC-0 v0.8.0

Runnable three-runtime reference implementation of the xOSG-0 Straight Computation Core.

This machine remains intentionally restricted to numerical/straight computation. Abstract logic, sets, relations, predicates, and abstract-object reasoning remain deferred to a different machine/module.

## v0.8 milestone

v0.8 pushes the numerical core to the current environment wall:

- directed-rounding interval enclosures for `sqrt`, `exp`, `log`, `sin`, `cos`, and `tan` through mpmath `libmp` interval primitives;
- exact-rational determinant, linear solve, and matrix inverse;
- float64 determinant/solve/inverse across Python, NumPy, and compiled C++;
- C++ LU/partial-pivoting kernels exported through the native C ABI;
- residual-based verification for solve and inverse;
- matrix condition-number and backward-error diagnostics;
- seeded differential, metamorphic, and interval-containment hardening tests;
- resource guards for numeric-string length, exact powers, and pathological interval endpoint materialization;
- authority hardening: a known contracted operation that fails deterministically is no longer allowed to fall through to web or LLM.

The browser UI remains retained/frozen at UI version `0.5.0`.

## Runtime roles

- **JavaScript / Node.js** — first contract gate, orchestration, authority policy, web fallback, strict LLM-last-resort enforcement, Python capability/benchmark calls.
- **Python** — second contract gate, exact/high-precision/interval computation, capability negotiation, verification, numerical evidence, replay fingerprints, and bindings to native kernels.
- **C/C++** — compiled float64 kernels and LU linear algebra behind a stable C ABI.

## Authority policy

Global order:

```text
deterministic local -> web -> LLM last resort
```

Deterministic-local policy order:

```text
exact -> high_precision -> interval -> accelerator -> open_compute -> native C/C++ -> NumPy -> CPU
```

For a **contracted** operation, deterministic local execution failure is terminal. Web/LLM are not permitted to substitute an answer after a domain, singularity, or implementation failure of a known mathematical operation.

Uncontracted/unknown operations retain the external fallback path.

## Interval computation

Algebraic interval operations use exact rational endpoints. Transcendental intervals use mpmath `libmp` interval functions that explicitly compute lower endpoints with floor rounding and upper endpoints with ceiling rounding, then convert those binary endpoints to exact `Fraction` values for the wire representation.

Supported interval operations:

```text
add sub mul div integer-pow
sqrt exp log sin cos tan
sum product mean min max dot matmul
```

The evidence layer deliberately labels transcendental intervals as `backend_directed_rounding`, not as independently formally certified. See `docs/directed_rounding_intervals.md` and `docs/hardening_and_walls.md`.

## Linear algebra

New operations:

```text
det
solve
inverse
```

Exact mode uses rational Gaussian/Gauss-Jordan arithmetic. Float64 may dispatch to compiled C++ LU kernels, NumPy, or the Python reference backend. `solve` and `inverse` are verified by residuals rather than by finite-output checks alone.

## Versioned interfaces

- Module release: `0.8.0`
- Protocol: `0.6`
- Operation contract: `0.6.0`
- Numerical evidence: `0.2.0`
- Capability protocol: `0.3.0`
- Replay format: `0.1.0`
- Benchmark format: `0.1.0`
- Native ABI: `xOSG-0/MATH.SC-0/native-0.8.0`
- Retained browser UI: `0.5.0`

## Build

```bash
./scripts/build_native.sh
```

## Test

```bash
PYTHONPATH=src python -m pytest -q
cd js && npm test
```

Release verification currently passes:

```text
Python tests                         58/58 PASS
JavaScript / integration             23/23 PASS
C/C++ native self-test                     PASS
AddressSanitizer + UBSan                    PASS
seeded interval containment                 PASS
seeded native LU differential               PASS
exact metamorphic identities                PASS
JS -> Python -> native LU                    PASS
JS -> Python -> directed interval            PASS
```

## Current environment wall

The next higher-assurance step is blocked by the host rather than by an unimplemented ordinary algorithm:

1. `libmpfr.so.6` exists, but MPFR development headers are absent. An independent compiled MPFR directed-rounding oracle cannot be built and certified here.
2. `libOpenCL.so.1` exists, but OpenCL headers are absent and no concrete open-compute provider is attached.
3. Torch is CPU-only on this host; CUDA, MPS, and XPU are unavailable, so accelerator kernels cannot be runtime-certified here.
4. Transcendental interval enclosures therefore depend on the installed mpmath/libmp implementation and are not promoted to an independently formally verified claim.

See `docs/hardening_and_walls.md`.
