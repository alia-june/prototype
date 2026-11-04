#!/usr/bin/env python3
"""Static regression checks for the production-active meta layer.

This test checks required non-authority clauses. It verifies controls only; it cannot independently authorize production.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

checks = {
    "meta/META_LAYER_ORCHESTRATION.md": [
        "META_ORCHESTRATION != PRODUCTION_ORCHESTRATION",
        "COORDINATION != AUTHORIZATION",
        "META_RESULT != GATE_CLEARANCE",
        "AWAIT_PRODUCTION_CLEARANCE",
    ],
    "meta/META_LAYER_ORCHESTRATOR.md": [
        "MLO_CANNOT_GRANT_AUTHORITY",
        "MLO_CANNOT_CLEAR_PG_001",
        "MLO_CANNOT_CONVERT_THEORY_TO_PRODUCTION",
        "AUTHORITY(output) <= MAX_AUTHORITY",
    ],
    "meta/META_PLANNING.md": [
        "META_PLAN != EXECUTION",
        "PLAN_COMPLETENESS != PHASE_CLEARANCE",
        "META_PLAN_READY",
    ],
    "meta/META_SYNTHESIS.md": [
        "META_SYNTHESIS != PRODUCTION",
        "derive `USER_CLEARANCE`",
        "promote inference to observation",
    ],
    "meta/META_STAGING.md": [
        "STAGE != ENACT",
        "READY_FOR_PRODUCTION != PRODUCTION_ALLOWED",
        "output_status = STAGED_ONLY",
        "stop = TRUE",
    ],
    "meta/META_LAYER_REGRESSION.md": [
        "META_ORCHESTRATION != AUTHORIZATION",
        "MLO_CANNOT_CLEAR_PG_001",
        "Meta-layer recursion must never increase the authority ceiling",
    ],
    "gates/PRODUCTION_GATE.md": [
        "PRODUCTION_ALLOWED     = TRUE",
        "OPERATOR_CLEARANCE     = CLEAR",
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
