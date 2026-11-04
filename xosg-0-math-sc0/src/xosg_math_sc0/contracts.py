from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

from .types import ComputeRequest


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class ContractValidation:
    request: ComputeRequest
    contract_state: str
    contract_version: str
    protocol_version: str
    operation_id: str | None
    input_shapes: tuple[tuple[int, ...], ...]
    scalar_count: int


class OperationContractRegistry:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else _default_contract_path()
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.contract_version = self.data["contract_version"]
        self.protocol_version = self.data["protocol_version"]
        self.operations = self.data["operations"]
        self.limits = self.data["resource_limits"]
        self.by_id = {spec["operation_id"]: name for name, spec in self.operations.items()}

    def resolve(self, operation: str) -> tuple[str, dict[str, Any]] | None:
        if operation in self.operations:
            return operation, self.operations[operation]
        name = self.by_id.get(operation)
        if name is None:
            return None
        return name, self.operations[name]

    def validate(self, request: ComputeRequest, *, allow_uncontracted: bool = False) -> ContractValidation:
        if request.protocol_version != self.protocol_version:
            raise ContractError(f"unsupported protocol version: {request.protocol_version}")
        if request.contract_version != self.contract_version:
            raise ContractError(f"unsupported contract version: {request.contract_version}")
        _validate_generic_limits(request, self.limits)
        resolved = self.resolve(request.operation)
        if resolved is None:
            if not allow_uncontracted:
                raise ContractError(f"uncontracted operation: {request.operation}")
            shapes = tuple(_shape_of(x, self.limits["max_rank"]) for x in request.operands)
            return ContractValidation(
                request=request,
                contract_state="uncontracted",
                contract_version=self.contract_version,
                protocol_version=self.protocol_version,
                operation_id=None,
                input_shapes=shapes,
                scalar_count=_scalar_count(request.operands),
            )

        canonical, spec = resolved
        normalized = replace(request, operation=canonical)
        _validate_known(normalized, spec, self.limits)
        shapes = tuple(_shape_of(x, self.limits["max_rank"]) for x in normalized.operands)
        return ContractValidation(
            request=normalized,
            contract_state="contracted",
            contract_version=self.contract_version,
            protocol_version=self.protocol_version,
            operation_id=spec["operation_id"],
            input_shapes=shapes,
            scalar_count=_scalar_count(normalized.operands),
        )


def _default_contract_path() -> Path:
    return Path(__file__).resolve().parents[2] / "protocol" / "operation_contracts.v0.6.json"


def _validate_generic_limits(request: ComputeRequest, limits: dict[str, Any]) -> None:
    if request.precision is not None and request.precision > limits["max_precision_digits"]:
        raise ContractError(f"precision exceeds limit {limits['max_precision_digits']}")
    if request.tolerance < 0 or request.tolerance > limits["max_tolerance"]:
        raise ContractError(f"tolerance must be between 0 and {limits['max_tolerance']}")
    count = _scalar_count(request.operands)
    if count > limits["max_scalar_count"]:
        raise ContractError(f"scalar count {count} exceeds limit {limits['max_scalar_count']}")
    for operand in request.operands:
        _shape_of(operand, limits["max_rank"])
        _validate_string_lengths(operand, limits.get("max_numeric_string_chars", 10000))
        _validate_scalar_values(operand, request)


def _validate_known(request: ComputeRequest, spec: dict[str, Any], limits: dict[str, Any]) -> None:
    if len(request.operands) not in spec["arity"]:
        raise ContractError(f"{request.operation} expects arity {spec['arity']}, got {len(request.operands)}")
    if request.mode.value not in spec["modes"]:
        raise ContractError(f"mode {request.mode.value} is not permitted for {request.operation}")

    shapes = tuple(_shape_of(x, limits["max_rank"]) for x in request.operands)
    signature = spec["signature"]
    if signature == "same_shape_binary":
        if shapes[0] != shapes[1]:
            raise ContractError(f"{request.operation} operands must have identical shapes")
        if len(shapes[0]) not in spec["ranks"]:
            raise ContractError(f"{request.operation} rank {len(shapes[0])} is not permitted")
    elif signature == "scalar_binary":
        if shapes != ((), ()):
            raise ContractError(f"{request.operation} requires two scalar operands")
    elif signature == "scalar_unary":
        if shapes != ((),):
            raise ContractError(f"{request.operation} requires one scalar operand")
    elif signature == "log_scalar":
        if any(shape != () for shape in shapes):
            raise ContractError("log requires scalar operands")
    elif signature == "vector_reduction":
        if len(shapes[0]) != 1:
            raise ContractError(f"{request.operation} requires a rank-1 vector")
        if shapes[0][0] < spec.get("min_length", 0):
            raise ContractError(f"{request.operation} vector is too short")
    elif signature == "vector_binary_same_length":
        if len(shapes[0]) != 1 or shapes[0] != shapes[1]:
            raise ContractError(f"{request.operation} requires equal-length rank-1 vectors")
        if shapes[0][0] < spec.get("min_length", 0):
            raise ContractError(f"{request.operation} vectors are too short")
    elif signature == "matrix_multiply":
        if len(shapes[0]) != 2 or len(shapes[1]) != 2:
            raise ContractError("matmul requires two rank-2 matrices")
        if shapes[0][1] != shapes[1][0]:
            raise ContractError(f"matmul inner dimensions differ: {shapes[0]} @ {shapes[1]}")
        if min(*shapes[0], *shapes[1]) < 1:
            raise ContractError("matmul matrices must be non-empty")
        estimated_ops = shapes[0][0] * shapes[0][1] * shapes[1][1]
        result_count = shapes[0][0] * shapes[1][1]
        if estimated_ops > limits["max_estimated_operations"]:
            raise ContractError(f"estimated operation count {estimated_ops} exceeds contract limit {limits['max_estimated_operations']}")
        if result_count > limits["max_result_scalar_count"]:
            raise ContractError(f"result scalar count {result_count} exceeds contract limit {limits['max_result_scalar_count']}")
    elif signature == "square_matrix_unary":
        if len(shapes[0]) != 2 or shapes[0][0] != shapes[0][1] or shapes[0][0] < 1:
            raise ContractError(f"{request.operation} requires a non-empty square matrix")
        n = shapes[0][0]
        if n * n * n > limits["max_estimated_operations"]:
            raise ContractError("estimated cubic matrix work exceeds contract limit")
        result_count = 1 if request.operation == "det" else n * n
        if result_count > limits["max_result_scalar_count"]:
            raise ContractError("result scalar count exceeds contract limit")
    elif signature == "linear_solve":
        if len(shapes[0]) != 2 or shapes[0][0] != shapes[0][1] or shapes[0][0] < 1:
            raise ContractError("solve requires a non-empty square coefficient matrix")
        n = shapes[0][0]
        if len(shapes[1]) == 1:
            if shapes[1][0] != n:
                raise ContractError("solve right-hand vector length must match matrix dimension")
            result_count = n
        elif len(shapes[1]) == 2:
            if shapes[1][0] != n or shapes[1][1] < 1:
                raise ContractError("solve right-hand matrix row count must match coefficient matrix")
            result_count = n * shapes[1][1]
        else:
            raise ContractError("solve right-hand operand must be a vector or matrix")
        if n * n * max(n, (shapes[1][1] if len(shapes[1]) == 2 else 1)) > limits["max_estimated_operations"]:
            raise ContractError("estimated linear solve work exceeds contract limit")
        if result_count > limits["max_result_scalar_count"]:
            raise ContractError("result scalar count exceeds contract limit")
    else:
        raise ContractError(f"unknown contract signature: {signature}")

    for shape in shapes:
        if len(shape) == 1 and shape[0] > limits["max_vector_length"]:
            raise ContractError("vector length exceeds contract limit")
        if len(shape) == 2:
            if shape[0] > limits["max_matrix_rows"] or shape[1] > limits["max_matrix_cols"]:
                raise ContractError("matrix dimensions exceed contract limit")

    _validate_constraints(request, spec.get("constraints", []))
    if request.operation == "pow" and request.mode.value == "exact":
        exponent = request.operands[1]
        try:
            q = Fraction(exponent)
        except Exception as exc:
            raise ContractError("exact pow exponent must be an integer") from exc
        if q.denominator != 1:
            raise ContractError("exact pow exponent must be an integer")
        if abs(q.numerator) > limits.get("max_exact_power_exponent", 100000):
            raise ContractError("exact pow exponent exceeds resource limit")
    if request.operation == "pow" and request.mode.value == "interval":
        lo, hi = _interval_bounds(request.operands[1])
        if lo != hi or lo.denominator != 1:
            raise ContractError("interval pow exponent must be a degenerate integer interval")
        if abs(lo.numerator) > limits.get("max_exact_power_exponent", 100000):
            raise ContractError("interval pow exponent exceeds resource limit")


def _validate_constraints(request: ComputeRequest, constraints: list[str]) -> None:
    a = request.operands
    for constraint in constraints:
        if constraint == "nonzero_operand_1":
            if request.mode.value == "interval":
                lo, hi = _interval_bounds(a[1])
                if lo <= 0 <= hi:
                    raise ContractError("interval denominator may not contain zero")
            elif _as_real(a[1]) == 0:
                raise ContractError("division by zero is prohibited")
        if constraint == "operand_0_nonnegative":
            if request.mode.value == "interval":
                lo, _ = _interval_bounds(a[0])
                if lo < 0:
                    raise ContractError("sqrt interval input must be nonnegative")
            elif _as_real(a[0]) < 0:
                raise ContractError("sqrt real-domain input must be nonnegative")
        if constraint == "operand_0_positive":
            if request.mode.value == "interval":
                lo, _ = _interval_bounds(a[0])
                if lo <= 0:
                    raise ContractError("log interval input must be strictly positive")
            elif _as_real(a[0]) <= 0:
                raise ContractError("log real-domain input must be positive")
        if constraint == "log_base_valid_if_present" and len(a) == 2:
            if request.mode.value == "interval":
                lo, hi = _interval_bounds(a[1])
                if lo <= 0 or lo <= 1 <= hi:
                    raise ContractError("log interval base must be positive and must not contain 1")
            else:
                base = _as_real(a[1])
                if base <= 0 or base == 1:
                    raise ContractError("log base must be positive and not equal to 1")


def _interval_bounds(value: Any) -> tuple[Fraction, Fraction]:
    if isinstance(value, dict) and value.get("$type") == "interval":
        return _interval_endpoint(value["lo"]), _interval_endpoint(value["hi"])
    q = _interval_endpoint(value)
    return q, q


def _validate_scalar_values(value: Any, request: ComputeRequest) -> None:
    if isinstance(value, dict):
        if request.mode.value != "interval" or value.get("$type") != "interval":
            raise ContractError("object operands are reserved for interval mode")
        if "lo" not in value or "hi" not in value:
            raise ContractError("interval operand requires lo and hi endpoints")
        lo = _interval_endpoint(value["lo"])
        hi = _interval_endpoint(value["hi"])
        if lo > hi:
            raise ContractError("interval lower endpoint exceeds upper endpoint")
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_scalar_values(item, request)
        return
    if isinstance(value, bool):
        raise ContractError("boolean values are not numeric operands")
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError("non-finite numeric input is prohibited")
    if isinstance(value, (int, float, Fraction)):
        return
    if isinstance(value, str):
        if request.mode.value not in {"auto", "exact", "high_precision", "interval"}:
            raise ContractError("numeric strings require auto, exact, high_precision, or interval mode")
        try:
            parsed = float(value)
        except ValueError:
            if request.mode.value in {"auto", "exact", "interval"}:
                try:
                    parsed = float(Fraction(value))
                except (ValueError, ZeroDivisionError) as exc:
                    raise ContractError(f"invalid numeric string: {value!r}") from exc
            else:
                raise ContractError(f"invalid numeric string: {value!r}")
        if not math.isfinite(parsed):
            raise ContractError("non-finite numeric string is prohibited")
        return
    raise ContractError(f"unsupported operand scalar type: {type(value).__name__}")


def _validate_string_lengths(value: Any, limit: int) -> None:
    if isinstance(value, str):
        if len(value) > limit:
            raise ContractError(f"numeric string length exceeds contract limit {limit}")
        return
    if isinstance(value, dict):
        for item in value.values():
            _validate_string_lengths(item, limit)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_string_lengths(item, limit)


def _interval_endpoint(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ContractError("boolean interval endpoint is prohibited")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError("non-finite interval endpoint is prohibited")
        return Fraction.from_float(value)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except Exception as exc:
            raise ContractError(f"invalid interval endpoint: {value!r}") from exc
    if isinstance(value, dict) and value.get("$type") == "fraction":
        try:
            return Fraction(int(value["numerator"]), int(value["denominator"]))
        except Exception as exc:
            raise ContractError("invalid fraction interval endpoint") from exc
    raise ContractError(f"unsupported interval endpoint type: {type(value).__name__}")

def _shape_of(value: Any, max_rank: int) -> tuple[int, ...]:
    if isinstance(value, dict):
        return ()
    if not isinstance(value, (list, tuple)):
        return ()
    if max_rank < 1:
        raise ContractError("operand rank exceeds contract limit")
    if len(value) == 0:
        return (0,)
    child_shapes = [_shape_of(item, max_rank - 1) for item in value]
    first = child_shapes[0]
    if any(shape != first for shape in child_shapes[1:]):
        raise ContractError("ragged arrays are prohibited")
    return (len(value),) + first


def _scalar_count(values: Any) -> int:
    count = 0
    stack = [values]
    while stack:
        item = stack.pop()
        if isinstance(item, (list, tuple)):
            stack.extend(item)
        else:
            count += 1
    return count


def _as_real(value: Any) -> float:
    try:
        x = float(value)
    except Exception:
        try:
            x = float(Fraction(value))
        except Exception as exc:
            raise ContractError(f"operand is not real-valued: {value!r}") from exc
    if not math.isfinite(x):
        raise ContractError("non-finite numeric input is prohibited")
    return x
