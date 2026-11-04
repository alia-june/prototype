from __future__ import annotations

from .backends.accelerator import TorchAcceleratorBackend
from .backends.cpu import CPUBackend
from .backends.exact import ExactBackend
from .backends.high_precision import HighPrecisionBackend
from .backends.interval_backend import IntervalBackend
from .backends.llm import LLMFallbackBackend
from .backends.native import NativeBackend
from .backends.numpy_backend import NumPyBackend
from .backends.open_compute import OpenComputeBackend
from .backends.web import WebBackend
from .contracts import ContractError, OperationContractRegistry
from .dispatcher import Dispatcher
from .types import ComputeRequest, ComputeResult, ResultStatus
from .verifier import Verifier
from .numerical import assess_numerics
from .capabilities import manifest as capability_manifest
from .replay import request_fingerprint, result_fingerprint
from .benchmark import load_profile
from pathlib import Path
import math
from fractions import Fraction
from numbers import Number


class ComputationEngine:
    def __init__(self, *, open_compute_provider=None, web_provider=None, llm_provider=None, vector_threshold=256, accelerator_threshold=4096, native_threshold=64, native_library=None, contract_registry=None):
        self.contracts = contract_registry or OperationContractRegistry()
        self.backends = [
            ExactBackend(),
            HighPrecisionBackend(),
            IntervalBackend(),
            TorchAcceleratorBackend(threshold=accelerator_threshold),
            OpenComputeBackend(open_compute_provider),
            NativeBackend(threshold=native_threshold, library_path=native_library),
            NumPyBackend(vector_threshold=vector_threshold),
            CPUBackend(),
            WebBackend(web_provider),
            LLMFallbackBackend(llm_provider),
        ]
        self.dispatcher = Dispatcher(self.backends)
        self.verifier = Verifier()

    def compute(self, request: ComputeRequest) -> ComputeResult:
        allow_uncontracted = bool(request.allow_web or request.allow_llm)
        try:
            validation = self.contracts.validate(request, allow_uncontracted=allow_uncontracted)
        except ContractError as exc:
            return ComputeResult(
                status=ResultStatus.FAILED,
                backend="contract",
                error=f"ContractError: {exc}",
                error_code="CONTRACT_VALIDATION_FAILED",
                trace=["contract validation failed"],
                metadata={
                    "contract_version": self.contracts.contract_version,
                    "protocol_version": self.contracts.protocol_version,
                    "contract_state": "rejected",
                },
            )

        normalized = validation.request
        req_fp = request_fingerprint(normalized)
        result = self.dispatcher.dispatch(normalized, contracted=(validation.contract_state == "contracted"))
        result = self.verifier.verify(normalized, result)
        result = assess_numerics(normalized, result)
        if result.status not in {ResultStatus.FAILED, ResultStatus.WEB_SOURCED, ResultStatus.LLM_INFERRED} and not _finite_output(result.value):
            result.status = ResultStatus.FAILED
            result.verified = False
            result.error = "contract rejected non-finite local output"
            result.error_code = "NONFINITE_OUTPUT_REJECTED"
            result.trace.append("contract output validation failed: non-finite value")
        result.metadata.update({
            "contract_version": validation.contract_version,
            "protocol_version": validation.protocol_version,
            "contract_state": validation.contract_state,
            "operation_id": validation.operation_id,
            "input_shapes": [list(x) for x in validation.input_shapes],
            "scalar_count": validation.scalar_count,
            "replay_version": "0.1.0",
            "request_fingerprint": req_fp,
        })
        result.metadata["result_fingerprint"] = result_fingerprint(normalized, result)
        return result

    def backend_state(self):
        profile = load_profile(Path(__file__).resolve().parents[2] / "config" / "backend_calibration.json")
        return capability_manifest(self.backends, calibration=profile)

    def negotiate(self, request: ComputeRequest):
        validation = self.contracts.validate(request, allow_uncontracted=bool(request.allow_web or request.allow_llm))
        return {
            "contract_state": validation.contract_state,
            "operation_id": validation.operation_id,
            "candidates": self.dispatcher.negotiate(validation.request),
        }


def _finite_output(value):
    if isinstance(value, Fraction):
        return True
    if isinstance(value, Number):
        try:
            return math.isfinite(float(value))
        except Exception:
            return False
    if isinstance(value, (list, tuple)):
        return all(_finite_output(x) for x in value)
    try:
        return math.isfinite(float(value))
    except Exception:
        return value is not None
