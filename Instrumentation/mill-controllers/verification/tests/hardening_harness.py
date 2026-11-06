#!/usr/bin/env python3
"""Seeded no-launch fuzzing and same-target contention hardening for one verifier."""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path(os.environ.get("MILL_FACTORY_ROOT", REPOSITORY_ROOT / "mill-factory"))
SPEC = importlib.util.spec_from_file_location("mill_verification_controller", ROOT / "controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(controller)

SEED = 2026110601
FUZZ_CASES = 1000
CONTENTION_ROUNDS = 20
CONTENTION_WORKERS = 32


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def request(batch: Path, request_id: str) -> dict[str, Any]:
    return {"request_id": request_id, "batch_path": str(batch)}


def authority(value: dict[str, Any], allowed_root: Path, identity: dict[str, Any]) -> dict[str, Any]:
    return {
        "authority_id": "approved-verifier-hardening-boundary",
        "authorized_by": "approved-hardening-harness",
        "request_digest": controller.request_digest(value),
        "tool_identity_sha256": identity["sha256"],
        "allowed_batch_roots": [str(allowed_root)],
    }


def run_unit_tests(reference: Path, run_root: Path) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["MILL_VERIFICATION_REFERENCE_BATCH"] = str(reference)
    process = subprocess.run(
        [sys.executable, "-B", str(HERE / "test_controller.py")],
        cwd=str(ROOT), env=environment, text=True, capture_output=True,
    )
    deterministic = run_root / "deterministic"
    deterministic.mkdir(parents=True, exist_ok=True)
    (deterministic / "unit-tests.stdout.txt").write_text(process.stdout, encoding="utf-8")
    (deterministic / "unit-tests.stderr.txt").write_text(process.stderr, encoding="utf-8")
    passed = process.returncode == 0 and "Ran 14 tests" in process.stderr and "OK" in process.stderr
    return {"result": "PASS" if passed else "FAIL", "exit_code": process.returncode, "expected_tests": 14}


def fuzz_case(category: str, index: int, root: Path, identity: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    value = request(root / "batches" / f"fuzz-{index:04d}", f"fuzz-{index:04d}")
    if category == "invalid_request_id":
        value["request_id"] = "invalid request id"
    elif category == "missing_batch_path":
        value.pop("batch_path")
    elif category == "nul_batch_path":
        value["batch_path"] = "bad\x00path"
    elif category == "oversized_request":
        value["padding"] = "x" * (controller.MAX_JSON_BYTES + 1)
    current_authority = authority(value, root / "batches", identity)
    if category == "bad_request_digest":
        current_authority["request_digest"] = "0" * 64
    elif category == "bad_tool_identity":
        current_authority["tool_identity_sha256"] = "1" * 64
    elif category == "empty_allowed_roots":
        current_authority["allowed_batch_roots"] = []
    elif category == "invalid_allowed_root":
        current_authority["allowed_batch_roots"] = [7]
    elif category == "outside_allowed_root":
        current_authority["allowed_batch_roots"] = [str(root / "other")]
    elif category == "missing_authority_id":
        current_authority.pop("authority_id")
    elif category == "missing_authorized_by":
        current_authority.pop("authorized_by")
    elif category == "nul_authority":
        current_authority["authorized_by"] = "bad\x00operator"
    return value, current_authority


def run_fuzz(run_root: Path, identity: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(SEED)
    fuzz_root = run_root / "fuzz"
    state = fuzz_root / "controller-state"
    categories = (
        "invalid_request_id", "missing_batch_path", "nul_batch_path", "oversized_request",
        "bad_request_digest", "bad_tool_identity", "empty_allowed_roots", "invalid_allowed_root",
        "outside_allowed_root", "missing_authority_id", "missing_authorized_by", "nul_authority",
    )
    outcome_counts: Counter[str] = Counter()
    records: list[dict[str, Any]] = []
    for index in range(FUZZ_CASES):
        # Keep exactly one malformed request ID: the controller intentionally
        # assigns malformed IDs a common retained identifier, so more than one
        # would measure request-ID collision behavior rather than fuzz admission.
        category = "invalid_request_id" if index == 0 else rng.choice(categories[1:])
        value, current_authority = fuzz_case(category, index, fuzz_root, identity)
        value["request_id"] = value.get("request_id", f"fuzz-{index:04d}")
        if isinstance(value["request_id"], str) and value["request_id"] != "invalid request id":
            value["request_id"] = f"fuzz-{index:04d}"
        current_authority["request_digest"] = controller.request_digest(value) if category != "bad_request_digest" else "0" * 64
        receipt = controller.execute(value, current_authority, SOURCE_ROOT, state, "pwsh")
        if receipt["process"]["launched"]:
            raise AssertionError(f"fuzz case {index} launched the Mill validator")
        if receipt["validator"]["reported_result"] == "PASS":
            raise AssertionError(f"fuzz case {index} reported a false PASS")
        outcome_counts[f"{category}:{receipt['admission']}:{receipt['retained_state']}"] += 1
        records.append({
            "index": index,
            "category": category,
            "request": value,
            "authority": current_authority,
            "receipt": {
                "admission": receipt["admission"],
                "validator_result": receipt["validator"]["reported_result"],
                "retained_state": receipt["retained_state"],
                "next_permitted_action": receipt["next_permitted_action"],
                "problems": receipt["problems"],
            },
        })
    receipts = list((state / "receipts").glob("*.json")) if (state / "receipts").is_dir() else []
    emergency = list((state / "emergency-receipts").glob("*.json")) if (state / "emergency-receipts").is_dir() else []
    if len(receipts) + len(emergency) != FUZZ_CASES:
        raise AssertionError(f"fuzz retained {len(receipts) + len(emergency)} outcomes, expected {FUZZ_CASES}")
    if (fuzz_root / "batches").exists():
        raise AssertionError("fuzzing created a batch output path")
    with (run_root / "fuzz-cases.jsonl").open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, sort_keys=True) + "\n")
    return {
        "seed": SEED,
        "cases": FUZZ_CASES,
        "mill_validator_launches": 0,
        "validator_passes": 0,
        "normal_receipts": len(receipts),
        "emergency_receipts": len(emergency),
        "outcomes": dict(sorted(outcome_counts.items())),
    }


def source_validation(batch: Path) -> dict[str, Any]:
    process = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(SOURCE_ROOT / "Test-MillBatch.ps1"), "-BatchPath", str(batch)],
        cwd=str(SOURCE_ROOT), text=True, capture_output=True,
    )
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        report = None
    return {"exit_code": process.returncode, "report": report, "stderr": process.stderr}


def wait_for_registered_operations(state: Path, expected: int, timeout_seconds: float = 30) -> None:
    """Wait until every simultaneous contender has registered before release.

    The controller intentionally releases its lease after a completed
    verification so later independent requests can verify again. The torture
    harness therefore must prove that all requests in *this* simultaneous round
    observed the one in-flight lease before allowing the validator to finish.
    """
    deadline = time.monotonic() + timeout_seconds
    database = state / "controller.sqlite3"
    observed = 0
    while time.monotonic() < deadline:
        if database.is_file():
            try:
                connection = sqlite3.connect(database, timeout=0.1)
                try:
                    observed = connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0]
                finally:
                    connection.close()
                if observed == expected:
                    return
            except sqlite3.Error:
                pass
        time.sleep(0.05)
    raise AssertionError(f"contention round registered {observed} operations, expected {expected}")


def run_contention_round(run_root: Path, reference: Path, identity: dict[str, Any], round_index: int) -> dict[str, Any]:
    round_root = run_root / "contention" / f"round-{round_index:02d}"
    batch = round_root / "batches" / "shared" / reference.name
    shutil.copytree(reference, batch)
    state = round_root / "controller-state"
    start = threading.Barrier(CONTENTION_WORKERS)
    process_entered = threading.Event()
    release_process = threading.Event()
    original_bounded_run = controller.bounded_run

    def gated_bounded_run(command: list[str], cwd: Path, timeout: float = controller.TOOL_TIMEOUT_SECONDS) -> dict[str, Any]:
        process_entered.set()
        if not release_process.wait(timeout=10):
            raise AssertionError("contention gate was not released")
        return original_bounded_run(command, cwd, timeout)

    def submit(worker: int) -> dict[str, Any]:
        value = request(batch, f"round-{round_index:02d}-worker-{worker:02d}")
        current_authority = authority(value, round_root / "batches", identity)
        start.wait(timeout=10)
        return controller.execute(value, current_authority, SOURCE_ROOT, state, "pwsh")

    controller.bounded_run = gated_bounded_run
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONTENTION_WORKERS) as pool:
            futures = [pool.submit(submit, worker) for worker in range(CONTENTION_WORKERS)]
            if not process_entered.wait(timeout=15):
                raise AssertionError(f"round {round_index} did not reach validator launch gate")
            wait_for_registered_operations(state, CONTENTION_WORKERS)
            release_process.set()
            receipts = [future.result(timeout=140) for future in futures]
    finally:
        release_process.set()
        controller.bounded_run = original_bounded_run

    launched = [receipt for receipt in receipts if receipt["process"]["launched"]]
    blocked = [receipt for receipt in receipts if receipt["admission"] == "not_permitted" and receipt["retained_state"] == "lease_preserved"]
    normal = list((state / "receipts").glob("*.json"))
    emergency = list((state / "emergency-receipts").glob("*.json")) if (state / "emergency-receipts").is_dir() else []
    connection = sqlite3.connect(state / "controller.sqlite3")
    try:
        leases = connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0]
    finally:
        connection.close()
    if len(launched) != 1 or launched[0]["validator"]["reported_result"] != "PASS":
        raise AssertionError(f"round {round_index}: expected one launched PASS, got {len(launched)}")
    if len(blocked) != CONTENTION_WORKERS - 1:
        raise AssertionError(f"round {round_index}: expected {CONTENTION_WORKERS - 1} lease blocks, got {len(blocked)}")
    if len(normal) != CONTENTION_WORKERS or emergency or leases:
        raise AssertionError(f"round {round_index}: receipts normal={len(normal)} emergency={len(emergency)} leases={leases}")
    return {
        "round": round_index,
        "workers": CONTENTION_WORKERS,
        "batch_path": str(batch),
        "launched_passes": len(launched),
        "lease_blocks": len(blocked),
        "normal_receipts": len(normal),
        "emergency_receipts": len(emergency),
        "remaining_leases": leases,
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
    allowed_preexisting = {"APPROVED_SCOPE.md", "CORRECTION_SCOPE.md", "harness.stdout.txt", "harness.stderr.txt"}
    if run_root.exists():
        unexpected = [path.name for path in run_root.iterdir() if path.name not in allowed_preexisting]
        if unexpected:
            raise SystemExit(f"Run root contains unexpected pre-existing content: {', '.join(sorted(unexpected))}")
    run_root.mkdir(parents=True, exist_ok=True)
    identity = controller.source_identity(SOURCE_ROOT)
    deterministic = run_unit_tests(reference, run_root)
    if deterministic["result"] != "PASS":
        write_json(run_root / "HARNESS_SUMMARY.json", {"result": "FAIL", "deterministic": deterministic})
        return 2
    fuzz = run_fuzz(run_root, identity)
    rounds = [run_contention_round(run_root, reference, identity, index) for index in range(CONTENTION_ROUNDS)]
    independent = {
        "first_round": source_validation(Path(rounds[0]["batch_path"])),
        "final_round": source_validation(Path(rounds[-1]["batch_path"])),
    }
    if any(value["exit_code"] != 0 or not value["report"] or value["report"].get("result") != "PASS" for value in independent.values()):
        raise AssertionError("independent source validation did not PASS for first and final rounds")
    summary = {
        "result": "PASS",
        "harness": "mill-batch-verification-controller",
        "deterministic": deterministic,
        "fuzz": fuzz,
        "contention": {"rounds": CONTENTION_ROUNDS, "workers_per_round": CONTENTION_WORKERS, "round_results": rounds},
        "independent_source_validation": independent,
        "tool_identity": identity,
        "llm_calls": 0,
        "scope_limit": "No public schema change, protected-source change, dependency installation, writer invocation, promotion, LLM comparison, or generic orchestration.",
    }
    write_json(run_root / "HARNESS_SUMMARY.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
