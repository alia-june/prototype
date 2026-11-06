"""Shared contract helpers for the non-executing ES-xOSG-0 example."""
from __future__ import annotations

import json
from typing import Any

ENVELOPE_SCHEMA = "es-xosg-0/receipt-envelope/v1"
DECISION_SCHEMA = "es-xosg-0/decision/v1"
MAX_INPUT_BYTES = 65_536
TOOL_KINDS = frozenset({"mill.creation", "mill.verification", "mill.gate"})
DECISIONS = frozenset({
    "AWAIT_HUMAN_REVIEW",
    "STOP_AND_RETAIN",
    "NEEDS_AUTHORITY",
    "UNMAPPED_OR_INSUFFICIENT_RECEIPT",
})


class ContractError(ValueError):
    """The supplied envelope cannot be safely interpreted by this example."""


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ContractError(f"input cannot be represented as canonical JSON: {error}") from error


def parse_envelope(value: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ContractError("envelope must be a JSON object")
    if len(canonical_bytes(value)) > MAX_INPUT_BYTES:
        raise ContractError(f"envelope exceeds {MAX_INPUT_BYTES} byte limit")
    if value.get("envelope_schema") != ENVELOPE_SCHEMA:
        raise ContractError(f"envelope_schema must equal {ENVELOPE_SCHEMA}")
    tool_kind = value.get("tool_kind")
    if tool_kind not in TOOL_KINDS:
        raise ContractError("tool_kind is not mapped by this example")
    receipt = value.get("receipt")
    if not isinstance(receipt, dict):
        raise ContractError("receipt must be a JSON object")
    return tool_kind, receipt


def decision(tool_kind: str, outcome: str, reason: str, facts: dict[str, str]) -> dict[str, Any]:
    if outcome not in DECISIONS:
        raise ContractError(f"unsupported decision outcome: {outcome}")
    return {
        "decision_schema": DECISION_SCHEMA,
        "tool_kind": tool_kind,
        "outcome": outcome,
        "reason": reason,
        "facts": facts,
        "execution": "not_performed",
        "authority": "human_decision_required",
        "limitations": [
            "This example classifies supplied receipt facts only.",
            "It does not invoke a controller, subprocess, network service, or LLM.",
            "It does not create, modify, promote, retry, recover, schedule, or accept work.",
        ],
    }
