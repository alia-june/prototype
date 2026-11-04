from fractions import Fraction

from xosg_math_sc0 import ComputationEngine, ComputeRequest, NumericMode, ResultStatus


def test_exact_fraction_preferred():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("div", ("1", "3"), mode=NumericMode.EXACT))
    assert r.value == Fraction(1, 3)
    assert r.backend == "exact"
    assert r.status == ResultStatus.VERIFIED
    assert r.exact


def test_cpu_scalar():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sqrt", (81.0,)))
    assert r.value == 9.0
    assert r.backend == "cpu"
    assert r.verified


def test_numpy_dispatch_for_large_vector():
    e = ComputationEngine(vector_threshold=8)
    values = list(range(20))
    r = e.compute(ComputeRequest("sum", (values,), mode=NumericMode.FLOAT64))
    assert r.value == 190.0
    assert r.backend in {"numpy", "accelerator"}
    assert r.verified


def test_web_before_llm():
    calls = []
    def web(req):
        calls.append("web")
        return 42
    def llm(req):
        calls.append("llm")
        return 99
    e = ComputationEngine(web_provider=web, llm_provider=llm)
    r = e.compute(ComputeRequest("unknown_operation", (1, 2)))
    assert r.value == 42
    assert r.backend == "web"
    assert calls == ["web"]
    assert r.status == ResultStatus.WEB_SOURCED


def test_llm_is_last_resort():
    calls = []
    def llm(req):
        calls.append("llm")
        return "heuristic"
    e = ComputationEngine(llm_provider=llm)
    r = e.compute(ComputeRequest("unknown_operation", (1, 2), allow_web=False))
    assert r.value == "heuristic"
    assert r.backend == "llm_fallback"
    assert calls == ["llm"]
    assert r.status == ResultStatus.LLM_INFERRED
    assert not r.verified


def test_disable_llm_yields_failure():
    e = ComputationEngine(llm_provider=lambda req: 7)
    r = e.compute(ComputeRequest("unknown_operation", (), allow_web=False, allow_llm=False))
    assert r.status == ResultStatus.FAILED


def test_open_compute_precedes_web_and_llm():
    calls = []
    def open_compute(req):
        calls.append("open_compute")
        return 123.0
    def web(req):
        calls.append("web")
        return 456.0
    def llm(req):
        calls.append("llm")
        return 789.0
    e = ComputationEngine(open_compute_provider=open_compute, web_provider=web, llm_provider=llm)
    r = e.compute(ComputeRequest("provider_only_operation", ()))
    assert r.value == 123.0
    assert r.backend == "open_compute"
    assert calls == ["open_compute"]


def test_high_precision_cross_verifies_against_cpu():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sqrt", ("2",), mode=NumericMode.HIGH_PRECISION, precision=80))
    assert r.backend == "high_precision"
    assert r.status == ResultStatus.VERIFIED
    assert r.verified


def test_native_dispatch_for_vector_workload():
    e = ComputationEngine(native_threshold=4, vector_threshold=10_000)
    values = list(range(1, 101))
    r = e.compute(ComputeRequest("sum", (values,), mode=NumericMode.FLOAT64))
    assert r.backend == "native"
    assert r.value == 5050.0
    assert r.status == ResultStatus.VERIFIED
    assert r.verified
    assert "native-0.8.0" in r.metadata["native_version"]


def test_native_matmul_cross_verifies():
    e = ComputationEngine(native_threshold=1, vector_threshold=10_000)
    left = [[1, 2, 3], [4, 5, 6]]
    right = [[7, 8], [9, 10], [11, 12]]
    r = e.compute(ComputeRequest("matmul", (left, right), mode=NumericMode.FLOAT64))
    assert r.backend == "native"
    assert r.value == [[58.0, 64.0], [139.0, 154.0]]
    assert r.status == ResultStatus.VERIFIED


def test_small_float_scalar_avoids_native_overhead():
    e = ComputationEngine(native_threshold=64)
    r = e.compute(ComputeRequest("sqrt", (81.0,), mode=NumericMode.FLOAT64))
    assert r.backend == "cpu"
    assert r.value == 9.0


def test_operation_id_resolves_to_canonical_operation():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("math.sc0.add.v1", (2, 3), mode=NumericMode.EXACT))
    assert r.value == 5
    assert r.status == ResultStatus.VERIFIED
    assert r.metadata["operation_id"] == "math.sc0.add.v1"
    assert r.metadata["contract_version"] == "0.6.0"


def test_contract_rejects_shape_mismatch_before_dispatch():
    e = ComputationEngine(web_provider=lambda req: 999, llm_provider=lambda req: 888)
    r = e.compute(ComputeRequest("add", ([1, 2], [3]), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "identical shapes" in r.error
    assert r.metadata["contract_state"] == "rejected"


def test_contract_rejects_real_domain_error_before_dispatch():
    e = ComputationEngine(web_provider=lambda req: 999)
    r = e.compute(ComputeRequest("sqrt", (-1.0,), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "nonnegative" in r.error


def test_contract_rejects_excess_precision():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sqrt", (2,), mode=NumericMode.HIGH_PRECISION, precision=4097))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "precision exceeds" in r.error


def test_contract_rejects_ragged_matrix():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("matmul", ([[1, 2], [3]], [[1], [2]]), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "ragged" in r.error


def test_exact_elementwise_vector_obeys_contract():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("add", (["1/3", "1/2"], ["2/3", "1/2"]), mode=NumericMode.EXACT))
    assert r.backend == "exact"
    assert r.value == [Fraction(1, 1), Fraction(1, 1)]
    assert r.status == ResultStatus.VERIFIED


def test_high_precision_log_base_contract_and_compute():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("log", ("8", "2"), mode=NumericMode.HIGH_PRECISION, precision=80))
    assert r.backend == "high_precision"
    assert abs(float(r.value) - 3.0) < 1e-15
    assert r.status == ResultStatus.VERIFIED


def test_unknown_operation_can_still_reach_web_as_uncontracted():
    e = ComputationEngine(web_provider=lambda req: 42)
    r = e.compute(ComputeRequest("future_operation", (1, 2)))
    assert r.backend == "web"
    assert r.status == ResultStatus.WEB_SOURCED
    assert r.metadata["contract_state"] == "uncontracted"


def test_contract_failure_has_stable_error_code():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("div", (1.0, 0.0), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.FAILED
    assert r.error_code == "CONTRACT_VALIDATION_FAILED"


def test_exact_pow_requires_integer_exponent():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("pow", ("4", "1/2"), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "integer" in r.error


def test_exact_result_has_rigorous_zero_width_error_evidence():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("div", ("1", "7"), mode=NumericMode.EXACT))
    a = r.metadata["numerical_assessment"]
    assert a["error_bound"]["kind"] == "exact_zero"
    assert a["error_bound"]["rigor"] == "rigorous"
    assert a["error_bound"]["max_absolute_error"] == 0.0
    assert a["error_bound"]["interval"] == {"lower": "1/7", "upper": "1/7"}


def test_float_cancellation_is_flagged_by_conditioning_diagnostic():
    e = ComputationEngine(native_threshold=10_000, vector_threshold=10_000)
    r = e.compute(ComputeRequest("add", (1.0e16, -1.0e16), mode=NumericMode.FLOAT64))
    a = r.metadata["numerical_assessment"]
    assert a["conditioning"]["estimate"] == "infinity"
    assert a["conditioning"]["classification"] == "singular_or_cancellation"
    assert "ill_conditioned_or_cancellation_sensitive" in a["warning_flags"]


def test_sum_has_quantified_forward_error_model():
    e = ComputationEngine(native_threshold=10_000, vector_threshold=10_000)
    r = e.compute(ComputeRequest("sum", ([0.1, 0.2, 0.3],), mode=NumericMode.FLOAT64))
    a = r.metadata["numerical_assessment"]
    assert a["error_bound"]["kind"] == "forward_error_model"
    assert a["error_bound"]["max_absolute_error"] > 0
    assert a["error_bound"]["rigor"] == "model_based"


def test_transcendental_uses_diagnostic_ulp_envelope_not_rigorous_claim():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sin", (0.5,), mode=NumericMode.FLOAT64))
    a = r.metadata["numerical_assessment"]
    assert a["error_bound"]["kind"] == "ulp_envelope"
    assert a["error_bound"]["rigor"] == "diagnostic"
    assert "transcendental_library_accuracy_is_runtime_dependent" in a["warning_flags"]


def test_dispatch_negotiation_records_backend_capability_claims():
    e = ComputationEngine(native_threshold=4, vector_threshold=10_000)
    r = e.compute(ComputeRequest("sum", (list(range(20)),), mode=NumericMode.FLOAT64))
    claims = r.metadata["dispatch_negotiation"]
    native = next(x for x in claims if x["name"] == "native")
    assert native["available"] is True
    assert native["supports_request"] is True
    assert native["priority"] < next(x for x in claims if x["name"] == "numpy")["priority"]


def test_backend_state_is_versioned_capability_manifest():
    e = ComputationEngine()
    state = e.backend_state()
    assert state["capability_protocol_version"] == "0.3.0"
    assert any(x["name"] == "cpu" and x["available"] for x in state["backends"])



def test_interval_add_uses_exact_rational_enclosure():
    e = ComputationEngine()
    req = ComputeRequest(
        "add",
        ({"$type": "interval", "lo": "1/10", "hi": "1/5"}, {"$type": "interval", "lo": "1/3", "hi": "1/2"}),
        mode=NumericMode.INTERVAL,
        protocol_version="0.6",
        contract_version="0.6.0",
    )
    r = e.compute(req)
    assert r.status == ResultStatus.VERIFIED
    assert r.backend == "interval"
    assert r.value["lo"] == Fraction(13, 30)
    assert r.value["hi"] == Fraction(7, 10)
    assert r.metadata["numerical_assessment"]["error_bound"]["rigor"] == "rigorous"


def test_interval_multiplication_crossing_zero_encloses_extrema():
    e = ComputationEngine()
    req = ComputeRequest(
        "mul",
        ({"$type": "interval", "lo": -2, "hi": 3}, {"$type": "interval", "lo": 4, "hi": 5}),
        mode=NumericMode.INTERVAL,
        protocol_version="0.6",
        contract_version="0.6.0",
    )
    r = e.compute(req)
    assert r.value["lo"] == -10
    assert r.value["hi"] == 15
    assert r.verified is True


def test_interval_division_rejects_denominator_containing_zero_before_dispatch():
    e = ComputationEngine()
    req = ComputeRequest(
        "div",
        (1, {"$type": "interval", "lo": -1, "hi": 1}),
        mode=NumericMode.INTERVAL,
        protocol_version="0.6",
        contract_version="0.6.0",
    )
    r = e.compute(req)
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "contain zero" in r.error


def test_interval_dot_produces_rigorous_enclosure():
    e = ComputationEngine()
    req = ComputeRequest(
        "dot",
        ([{"$type":"interval","lo":1,"hi":2}, 3], [4, {"$type":"interval","lo":5,"hi":6}]),
        mode=NumericMode.INTERVAL,
        protocol_version="0.6",
        contract_version="0.6.0",
    )
    r = e.compute(req)
    assert r.value["lo"] == 19
    assert r.value["hi"] == 26
    assert r.status == ResultStatus.VERIFIED


def test_replay_fingerprint_is_deterministic_and_result_fingerprint_present():
    e = ComputationEngine()
    req = ComputeRequest("add", (7, 8), mode=NumericMode.EXACT, protocol_version="0.6", contract_version="0.6.0")
    a = e.compute(req)
    b = e.compute(req)
    assert a.metadata["request_fingerprint"] == b.metadata["request_fingerprint"]
    assert a.metadata["result_fingerprint"] == b.metadata["result_fingerprint"]
    assert len(a.metadata["request_fingerprint"]) == 64


def test_replay_fingerprint_changes_when_operand_changes():
    e = ComputationEngine()
    a = e.compute(ComputeRequest("add", (7, 8), mode=NumericMode.EXACT, protocol_version="0.6", contract_version="0.6.0"))
    b = e.compute(ComputeRequest("add", (7, 9), mode=NumericMode.EXACT, protocol_version="0.6", contract_version="0.6.0"))
    assert a.metadata["request_fingerprint"] != b.metadata["request_fingerprint"]


def _iv(lo, hi=None):
    return {"$type": "interval", "lo": lo, "hi": lo if hi is None else hi}


def test_interval_sqrt_directed_enclosure_contains_high_precision_value():
    import mpmath as mp
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sqrt", (_iv("2"),), mode=NumericMode.INTERVAL, precision=80))
    assert r.status == ResultStatus.VERIFIED
    assert r.backend == "interval"
    mp.mp.dps = 100
    x = mp.sqrt(2)
    assert mp.mpf(r.value["lo"].numerator) / r.value["lo"].denominator <= x
    assert mp.mpf(r.value["hi"].numerator) / r.value["hi"].denominator >= x
    assert r.metadata["enclosure_rigor"] == "directed_rounding_backend_enclosure"


def test_interval_sin_encloses_extrema_across_half_pi():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("sin", (_iv("1", "2"),), mode=NumericMode.INTERVAL, precision=80))
    assert r.status == ResultStatus.VERIFIED
    import math
    assert float(r.value["lo"]) <= min(math.sin(1.0), math.sin(2.0))
    assert r.value["hi"] >= Fraction(1)


def test_interval_log_base_enclosure_contains_exact_case():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("log", (_iv("8"), _iv("2")), mode=NumericMode.INTERVAL, precision=80))
    assert r.status == ResultStatus.VERIFIED
    assert r.value["lo"] <= 3 <= r.value["hi"]


def test_interval_log_base_rejects_base_spanning_one():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("log", (_iv("8"), _iv("1/2", "2")), mode=NumericMode.INTERVAL))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "contain 1" in r.error


def test_exact_determinant():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("det", ([["1/2", "1/3"], ["2/5", "3/7"]],), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.VERIFIED
    assert r.backend == "exact"
    assert r.value == Fraction(17, 210)


def test_exact_linear_solve():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("solve", ([[2, 1], [1, 3]], [1, 2]), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.VERIFIED
    assert r.value == [Fraction(1, 5), Fraction(3, 5)]


def test_exact_inverse():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("inverse", ([[2, 1], [1, 3]],), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.VERIFIED
    assert r.value == [[Fraction(3,5), Fraction(-1,5)], [Fraction(-1,5), Fraction(2,5)]]


def test_float_solve_cross_backend_and_residual():
    e = ComputationEngine(vector_threshold=1, native_threshold=10_000)
    r = e.compute(ComputeRequest("solve", ([[3.0, 1.0], [1.0, 2.0]], [9.0, 8.0]), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.VERIFIED
    assert abs(r.value[0] - 2.0) < 1e-12
    assert abs(r.value[1] - 3.0) < 1e-12


def test_singular_exact_solve_fails_without_external_fallback_when_disabled():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("solve", ([[1, 2], [2, 4]], [1, 2]), mode=NumericMode.EXACT, allow_web=False, allow_llm=False))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "none"


def test_contracted_singular_solve_does_not_escalate_to_web_or_llm():
    calls = []
    e = ComputationEngine(web_provider=lambda req: calls.append("web") or 123, llm_provider=lambda req: calls.append("llm") or 456)
    r = e.compute(ComputeRequest("solve", ([[1, 2], [2, 4]], [1, 2]), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.FAILED
    assert r.error_code == "CONTRACTED_LOCAL_EXECUTION_FAILED"
    assert calls == []


def test_float_solve_has_residual_verification_metadata():
    e = ComputationEngine(native_threshold=1, vector_threshold=10_000)
    r = e.compute(ComputeRequest("solve", ([[3.0, 1.0], [1.0, 2.0]], [9.0, 8.0]), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.VERIFIED
    assert r.metadata["verification_residual_inf"] <= r.metadata["verification_threshold"]
    la = r.metadata["numerical_assessment"]["linear_algebra"]
    assert la["residual_inf"] < 1e-12
    assert la["condition_number_inf"] > 1


def test_float_inverse_has_identity_residual_verification_metadata():
    e = ComputationEngine(native_threshold=1, vector_threshold=10_000)
    r = e.compute(ComputeRequest("inverse", ([[4.0, 1.0], [2.0, 3.0]],), mode=NumericMode.FLOAT64))
    assert r.status == ResultStatus.VERIFIED
    assert r.metadata["verification_residual_inf"] <= r.metadata["verification_threshold"]
    assert r.metadata["numerical_assessment"]["linear_algebra"]["identity_residual_inf"] < 1e-12


def test_exact_power_resource_ceiling_is_enforced():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("pow", (2, 100001), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "resource limit" in r.error


def test_numeric_string_length_resource_ceiling_is_enforced():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("add", ("1" * 10001, "1"), mode=NumericMode.EXACT))
    assert r.status == ResultStatus.FAILED
    assert r.backend == "contract"
    assert "string length" in r.error


def test_interval_exp_materialization_guard_prevents_pathological_fraction():
    e = ComputationEngine()
    r = e.compute(ComputeRequest("exp", (_iv("1000000"),), mode=NumericMode.INTERVAL, precision=50))
    assert r.status == ResultStatus.FAILED
    assert r.error_code == "CONTRACTED_LOCAL_EXECUTION_FAILED"
