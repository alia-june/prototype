#!/usr/bin/env python3
"""Static regression checks for production-active operational-control documents.

This harness verifies required non-authority and gate-boundary clauses are present.
It verifies controls only; production authorization comes from the Operator gate record.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

checks = {
    "operations/OPERATIONAL_AXIOMS.md": [
        "THEORETICAL_STATEMENT != AUTHORIZATION",
        "Rights and privileges are non-derivable",
        "Production authorization is user-exclusive",
        "Regression evidence cannot self-promote",
    ],
    "operations/THEORETICAL_CONVERSATION_BOUNDARY.md": [
        "CONVERSATION_MODE = THEORETICAL_ONLY",
        "AUTHORITY_EFFECT  = NONE",
        "PRIVILEGE_EFFECT  = NONE",
        "PRODUCTION_EFFECT = NONE",
    ],
    "operations/OPERATIONAL_LOGIC_ORCHESTRATOR.md": [
        "ORCHESTRATOR_CANNOT_GRANT_ITSELF_AUTHORITY",
        "ORCHESTRATOR_CANNOT_CLEAR_PG_001",
        "ORCHESTRATOR_CANNOT_CONVERT_THEORY_INTO_PRIVILEGE",
    ],
    "operations/OPERATIONAL_REGRESSION.md": [
        "THEORY != AUTHORITY",
        "STAGING != PRODUCTION",
        "READINESS != CLEARANCE",
        "PROOF != PERMISSION",
        "ORCHESTRATION != SOVEREIGNTY",
    ],
    "gates/PRODUCTION_GATE.md": [
        "CURRENT_RELEASE_ACTIVE = TRUE",
        "GATE_STATE             = LOCKED_POST_RELEASE",
    ],
}

failed = []
passed = 0
for rel, needles in checks.items():
    p = ROOT / rel
    if not p.is_file():
        failed.append(f"missing:{rel}")
        continue
    text = p.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            failed.append(f"{rel}:missing:{needle}")
        else:
            passed += 1

print(f"checks={passed + len(failed)} pass={passed} fail={len(failed)}")
for item in failed:
    print("FAIL", item)

sys.exit(1 if failed else 0)
