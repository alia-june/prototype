"""Closed meta-checks against controlled packets and the current service harness."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import secrets
import sys
import threading
import time
from unittest.mock import patch

from ..harness import runner as target_runner
from ..harness.core import encoded as target_encode
from .audit import AuditError, audit_run, encode, strict_json


SERVICE = Path(__file__).resolve().parents[3]
WORKSPACE = SERVICE.parent


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def clean_packet(root: Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    mode_root = root / "rigid"
    (mode_root / "inputs").mkdir(parents=True)
    case = {"schema": "docstream.harness.case/1", "kind": "regression", "seed": 1,
            "input": {"name": "controlled"}}
    input_path = mode_root / "inputs" / "0000-control.json"
    _write(input_path, case)
    row = {"name": "controlled", "kind": "regression", "status": "passed",
           "input_file": str(input_path.resolve()),
           "input_sha256": sha256(target_encode(case)).hexdigest(),
           "elapsed_seconds": 0.0, "result": {"controlled": True}}
    events = [
        {"event": "mode_started", "mode": "rigid", "seed": 1},
        {"event": "case_started", "name": "controlled", "kind": "regression"},
        {"event": "case_finished", **row},
        {"event": "mode_finished", "status": "passed", "counts": {"passed": 1}},
    ]
    with (mode_root / "events.jsonl").open("wb") as handle:
        for event in events: handle.write(encode(event) + b"\n")
    cleanup = {"status": "confirmed", "scope": "windows_job" if os.name == "nt" else "launcher",
               "job_assigned": os.name == "nt", "active_processes_before": 1,
               "active_processes_after": 0, "termination_requested": False,
               "job_query_samples": 1, "job_handle_closed": True,
               "process_ids_observed": [], "process_exit_waits": 0,
               "launcher_stopped": True, "elapsed_seconds": 0.0}
    _write(mode_root / "cleanup.json", cleanup)
    mode = {"schema": "docstream.harness/1.3", "mode": "rigid", "seed": 1,
            "status": "passed", "coverage_complete": True, "counts": {"passed": 1},
            "cases": [row], "metrics": {}, "incomplete_reasons": [],
            "owned_worker_started": True, "owned_worker_pid": 1, "owned_worker_stopped": True,
            "owned_cleanup": cleanup, "owned_job_stopped": os.name == "nt"}
    _write(mode_root / "results.json", mode)
    metadata = {"schema": "docstream.harness/1.3", "run_id": root.name,
                "product_hashes_before": {"controlled.py": "same"},
                "harness_hashes": {"runner.py": "controlled"}, "limits": {}}
    summary = {"schema": "docstream.harness/1.3", "status": "passed", "run_id": root.name,
               "product_files_changed": [], "modes": [mode], "limits": {},
               "elapsed_seconds": 0.0, "retained_bytes": 0, "render_calls": 0}
    _write(root / "run.json", metadata)
    _write(root / "summary.json", summary)
    return root


def _load_summary(root: Path):
    return json.loads((root / "summary.json").read_text(encoding="utf-8"))


def _save_summary(root: Path, value):
    _write(root / "summary.json", value)


def apply_mutation(root: Path, mutation: str) -> None:
    summary = _load_summary(root)
    mode = summary["modes"][0]
    mode_root = root / "rigid"
    if mutation == "wrong_schema": summary["schema"] = "unknown/999"
    elif mutation == "wrong_run_id": summary["run_id"] = "different"
    elif mutation == "wrong_overall_status": summary["status"] = "failed"
    elif mutation == "missing_modes": summary.pop("modes")
    elif mutation == "duplicate_mode": summary["modes"].append(deepcopy(mode))
    elif mutation == "missing_worker_stopped": mode.pop("owned_worker_stopped")
    elif mutation == "wrong_worker_type": mode["owned_worker_stopped"] = 1
    elif mutation == "missing_cleanup": mode.pop("owned_cleanup")
    elif mutation == "cleanup_status_pending": mode["owned_cleanup"]["status"] = "pending"
    elif mutation == "cleanup_mismatch": mode["owned_cleanup"]["process_exit_waits"] = 99
    elif mutation == "job_claim_without_zero": mode["owned_cleanup"]["active_processes_after"] = 1
    elif mutation == "wrong_counts": mode["counts"] = {"passed": 99}
    elif mutation == "duplicate_case": mode["cases"].append(deepcopy(mode["cases"][0]))
    elif mutation == "missing_input": Path(mode["cases"][0]["input_file"]).unlink()
    elif mutation == "tampered_input": Path(mode["cases"][0]["input_file"]).write_text("{}\n", encoding="utf-8")
    elif mutation == "escaped_input": mode["cases"][0]["input_file"] = str((root.parent / "outside.json").resolve())
    elif mutation == "missing_events": (mode_root / "events.jsonl").unlink()
    elif mutation == "contradictory_event":
        with (mode_root / "events.jsonl").open("ab") as handle:
            handle.write(encode({"event": "case_finished", "name": "controlled", "status": "failed"}) + b"\n")
    elif mutation == "passed_without_coverage": mode["coverage_complete"] = False
    elif mutation == "product_changed": summary["product_files_changed"] = ["service/src/docstream_cpu/service.py"]
    else: raise ValueError("unknown closed mutation")
    _save_summary(root, summary)


def check_packet(parent: Path, mutation: str, label: str) -> dict:
    root = clean_packet(parent / label)
    if mutation != "clean_control": apply_mutation(root, mutation)
    issues = audit_run(root)
    if mutation == "clean_control":
        if issues: raise AssertionError(f"clean packet rejected: {issues}")
        return {"observed": "PASS", "issues": []}
    if not issues: raise AssertionError(f"mutation accepted: {mutation}")
    return {"observed": "REJECT", "issues": issues}


def run_hardening(name: str, parent: Path) -> dict:
    if name in ("clean_control", "wrong_schema", "wrong_run_id", "wrong_overall_status",
                "missing_modes", "duplicate_mode", "missing_worker_stopped", "wrong_worker_type",
                "missing_cleanup", "cleanup_status_pending", "cleanup_mismatch",
                "job_claim_without_zero", "wrong_counts", "duplicate_case", "missing_input",
                "tampered_input", "escaped_input", "missing_events", "contradictory_event",
                "passed_without_coverage", "product_changed"):
        return check_packet(parent, name, "hardening-" + name)
    root = clean_packet(parent / ("hardening-" + name))
    if name == "strict_duplicate_json":
        path = root / "summary.json"; path.write_text('{"schema":"a","schema":"b"}', encoding="utf-8")
        try: strict_json(path)
        except AuditError as exc:
            if exc.code == "DUPLICATE_JSON_KEY": return {"observed": "REJECT", "code": exc.code}
        raise AssertionError("duplicate key accepted")
    if name == "truncated_json":
        (root / "summary.json").write_text('{"schema":', encoding="utf-8")
        if audit_run(root): return {"observed": "REJECT"}
        raise AssertionError("truncated JSON accepted")
    if name == "oversized_json":
        (root / "summary.json").write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        if audit_run(root): return {"observed": "REJECT"}
        raise AssertionError("oversized JSON accepted")
    if name == "failure_precedence":
        apply_mutation(root, "contradictory_event")
        issues = audit_run(root)
        if not any("FAILURE_DEMOTED" in issue for issue in issues): raise AssertionError("failure demoted")
        return {"observed": "REJECT", "issues": issues}
    if name == "incomplete_precedence": return check_packet(parent, "passed_without_coverage", "incomplete-precedence")
    if name == "source_identity_guard": return check_packet(parent, "product_changed", "source-identity")
    if name == "non_overwrite":
        before = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
        try: clean_packet(root)
        except FileExistsError: pass
        else: raise AssertionError("existing evidence overwritten")
        after = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
        if before != after: raise AssertionError("existing evidence changed")
        return {"observed": "REJECT"}
    if name == "configuration_bounds":
        from .cases import fuzzy_cases
        rejected = 0
        for kwargs in ({"seed": True}, {"seed": -1}, {"count": 6}, {"count": 1005}):
            try: list(fuzzy_cases(**kwargs))
            except ValueError: rejected += 1
        if rejected != 4: raise AssertionError("configuration coercion accepted")
        return {"observed": "REJECT", "rejected": rejected}
    if name == "input_retained_before_actor":
        return {"observed": "PASS", "retained": (root / "rigid/inputs/0000-control.json").is_file()}
    raise ValueError(name)


def _owned_command(command: list[str], timeout: float) -> tuple[int, bytes, bool]:
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(command, cwd=WORKSPACE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, creationflags=creation,
                               start_new_session=os.name != "nt")
    job = None
    try:
        if os.name == "nt":
            import win32api, win32con, win32job
            job = win32job.CreateJobObject(None, "DocstreamHarnessMeta-" + secrets.token_hex(12))
            info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
            info["BasicLimitInformation"]["LimitFlags"] = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, info)
            handle = win32api.OpenProcess(win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE,
                                          False, process.pid)
            try: win32job.AssignProcessToJobObject(job, handle)
            finally: handle.Close()
        try:
            output, _ = process.communicate(timeout=timeout)
            return process.returncode, output, False
        except subprocess.TimeoutExpired:
            if job is not None:
                import win32job
                win32job.TerminateJobObject(job, 2)
            else: process.kill()
            output, _ = process.communicate(timeout=10)
            return process.returncode, output, True
    finally:
        if job is not None: job.Close()


def _save_command_result(root: Path, name: str, command: list[str], timeout: float) -> dict:
    code, output, timed_out = _owned_command(command, timeout)
    path = root / (name + ".txt")
    path.write_bytes(output)
    return {"exit_code": code, "timed_out": timed_out, "output": str(path),
            "output_sha256": sha256(output).hexdigest(), "bytes": len(output)}


def run_torture(name: str, root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    if name == "deadline_summary_cycles":
        target_root = root / "deadline-runs"; target_root.mkdir()
        outcomes = []
        for number in range(8):
            run_id = f"deadline-{number:02d}"
            with patch.object(target_runner, "RUNS_ROOT", target_root):
                code = target_runner.main(["fuzzy", "--cases", "8", "--max-seconds", "0.05", "--run-id", run_id])
            packet = target_root / run_id
            issues = audit_run(packet)
            outcomes.append({"run_id": run_id, "exit_code": code, "issues": issues})
        failures = [row for row in outcomes if row["issues"]]
        return {"cycles": 8, "observed_failures": len(failures), "outcomes": outcomes,
                "status": "FAIL" if failures else "PASS"}
    if name == "exclusive_log_observation":
        deadline = root.parent / "deadline_summary_cycles" / "deadline-runs"
        rows = []
        for path in sorted(deadline.glob("*/fuzzy/process-output.txt")):
            opened = False; error = None
            try:
                if os.name == "nt":
                    import win32con, win32file
                    handle = win32file.CreateFile(str(path), win32con.GENERIC_READ, 0, None,
                                                  win32con.OPEN_EXISTING, 0, None)
                    handle.Close()
                else:
                    with path.open("rb"): pass
                opened = True
            except Exception as exc: error = f"{type(exc).__name__}: {exc}"
            rows.append({"path": str(path), "exclusive_open": opened, "error": error})
        return {"expected_cycles": 8, "observations": rows,
                "status": "PASS" if len(rows) == 8 and all(r["exclusive_open"] for r in rows) else "FAIL"}
    if name == "aggregate_order_cycles":
        tests = [
            "service.tests.test_harness.HarnessTests.test_supervisor_deadline_produces_incomplete_and_stops_child",
            "service.tests.test_native_harness.NativeHarnessTests.test_real_supervisor_timeout_stops_its_owned_child",
        ]
        rows = []
        for number, order in enumerate((tests, list(reversed(tests)), tests)):
            rows.append(_save_command_result(root, f"order-{number}",
                        [sys.executable, "-m", "unittest", *order, "-v"], 120))
        return {"runs": rows, "status": "PASS" if all(r["exit_code"] == 0 and not r["timed_out"] for r in rows) else "FAIL"}
    if name == "full_discovery_cycles":
        rows = []
        for number in range(3):
            rows.append(_save_command_result(root, f"discovery-{number}",
                [sys.executable, "-m", "unittest", "discover", "-s", "service/tests", "-p", "test_*.py", "-v"], 240))
        return {"runs": rows, "status": "PASS" if all(r["exit_code"] == 0 and not r["timed_out"] for r in rows) else "FAIL"}
    if name == "parallel_packet_audits":
        def one(number): return check_packet(root, "clean_control", f"parallel-{number}")
        with ThreadPoolExecutor(max_workers=4) as pool: rows = list(pool.map(one, range(4)))
        return {"runs": 4, "status": "PASS" if all(r["observed"] == "PASS" for r in rows) else "FAIL"}
    if name == "long_unfinished_journal":
        packet = clean_packet(root / "long")
        with (packet / "rigid/events.jsonl").open("wb") as handle:
            for number in range(2000):
                handle.write(encode({"event": "case_started", "name": f"pending-{number}"}) + b"\n")
        summary = _load_summary(packet); summary["modes"][0]["coverage_complete"] = False
        _save_summary(packet, summary)
        issues = audit_run(packet)
        return {"events": 2000, "issues": issues, "status": "PASS" if issues else "FAIL"}
    if name == "sticky_failure_recovery":
        for number in range(20):
            check_packet(root, "contradictory_event", f"sticky-{number}")
        return {"recoveries": 20, "status": "PASS"}
    if name == "isolated_evidence_roots":
        roots = [str(clean_packet(root / f"isolated-{number}")) for number in range(8)]
        return {"roots": roots, "status": "PASS" if len(set(roots)) == 8 else "FAIL"}
    raise ValueError(name)
