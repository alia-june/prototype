from __future__ import annotations

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus


class TorchAcceleratorBackend(Backend):
    """Optional tensor accelerator. Uses CUDA/MPS/XPU only when actually available."""

    name = "accelerator"
    _ops = {"sum", "mean", "norm", "dot", "matmul"}

    def __init__(self, threshold: int = 4096):
        self.threshold = threshold
        try:
            import torch
            self.torch = torch
        except Exception:
            self.torch = None

    def _device(self):
        if self.torch is None:
            return None
        t = self.torch
        if getattr(t, "cuda", None) is not None and t.cuda.is_available():
            return "cuda"
        if getattr(t.backends, "mps", None) is not None and t.backends.mps.is_available():
            return "mps"
        if hasattr(t, "xpu") and t.xpu.is_available():
            return "xpu"
        return None

    def available(self) -> bool:
        return self._device() is not None

    def supports(self, request: ComputeRequest) -> bool:
        return (
            self.available()
            and request.mode != NumericMode.EXACT
            and request.operation in self._ops
            and _work_size(request.operands) >= self.threshold
        )

    def cost_hint(self, request: ComputeRequest) -> float:
        return 0.1

    def compute(self, request: ComputeRequest) -> ComputeResult:
        t, device = self.torch, self._device()
        op, a = request.operation, request.operands
        if op in {"sum", "mean", "norm"}:
            x = t.tensor(a[0], dtype=t.float64, device=device)
            value = {"sum": t.sum, "mean": t.mean, "norm": t.linalg.vector_norm}[op](x)
        elif op == "dot":
            x = t.tensor(a[0], dtype=t.float64, device=device)
            y = t.tensor(a[1], dtype=t.float64, device=device)
            value = t.dot(x.flatten(), y.flatten())
        elif op == "matmul":
            x = t.tensor(a[0], dtype=t.float64, device=device)
            y = t.tensor(a[1], dtype=t.float64, device=device)
            value = t.matmul(x, y)
        else:
            raise ValueError(op)
        value = value.detach().cpu().numpy()
        value = value.tolist() if getattr(value, "ndim", 0) else value.item()
        return ComputeResult(
            value=value,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm=f"torch.{op}",
            exact=False,
            tolerance=request.tolerance,
            metadata={"device": device},
        )


def _work_size(values):
    total = 0
    stack = list(values)
    while stack:
        item = stack.pop()
        if isinstance(item, (list, tuple)):
            stack.extend(item)
        else:
            total += 1
    return total
