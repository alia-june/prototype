"""Independent strict readback of service-harness evidence."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


MAX_JSON_BYTES = 2 * 1024 * 1024


class AuditError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def encode(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError("DUPLICATE_JSON_KEY", key)
        result[key] = value
    return result


def strict_json(path: Path) -> dict:
    path = Path(path)
    size = path.stat().st_size
    if size > MAX_JSON_BYTES:
        raise AuditError("JSON_LIMIT", str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except AuditError:
        raise
    except (UnicodeError, ValueError) as exc:
        raise AuditError("INVALID_JSON", f"{path}: {exc}") from exc
    if type(value) is not dict:
        raise AuditError("INVALID_JSON_ROOT", str(path))
    return value


def _contained(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _events(path: Path):
    if not path.is_file():
        return [], ["MISSING_EVENTS"]
    rows, issues = [], []
    with path.open("rb") as handle:
        for number, raw in enumerate(handle, 1):
            try:
                value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
                if type(value) is not dict:
                    raise ValueError("event is not an object")
                rows.append(value)
            except (UnicodeError, ValueError, AuditError):
                issues.append(f"INVALID_EVENT:{number}")
    return rows, issues


def audit_run(root: Path) -> list[str]:
    root = Path(root).resolve()
    issues: list[str] = []
    try:
        summary = strict_json(root / "summary.json")
        metadata = strict_json(root / "run.json")
    except (OSError, AuditError) as exc:
        return [getattr(exc, "code", "MISSING_RUN_FILE")]
    if summary.get("schema") != "docstream.harness/1.3": issues.append("SUMMARY_SCHEMA")
    if metadata.get("schema") != "docstream.harness/1.3": issues.append("RUN_SCHEMA")
    if summary.get("run_id") != metadata.get("run_id") or summary.get("run_id") != root.name:
        issues.append("RUN_ID_MISMATCH")
    modes = summary.get("modes")
    if type(modes) is not list or not modes:
        return issues + ["MISSING_MODES"]
    names = [row.get("mode") for row in modes if type(row) is dict]
    if len(names) != len(set(names)): issues.append("DUPLICATE_MODE")
    derived = "failed" if summary.get("product_files_changed") or any(
        type(row) is dict and row.get("status") == "failed" for row in modes) else "incomplete" if any(
        type(row) is not dict or row.get("status") != "passed" for row in modes) else "passed"
    if summary.get("status") != derived: issues.append("OVERALL_STATUS_MISMATCH")
    if summary.get("product_files_changed"): issues.append("PRODUCT_CHANGED")
    for index, mode in enumerate(modes):
        prefix = f"MODE[{index}]"
        if type(mode) is not dict:
            issues.append(prefix + ":INVALID")
            continue
        for field in ("mode", "status", "counts", "cases", "owned_worker_started",
                      "owned_worker_stopped", "owned_cleanup"):
            if field not in mode: issues.append(prefix + ":MISSING_" + field.upper())
        started = mode.get("owned_worker_started")
        if type(started) is not bool: issues.append(prefix + ":WORKER_START_TYPE")
        if started is True and type(mode.get("owned_worker_stopped")) is not bool:
            issues.append(prefix + ":WORKER_STOP_TYPE")
        if started is False and mode.get("owned_worker_stopped") is not None:
            issues.append(prefix + ":NOT_STARTED_STOP_CLAIM")
        cleanup = mode.get("owned_cleanup")
        if type(cleanup) is not dict:
            issues.append(prefix + ":CLEANUP_INVALID")
        else:
            allowed_cleanup = ("confirmed", "failed") if started is True else ("not_started",)
            if cleanup.get("status") not in allowed_cleanup:
                issues.append(prefix + ":CLEANUP_UNRESOLVED")
            if started is False and (cleanup.get("job_assigned") is not False or
                                     mode.get("owned_worker_pid") is not None or
                                     mode.get("owned_job_stopped") is not None):
                issues.append(prefix + ":NOT_STARTED_CLAIM")
            if mode.get("owned_job_stopped") is True and not (
                cleanup.get("status") == "confirmed" and cleanup.get("active_processes_after") == 0):
                issues.append(prefix + ":JOB_STOP_UNSUPPORTED")
        mode_name = mode.get("mode")
        mode_root = root / str(mode_name)
        cleanup_path = mode_root / "cleanup.json"
        if mode_name != "supervisor" and started is True:
            if not cleanup_path.is_file():
                issues.append(prefix + ":MISSING_CLEANUP_FILE")
            elif type(cleanup) is dict:
                try:
                    if strict_json(cleanup_path) != cleanup:
                        issues.append(prefix + ":CLEANUP_MISMATCH")
                except (OSError, AuditError): issues.append(prefix + ":CLEANUP_INVALID_FILE")
        cases = mode.get("cases")
        if type(cases) is not list:
            issues.append(prefix + ":CASES_INVALID")
            continue
        counts = Counter(row.get("status") for row in cases if type(row) is dict)
        if mode.get("counts") != dict(counts): issues.append(prefix + ":COUNT_MISMATCH")
        identities = [row.get("name") for row in cases if type(row) is dict]
        if len(identities) != len(set(identities)): issues.append(prefix + ":DUPLICATE_CASE")
        events, event_issues = _events(mode_root / "events.jsonl")
        # A deadline may stop a newly launched worker before it creates a journal.
        # Absence is acceptable only when the retained mode is incomplete and has
        # no cases; malformed existing journals and missing journals with cases
        # remain evidence defects.
        if not (event_issues == ["MISSING_EVENTS"] and not cases and mode.get("status") == "incomplete"):
            issues.extend(prefix + ":" + value for value in event_issues)
        event_failures = {row.get("name") for row in events
                          if row.get("event") == "case_finished" and row.get("status") == "failed"}
        if event_failures and mode.get("status") == "passed":
            issues.append(prefix + ":FAILURE_DEMOTED")
        if mode.get("coverage_complete") is False and mode.get("status") == "passed":
            issues.append(prefix + ":INCOMPLETE_DEMOTED")
        for case in cases:
            if type(case) is not dict: continue
            name = case.get("input_file")
            if type(name) is not str:
                issues.append(prefix + ":MISSING_INPUT")
                continue
            input_path = Path(name)
            if not input_path.is_absolute(): input_path = mode_root / input_path
            if not _contained(mode_root, input_path):
                issues.append(prefix + ":INPUT_ESCAPE")
                continue
            if not input_path.is_file():
                issues.append(prefix + ":MISSING_INPUT")
                continue
            try:
                value = strict_json(input_path)
                if sha256(encode(value)).hexdigest() != case.get("input_sha256"):
                    issues.append(prefix + ":INPUT_HASH")
            except (OSError, AuditError): issues.append(prefix + ":INPUT_INVALID")
    return sorted(set(issues))
