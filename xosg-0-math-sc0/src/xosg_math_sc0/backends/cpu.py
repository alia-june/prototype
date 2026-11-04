from __future__ import annotations

import math
import statistics
from functools import reduce
from operator import mul

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus
from ..linalg import determinant, solve, inverse


class CPUBackend(Backend):
    name = "cpu"

    _ops = {
        "add", "sub", "mul", "div", "pow", "sqrt", "exp", "log", "sin", "cos", "tan",
        "sum", "product", "mean", "min", "max", "norm", "dot", "matmul", "det", "solve", "inverse"
    }

    def available(self) -> bool:
        return True

    def supports(self, request: ComputeRequest) -> bool:
        return request.operation in self._ops and request.mode != NumericMode.EXACT

    def compute(self, request: ComputeRequest) -> ComputeResult:
        op, a = request.operation, request.operands
        if op == "add": value = _elementwise_binary(a[0], a[1], lambda x, y: x + y)
        elif op == "sub": value = _elementwise_binary(a[0], a[1], lambda x, y: x - y)
        elif op == "mul": value = _elementwise_binary(a[0], a[1], lambda x, y: x * y)
        elif op == "div": value = a[0] / a[1]
        elif op == "pow": value = a[0] ** a[1]
        elif op == "sqrt": value = math.sqrt(a[0])
        elif op == "exp": value = math.exp(a[0])
        elif op == "log": value = math.log(a[0]) if len(a) == 1 else math.log(a[0], a[1])
        elif op == "sin": value = math.sin(a[0])
        elif op == "cos": value = math.cos(a[0])
        elif op == "tan": value = math.tan(a[0])
        elif op == "sum": value = math.fsum(a[0])
        elif op == "product": value = reduce(mul, a[0], 1)
        elif op == "mean": value = statistics.fmean(a[0])
        elif op == "min": value = min(a[0])
        elif op == "max": value = max(a[0])
        elif op == "norm": value = math.sqrt(math.fsum(float(x) * float(x) for x in a[0]))
        elif op == "dot": value = math.fsum(float(x) * float(y) for x, y in zip(a[0], a[1], strict=True))
        elif op == "matmul": value = _matmul(a[0], a[1])
        elif op == "det": value = determinant(a[0], float)
        elif op == "solve": value = solve(a[0], a[1], float)
        elif op == "inverse": value = inverse(a[0], float)
        else: raise ValueError(f"unsupported CPU operation: {op}")
        return ComputeResult(
            value=value,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm=f"python.{op}",
            exact=False,
            tolerance=request.tolerance,
        )


def _matmul(left, right):
    if not left or not right:
        return []
    cols = list(zip(*right, strict=True))
    return [[math.fsum(float(x) * float(y) for x, y in zip(row, col, strict=True)) for col in cols] for row in left]


def _elementwise_binary(left, right, fn):
    left_seq = isinstance(left, (list, tuple))
    right_seq = isinstance(right, (list, tuple))
    if left_seq != right_seq:
        raise ValueError("binary operands must both be scalars or have matching shapes")
    if not left_seq:
        return fn(left, right)
    if len(left) != len(right):
        raise ValueError("binary operands must have matching shapes")
    return [_elementwise_binary(x, y, fn) for x, y in zip(left, right, strict=True)]
