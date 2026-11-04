#!/usr/bin/env python3
"""JSON boundary for the deterministic Python MATH.SC-0 data plane.

The worker intentionally disables web and LLM fallbacks. Those are owned by the
outer control plane so the final fallback order can be enforced independently of
numerical execution.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xosg_math_sc0 import ComputationEngine, ComputeRequest, NumericMode  # noqa: E402
from xosg_math_sc0.benchmark import calibrate_backends  # noqa: E402


def _json_value(value: Any):
    if isinstance(value, Fraction):
        return {
            "$type": "fraction",
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(x) for x in value]
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    # mpmath and other high-precision scalar types are preserved textually.
    return {"$type": type(value).__name__, "value": str(value)}


def _load_open_compute_provider():
    """Load an operator-trusted local provider from `module:attribute`.

    Example: XOSG_SC0_OPEN_COMPUTE_PROVIDER=my_runtime:provider
    The provider runs inside the deterministic local data plane and is never
    treated as web or LLM fallback.
    """
    spec = os.getenv("XOSG_SC0_OPEN_COMPUTE_PROVIDER", "").strip()
    if not spec:
        return None
    module_name, sep, attribute = spec.partition(":")
    if not sep or not module_name or not attribute:
        raise ValueError("XOSG_SC0_OPEN_COMPUTE_PROVIDER must be module:attribute")
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


def _request_from_json(raw: dict[str, Any]) -> ComputeRequest:
    mode = NumericMode(raw.get("mode", NumericMode.AUTO.value))
    return ComputeRequest(
        operation=raw["operation"],
        operands=tuple(raw.get("operands", [])),
        mode=mode,
        precision=raw.get("precision"),
        tolerance=float(raw.get("tolerance", 1e-12)),
        deterministic=bool(raw.get("deterministic", True)),
        allow_web=False,
        allow_llm=False,
        metadata=raw.get("metadata", {}),
        protocol_version=raw.get("protocol_version", "0.6"),
        contract_version=raw.get("contract_version", "0.6.0"),
    )


def _result_to_json(result):
    payload = asdict(result)
    payload["value"] = _json_value(result.value)
    payload["status"] = result.status.value
    payload["authority"] = "deterministic_local" if result.backend != "none" else "none"
    payload["control_plane"] = "python-data-plane"
    return payload


def main() -> int:
    try:
        raw_text = sys.stdin.read()
        if not raw_text.strip():
            raise ValueError("expected one JSON request on stdin")
        raw = json.loads(raw_text)
        engine = ComputationEngine(open_compute_provider=_load_open_compute_provider())
        if raw.get("$control") == "capabilities":
            print(json.dumps(engine.backend_state(), separators=(",", ":")))
            return 0
        if raw.get("$control") == "benchmark":
            repeats = int(raw.get("repeats", 3))
            sizes = tuple(int(x) for x in raw.get("sizes", [64, 1024, 16384]))
            print(json.dumps(calibrate_backends(engine.backends, repeats=repeats, sizes=sizes), separators=(",", ":")))
            return 0
        request = _request_from_json(raw)
        result = engine.compute(request)
        print(json.dumps(_result_to_json(result), separators=(",", ":")))
        return 0
    except Exception as exc:
        print(json.dumps({
            "value": None,
            "status": "failed",
            "backend": "python_worker",
            "verified": False,
            "exact": False,
            "error": f"{type(exc).__name__}: {exc}",
            "error_code": "WORKER_BOUNDARY_FAILURE",
            "trace": ["python worker boundary failure"],
            "metadata": {},
            "authority": "none",
            "control_plane": "python-data-plane"
        }, separators=(",", ":")))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
