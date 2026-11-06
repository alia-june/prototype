#!/usr/bin/env python3
"""Run bounded functional validation and retain evidence for the verification controller."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path(os.environ.get("MILL_FACTORY_ROOT", REPOSITORY_ROOT / "mill-factory"))
SPEC = importlib.util.spec_from_file_location("mill_verification_controller", ROOT / "controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(controller)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def request(batch: Path, request_id: str) -> dict:
    return {"request_id": request_id, "batch_path": str(batch)}


def authority(value: dict, root: Path, identity: dict) -> dict:
    return {
        "authority_id": "approved-implementation-validation-boundary",
        "authorized_by": "approved-bounded-harness",
        "request_digest": controller.request_digest(value),
        "tool_identity_sha256": identity["sha256"],
        "allowed_batch_roots": [str(root / "validation" / "batches")],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-batch", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    arguments = parser.parse_args()
    reference = arguments.reference_batch.resolve()
    run_root = arguments.run_root.resolve()
    if not reference.is_dir() or not (reference / "MILL_BATCH.json").is_file():
        raise SystemExit(f"Reference must be an existing Mill batch: {reference}")
    allowed_preexisting = {"APPROVED_SCOPE.md", "CORRECTION_SCOPE.md"}
    if run_root.exists():
        unexpected = [path.name for path in run_root.iterdir() if path.name not in allowed_preexisting]
        if unexpected:
            raise SystemExit(f"Run root contains unexpected pre-existing content: {', '.join(sorted(unexpected))}")
    run_root.mkdir(parents=True, exist_ok=True)

    environment = os.environ.copy()
    environment["MILL_VERIFICATION_REFERENCE_BATCH"] = str(reference)
    unit = subprocess.run([sys.executable, "-B", str(HERE / "test_controller.py")], cwd=str(ROOT), env=environment, text=True, capture_output=True)
    (run_root / "validation" / "unit-tests.stdout.txt").parent.mkdir(parents=True, exist_ok=True)
    (run_root / "validation" / "unit-tests.stdout.txt").write_text(unit.stdout, encoding="utf-8")
    (run_root / "validation" / "unit-tests.stderr.txt").write_text(unit.stderr, encoding="utf-8")
    if unit.returncode != 0:
        write_json(run_root / "validation" / "test-summary.json", {"result": "FAIL", "unit_exit_code": unit.returncode})
        return unit.returncode

    # Mill validates that the directory leaf equals metadata.batch_id.  The
    # copies therefore use the reference leaf beneath distinct parent roots.
    clean = run_root / "validation" / "batches" / "clean" / reference.name
    altered = run_root / "validation" / "batches" / "tampered" / reference.name
    shutil.copytree(reference, clean)
    shutil.copytree(reference, altered)
    with (altered / "README.md").open("a", encoding="utf-8") as output:
        output.write("\nIntentional disposable harness tamper.\n")
    identity = controller.source_identity(SOURCE_ROOT)
    records = []
    for batch, identifier in ((clean, "implementation-clean-001"), (altered, "implementation-tamper-001")):
        value = request(batch, identifier)
        receipt = controller.execute(value, authority(value, run_root, identity), SOURCE_ROOT, run_root / "validation" / "controller-state", "pwsh")
        records.append({"request": value, "receipt": receipt})
    write_json(run_root / "validation" / "controller-records.json", records)
    clean_result, tamper_result = (record["receipt"]["validator"]["reported_result"] for record in records)
    summary = {
        "result": "PASS" if clean_result == "PASS" and tamper_result == "FAIL" else "FAIL",
        "unit_exit_code": unit.returncode,
        "reference_batch": str(reference),
        "reference_copied": True,
        "source_identity": identity,
        "clean_validator_result": clean_result,
        "tampered_validator_result": tamper_result,
        "llm_calls": 0,
        "scope": "bounded basic functional validation only; no fuzzing, torture, or LLM comparison",
    }
    write_json(run_root / "validation" / "test-summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
