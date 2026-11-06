#!/usr/bin/env python3
"""Bounded integration validation for the Mill gate controller.

Creates only copied batches and controller state below the supplied run root.
It never writes to the factory source or reference fixture.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, sys
from pathlib import Path


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_controller(path: Path):
    spec = importlib.util.spec_from_file_location("mill_gate_controller", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_batch(fixture: Path, root: Path, name: str) -> Path:
    # Mill validates that metadata batch_id equals the leaf directory name.
    # Keep the fixture leaf unchanged while isolating every case one level up.
    destination = root / "batches" / name / fixture.name
    shutil.copytree(fixture, destination)
    return destination


def authority(controller, request, tool_root, allowed_root, evidence=None, mutate=None):
    value = {
        "request_digest": controller.rh(request),
        "tool_identity_sha256": controller.ident(tool_root)["sha256"],
        "allowed_batch_roots": [str(allowed_root)],
    }
    if evidence is not None:
        value["evidence_sha256"] = digest_file(evidence)
    if mutate:
        mutate(value)
    return value


def run_case(name, controller, request, auth, tool_root, state, expected, checks):
    receipt = controller.execute(request, auth, tool_root, state)
    actual = receipt["retained_state"]
    passed = actual == expected and all(check(receipt) for check in checks)
    return {
        "name": name,
        "pass": passed,
        "expected_retained_state": expected,
        "actual_retained_state": actual,
        "receipt": receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", required=True, type=Path)
    parser.add_argument("--tool-root", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--validation-name", default="validation")
    parser.add_argument("--powershell", default="pwsh")
    args = parser.parse_args()

    controller = load_controller(args.controller.resolve())
    tool_root, fixture, run_root = args.tool_root.resolve(), args.fixture.resolve(), args.run_root.resolve()
    validation = run_root / args.validation_name
    state = validation / "controller-state"
    validation.mkdir(parents=True, exist_ok=True)
    results = []

    def request(batch, name, gate="source_freeze", result="PENDING", evidence=None):
        value = {"request_id": name, "batch_path": str(batch), "gate": gate, "result": result,
                 "reviewer": "validation-harness", "notes": "bounded basic validation"}
        if evidence is not None:
            value["evidence_path"] = str(evidence.relative_to(batch)).replace("\\", "/")
        return value

    # 1. Pending is admitted without evidence and reseals a valid copied batch.
    batch = make_batch(fixture, validation, "pending")
    req = request(batch, "case-01-pending")
    results.append(run_case("pending gate records and validates", controller, req,
        authority(controller, req, tool_root, validation), tool_root, state, "receipt_retained",
        [lambda r: r["gate_write_reported"] == "true", lambda r: r["structural_validation"] == "PASS"]))

    # 2-4. Every evidence-bearing result verifies the evidence digest before write.
    for index, result in enumerate(("PASS", "FAIL", "BLOCKED"), start=2):
        batch = make_batch(fixture, validation, f"{result.lower()}")
        evidence = batch / "evidence" / result.lower() / "result.txt"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(f"{result} evidence for bounded validation\n", encoding="utf-8")
        req = request(batch, f"case-{index:02d}-{result.lower()}", "static", result, evidence)
        results.append(run_case(f"{result} with bound evidence", controller, req,
            authority(controller, req, tool_root, validation, evidence), tool_root, state, "receipt_retained",
            [lambda r, expected=result: r["evidence_identity"]["sha256"] is not None,
             lambda r: r["structural_validation"] == "PASS"]))

    # 5. Missing evidence cannot reach the writer.
    batch = make_batch(fixture, validation, "missing-evidence")
    req = request(batch, "case-05-missing-evidence", "candidate", "PASS")
    req["evidence_path"] = "evidence/no/such/file.txt"
    results.append(run_case("missing evidence is refused", controller, req,
        authority(controller, req, tool_root, validation), tool_root, state, "none_observed",
        [lambda r: r["admission"] == "not_permitted", lambda r: r["gate_write_reported"] == "not_run"]))

    # 6. Traversal is refused even when an authority assertion otherwise matches.
    batch = make_batch(fixture, validation, "unsafe-path")
    req = request(batch, "case-06-unsafe-path", "candidate", "PASS")
    req["evidence_path"] = "../outside.txt"
    results.append(run_case("traversal evidence path is refused", controller, req,
        authority(controller, req, tool_root, validation), tool_root, state, "none_observed",
        [lambda r: "unsafe evidence_path" in r["problems"], lambda r: r["gate_write_reported"] == "not_run"]))

    # 7. A source identity mismatch is refused before the writer can run.
    batch = make_batch(fixture, validation, "source-mismatch")
    req = request(batch, "case-07-source-mismatch")
    results.append(run_case("source identity mismatch is refused", controller, req,
        authority(controller, req, tool_root, validation, mutate=lambda a: a.update({"tool_identity_sha256": "0" * 64})),
        tool_root, state, "none_observed", [lambda r: "authority binding mismatch" in r["problems"]]))

    # 8. A changed evidence file invalidates a formerly matching evidence assertion.
    batch = make_batch(fixture, validation, "digest-mismatch")
    evidence = batch / "evidence" / "digest" / "result.txt"
    evidence.parent.mkdir(parents=True, exist_ok=True); evidence.write_text("before\n", encoding="utf-8")
    req = request(batch, "case-08-digest-mismatch", "compiler", "PASS", evidence)
    auth = authority(controller, req, tool_root, validation, evidence)
    evidence.write_text("after\n", encoding="utf-8")
    results.append(run_case("evidence digest mismatch is refused", controller, req, auth, tool_root, state, "none_observed",
        [lambda r: "evidence digest mismatch" in r["problems"], lambda r: r["gate_write_reported"] == "not_run"]))

    # 9. Duplicate request IDs remain bound to their first receipt.
    batch = make_batch(fixture, validation, "duplicate")
    req = request(batch, "case-09-duplicate")
    first = controller.execute(req, authority(controller, req, tool_root, validation), tool_root, state)
    second = controller.execute(req, authority(controller, req, tool_root, validation), tool_root, state)
    results.append({"name": "duplicate request id is preserved", "pass": first["retained_state"] == "receipt_retained" and "request_id already bound" in second["problems"],
                    "expected_retained_state": "prior_request_preserved", "actual_retained_state": second["retained_state"], "receipt": second})

    # 10. A lease held in retained state prevents a second writer invocation.
    batch = make_batch(fixture, validation, "lease")
    req = request(batch, "case-10-held-lease")
    connection = controller.db(state)
    connection.execute("INSERT OR REPLACE INTO leases VALUES (?,?)", (str(batch), "manual-held-lease")); connection.close()
    results.append(run_case("held lease is refused", controller, req, authority(controller, req, tool_root, validation), tool_root, state, "lease_preserved",
        [lambda r: r["gate_write_reported"] == "not_run", lambda r: r["next_permitted_action"] == "await_recovery_authority"]))

    # 11. An unavailable launcher is retained as an uncertain process outcome.
    batch = make_batch(fixture, validation, "missing-launcher")
    req = request(batch, "case-11-missing-launcher")
    receipt = controller.execute(req, authority(controller, req, tool_root, validation), tool_root, state, "definitely-not-a-launcher")
    results.append({"name": "unavailable launcher retains uncertainty", "pass": receipt["retained_state"] == "partial_or_unknown" and receipt["process_outcome"]["launched"] is False,
                    "expected_retained_state": "partial_or_unknown", "actual_retained_state": receipt["retained_state"], "receipt": receipt})

    # 12. An allowed root assertion is required; adjacent batch roots are not implied.
    batch = make_batch(fixture, validation, "outside-authorized-root")
    req = request(batch, "case-12-outside-root")
    results.append(run_case("outside authorized root is refused", controller, req,
        authority(controller, req, tool_root, validation / "different-root"), tool_root, state, "none_observed",
        [lambda r: "batch outside authorized roots" in r["problems"]]))

    summary = {"schema": "mill-gate-controller-basic-validation/v1", "case_count": len(results),
               "passed": sum(1 for item in results if item["pass"]), "failed": sum(1 for item in results if not item["pass"]),
               "tool_identity": controller.ident(tool_root), "cases": results}
    (validation / "HARNESS_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("schema", "case_count", "passed", "failed")}, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
