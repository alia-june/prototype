# xOSG-0 MATH.SC-0 — Straight Computation Core v0.3.0

## Purpose

MATH.SC-0 is the deterministic numerical substrate for the xOSG-0 Mathematics Module. It separates interpretation, computation, verification, and external fallback authority.

## Core invariant

`interpretation != computation != verification`

A backend may generate a result without having authority to certify that result.

## Global dispatch order

1. Deterministic local computation
2. Web retrieval/reference fallback
3. LLM fallback, always last

## Deterministic-local order

1. Exact arithmetic
2. Arbitrary/high precision
3. Hardware accelerator when worthwhile and available
4. Open-compute / heterogeneous provider
5. Native C/C++ kernels
6. NumPy/vectorized computation
7. Scalar/reference CPU

Web and LLM are not computational peers. Web is an external retrieval/reference channel. LLM is a non-authoritative inference fallback.

## Three-runtime allocation

- JavaScript: contracts, orchestration, global authority and external fallback boundary.
- Python: numerical mode system, deterministic backend integration, verification.
- C/C++: performance-critical float64 kernels behind a stable C ABI.

## Native policy

The native plane is selected only after exact/high-precision/accelerator/open-compute opportunities and only when the workload crosses a configurable threshold. Small scalar work stays on the lower-overhead CPU path by default.

Native results are marked `COMPUTED` first. The Python verifier then recomputes supported operations with the independent CPU backend; matching results become `VERIFIED`.

## Result states

- COMPUTED: execution completed but is not yet accepted by verification.
- VERIFIED: internally verified deterministic result.
- EXTERNALLY_VERIFIED: reserved for externally sourced values independently validated against authoritative evidence.
- WEB_SOURCED: supplied by an external web provider.
- LLM_INFERRED: supplied by the final LLM fallback and non-authoritative until independently checked.
- UNVERIFIED: execution completed but verification failed or could not establish validity.
- FAILED: no backend completed the request.

## Near-term hardening

- versioned operation registry with typed arity/shape contracts
- explicit overflow, underflow, NaN and infinity policy
- interval/error-bound arithmetic
- deterministic resource ceilings
- SIMD-specialized native kernels
- native benchmark-driven dispatch thresholds
- provenance schema for web results
- property-based and mutation testing
