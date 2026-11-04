# MATH.SC-0 v0.6.0 Formal Operation Contract

Protocol `0.6` / contract `0.6.0` defines the current straight-computation semantics.

## Numeric modes

```text
auto
exact
float64
high_precision
interval
```

## Core constraints

Requests are rejected before dispatch when they violate arity, shape, numeric-domain, precision, work, or resource limits. JavaScript and Python enforce the same contract independently.

The contract includes ceilings for scalar count, rank, vector and matrix size, estimated operations, result size, precision, numeric-string length, and exact/interval power exponents.

## Interval extension

Interval mode accepts closed finite interval objects:

```json
{"$type":"interval","lo":"1/3","hi":"1/2"}
```

Algebraic interval operations use exact rational endpoints. `sqrt`, `exp`, `log`, `sin`, `cos`, and `tan` are eligible for directed-rounding interval execution. Domain-invalid interval requests are rejected or terminate local deterministic execution; they are not allowed to escape to web/LLM as substitute answers.

## Linear algebra extension

The following contracted operations are added:

```text
math.sc0.det.v1
math.sc0.solve.v1
math.sc0.inverse.v1
```

`det` and `inverse` require a non-empty square matrix. `solve` requires a non-empty square coefficient matrix and a conforming vector or matrix right-hand side.

## Authority rule

For a contracted operation:

```text
local deterministic attempt + local failure => terminal deterministic failure
```

External web/LLM fallback remains available for uncontracted/unknown operations, but cannot override a known operation's deterministic domain or singularity failure.
