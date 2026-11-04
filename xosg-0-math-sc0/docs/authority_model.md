# Authority model — MATH.SC-0 v0.3.0

## A0 — deterministic local generation

Exact, high-precision, accelerator, open-compute, native C/C++, NumPy, and CPU backends may generate mathematical results.

## A1 — independent verification

The verifier can recompute or structurally validate deterministic results. Generation authority and verification authority remain separate. Native C/C++ output is cross-checked against the Python CPU reference backend when that backend supports the operation.

## A2 — external evidence

Web providers may supply external values or references. Such results remain `WEB_SOURCED` until a provenance-aware verifier independently validates them.

## A3 — heuristic inference

LLM fallback may propose a result only after deterministic-local and web layers are exhausted. LLM output is forced to `LLM_INFERRED` and `verified=false` by the JavaScript control plane.

## Required ordering

`deterministic local -> web -> LLM`

No runtime below the JavaScript control plane may directly invoke web or LLM fallback.
