# Numerical Evidence Layer — MATH.SC-0 v0.7.0

The numerical-evidence layer runs **after** backend execution and verification. It is evidence-producing only: it cannot change a result from unverified to verified.

## Evidence classes

1. `exact_zero` — rigorous zero-width enclosure for exact rational results.
2. `forward_error_model` — model-based float64 forward-error estimate using standard `gamma(n)` style roundoff bounds.
3. `working_precision_model` — model-based estimate for high-precision working arithmetic.
4. `ulp_envelope` — diagnostic two-ULP envelope for runtime transcendental/library operations. It is explicitly not a proof of correctly-rounded libm behavior.
5. `generic_roundoff_envelope` — diagnostic fallback when no operation-specific model is implemented.

Every deterministic local result may carry `metadata.numerical_assessment`, including:

- evidence version;
- numeric regime;
- maximum absolute and relative error estimate;
- scalar interval when meaningful;
- conditioning estimate and classification;
- warning flags.

## Conditioning diagnostics

The module reports operation-specific condition proxies where useful. Cancellation-sensitive operations (`add`, `sub`, `sum`, `mean`, `dot`, and `matmul`) use ratios based on absolute contribution magnitude divided by result magnitude. Large ratios indicate that small input or rounding perturbations can produce large relative output changes.

The classifications are diagnostic:

- `well_conditioned`: estimate < 1e3
- `sensitive`: 1e3 <= estimate < 1e8
- `ill_conditioned`: estimate >= 1e8
- `singular_or_cancellation`: infinite estimate
- `not_reported`: a scalar condition proxy is not appropriate

These thresholds are policy diagnostics, not mathematical theorems.

## Authority rule

Numerical evidence does not replace verification:

```text
backend result -> verifier -> numerical evidence annotation
```

A model-based error estimate therefore never upgrades an unverified value.
