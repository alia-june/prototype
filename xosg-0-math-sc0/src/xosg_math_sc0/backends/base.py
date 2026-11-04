from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..types import ComputeRequest, ComputeResult


class Backend(ABC):
    name = "base"
    authoritative = True

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supports(self, request: ComputeRequest) -> bool:
        raise NotImplementedError

    @abstractmethod
    def compute(self, request: ComputeRequest) -> ComputeResult:
        raise NotImplementedError

    def cost_hint(self, request: ComputeRequest) -> float:
        return 1.0


class ProviderBackend(Backend):
    """Backend whose implementation is supplied by an external callable/provider."""

    def __init__(self, provider: Any | None = None):
        self.provider = provider

    def available(self) -> bool:
        return self.provider is not None
