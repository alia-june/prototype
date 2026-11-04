from __future__ import annotations

import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .types import ComputeRequest, NumericMode

BENCHMARK_VERSION = "0.1.0"


def calibrate_backends(backends, *, repeats: int = 5, sizes=(64, 1024, 16384)) -> dict[str, Any]:
    """Measure local float64 reduction latency without changing policy priority.

    The profile is host-specific evidence only. It MUST NOT reorder exactness or
    the external web/LLM authority boundary.
    """
    profile: dict[str, Any] = {
        "benchmark_version": BENCHMARK_VERSION,
        "host_specific": True,
        "policy_effect": "informational_only",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "workloads": [],
    }
    candidates = [b for b in backends if b.name in {"native", "numpy", "cpu", "accelerator", "open_compute"}]
    for size in sizes:
        values = [float((i % 97) - 48) for i in range(int(size))]
        request = ComputeRequest(
            operation="sum",
            operands=(values,),
            mode=NumericMode.FLOAT64,
            allow_web=False,
            allow_llm=False,
            protocol_version="0.6",
            contract_version="0.6.0",
        )
        row = {"operation": "sum", "size": int(size), "backends": {}}
        for backend in candidates:
            try:
                if not backend.available() or not backend.supports(request):
                    row["backends"][backend.name] = {"eligible": False}
                    continue
                timings = []
                result_value = None
                for _ in range(max(1, repeats)):
                    t0 = time.perf_counter_ns()
                    result = backend.compute(request)
                    timings.append(time.perf_counter_ns() - t0)
                    result_value = result.value
                row["backends"][backend.name] = {
                    "eligible": True,
                    "median_ns": int(statistics.median(timings)),
                    "min_ns": int(min(timings)),
                    "repeats": len(timings),
                    "sample_value": float(result_value),
                }
            except Exception as exc:
                row["backends"][backend.name] = {"eligible": False, "error": f"{type(exc).__name__}: {exc}"}
        profile["workloads"].append(row)
    return profile


def save_profile(profile: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_profile(path: str | Path) -> dict[str, Any] | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
