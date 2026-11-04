# Interval Arithmetic — MATH.SC-0 v0.8.0

SC-0 supports closed finite intervals with exact rational wire endpoints.

## Exact algebraic interval operations

```text
add sub mul div integer-pow
sum product mean min max dot matmul
```

These use exact `Fraction` endpoint arithmetic.

## Directed-rounding transcendental operations

```text
sqrt exp log sin cos tan
```

These use mpmath `libmp` interval primitives with floor/ceiling directed rounding and convert the resulting binary endpoints back to exact rational wire values.

The evidence layer distinguishes exact rational interval rigor from backend-directed transcendental rounding. See `directed_rounding_intervals.md`.
