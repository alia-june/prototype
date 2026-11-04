from __future__ import annotations

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus


class NumPyBackend(Backend):
    name = "numpy"
    _ops = {"sum", "mean", "norm", "dot", "matmul", "add", "sub", "mul", "det", "solve", "inverse"}

    def __init__(self, vector_threshold: int = 256):
        self.vector_threshold = vector_threshold
        try:
            import numpy as np
            self.np = np
        except Exception:
            self.np = None

    def available(self) -> bool:
        return self.np is not None

    def supports(self, request: ComputeRequest) -> bool:
        if not self.available() or request.mode == NumericMode.EXACT or request.operation not in self._ops:
            return False
        return _work_size(request.operands) >= self.vector_threshold

    def cost_hint(self, request: ComputeRequest) -> float:
        return 0.3

    def compute(self, request: ComputeRequest) -> ComputeResult:
        np = self.np
        op, a = request.operation, request.operands
        if op in {"add", "sub", "mul"}:
            left, right = np.asarray(a[0], dtype=float), np.asarray(a[1], dtype=float)
            value = {"add": np.add, "sub": np.subtract, "mul": np.multiply}[op](left, right)
        elif op == "sum": value = np.sum(np.asarray(a[0], dtype=float))
        elif op == "mean": value = np.mean(np.asarray(a[0], dtype=float))
        elif op == "norm": value = np.linalg.norm(np.asarray(a[0], dtype=float))
        elif op == "dot": value = np.dot(np.asarray(a[0], dtype=float), np.asarray(a[1], dtype=float))
        elif op == "matmul": value = np.matmul(np.asarray(a[0], dtype=float), np.asarray(a[1], dtype=float))
        elif op == "det": value = np.linalg.det(np.asarray(a[0], dtype=float))
        elif op == "solve": value = np.linalg.solve(np.asarray(a[0], dtype=float), np.asarray(a[1], dtype=float))
        elif op == "inverse": value = np.linalg.inv(np.asarray(a[0], dtype=float))
        else: raise ValueError(op)
        if hasattr(value, "tolist"):
            value = value.tolist()
        elif hasattr(value, "item"):
            value = value.item()
        return ComputeResult(
            value=value,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm=f"numpy.{op}",
            exact=False,
            tolerance=request.tolerance,
        )


def _work_size(values):
    total = 0
    stack = list(values)
    while stack:
        item = stack.pop()
        if isinstance(item, (list, tuple)):
            stack.extend(item)
        else:
            total += 1
    return total
