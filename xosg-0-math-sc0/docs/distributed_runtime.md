# Distributed Runtime Architecture — MATH.SC-0 v0.3.0

MATH.SC-0 currently uses exactly three implementation families: JavaScript, Python, and C/C++.

## JavaScript control plane

Owns the global request contract and the authority ordering:

`deterministic_local -> web -> llm_fallback`

It launches the Python data plane with both external fallbacks disabled. Therefore a numerical worker cannot silently escalate itself to retrieval or generative inference.

## Python numerical plane

Owns backend integration, exact/high-precision computation, optional hardware/open-compute dispatch, C/C++ binding, NumPy/CPU fallback, and verification:

`exact -> high_precision -> accelerator -> open_compute -> native -> numpy -> cpu`

An operator-trusted open-compute provider can be injected with `XOSG_SC0_OPEN_COMPUTE_PROVIDER=module:attribute`.

## C/C++ native plane

Owns compiled float64 kernels only. The native shared library exposes a C ABI and has no web or LLM capability. Python binds it with `ctypes`.

Pure C currently implements compensated reductions. C++ implements the public ABI plus scalar, vector, and matrix operations.

## Process and ABI boundaries

JavaScript exchanges JSON with `scripts/sc0_worker.py`. Python exchanges typed arrays/scalars with the native shared library through the C ABI in `native/include/sc0_native.h`.

Exact rationals crossing the JavaScript/Python boundary use tagged JSON values such as:

```json
{"$type":"fraction","numerator":1,"denominator":3}
```

Native results remain ordinary float64 values and are independently cross-checked by the Python CPU reference backend when supported.
