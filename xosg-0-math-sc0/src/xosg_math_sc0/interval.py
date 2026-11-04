from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable


@dataclass(frozen=True)
class Interval:
    """Closed rational interval [lo, hi].

    Endpoints are exact Fractions.  For JSON numeric inputs that arrived as
    binary floats, Fraction.from_float preserves the exact supplied machine
    value; string endpoints such as "0.1" preserve the exact decimal rational.
    """

    lo: Fraction
    hi: Fraction

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @property
    def width(self) -> Fraction:
        return self.hi - self.lo

    def contains_zero(self) -> bool:
        return self.lo <= 0 <= self.hi

    def to_wire(self) -> dict[str, Any]:
        return {"$type": "interval", "lo": self.lo, "hi": self.hi}


def as_interval(value: Any) -> Interval:
    if isinstance(value, Interval):
        return value
    if isinstance(value, dict) and value.get("$type") == "interval":
        return Interval(_as_fraction(value.get("lo")), _as_fraction(value.get("hi")))
    q = _as_fraction(value)
    return Interval(q, q)


def add(a: Interval, b: Interval) -> Interval:
    return Interval(a.lo + b.lo, a.hi + b.hi)


def sub(a: Interval, b: Interval) -> Interval:
    return Interval(a.lo - b.hi, a.hi - b.lo)


def mul(a: Interval, b: Interval) -> Interval:
    vals = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
    return Interval(min(vals), max(vals))


def div(a: Interval, b: Interval) -> Interval:
    if b.contains_zero():
        raise ZeroDivisionError("interval denominator contains zero")
    recip = Interval(min(Fraction(1, 1) / b.lo, Fraction(1, 1) / b.hi), max(Fraction(1, 1) / b.lo, Fraction(1, 1) / b.hi))
    return mul(a, recip)


def pow_int(a: Interval, exponent: int) -> Interval:
    if exponent == 0:
        return Interval(Fraction(1), Fraction(1))
    if exponent < 0:
        if a.contains_zero():
            raise ZeroDivisionError("negative interval power undefined when base contains zero")
        return div(Interval(Fraction(1), Fraction(1)), pow_int(a, -exponent))
    if exponent % 2 == 1:
        return Interval(a.lo ** exponent, a.hi ** exponent)
    vals = (a.lo ** exponent, a.hi ** exponent)
    lo = Fraction(0) if a.contains_zero() else min(vals)
    return Interval(lo, max(vals))


def elementwise(left: Any, right: Any, fn: Callable[[Interval, Interval], Interval]) -> Any:
    lseq = isinstance(left, (list, tuple)); rseq = isinstance(right, (list, tuple))
    if lseq != rseq:
        raise ValueError("interval elementwise operands must have identical shapes")
    if not lseq:
        return fn(as_interval(left), as_interval(right)).to_wire()
    if len(left) != len(right):
        raise ValueError("interval elementwise operands must have identical shapes")
    return [elementwise(x, y, fn) for x, y in zip(left, right, strict=True)]


def reduce_sum(values: list[Any] | tuple[Any, ...]) -> Interval:
    out = Interval(Fraction(0), Fraction(0))
    for value in values:
        out = add(out, as_interval(value))
    return out


def reduce_product(values: list[Any] | tuple[Any, ...]) -> Interval:
    out = Interval(Fraction(1), Fraction(1))
    for value in values:
        out = mul(out, as_interval(value))
    return out


def mean(values: list[Any] | tuple[Any, ...]) -> Interval:
    if not values:
        raise ValueError("mean requires at least one value")
    return div(reduce_sum(values), Interval(Fraction(len(values)), Fraction(len(values))))


def minimum(values: list[Any] | tuple[Any, ...]) -> Interval:
    items = [as_interval(x) for x in values]
    if not items:
        raise ValueError("min requires at least one value")
    return Interval(min(x.lo for x in items), min(x.hi for x in items))


def maximum(values: list[Any] | tuple[Any, ...]) -> Interval:
    items = [as_interval(x) for x in values]
    if not items:
        raise ValueError("max requires at least one value")
    return Interval(max(x.lo for x in items), max(x.hi for x in items))


def dot(left: list[Any], right: list[Any]) -> Interval:
    if len(left) != len(right):
        raise ValueError("dot requires equal-length vectors")
    out = Interval(Fraction(0), Fraction(0))
    for x, y in zip(left, right, strict=True):
        out = add(out, mul(as_interval(x), as_interval(y)))
    return out


def matmul(left: list[list[Any]], right: list[list[Any]]) -> list[list[dict[str, Any]]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matmul dimension mismatch")
    cols = list(zip(*right, strict=True))
    return [[dot(row, list(col)).to_wire() for col in cols] for row in left]


def validate_wire(value: Any) -> bool:
    if isinstance(value, dict) and value.get("$type") == "interval":
        try:
            as_interval(value)
            return True
        except Exception:
            return False
    if isinstance(value, (list, tuple)):
        return all(validate_wire(x) for x in value)
    return False


def widths(value: Any) -> list[Fraction]:
    if isinstance(value, dict) and value.get("$type") == "interval":
        return [as_interval(value).width]
    if isinstance(value, (list, tuple)):
        out: list[Fraction] = []
        for item in value:
            out.extend(widths(item))
        return out
    return []


def _as_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise TypeError("boolean is not an interval endpoint")
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        return Fraction.from_float(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict) and value.get("$type") == "fraction":
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise TypeError(f"unsupported interval endpoint type: {type(value).__name__}")

# Directed-rounding transcendental interval support. This uses mpmath's libmp
# interval primitives, which explicitly evaluate lower endpoints with floor
# rounding and upper endpoints with ceiling rounding. Endpoints are converted
# back to exact binary rationals for the wire representation.

def _precision_bits(decimal_digits: int | None) -> int:
    import math
    digits = max(18, int(decimal_digits or 50))
    return max(64, int(math.ceil(digits * math.log2(10))) + 24)


def _fraction_to_mpf(q: Fraction, prec: int, rounding: str):
    from mpmath.libmp import from_rational
    return from_rational(q.numerator, q.denominator, prec, rounding)


def _mpf_to_fraction(value) -> Fraction:
    from mpmath.libmp import finf, fninf, fnan
    if value in {finf, fninf, fnan}:
        raise ArithmeticError("extended/non-finite interval endpoint cannot be represented by SC-0 closed finite interval")
    sign, man, exp, _bc = value
    if man == 0:
        return Fraction(0, 1)
    # Guard wire-materialization cost. mpf stores large exponents compactly,
    # while Fraction would expand them into enormous Python integers.
    max_bits = 1_000_000
    projected_bits = int(man).bit_length() + max(0, int(exp))
    denominator_bits = max(0, -int(exp))
    if max(projected_bits, denominator_bits) > max_bits:
        raise OverflowError(f"interval endpoint would exceed {max_bits} bits")
    q = Fraction(-man if sign else man, 1)
    if exp >= 0:
        return q * (1 << exp)
    return q / (1 << (-exp))


def _to_mpi(a: Interval, prec: int):
    from mpmath.libmp import round_floor, round_ceiling
    return (
        _fraction_to_mpf(a.lo, prec, round_floor),
        _fraction_to_mpf(a.hi, prec, round_ceiling),
    )


def _from_mpi(pair) -> Interval:
    return Interval(_mpf_to_fraction(pair[0]), _mpf_to_fraction(pair[1]))


def transcendental_unary(a: Interval, operation: str, *, decimal_digits: int | None = None) -> Interval:
    from mpmath.libmp.libmpi import mpi_sqrt, mpi_exp, mpi_log, mpi_sin, mpi_cos, mpi_tan
    if operation == "sqrt" and a.lo < 0:
        raise ValueError("sqrt interval requires nonnegative lower endpoint")
    if operation == "log" and a.lo <= 0:
        raise ValueError("log interval requires strictly positive lower endpoint")
    prec = _precision_bits(decimal_digits)
    funcs = {
        "sqrt": mpi_sqrt,
        "exp": mpi_exp,
        "log": mpi_log,
        "sin": mpi_sin,
        "cos": mpi_cos,
        "tan": mpi_tan,
    }
    if operation not in funcs:
        raise ValueError(f"unsupported directed interval unary operation: {operation}")
    out = _from_mpi(funcs[operation](_to_mpi(a, prec), prec))
    return out


def interval_log(value: Interval, base: Interval | None = None, *, decimal_digits: int | None = None) -> Interval:
    numerator = transcendental_unary(value, "log", decimal_digits=decimal_digits)
    if base is None:
        return numerator
    if base.lo <= 0 or base.contains_zero() or base.lo <= 1 <= base.hi:
        raise ValueError("log interval base must be positive and must not contain 1")
    denominator = transcendental_unary(base, "log", decimal_digits=decimal_digits)
    if denominator.contains_zero():
        raise ZeroDivisionError("log base enclosure contains zero")
    return div(numerator, denominator)
