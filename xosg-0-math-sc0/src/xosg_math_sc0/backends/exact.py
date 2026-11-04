from __future__ import annotations

from fractions import Fraction
from math import prod

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus
from ..linalg import determinant, solve, inverse


class ExactBackend(Backend):
    name = "exact"
    _ops = {"add", "sub", "mul", "div", "pow", "sum", "product", "det", "solve", "inverse"}

    def available(self) -> bool:
        return True

    def supports(self, request: ComputeRequest) -> bool:
        if request.operation not in self._ops or request.mode not in (NumericMode.AUTO, NumericMode.EXACT):
            return False
        try:
            for value in _flatten(request.operands):
                _as_fraction(value)
            return True
        except (TypeError, ValueError, ZeroDivisionError):
            return False

    def compute(self, request: ComputeRequest) -> ComputeResult:
        op, a = request.operation, request.operands
        if op == "add": value = _elementwise(a[0], a[1], lambda x, y: x + y)
        elif op == "sub": value = _elementwise(a[0], a[1], lambda x, y: x - y)
        elif op == "mul": value = _elementwise(a[0], a[1], lambda x, y: x * y)
        elif op == "div": value = _as_fraction(a[0]) / _as_fraction(a[1])
        elif op == "pow":
            base, exponent = _as_fraction(a[0]), a[1]
            if isinstance(exponent, str):
                try: exponent = int(exponent)
                except ValueError as exc: raise ValueError("exact pow requires an integer exponent") from exc
            if not isinstance(exponent, int): raise ValueError("exact pow requires an integer exponent")
            value = base ** exponent
        elif op == "sum": value = sum((_as_fraction(x) for x in a[0]), Fraction(0, 1))
        elif op == "product": value = prod((_as_fraction(x) for x in a[0]), start=Fraction(1, 1))
        elif op == "det": value = determinant(a[0], _as_fraction)
        elif op == "solve": value = solve(a[0], a[1], _as_fraction)
        elif op == "inverse": value = inverse(a[0], _as_fraction)
        else: raise ValueError(f"unsupported exact operation: {op}")
        return ComputeResult(value=value, status=ResultStatus.COMPUTED, backend=self.name, algorithm=f"fraction.{op}", exact=True)


def _elementwise(left, right, fn):
    left_seq = isinstance(left, (list, tuple)); right_seq = isinstance(right, (list, tuple))
    if left_seq != right_seq: raise ValueError("exact elementwise operands must have identical shapes")
    if not left_seq: return fn(_as_fraction(left), _as_fraction(right))
    if len(left) != len(right): raise ValueError("exact elementwise operands must have identical shapes")
    return [_elementwise(x, y, fn) for x, y in zip(left, right, strict=True)]


def _as_fraction(value):
    if isinstance(value, Fraction): return value
    if isinstance(value, int) and not isinstance(value, bool): return Fraction(value, 1)
    if isinstance(value, str): return Fraction(value)
    raise TypeError(f"not exact-compatible: {type(value).__name__}")


def _flatten(values):
    for value in values:
        if isinstance(value, (list, tuple)): yield from _flatten(value)
        else: yield value
