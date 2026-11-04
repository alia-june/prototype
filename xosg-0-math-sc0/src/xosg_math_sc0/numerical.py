from __future__ import annotations

import math
from fractions import Fraction
from numbers import Number
from typing import Any

from .types import ComputeRequest, ComputeResult, NumericMode, ResultStatus
from .interval import widths

EVIDENCE_VERSION = "0.2.0"
_FLOAT_EPS = 2.0 ** -52


def assess_numerics(request: ComputeRequest, result: ComputeResult) -> ComputeResult:
    """Attach quantitative numerical evidence to deterministic local results.

    This layer deliberately distinguishes rigorous evidence from model-based or
    diagnostic estimates.  It never upgrades a result's verification status.
    """
    if result.status in {ResultStatus.FAILED, ResultStatus.WEB_SOURCED, ResultStatus.LLM_INFERRED}:
        return result

    if request.mode == NumericMode.INTERVAL and result.backend == "interval":
        ws = widths(result.value)
        max_width = max(ws, default=Fraction(0))
        directed = request.operation in {"sqrt", "exp", "log", "sin", "cos", "tan"}
        assessment = {
            "evidence_version": EVIDENCE_VERSION,
            "numeric_regime": "directed_rounding_interval" if directed else "rational_interval",
            "error_bound": {
                "kind": "closed_interval_enclosure",
                "rigor": "backend_directed_rounding" if directed else "rigorous",
                "method": (
                    "mpmath libmp floor/ceiling directed rounding; exact binary-rational wire endpoints"
                    if directed else "exact rational endpoint interval arithmetic"
                ),
                "max_interval_width": str(max_width),
                "endpoint_arithmetic": (
                    "directed_binary_rounding_then_exact_fraction" if directed else "exact_fraction"
                ),
            },
            "conditioning": {"estimate": None, "classification": "not_applicable_to_enclosure", "method": "interval enclosure carried directly"},
            "warning_flags": (["transcendental_enclosure_depends_on_libmp_correctness"] if directed else []),
        }
        result.metadata["numerical_assessment"] = assessment
        result.trace.append("numerics: directed-rounding interval enclosure attached" if directed else "numerics: rigorous rational interval enclosure attached")
        return result

    if result.exact:
        assessment = {
            "evidence_version": EVIDENCE_VERSION,
            "numeric_regime": "exact",
            "error_bound": {
                "kind": "exact_zero",
                "rigor": "rigorous",
                "max_absolute_error": 0.0,
                "max_relative_error": 0.0,
                "interval": _exact_interval(result.value),
            },
            "conditioning": _conditioning(request, result.value),
            "warning_flags": [],
        }
        result.metadata["numerical_assessment"] = assessment
        result.trace.append("numerics: exact zero-width error enclosure")
        return result

    if request.mode == NumericMode.HIGH_PRECISION or result.backend == "high_precision":
        digits = int(result.metadata.get("decimal_digits") or request.precision or 50)
        magnitude = _max_abs(result.value)
        # mpmath normally carries more internal detail, but this is explicitly a
        # model-based decimal working-precision estimate, not a proof enclosure.
        abs_bound = (10.0 ** max(-307, -(digits - 2))) * max(1.0, magnitude)
        assessment = _assessment_payload(
            request,
            result,
            abs_bound=abs_bound,
            kind="working_precision_model",
            rigor="model_based",
            method=f"decimal_digits={digits}",
        )
        if request.operation in {"solve", "inverse", "det"}:
            assessment["linear_algebra"] = _linear_algebra_diagnostics(request, result.value)
            _append_linalg_warnings(assessment)
        result.metadata["numerical_assessment"] = assessment
        result.trace.append("numerics: high-precision working-precision error model attached")
        return result

    abs_bound, kind, rigor, method = _float64_bound(request, result.value)
    assessment = _assessment_payload(
        request,
        result,
        abs_bound=abs_bound,
        kind=kind,
        rigor=rigor,
        method=method,
    )
    if request.operation in {"solve", "inverse", "det"}:
        assessment["linear_algebra"] = _linear_algebra_diagnostics(request, result.value)
        _append_linalg_warnings(assessment)
    result.metadata["numerical_assessment"] = assessment
    result.trace.append(f"numerics: {kind} evidence attached")
    return result


def _assessment_payload(request, result, *, abs_bound: float, kind: str, rigor: str, method: str):
    magnitude = _max_abs(result.value)
    rel = 0.0 if abs_bound == 0.0 and magnitude == 0.0 else (abs_bound / magnitude if magnitude else math.inf)
    error = {
        "kind": kind,
        "rigor": rigor,
        "method": method,
        "max_absolute_error": _finite_json_number(abs_bound),
        "max_relative_error": _finite_json_number(rel),
    }
    if _is_scalar(result.value):
        error["interval"] = _scalar_interval(result.value, abs_bound)
    conditioning = _conditioning(request, result.value)
    warnings = []
    if rigor != "rigorous":
        warnings.append("error_bound_not_formal_proof")
    estimate = conditioning.get("estimate")
    if estimate == "infinity" or (isinstance(estimate, (int, float)) and estimate >= 1e8):
        warnings.append("ill_conditioned_or_cancellation_sensitive")
    if kind == "ulp_envelope":
        warnings.append("transcendental_library_accuracy_is_runtime_dependent")
    return {
        "evidence_version": EVIDENCE_VERSION,
        "numeric_regime": "float64" if request.mode != NumericMode.HIGH_PRECISION else "high_precision",
        "error_bound": error,
        "conditioning": conditioning,
        "warning_flags": warnings,
    }


def _float64_bound(request: ComputeRequest, value: Any):
    op, a = request.operation, request.operands
    try:
        if op in {"add", "sub"}:
            scale = _binary_component_scale(a[0], a[1], lambda x, y: abs(x) + abs(y))
            return _gamma(1) * scale, "forward_error_model", "model_based", "gamma(1)*(|a|+|b|)"
        if op == "mul":
            return _gamma(1) * _max_abs(value), "forward_error_model", "model_based", "gamma(1)*|result|"
        if op == "div":
            return _gamma(2) * _max_abs(value), "forward_error_model", "model_based", "gamma(2)*|result|"
        if op == "sum":
            vals = [float(x) for x in a[0]]
            return _gamma(max(1, len(vals))) * math.fsum(abs(x) for x in vals), "forward_error_model", "model_based", "gamma(n)*sum(abs(x))"
        if op == "product":
            n = len(a[0])
            return _gamma(max(1, n)) * _max_abs(value), "forward_error_model", "model_based", "gamma(n)*|result|"
        if op == "mean":
            vals = [float(x) for x in a[0]]
            sb = _gamma(max(1, len(vals))) * math.fsum(abs(x) for x in vals)
            return sb / len(vals) + _FLOAT_EPS * _max_abs(value), "forward_error_model", "model_based", "sum-bound/n + eps*|mean|"
        if op == "dot":
            left, right = [float(x) for x in a[0]], [float(x) for x in a[1]]
            scale = math.fsum(abs(x * y) for x, y in zip(left, right, strict=True))
            return _gamma(max(1, 2 * len(left))) * scale, "forward_error_model", "model_based", "gamma(2n)*sum(abs(x*y))"
        if op == "matmul":
            left, right = a[0], a[1]
            k = len(left[0])
            cols = list(zip(*right, strict=True))
            worst = 0.0
            for row in left:
                for col in cols:
                    scale = math.fsum(abs(float(x) * float(y)) for x, y in zip(row, col, strict=True))
                    worst = max(worst, _gamma(max(1, 2 * k)) * scale)
            return worst, "forward_error_model", "model_based", "max_ij gamma(2k)*sum(abs(a_ik*b_kj))"
        if op == "norm":
            n = len(a[0])
            return _gamma(max(1, 2 * n + 2)) * max(1.0, _max_abs(value)), "forward_error_model", "model_based", "gamma(2n+2)*max(1,|norm|)"
        if op in {"min", "max"}:
            return 0.0, "selection_exact_for_supplied_float_inputs", "model_based", "selected input value; excludes input-representation error"
        if op in {"sqrt", "exp", "log", "sin", "cos", "tan", "pow"}:
            return _ulp_bound(value), "ulp_envelope", "diagnostic", "two-ULP runtime diagnostic envelope"
    except Exception:
        pass
    return max(_ulp_bound(value), _FLOAT_EPS * max(1.0, _max_abs(value))), "generic_roundoff_envelope", "diagnostic", "eps/ULP fallback envelope"


def _conditioning(request: ComputeRequest, value: Any) -> dict[str, Any]:
    op, a = request.operation, request.operands
    estimate: float | None = None
    method = "not_available"
    try:
        if op in {"add", "sub"}:
            estimate = _max_component_condition(a[0], a[1], value)
            method = "max (|a|+|b|)/|a±b|"
        elif op == "sum" or op == "mean":
            vals = [float(x) for x in a[0]]
            denom = abs(math.fsum(vals))
            estimate = _ratio_or_inf(math.fsum(abs(x) for x in vals), denom)
            method = "sum(abs(x))/abs(sum(x))"
        elif op == "dot":
            left, right = [float(x) for x in a[0]], [float(x) for x in a[1]]
            num = math.fsum(abs(x * y) for x, y in zip(left, right, strict=True))
            estimate = _ratio_or_inf(num, abs(float(value)))
            method = "sum(abs(x*y))/abs(dot(x,y))"
        elif op == "matmul":
            estimate = _matmul_condition_proxy(a[0], a[1], value)
            method = "max componentwise cancellation ratio"
        elif op in {"mul", "div"}:
            estimate = 2.0
            method = "componentwise relative perturbation proxy"
        elif op == "sqrt":
            estimate = 0.5 if float(a[0]) > 0 else math.inf
            method = "relative condition |x f'(x)/f(x)|"
        elif op == "exp":
            estimate = abs(float(a[0]))
            method = "relative condition |x|"
        elif op == "log":
            x = float(a[0])
            lx = math.log(x)
            estimate = _ratio_or_inf(1.0, abs(lx))
            method = "relative condition 1/|ln(x)| for primary argument"
        elif op == "sin":
            x = float(a[0]); s = math.sin(x)
            estimate = _ratio_or_inf(abs(x * math.cos(x)), abs(s))
            method = "relative condition |x cos(x)/sin(x)|"
        elif op == "cos":
            x = float(a[0]); c = math.cos(x)
            estimate = _ratio_or_inf(abs(x * math.sin(x)), abs(c))
            method = "relative condition |x sin(x)/cos(x)|"
        elif op == "tan":
            x = float(a[0]); denom = abs(math.sin(x) * math.cos(x))
            estimate = _ratio_or_inf(abs(x), denom)
            method = "relative condition |x/(sin(x)cos(x))|"
        elif op == "norm":
            estimate = 1.0
            method = "2-norm relative condition proxy"
        elif op in {"solve", "inverse", "det"}:
            try:
                import numpy as np
                estimate = float(np.linalg.cond(np.asarray(a[0], dtype=float), np.inf))
                method = "matrix infinity-norm condition number via NumPy"
            except Exception:
                estimate = None
                method = "matrix condition estimation unavailable"
        elif op in {"min", "max"}:
            estimate = None
            method = "order-statistic discontinuity; scalar condition not reported"
    except Exception:
        estimate = None
        method = "condition estimation failed"

    return {
        "estimate": _condition_json(estimate),
        "classification": _condition_class(estimate),
        "method": method,
    }


def _gamma(n: int) -> float:
    n = max(1, int(n))
    ne = n * _FLOAT_EPS
    return math.inf if ne >= 1.0 else ne / (1.0 - ne)


def _ulp_bound(value: Any) -> float:
    if not _is_scalar(value):
        return max((_ulp_bound(x) for x in _flatten(value)), default=0.0)
    try:
        x = float(value)
        return 2.0 * math.ulp(x)
    except Exception:
        return 0.0


def _binary_component_scale(left, right, fn) -> float:
    if isinstance(left, (list, tuple)):
        return max((_binary_component_scale(x, y, fn) for x, y in zip(left, right, strict=True)), default=0.0)
    return float(fn(float(left), float(right)))


def _max_component_condition(left, right, value) -> float:
    if isinstance(left, (list, tuple)):
        return max((_max_component_condition(x, y, z) for x, y, z in zip(left, right, value, strict=True)), default=1.0)
    num = abs(float(left)) + abs(float(right))
    return _ratio_or_inf(num, abs(float(value)))


def _matmul_condition_proxy(left, right, value) -> float:
    cols = list(zip(*right, strict=True))
    worst = 1.0
    for i, row in enumerate(left):
        for j, col in enumerate(cols):
            num = math.fsum(abs(float(x) * float(y)) for x, y in zip(row, col, strict=True))
            den = abs(float(value[i][j]))
            worst = max(worst, _ratio_or_inf(num, den))
    return worst


def _ratio_or_inf(num: float, den: float) -> float:
    if den == 0.0:
        return 1.0 if num == 0.0 else math.inf
    return num / den


def _condition_class(estimate: float | None) -> str:
    if estimate is None:
        return "not_reported"
    if not math.isfinite(estimate):
        return "singular_or_cancellation"
    if estimate < 1e3:
        return "well_conditioned"
    if estimate < 1e8:
        return "sensitive"
    return "ill_conditioned"


def _condition_json(value: float | None):
    if value is None:
        return None
    if math.isinf(value):
        return "infinity"
    if math.isnan(value):
        return None
    return value


def _scalar_interval(value: Any, bound: float):
    try:
        x = float(value)
        lo = math.nextafter(x - bound, -math.inf)
        hi = math.nextafter(x + bound, math.inf)
        return {"lower": lo, "upper": hi}
    except Exception:
        return None


def _exact_interval(value: Any):
    if _is_scalar(value):
        return {"lower": _exact_text(value), "upper": _exact_text(value)}
    return None


def _exact_text(value: Any) -> str:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    return str(value)


def _is_scalar(value: Any) -> bool:
    return not isinstance(value, (list, tuple))


def _flatten(value: Any):
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _flatten(item)
    else:
        yield value


def _max_abs(value: Any) -> float:
    vals = []
    for x in _flatten(value):
        try:
            vals.append(abs(float(x)))
        except Exception:
            pass
    return max(vals, default=0.0)


def _finite_json_number(value: float):
    if math.isinf(value):
        return "infinity"
    if math.isnan(value):
        return None
    return value


def _linear_algebra_diagnostics(request: ComputeRequest, value: Any) -> dict[str, Any]:
    from .linalg import residual_inf_norm, inverse_residual_inf_norm
    op = request.operation
    out: dict[str, Any] = {"kind": "a_posteriori_diagnostic"}
    try:
        import numpy as np
        A = np.asarray(request.operands[0], dtype=float)
        cond = float(np.linalg.cond(A, np.inf))
        out["condition_number_inf"] = _finite_json_number(cond)
        out["matrix_norm_inf"] = float(np.linalg.norm(A, np.inf))
    except Exception:
        cond = math.inf
        out["condition_number_inf"] = None
    try:
        if op == "solve":
            residual = residual_inf_norm(request.operands[0], value, request.operands[1])
            out["residual_inf"] = residual
            A_norm = _matrix_inf_norm_local(request.operands[0])
            x_norm = _rhs_inf_norm_local(value)
            b_norm = _rhs_inf_norm_local(request.operands[1])
            denom = A_norm * x_norm + b_norm
            backward = 0.0 if residual == 0.0 else (residual / denom if denom else math.inf)
            out["relative_backward_error"] = _finite_json_number(backward)
            product = cond * backward if math.isfinite(cond) and math.isfinite(backward) else math.inf
            if product < 1.0:
                out["forward_error_bound_proxy"] = _finite_json_number(product / max(1e-300, 1.0 - product))
            else:
                out["forward_error_bound_proxy"] = "infinity"
        elif op == "inverse":
            residual = inverse_residual_inf_norm(request.operands[0], value)
            out["identity_residual_inf"] = residual
            out["inverse_norm_inf"] = _matrix_inf_norm_local(value)
        elif op == "det":
            out["determinant_abs"] = abs(float(value))
    except Exception as exc:
        out["diagnostic_error"] = f"{type(exc).__name__}: {exc}"
    return out

def _append_linalg_warnings(assessment: dict[str, Any]) -> None:
    la = assessment.get("linear_algebra") or {}
    cond = la.get("condition_number_inf")
    warnings = assessment.setdefault("warning_flags", [])
    if cond == "infinity" or (isinstance(cond, (int, float)) and cond >= 1e8):
        if "ill_conditioned_or_cancellation_sensitive" not in warnings:
            warnings.append("ill_conditioned_or_cancellation_sensitive")
    backward = la.get("relative_backward_error")
    if isinstance(backward, (int, float)) and backward > 1e-8:
        warnings.append("large_linear_solve_backward_error")

def _matrix_inf_norm_local(matrix) -> float:
    return max((sum(abs(float(x)) for x in row) for row in matrix), default=0.0)

def _rhs_inf_norm_local(value) -> float:
    if value and isinstance(value[0], (list, tuple)):
        return max((sum(abs(float(x)) for x in row) for row in value), default=0.0)
    return max((abs(float(x)) for x in value), default=0.0)
