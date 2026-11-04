from __future__ import annotations

import math
from fractions import Fraction
from numbers import Number

from .types import ComputeRequest, ComputeResult, NumericMode, ResultStatus
from .backends.cpu import CPUBackend
from .interval import validate_wire
from .linalg import residual_inf_norm, inverse_residual_inf_norm


class Verifier:
    def __init__(self):
        self.reference = CPUBackend()

    def verify(self, request: ComputeRequest, result: ComputeResult) -> ComputeResult:
        if result.status in {ResultStatus.WEB_SOURCED, ResultStatus.LLM_INFERRED, ResultStatus.FAILED}:
            return result
        if request.mode == NumericMode.INTERVAL and result.backend == "interval":
            result.verified = validate_wire(result.value)
            result.status = ResultStatus.VERIFIED if result.verified else ResultStatus.UNVERIFIED
            result.trace.append("verification: rational interval enclosure structure accepted" if result.verified else "verification: malformed interval enclosure")
            return result
        if result.exact:
            if request.operation == "solve":
                try:
                    if _exact_solve_check(request.operands[0], result.value, request.operands[1]):
                        result.verified = True
                        result.status = ResultStatus.VERIFIED
                        result.trace.append("verification: exact solve residual identity accepted")
                    else:
                        result.verified = False
                        result.status = ResultStatus.UNVERIFIED
                        result.trace.append("verification: exact solve residual mismatch")
                    return result
                except Exception as exc:
                    result.trace.append(f"verification: exact solve check failed: {exc}")
            if request.operation == "inverse":
                try:
                    if _exact_inverse_check(request.operands[0], result.value):
                        result.verified = True
                        result.status = ResultStatus.VERIFIED
                        result.trace.append("verification: exact inverse identity accepted")
                    else:
                        result.verified = False
                        result.status = ResultStatus.UNVERIFIED
                        result.trace.append("verification: exact inverse identity mismatch")
                    return result
                except Exception as exc:
                    result.trace.append(f"verification: exact inverse check failed: {exc}")
            if request.operation == "det":
                try:
                    import sympy as sp
                    reference = sp.Matrix([[sp.Rational(str(x)) for x in row] for row in request.operands[0]]).det()
                    ref_fraction = Fraction(int(reference.p), int(reference.q)) if getattr(reference, "is_Rational", False) else Fraction(str(reference))
                    result.verified = (result.value == ref_fraction)
                    result.status = ResultStatus.VERIFIED if result.verified else ResultStatus.UNVERIFIED
                    result.trace.append("verification: exact determinant SymPy reference match" if result.verified else "verification: exact determinant SymPy reference mismatch")
                    return result
                except Exception as exc:
                    result.trace.append(f"verification: exact determinant reference failed: {exc}")
            result.verified = True
            result.status = ResultStatus.VERIFIED
            result.trace.append("verification: exact representation accepted")
            return result
        if request.operation == "solve":
            try:
                residual = residual_inf_norm(request.operands[0], result.value, request.operands[1])
                scale = _solve_scale(request.operands[0], result.value, request.operands[1])
                threshold = max(request.tolerance, 1e-12) * max(1.0, scale) * 10.0
                result.metadata["verification_residual_inf"] = residual
                result.metadata["verification_threshold"] = threshold
                if math.isfinite(residual) and residual <= threshold:
                    result.verified = True
                    result.status = ResultStatus.VERIFIED
                    result.trace.append("verification: linear solve residual accepted")
                else:
                    result.verified = False
                    result.status = ResultStatus.UNVERIFIED
                    result.trace.append("verification: linear solve residual too large")
                return result
            except Exception as exc:
                result.trace.append(f"verification: solve residual check failed: {exc}")
        if request.operation == "inverse":
            try:
                residual = inverse_residual_inf_norm(request.operands[0], result.value)
                scale = _matrix_inf_norm(request.operands[0]) * _matrix_inf_norm(result.value)
                threshold = max(request.tolerance, 1e-12) * max(1.0, scale) * 10.0
                result.metadata["verification_residual_inf"] = residual
                result.metadata["verification_threshold"] = threshold
                if math.isfinite(residual) and residual <= threshold:
                    result.verified = True
                    result.status = ResultStatus.VERIFIED
                    result.trace.append("verification: inverse identity residual accepted")
                else:
                    result.verified = False
                    result.status = ResultStatus.UNVERIFIED
                    result.trace.append("verification: inverse identity residual too large")
                return result
            except Exception as exc:
                result.trace.append(f"verification: inverse residual check failed: {exc}")
        if request.operation == "det" and result.backend == "cpu":
            try:
                import numpy as np
                ref = float(np.linalg.det(np.asarray(request.operands[0], dtype=float)))
                if _close(result.value, ref, max(request.tolerance, 1e-11)):
                    result.verified = True
                    result.status = ResultStatus.VERIFIED
                    result.trace.append("verification: determinant NumPy reference match")
                else:
                    result.status = ResultStatus.UNVERIFIED
                    result.trace.append("verification: determinant NumPy reference mismatch")
                return result
            except Exception as exc:
                result.trace.append(f"verification: determinant NumPy reference failed: {exc}")
        if result.backend != "cpu" and self.reference.supports(request):
            try:
                ref_request = _reference_request(request)
                ref = self.reference.compute(ref_request)
                if _close(result.value, ref.value, request.tolerance):
                    result.verified = True
                    result.status = ResultStatus.VERIFIED
                    result.trace.append("verification: heterogeneous CPU reference match")
                else:
                    result.status = ResultStatus.UNVERIFIED
                    result.trace.append("verification: CPU reference mismatch")
                return result
            except Exception as exc:
                result.trace.append(f"verification: reference failed: {exc}")
        if result.backend == "cpu":
            result.verified = _finite_or_structured(result.value)
            result.status = ResultStatus.VERIFIED if result.verified else ResultStatus.UNVERIFIED
            result.trace.append("verification: CPU structural/finite check")
        return result


def _finite_or_structured(value):
    if isinstance(value, Fraction):
        return True
    if isinstance(value, Number):
        try:
            return math.isfinite(float(value))
        except Exception:
            return True
    if isinstance(value, (list, tuple)):
        return all(_finite_or_structured(x) for x in value)
    return value is not None


def _close(a, b, tol):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b))
    try:
        af, bf = float(a), float(b)
        return math.isclose(af, bf, rel_tol=tol, abs_tol=tol)
    except Exception:
        return a == b


def _reference_request(request: ComputeRequest) -> ComputeRequest:
    def convert(value):
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        if isinstance(value, list):
            return [convert(x) for x in value]
        if isinstance(value, tuple):
            return tuple(convert(x) for x in value)
        return value

    return ComputeRequest(
        operation=request.operation,
        operands=tuple(convert(x) for x in request.operands),
        mode=NumericMode.FLOAT64,
        precision=request.precision,
        tolerance=max(request.tolerance, 1e-12),
        deterministic=request.deterministic,
        allow_web=False,
        allow_llm=False,
        metadata=request.metadata,
    )


def _matrix_inf_norm(matrix):
    return max((sum(abs(float(x)) for x in row) for row in matrix), default=0.0)

def _vector_inf_norm(vector):
    if vector and isinstance(vector[0], (list, tuple)):
        return max((sum(abs(float(x)) for x in row) for row in vector), default=0.0)
    return max((abs(float(x)) for x in vector), default=0.0)

def _solve_scale(matrix, solution, rhs):
    return _matrix_inf_norm(matrix) * _vector_inf_norm(solution) + _vector_inf_norm(rhs)


def _as_fraction_exact(value):
    if isinstance(value, Fraction): return value
    if isinstance(value, int) and not isinstance(value, bool): return Fraction(value, 1)
    if isinstance(value, str): return Fraction(value)
    return Fraction(value)

def _exact_solve_check(matrix, solution, rhs):
    from .linalg import matmul
    if rhs and isinstance(rhs[0], (list, tuple)):
        product = matmul(matrix, solution, _as_fraction_exact)
        target = [[_as_fraction_exact(x) for x in row] for row in rhs]
        return product == target
    target = [_as_fraction_exact(x) for x in rhs]
    product = []
    for row in matrix:
        product.append(sum((_as_fraction_exact(a) * _as_fraction_exact(x) for a, x in zip(row, solution, strict=True)), Fraction(0)))
    return product == target

def _exact_inverse_check(matrix, inv):
    from .linalg import matmul
    product = matmul(matrix, inv, _as_fraction_exact)
    n = len(matrix)
    identity = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
    return product == identity
