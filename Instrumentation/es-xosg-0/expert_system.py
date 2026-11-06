#!/usr/bin/env python3
"""Non-executing expert-system working example for fitted Instrumentation receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from contracts import ContractError, decision, parse_envelope


def text(value: Any) -> str:
    return value if isinstance(value, str) else "<missing-or-invalid>"


def common_non_permitted(tool_kind: str, receipt: dict[str, Any], facts: dict[str, str]) -> dict[str, Any] | None:
    admission = facts["admission"]
    retained = facts["retained_state"]
    next_action = facts["next_permitted_action"]
    if admission == "permitted":
        return None
    if retained in {"unknown", "partial_observed", "partial_or_unknown", "emergency_receipt_retained", "lease_preserved"} or next_action == "await_recovery_authority":
        return decision(tool_kind, "STOP_AND_RETAIN", "receipt reports a partial, uncertain, or recovery-bound state", facts)
    if admission == "not_permitted":
        return decision(tool_kind, "NEEDS_AUTHORITY", "controller admission was not permitted; correct the request or authority before any new action", facts)
    return decision(tool_kind, "UNMAPPED_OR_INSUFFICIENT_RECEIPT", "admission value is not mapped by this example", facts)


def adapt_creation(receipt: dict[str, Any]) -> dict[str, Any]:
    facts = {
        "admission": text(receipt.get("admission")),
        "creation_reported": text(receipt.get("creation_reported")),
        "artifact_verification": text(receipt.get("artifact_verification")),
        "retained_state": text(receipt.get("retained_state")),
        "next_permitted_action": text(receipt.get("next_permitted_action")),
        "authority": text(receipt.get("authority")),
    }
    early = common_non_permitted("mill.creation", receipt, facts)
    if early:
        return early
    if facts["creation_reported"] == "true" and facts["artifact_verification"] == "pass" and facts["retained_state"] == "none_observed":
        return decision("mill.creation", "AWAIT_HUMAN_REVIEW", "creation was reported and the existing structural verifier passed; human review remains required", facts)
    if facts["artifact_verification"] == "fail" or facts["retained_state"] in {"partial_observed", "unknown"} or facts["next_permitted_action"] == "await_recovery_authority":
        return decision("mill.creation", "STOP_AND_RETAIN", "creation receipt is failed, partial, unknown, or recovery-bound", facts)
    return decision("mill.creation", "UNMAPPED_OR_INSUFFICIENT_RECEIPT", "creation receipt lacks the complete known-valid or known-stop fact pattern", facts)


def adapt_verification(receipt: dict[str, Any]) -> dict[str, Any]:
    validator = receipt.get("validator") if isinstance(receipt.get("validator"), dict) else {}
    process = receipt.get("process") if isinstance(receipt.get("process"), dict) else {}
    facts = {
        "admission": text(receipt.get("admission")),
        "validator_result": text(validator.get("reported_result")),
        "process_exit_code": str(process.get("exit_code", "<missing-or-invalid>")),
        "process_timed_out": str(process.get("timed_out", "<missing-or-invalid>")).lower(),
        "retained_state": text(receipt.get("retained_state")),
        "next_permitted_action": text(receipt.get("next_permitted_action")),
        "authority": text(receipt.get("authority")),
    }
    early = common_non_permitted("mill.verification", receipt, facts)
    if early:
        return early
    if facts["validator_result"] == "PASS" and facts["process_exit_code"] == "0" and facts["process_timed_out"] == "false" and facts["retained_state"] == "receipt_retained":
        return decision("mill.verification", "AWAIT_HUMAN_REVIEW", "existing Mill verification reported PASS; this remains structural evidence for human review", facts)
    if facts["validator_result"] == "FAIL" or facts["next_permitted_action"] in {"review_validator_failures", "await_recovery_authority"}:
        return decision("mill.verification", "STOP_AND_RETAIN", "verification receipt reports failure or an unresolved recovery/review condition", facts)
    return decision("mill.verification", "UNMAPPED_OR_INSUFFICIENT_RECEIPT", "verification receipt lacks a complete known-valid or known-stop fact pattern", facts)


def adapt_gate(receipt: dict[str, Any]) -> dict[str, Any]:
    facts = {
        "admission": text(receipt.get("admission")),
        "gate_write_reported": text(receipt.get("gate_write_reported")),
        "structural_validation": text(receipt.get("structural_validation")),
        "retained_state": text(receipt.get("retained_state")),
        "next_permitted_action": text(receipt.get("next_permitted_action")),
        "authority": text(receipt.get("authority")),
    }
    early = common_non_permitted("mill.gate", receipt, facts)
    if early:
        return early
    if facts["gate_write_reported"] == "true" and facts["structural_validation"] == "PASS" and facts["retained_state"] == "receipt_retained":
        return decision("mill.gate", "AWAIT_HUMAN_REVIEW", "gate write and existing structural validation were observed; human review remains required", facts)
    if facts["gate_write_reported"] == "unknown" or facts["structural_validation"] in {"FAIL", "unknown"} or facts["retained_state"] == "partial_or_unknown" or facts["next_permitted_action"] == "await_recovery_authority":
        return decision("mill.gate", "STOP_AND_RETAIN", "gate receipt is failed, partial, unknown, or recovery-bound", facts)
    return decision("mill.gate", "UNMAPPED_OR_INSUFFICIENT_RECEIPT", "gate receipt lacks a complete known-valid or known-stop fact pattern", facts)


ADAPTERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "mill.creation": adapt_creation,
    "mill.verification": adapt_verification,
    "mill.gate": adapt_gate,
}


def evaluate(envelope: Any) -> dict[str, Any]:
    try:
        tool_kind, receipt = parse_envelope(envelope)
    except ContractError as error:
        return decision("unmapped", "UNMAPPED_OR_INSUFFICIENT_RECEIPT", str(error), {})
    return ADAPTERS[tool_kind](receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path, help="one receipt-envelope JSON file")
    arguments = parser.parse_args()
    try:
        envelope = json.loads(arguments.envelope.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result = decision("unmapped", "UNMAPPED_OR_INSUFFICIENT_RECEIPT", f"envelope could not be read as JSON: {error}", {})
    else:
        result = evaluate(envelope)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
