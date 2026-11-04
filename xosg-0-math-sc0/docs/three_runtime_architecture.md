# MATH.SC-0 v0.3.0 — Three-Runtime Architecture

## Runtime allocation

### JavaScript — control plane
Owns request normalization, global authority ordering, process orchestration, web fallback, and the final LLM fallback. The JavaScript plane does not perform trusted numerical computation itself.

### Python — numerical integration and verification plane
Owns numeric modes, exact and arbitrary precision calculation, backend selection within the deterministic-local domain, native-library binding, and independent result verification.

### C/C++ — native kernel plane
Owns performance-oriented float64 kernels behind a stable C ABI. Pure C provides compensated reductions; C++ supplies the public ABI and vector/matrix kernels. Python loads the shared library through `ctypes`.

## Authority flow

```text
JavaScript request contract
        |
        v
Python deterministic-local plane
        |
        +-> exact
        +-> high precision
        +-> hardware accelerator
        +-> open compute
        +-> native C/C++
        +-> NumPy
        +-> CPU reference
        |
        v
JavaScript external fallback boundary
        +-> web
        +-> LLM (strict last resort)
```

The C/C++ plane cannot call web or LLM. The Python worker launched by JavaScript also disables web and LLM. Therefore external escalation is possible only through the JavaScript control plane.

## Native verification

Native results return as `computed`, then the Python verifier recomputes supported operations with the CPU reference backend. A matching value within the request tolerance becomes `verified`; a mismatch remains `unverified`.

## Native ABI operations

- scalar: add, subtract, multiply, divide, power
- unary: square root, exponential, natural logarithm, sine, cosine, tangent
- vector: add, subtract, multiply
- reductions: sum, mean, Euclidean norm, dot product
- matrix: dense matrix multiplication

The native selector uses a workload threshold so trivial scalar calls normally stay on the lower-overhead CPU path.
