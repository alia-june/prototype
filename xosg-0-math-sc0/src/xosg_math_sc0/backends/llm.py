from __future__ import annotations

from .base import ProviderBackend
from ..types import ComputeRequest, ComputeResult, ResultStatus


class LLMFallbackBackend(ProviderBackend):
    """Non-authoritative final fallback. Provider signature: provider(request) -> value | ComputeResult."""

    name = "llm_fallback"
    authoritative = False

    def supports(self, request: ComputeRequest) -> bool:
        return self.available() and request.allow_llm

    def cost_hint(self, request: ComputeRequest) -> float:
        return 100.0

    def compute(self, request: ComputeRequest) -> ComputeResult:
        raw = self.provider(request)
        if isinstance(raw, ComputeResult):
            raw.backend = self.name
            raw.status = ResultStatus.LLM_INFERRED
            raw.verified = False
            return raw
        return ComputeResult(
            value=raw,
            status=ResultStatus.LLM_INFERRED,
            backend=self.name,
            algorithm="external.llm_provider",
            verified=False,
            exact=False,
        )
