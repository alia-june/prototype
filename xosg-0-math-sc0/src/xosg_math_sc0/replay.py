from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, is_dataclass
from enum import Enum
from fractions import Fraction
from typing import Any

from .types import ComputeRequest, ComputeResult

REPLAY_VERSION = "0.1.0"


def request_fingerprint(request: ComputeRequest) -> str:
    payload = {
        "replay_version": REPLAY_VERSION,
        "protocol_version": request.protocol_version,
        "contract_version": request.contract_version,
        "operation": request.operation,
        "operands": _canonical(request.operands),
        "mode": request.mode.value,
        "precision": request.precision,
        "tolerance": _canonical_number(request.tolerance),
        "deterministic": request.deterministic,
        "allow_web": request.allow_web,
        "allow_llm": request.allow_llm,
        "metadata": _canonical(dict(request.metadata)),
    }
    return _sha(payload)


def result_fingerprint(request: ComputeRequest, result: ComputeResult) -> str:
    payload = {
        "replay_version": REPLAY_VERSION,
        "request_fingerprint": request_fingerprint(request),
        "status": result.status.value,
        "backend": result.backend,
        "algorithm": result.algorithm,
        "verified": result.verified,
        "exact": result.exact,
        "value": _canonical(result.value),
        "error_code": result.error_code,
    }
    return _sha(payload)


def _sha(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"$type": "fraction", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, (list, tuple)):
        return [_canonical(x) for x in value]
    if isinstance(value, float):
        return _canonical_number(value)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return {"$type": type(value).__name__, "value": str(value)}


def _canonical_number(value: float) -> Any:
    if not math.isfinite(value):
        raise ValueError("non-finite values cannot be replay-fingerprinted")
    if value == 0:
        return 0
    if value.is_integer() and abs(value) <= 9007199254740991:
        return int(value)
    return format(value, ".17g")
