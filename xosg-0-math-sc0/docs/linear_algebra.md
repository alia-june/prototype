# Linear Algebra Core — MATH.SC-0 v0.8.0

## Operations

```text
det(A)
solve(A, b)
solve(A, B)
inverse(A)
```

Coefficient matrices must be non-empty and square. Resource limits are checked before execution.

## Exact mode

Exact mode converts compatible operands to `Fraction` and uses partial-pivoted Gaussian/Gauss-Jordan elimination. Results are exact rational values and are accepted as exact representations.

## Float64 mode

Float64 may execute through:

- compiled C++ LU/partial-pivoting kernels;
- NumPy/LAPACK;
- the pure-Python CPU reference implementation.

The native C ABI exposes:

```text
sc0_det
sc0_solve
sc0_inverse
```

## Verification

`solve` is verified using the infinity-norm residual `||A x - b||_inf` (or `||A X-B||_inf`).

`inverse` is verified using `||A A^-1 - I||_inf`.

The numerical-evidence layer also reports an infinity-norm matrix condition number when NumPy is available, relative backward error for solves, and a forward-error proxy when the standard condition/backward-error relation is usable.

These diagnostics can warn about ill-conditioned problems without reclassifying an unverified result as verified.
