from __future__ import annotations

from .types import ComputeRequest, ComputeResult, NumericMode, ResultStatus
from .capabilities import backend_capability


class Dispatcher:
    """
    Policy order:
      exact -> high precision -> interval -> accelerator -> open compute -> native C/C++ -> vectorized -> CPU -> web -> LLM.

    Web and LLM are fallback classes, not trusted computational peers.
    LLM is always last.
    """

    def __init__(self, backends):
        self.backends = list(backends)

    def negotiate(self, request: ComputeRequest):
        """Return ordered backend capability claims for this request.

        Priority remains policy-defined; capability negotiation decides eligibility,
        not authority. This prevents a faster backend from outranking exactness or
        the external-fallback boundary merely because it advertises a lower cost.
        """
        return [backend_capability(b, request=request, priority=i) for i, b in enumerate(self.backends)]

    def dispatch(self, request: ComputeRequest, *, contracted: bool = False) -> ComputeResult:
        trace = []
        negotiation = self.negotiate(request)
        by_name = {x["name"]: x for x in negotiation}
        external_names = {"web", "llm_fallback"}
        local_attempted = False
        local_failures = []
        for backend in self.backends:
            claim = by_name[backend.name]
            is_external = backend.name in external_names
            if contracted and is_external and local_attempted and local_failures:
                trace.append(f"stop before {backend.name}: contracted deterministic operation failed locally")
                break
            if not claim["available"]:
                trace.append(f"skip {backend.name}: unavailable")
                continue
            if not claim.get("supports_request", False):
                trace.append(f"skip {backend.name}: unsupported")
                continue
            try:
                if not is_external:
                    local_attempted = True
                trace.append(f"dispatch {backend.name}")
                result = backend.compute(request)
                result.trace = trace + result.trace
                result.metadata.setdefault("dispatch_negotiation", negotiation)
                return result
            except Exception as exc:
                trace.append(f"fail {backend.name}: {type(exc).__name__}: {exc}")
                if not is_external:
                    local_failures.append(f"{backend.name}:{type(exc).__name__}")
        error_code = "CONTRACTED_LOCAL_EXECUTION_FAILED" if contracted and local_attempted and local_failures else "NO_BACKEND_COMPLETED"
        return ComputeResult(
            status=ResultStatus.FAILED,
            backend="none",
            error="no backend completed the request",
            error_code=error_code,
            trace=trace,
            metadata={"dispatch_negotiation": negotiation},
        )
