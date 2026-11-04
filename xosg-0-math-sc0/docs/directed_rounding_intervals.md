# Directed-Rounding Interval Enclosures — MATH.SC-0 v0.8.0

## Representation

SC-0 interval values remain closed finite intervals:

```text
[lo, hi]
```

Wire endpoints are exact rational values. Algebraic interval operations operate directly on `Fraction` endpoints.

For transcendental functions, SC-0 converts exact rational endpoints into mpmath `libmp` values using floor rounding for the lower endpoint and ceiling rounding for the upper endpoint. The mpmath interval primitives then use directed rounding internally. The resulting binary endpoints are converted exactly back to rational numbers.

## Supported transcendental operations

```text
sqrt exp log sin cos tan
```

`log(x, base)` is implemented as interval `ln(x) / ln(base)` and requires a positive base interval that does not contain 1.

A finite closed interval is the only supported interval output form. If a computation would require an extended endpoint (`+/-inf`) or materialize an endpoint beyond the configured safety ceiling, the deterministic operation fails rather than emitting a misleading finite enclosure.

## Evidence semantics

Algebraic rational intervals are labeled:

```text
rigor = rigorous
```

Transcendental interval results are labeled:

```text
rigor = backend_directed_rounding
warning = transcendental_enclosure_depends_on_libmp_correctness
```

This is deliberate. The implementation uses directed rounding, but the current host cannot compile an independent MPFR oracle because the MPFR development headers are absent.

## Hardening

The test suite includes seeded interval-containment sampling against 100-digit mpmath evaluations for `sqrt`, `exp`, `log`, `sin`, and `cos`, plus wide-range trigonometric extrema tests.
