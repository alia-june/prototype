from __future__ import annotations

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus


class HighPrecisionBackend(Backend):
    name = "high_precision"
    _ops = {"add", "sub", "mul", "div", "pow", "sqrt", "exp", "log", "sin", "cos", "tan", "sum", "det", "solve", "inverse"}

    def __init__(self):
        try:
            import mpmath as mp
            self.mp = mp
        except Exception:
            self.mp = None

    def available(self) -> bool:
        return self.mp is not None

    def supports(self, request: ComputeRequest) -> bool:
        return self.available() and request.operation in self._ops and request.mode == NumericMode.HIGH_PRECISION

    def compute(self, request: ComputeRequest) -> ComputeResult:
        mp = self.mp
        mp.mp.dps = request.precision or 50
        op, a, cvt = request.operation, request.operands, mp.mpf
        if op == "add": value = _elementwise(a[0], a[1], lambda x, y: cvt(x) + cvt(y))
        elif op == "sub": value = _elementwise(a[0], a[1], lambda x, y: cvt(x) - cvt(y))
        elif op == "mul": value = _elementwise(a[0], a[1], lambda x, y: cvt(x) * cvt(y))
        elif op == "div": value = cvt(a[0]) / cvt(a[1])
        elif op == "pow": value = mp.power(cvt(a[0]), cvt(a[1]))
        elif op == "sqrt": value = mp.sqrt(cvt(a[0]))
        elif op == "exp": value = mp.exp(cvt(a[0]))
        elif op == "log": value = mp.log(cvt(a[0])) if len(a) == 1 else mp.log(cvt(a[0]), cvt(a[1]))
        elif op == "sin": value = mp.sin(cvt(a[0]))
        elif op == "cos": value = mp.cos(cvt(a[0]))
        elif op == "tan": value = mp.tan(cvt(a[0]))
        elif op == "sum": value = mp.fsum(cvt(x) for x in a[0])
        elif op == "det":
            value = mp.det(mp.matrix([[cvt(x) for x in row] for row in a[0]]))
        elif op == "solve":
            A = mp.matrix([[cvt(x) for x in row] for row in a[0]])
            if a[1] and isinstance(a[1][0], (list, tuple)):
                B = [[cvt(x) for x in row] for row in a[1]]
                cols = list(zip(*B, strict=True))
                solved = [mp.lu_solve(A, mp.matrix(list(col))) for col in cols]
                value = [[solved[j][i] for j in range(len(solved))] for i in range(A.rows)]
            else:
                x = mp.lu_solve(A, mp.matrix([cvt(v) for v in a[1]]))
                value = [x[i] for i in range(x.rows)]
        elif op == "inverse":
            inv = mp.inverse(mp.matrix([[cvt(x) for x in row] for row in a[0]]))
            value = [[inv[i, j] for j in range(inv.cols)] for i in range(inv.rows)]
        else: raise ValueError(op)
        return ComputeResult(value=value, status=ResultStatus.COMPUTED, backend=self.name, algorithm=f"mpmath.{op}", exact=False, tolerance=request.tolerance, metadata={"decimal_digits": mp.mp.dps})


def _elementwise(left, right, fn):
    left_seq = isinstance(left, (list, tuple)); right_seq = isinstance(right, (list, tuple))
    if left_seq != right_seq: raise ValueError("high-precision elementwise operands must have identical shapes")
    if not left_seq: return fn(left, right)
    if len(left) != len(right): raise ValueError("high-precision elementwise operands must have identical shapes")
    return [_elementwise(x, y, fn) for x, y in zip(left, right, strict=True)]
