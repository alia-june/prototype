from __future__ import annotations

from .base import Backend
from ..interval import add, sub, mul, div, pow_int, elementwise, reduce_sum, reduce_product, mean, minimum, maximum, dot, matmul, as_interval, transcendental_unary, interval_log
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus


class IntervalBackend(Backend):
    name = "interval"
    _ops = {"add", "sub", "mul", "div", "pow", "sqrt", "exp", "log", "sin", "cos", "tan", "sum", "product", "mean", "min", "max", "dot", "matmul"}

    def available(self) -> bool:
        return True

    def supports(self, request: ComputeRequest) -> bool:
        return request.mode == NumericMode.INTERVAL and request.operation in self._ops

    def compute(self, request: ComputeRequest) -> ComputeResult:
        op, a = request.operation, request.operands
        if op == "add": value = elementwise(a[0], a[1], add)
        elif op == "sub": value = elementwise(a[0], a[1], sub)
        elif op == "mul": value = elementwise(a[0], a[1], mul)
        elif op == "div": value = div(as_interval(a[0]), as_interval(a[1])).to_wire()
        elif op == "pow":
            exponent = as_interval(a[1])
            if exponent.lo != exponent.hi or exponent.lo.denominator != 1:
                raise ValueError("interval pow requires a degenerate integer exponent")
            value = pow_int(as_interval(a[0]), int(exponent.lo)).to_wire()
        elif op in {"sqrt", "exp", "sin", "cos", "tan"}:
            value = transcendental_unary(as_interval(a[0]), op, decimal_digits=request.precision).to_wire()
        elif op == "log":
            base = as_interval(a[1]) if len(a) == 2 else None
            value = interval_log(as_interval(a[0]), base, decimal_digits=request.precision).to_wire()
        elif op == "sum": value = reduce_sum(a[0]).to_wire()
        elif op == "product": value = reduce_product(a[0]).to_wire()
        elif op == "mean": value = mean(a[0]).to_wire()
        elif op == "min": value = minimum(a[0]).to_wire()
        elif op == "max": value = maximum(a[0]).to_wire()
        elif op == "dot": value = dot(a[0], a[1]).to_wire()
        elif op == "matmul": value = matmul(a[0], a[1])
        else: raise ValueError(f"unsupported interval operation: {op}")
        return ComputeResult(
            value=value,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm=f"rational_interval.{op}",
            exact=False,
            metadata={
                "interval_semantics": "closed_finite_enclosure",
                "endpoint_arithmetic": "exact_fraction" if op not in {"sqrt", "exp", "log", "sin", "cos", "tan"} else "mpmath_libmp_directed_rounding_to_exact_binary_rational",
                "enclosure_rigor": "rigorous_for_supported_algebraic_operations" if op not in {"sqrt", "exp", "log", "sin", "cos", "tan"} else "directed_rounding_backend_enclosure",
                "interval_precision_digits": request.precision or 50,
            },
        )
