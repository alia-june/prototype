"""Closed deterministic meta-cases. Values are data and never select code."""
from __future__ import annotations

import random

from . import CASE_SCHEMA


MUTATIONS = (
    "wrong_schema", "wrong_run_id", "wrong_overall_status", "missing_modes",
    "duplicate_mode", "missing_worker_stopped", "wrong_worker_type", "missing_cleanup",
    "cleanup_status_pending", "cleanup_mismatch", "job_claim_without_zero", "wrong_counts",
    "duplicate_case", "missing_input", "tampered_input", "escaped_input",
    "missing_events", "contradictory_event", "passed_without_coverage", "product_changed",
)


HARDENING = (
    "clean_control", "strict_duplicate_json", "truncated_json", "oversized_json",
    "wrong_schema", "wrong_run_id", "wrong_overall_status", "missing_modes",
    "duplicate_mode", "missing_worker_stopped", "wrong_worker_type", "missing_cleanup",
    "cleanup_status_pending", "cleanup_mismatch", "job_claim_without_zero", "wrong_counts",
    "duplicate_case", "missing_input", "tampered_input", "escaped_input",
    "missing_events", "contradictory_event", "passed_without_coverage", "product_changed",
    "failure_precedence", "incomplete_precedence", "source_identity_guard",
    "non_overwrite", "configuration_bounds", "input_retained_before_actor",
)


TORTURE = (
    "deadline_summary_cycles", "aggregate_order_cycles", "full_discovery_cycles",
    "parallel_packet_audits", "long_unfinished_journal", "sticky_failure_recovery",
    "isolated_evidence_roots", "exclusive_log_observation",
)


def meta_case(case_id: str, mode: str, family: str, mutation: str, expected: str):
    return {"schema": CASE_SCHEMA, "case_id": case_id, "mode": mode,
            "family": family, "mutation": mutation, "expected": expected}


def fuzzy_cases(seed: int = 20261031, count: int = 1000):
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("seed must be a 32-bit nonnegative integer")
    if type(count) is not int or not 5 <= count <= 1000 or count % 5:
        raise ValueError("count must be a multiple of five in 5..1000")
    rng = random.Random(seed)
    invalid_index = 0
    for index in range(count):
        if index % 5 == 4:
            yield meta_case(f"fuzzy-{index:04d}", "fuzzy", "control", "clean_control", "PASS")
            continue
        mutation = MUTATIONS[invalid_index % len(MUTATIONS)]
        invalid_index += 1
        # Salt is retained to prove seed/order reproducibility; it has no dispatch role.
        case = meta_case(f"fuzzy-{index:04d}", "fuzzy", "invalid", mutation, "REJECT")
        case["salt"] = rng.getrandbits(64)
        yield case
