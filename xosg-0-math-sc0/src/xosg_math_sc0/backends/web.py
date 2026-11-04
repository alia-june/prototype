from __future__ import annotations

from .base import ProviderBackend
from ..types import ComputeRequest, ComputeResult, ResultStatus


class WebBackend(ProviderBackend):
    """
    Retrieval/reference fallback. Provider signature:
        provider(request) -> value | ComputeResult

    The engine never treats a web-sourced value as intrinsic deterministic computation.
    """

    name = "web"
    authoritative = False

    def supports(self, request: ComputeRequest) -> bool:
        return self.available() and request.allow_web

    def cost_hint(self, request: ComputeRequest) -> float:
        return 50.0

    def compute(self, request: ComputeRequest) -> ComputeResult:
        raw = self.provider(request)
        if isinstance(raw, ComputeResult):
            raw.backend = self.name
            if raw.status == ResultStatus.COMPUTED:
                raw.status = ResultStatus.WEB_SOURCED
            return raw
        return ComputeResult(
            value=raw,
            status=ResultStatus.WEB_SOURCED,
            backend=self.name,
            algorithm="external.web_provider",
            verified=False,
            exact=False,
        )
