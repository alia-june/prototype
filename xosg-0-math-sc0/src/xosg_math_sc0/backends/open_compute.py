from __future__ import annotations

from .base import ProviderBackend
from ..types import ComputeRequest, ComputeResult, ResultStatus


class OpenComputeBackend(ProviderBackend):
    """
    Adapter boundary for an external heterogeneous/open-compute runtime.

    Provider may be either:
      * a callable: provider(request) -> value | ComputeResult
      * an object with supports(request) and compute(request)

    Intended integrations include OpenCL/SYCL/ROCm/HIP or another portable
    execution layer. The core remains independent of a specific vendor stack.
    """

    name = "open_compute"
    authoritative = True

    def supports(self, request: ComputeRequest) -> bool:
        if not self.available():
            return False
        fn = getattr(self.provider, "supports", None)
        return bool(fn(request)) if callable(fn) else True

    def cost_hint(self, request: ComputeRequest) -> float:
        return 0.2

    def compute(self, request: ComputeRequest) -> ComputeResult:
        compute_fn = getattr(self.provider, "compute", None)
        raw = compute_fn(request) if callable(compute_fn) else self.provider(request)
        if isinstance(raw, ComputeResult):
            raw.backend = self.name
            return raw
        return ComputeResult(
            value=raw,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm="external.open_compute_provider",
            verified=False,
            exact=False,
            tolerance=request.tolerance,
        )
