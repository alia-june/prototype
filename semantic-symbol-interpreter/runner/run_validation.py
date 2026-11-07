#!/usr/bin/env python3
"""SSMI whole-bearer validation harness.

Zero-dependency CLI with two input modes:
  1. Fixture definition -> structural fixture validation.
  2. Candidate result    -> grade candidate against referenced fixture.

The mode is auto-detected from the JSON document shape.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REQUIRED = {
    "fixture_id", "bearer", "expected", "forbidden_inferences",
    "required_unknowns", "properties",
}
CANDIDATE_REQUIRED = {
    "fixture_id", "claims", "unknowns", "provenance", "invariants",
}
INVARIANT_REQUIRED = {
    "raw_observation_preserved",
    "whole_bearer_preserved",
    "alternatives_preserved",
    "no_unobserved_as_observed",
    "scope_respected",
    "provenance_complete",
}
EXPECTED_LIST_FIELDS = {
    "observations", "structures", "symbols", "signs", "messages",
    "implications", "provenance",
}


def emit(obj, *, stream=sys.stdout):
    print(json.dumps(obj, indent=2), file=stream)


def fail(message, *, details=None, code=2):
    payload = {"pass": False, "error": message}
    if details:
        payload["details"] = details
    emit(payload, stream=sys.stderr)
    raise SystemExit(code)


def load_json(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail("input file not found", details={"path": str(path)})
    except OSError as exc:
        fail("unable to read input file", details={"path": str(path), "reason": str(exc)})
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(
            "input is not valid JSON",
            details={"path": str(path), "line": exc.lineno, "column": exc.colno, "reason": exc.msg},
        )
    if not isinstance(obj, dict):
        fail("top-level JSON value must be an object", details={"path": str(path)})
    return obj


def detect_document_type(obj):
    keys = set(obj)
    if FIXTURE_REQUIRED.issubset(keys):
        return "fixture"
    if CANDIDATE_REQUIRED.issubset(keys):
        return "candidate_result"
    # Helpful partial detection for clearer diagnostics.
    if "expected" in keys or "bearer" in keys or "forbidden_inferences" in keys:
        return "fixture"
    if "claims" in keys or "invariants" in keys or "unknowns" in keys:
        return "candidate_result"
    return "unknown"


def validate_fixture_structure(f):
    errors = []
    missing = sorted(FIXTURE_REQUIRED - set(f))
    if missing:
        errors.append(f"missing required fixture fields: {', '.join(missing)}")

    if "fixture_id" in f and not isinstance(f["fixture_id"], str):
        errors.append("fixture_id must be a string")
    if "bearer" in f and not isinstance(f["bearer"], dict):
        errors.append("bearer must be an object")
    elif isinstance(f.get("bearer"), dict):
        if "kind" not in f["bearer"]:
            errors.append("bearer.kind is required")
        if "source" not in f["bearer"]:
            errors.append("bearer.source is required")

    expected = f.get("expected")
    if expected is not None and not isinstance(expected, dict):
        errors.append("expected must be an object")
    elif isinstance(expected, dict):
        unexpected_fields = sorted(set(expected) - EXPECTED_LIST_FIELDS)
        if unexpected_fields:
            errors.append("unexpected expected.* fields: " + ", ".join(unexpected_fields))
        for key, value in expected.items():
            if key in EXPECTED_LIST_FIELDS and not isinstance(value, list):
                errors.append(f"expected.{key} must be an array")
            elif key in EXPECTED_LIST_FIELDS and any(not isinstance(x, str) for x in value):
                errors.append(f"expected.{key} entries must be strings")

    for key in ("forbidden_inferences", "required_unknowns", "properties"):
        if key in f:
            if not isinstance(f[key], list):
                errors.append(f"{key} must be an array")
            elif any(not isinstance(x, str) for x in f[key]):
                errors.append(f"{key} entries must be strings")

    if "notes" in f:
        if not isinstance(f["notes"], list):
            errors.append("notes must be an array")
        elif any(not isinstance(x, str) for x in f["notes"]):
            errors.append("notes entries must be strings")
    return errors


def validate_candidate_structure(c):
    errors = []
    missing = sorted(CANDIDATE_REQUIRED - set(c))
    if missing:
        errors.append(f"missing required candidate fields: {', '.join(missing)}")
    if "fixture_id" in c and not isinstance(c["fixture_id"], str):
        errors.append("fixture_id must be a string")
    for key in ("claims", "unknowns", "provenance"):
        if key in c:
            if not isinstance(c[key], list):
                errors.append(f"{key} must be an array")
            elif any(not isinstance(x, str) for x in c[key]):
                errors.append(f"{key} entries must be strings")
    inv = c.get("invariants")
    if inv is not None and not isinstance(inv, dict):
        errors.append("invariants must be an object")
    elif isinstance(inv, dict):
        missing_inv = sorted(INVARIANT_REQUIRED - set(inv))
        if missing_inv:
            errors.append("missing invariant fields: " + ", ".join(missing_inv))
        for key, value in inv.items():
            if key in INVARIANT_REQUIRED and not isinstance(value, bool):
                errors.append(f"invariants.{key} must be boolean")
    if 'interpretation' in c:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from engine.trace import inspect_result
        try:
            errors.extend(inspect_result(c))
        except (KeyError, TypeError, ValueError, RecursionError) as exc:
            errors.append('malformed interpretation graph: ' + str(exc))
    return errors


def fixture_path(fid):
    return ROOT / "fixtures" / f"{fid.lower()}.json"


def load_fixture(fid):
    p = fixture_path(fid)
    if not p.exists():
        fail("unknown fixture_id", details={"fixture_id": fid, "expected_path": str(p)})
    f = load_json(p)
    errors = validate_fixture_structure(f)
    if errors:
        fail("referenced fixture is structurally invalid", details={"fixture_id": fid, "errors": errors})
    return f


def validate_fixture_document(f, source_path):
    errors = validate_fixture_structure(f)
    expected = f.get("expected", {}) if isinstance(f.get("expected"), dict) else {}
    summary = {
        "expected_observations": len(expected.get("observations", [])),
        "expected_structures": len(expected.get("structures", [])),
        "expected_symbols": len(expected.get("symbols", [])),
        "expected_signs": len(expected.get("signs", [])),
        "expected_messages": len(expected.get("messages", [])),
        "expected_implications": len(expected.get("implications", [])),
        "expected_provenance_items": len(expected.get("provenance", [])),
        "forbidden_inferences": len(f.get("forbidden_inferences", [])) if isinstance(f.get("forbidden_inferences"), list) else 0,
        "required_unknowns": len(f.get("required_unknowns", [])) if isinstance(f.get("required_unknowns"), list) else 0,
        "properties": len(f.get("properties", [])) if isinstance(f.get("properties"), list) else 0,
    }
    report = {
        "document_type": "fixture",
        "fixture_id": f.get("fixture_id"),
        "source": str(source_path),
        "pass": not errors,
        "errors": errors,
        "summary": summary,
        "note": "Fixture definitions are test specifications. They are structurally validated here; they are not graded as candidate outputs.",
    }
    emit(report)
    raise SystemExit(0 if not errors else 2)


def grade_candidate(c, source_path):
    errors = validate_candidate_structure(c)
    if errors:
        fail("candidate result is structurally invalid", details={"source": str(source_path), "errors": errors})

    f = load_fixture(c["fixture_id"])
    if 'interpretation' in c:
        from engine.trace import inspect_result
        source_errors = inspect_result(c, f['bearer'])
        if source_errors:
            fail('candidate result source does not match fixture', details={'errors': source_errors})
    expected = []
    for value in f["expected"].values():
        if isinstance(value, list):
            expected.extend(value)

    available = set(c["claims"]) | set(c["provenance"])
    missing = [x for x in expected if x not in available]
    forbidden = [x for x in f["forbidden_inferences"] if x in c["claims"]]
    missing_unknowns = [x for x in f["required_unknowns"] if x not in c["unknowns"]]
    invariant_failures = [k for k in sorted(INVARIANT_REQUIRED) if not c["invariants"].get(k, False)]

    passed = not (missing or forbidden or missing_unknowns or invariant_failures)
    n = max(len(expected), 1)
    report = {
        "document_type": "candidate_result",
        "source": str(source_path),
        "fixture_id": c["fixture_id"],
        "pass": passed,
        "missing_required": missing,
        "forbidden_present": forbidden,
        "missing_required_unknowns": missing_unknowns,
        "invariant_failures": invariant_failures,
        "scores": {
            "required_claim_recall": round(1 - min(len(missing) / n, 1), 4),
            "overreach_count": len(forbidden),
            "ambiguity_retention": 1.0 if not missing_unknowns else 0.0,
            "provenance_completeness": 1.0 if c["invariants"].get("provenance_complete") else 0.0,
            "source_preservation": 1.0 if (
                c["invariants"].get("raw_observation_preserved")
                and c["invariants"].get("whole_bearer_preserved")
                and c["invariants"].get("no_unobserved_as_observed")
            ) else 0.0,
        },
    }
    emit(report)
    raise SystemExit(0 if passed else 1)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(
            "usage: python runner/run_validation.py <fixture.json|candidate-result.json>\n\n"
            "The input type is auto-detected:\n"
            "  fixture definition  -> structural validation\n"
            "  candidate result     -> graded against fixtures/<fixture_id>.json\n"
        )
        raise SystemExit(0 if len(sys.argv) == 2 else 2)

    path = Path(sys.argv[1])
    obj = load_json(path)
    doc_type = detect_document_type(obj)
    if doc_type == "fixture":
        validate_fixture_document(obj, path)
    if doc_type == "candidate_result":
        grade_candidate(obj, path)
    fail(
        "unable to determine JSON document type",
        details={
            "source": str(path),
            "expected_fixture_fields": sorted(FIXTURE_REQUIRED),
            "expected_candidate_fields": sorted(CANDIDATE_REQUIRED),
        },
    )


if __name__ == "__main__":
    main()
