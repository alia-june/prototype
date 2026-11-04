from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class NumericMode(str, Enum):
    AUTO = "auto"
    EXACT = "exact"
    FLOAT64 = "float64"
    HIGH_PRECISION = "high_precision"
    INTERVAL = "interval"


class ResultStatus(str, Enum):
    COMPUTED = "computed"
    VERIFIED = "verified"
    EXTERNALLY_VERIFIED = "externally_verified"
    WEB_SOURCED = "web_sourced"
    LLM_INFERRED = "llm_inferred"
    UNVERIFIED = "unverified"
    FAILED = "failed"


@dataclass(frozen=True)
class ComputeRequest:
    operation: str
    operands: tuple[Any, ...]
    mode: NumericMode = NumericMode.AUTO
    precision: int | None = None
    tolerance: float = 1e-12
    deterministic: bool = True
    allow_web: bool = True
    allow_llm: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)
    protocol_version: str = "0.6"
    contract_version: str = "0.6.0"


@dataclass
class ComputeResult:
    value: Any = None
    status: ResultStatus = ResultStatus.FAILED
    backend: str = "none"
    algorithm: str = ""
    verified: bool = False
    exact: bool = False
    tolerance: float | None = None
    error: str | None = None
    error_code: str | None = None
    trace: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
