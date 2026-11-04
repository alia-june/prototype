from __future__ import annotations

from typing import Any

from .types import ComputeRequest

CAPABILITY_PROTOCOL_VERSION = "0.3.0"


def backend_capability(backend, request: ComputeRequest | None = None, priority: int | None = None) -> dict[str, Any]:
    try:
        available = bool(backend.available())
    except Exception:
        available = False
    descriptor: dict[str, Any] = {
        "name": backend.name,
        "available": available,
        "authoritative": bool(getattr(backend, "authoritative", True)),
        "priority": priority,
        "class": type(backend).__name__,
    }
    ops = _operations(backend)
    if ops is not None:
        descriptor["operations"] = sorted(ops)
    if request is not None:
        try:
            supports = available and bool(backend.supports(request))
        except Exception:
            supports = False
        descriptor["supports_request"] = supports
        if supports:
            try:
                descriptor["cost_hint"] = float(backend.cost_hint(request))
            except Exception:
                descriptor["cost_hint"] = None
    if backend.name == "accelerator" and available:
        try:
            descriptor["device"] = backend._device()
        except Exception:
            pass
    if backend.name == "native":
        descriptor["library"] = getattr(backend, "library_path", None)
        if available:
            try:
                descriptor["native_version"] = backend.lib.sc0_native_version().decode("utf-8")
            except Exception:
                pass
    if backend.name in {"web", "llm_fallback", "open_compute"}:
        descriptor["provider_attached"] = getattr(backend, "provider", None) is not None
    return descriptor


def manifest(backends, calibration=None) -> dict[str, Any]:
    payload = {
        "capability_protocol_version": CAPABILITY_PROTOCOL_VERSION,
        "backends": [backend_capability(b, priority=i) for i, b in enumerate(backends)],
    }
    if calibration is not None:
        payload["calibration"] = calibration
    return payload


def _operations(backend):
    if hasattr(backend, "_ops"):
        try:
            return set(backend._ops)
        except Exception:
            return None
    if backend.name == "native":
        return {"add", "sub", "mul", "div", "pow", "sqrt", "exp", "log", "sin", "cos", "tan", "sum", "mean", "norm", "dot", "matmul", "det", "solve", "inverse"}
    if backend.name in {"open_compute", "web", "llm_fallback"}:
        return None
    return None
