"""Reconcile worker claims against retained events, planned inputs and identities."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from . import HARNESS_VERSION
from .core import encoded, load_case, reject_link


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError("duplicate evidence JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite evidence value")))


def read_events(root):
    started, finished, pending, issues, ending = {}, {}, {}, [], None
    path = root / "events.jsonl"
    try:
        reject_link(path)
        with path.open("r", encoding="utf-8") as file:
            for number, line in enumerate(file, 1):
                try:
                    event = strict_json(line)
                    if type(event) is not dict: raise ValueError("event is not an object")
                    kind = event.get("event")
                    if kind == "mode_finished":
                        if ending is not None: issues.append("duplicate mode_finished")
                        ending = event
                        continue
                    if kind == "worker_error":
                        issues.append("worker infrastructure error: " + str(event.get("reason"))); continue
                    if kind not in ("case_started", "case_failed", "case_finished"):
                        raise ValueError("unknown journal event")
                    key = event.get("case_id")
                    if type(key) is not str: raise ValueError("invalid event case ID")
                    if ending is not None: issues.append("case event after mode_finished")
                    if kind == "case_started":
                        if key in started: issues.append("duplicate started identity: " + key)
                        started[key] = event; pending[key] = event
                    else:
                        if key not in started: issues.append("finished case lacks started event: " + key)
                        if event.get("status") not in ("PASS", "FAIL"): raise ValueError("invalid finished status")
                        if kind == "case_failed" and event["status"] != "FAIL": raise ValueError("case_failed without FAIL")
                        previous = finished.get(key)
                        if previous and previous.get("status") == "FAIL" and event["status"] != "FAIL":
                            issues.append("failure contradicted by later PASS: " + key)
                        else: finished[key] = event
                        if kind == "case_finished": pending.pop(key, None)
                except (ValueError, TypeError, KeyError) as exc:
                    issues.append(f"invalid journal line {number}: {exc}")
    except (OSError, UnicodeError, ValueError) as exc:
        issues.append("unreadable journal: " + str(exc))
    return started, finished, pending, issues, ending


def recovered(root, mode, reason):
    _, finished, pending, issues, _ = read_events(root)
    records = list(finished.values())
    return {"schema": HARNESS_VERSION, "mode": mode,
            "status": "FAIL" if any(x["status"] == "FAIL" for x in records) else "INCOMPLETE",
            "incomplete_reason": reason, "cases": records, "interrupted_cases": list(pending),
            "passed": sum(x["status"] == "PASS" for x in records),
            "failed": sum(x["status"] == "FAIL" for x in records),
            "submitted_transformation_attempts": None, "audit_issues": issues}


def reconcile(root, mode, summary, planned, owned):
    """Return audited counts and sticky outcomes; preserve the worker summary on disk."""
    started, finished, pending, issues, ending = read_events(root)
    records = list(finished.values())
    if type(summary) is not dict:
        issues.append("missing or non-object worker summary"); summary = {}
    if summary.get("schema") != HARNESS_VERSION or summary.get("mode") != mode:
        issues.append("worker summary schema/mode mismatch")
    if summary.get("status") not in ("PASS", "FAIL", "INCOMPLETE"):
        issues.append("unknown worker summary status")
    rows = summary.get("cases")
    if type(rows) is not list or any(type(row) is not dict for row in rows):
        issues.append("invalid summary case list"); rows = []
    row_ids = [r.get("case_id") for r in rows]
    if any(type(key) is not str for key in row_ids) or len(set(str(k) for k in row_ids)) != len(row_ids):
        issues.append("invalid or duplicate summary case identities")
    if row_ids != list(finished): issues.append("summary/journal case identities differ")
    planned_by_id = {c["case_id"]: c for c in planned}
    if summary.get("status") == "PASS" and list(started) != list(planned_by_id):
        issues.append("PASS does not cover every planned case in order")
    for key, initial in started.items():
        try:
            relative = initial.get("input")
            if type(relative) is not str or "\\" in relative: raise ValueError("invalid relative input path")
            parts = PurePosixPath(relative)
            if parts.is_absolute() or ".." in parts.parts or not parts.parts or parts.parts[0] != "inputs":
                raise ValueError("input path is outside inputs")
            path = root / relative
            if not path.resolve().is_relative_to(root.resolve()): raise ValueError("input escaped run root")
            reject_link(path)
            case = load_case(path)
            if sha256(path.read_bytes()).hexdigest() != initial.get("input_sha256"):
                raise ValueError("saved input digest mismatch")
            if key not in planned_by_id or encoded(case) != encoded(planned_by_id[key]):
                raise ValueError("saved input differs from planned case")
            if case["case_id"] != key or case["mode"] != mode or case["family"] != initial.get("family"):
                raise ValueError("saved input identity/mode/family mismatch")
            final = finished.get(key)
            if final:
                for field in ("case_id", "family", "input", "input_sha256"):
                    if initial.get(field) != final.get(field): raise ValueError("started/finished input identity mismatch")
        except (OSError, ValueError, TypeError, RecursionError) as exc:
            issues.append(f"input verification failed for {key}: {exc}")
    for row in rows:
        final = finished.get(str(row.get("case_id")))
        if final:
            for field in ("case_id", "family", "input", "input_sha256", "status"):
                if row.get(field) != final.get(field): issues.append("summary/journal mismatch: " + str(row.get("case_id")) + "/" + field)
    passed = sum(x["status"] == "PASS" for x in records)
    failed = sum(x["status"] == "FAIL" for x in records)
    if type(summary.get("passed")) is not int or summary["passed"] != passed or type(summary.get("failed")) is not int or summary["failed"] != failed:
        issues.append("summary counts disagree with journal")
    if pending: issues.append("unfinished started cases")
    if ending is None or ending.get("status") != summary.get("status") or ending.get("incomplete_reason") != summary.get("incomplete_reason"):
        issues.append("missing or contradictory mode_finished")
    if summary.get("status") == "PASS" and (failed or summary.get("incomplete_reason")):
        issues.append("PASS contradicts failure/incompletion")
    if summary.get("status") == "FAIL" and not failed: issues.append("unexplained FAIL summary")
    if owned.get("exit_code") != {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}.get(summary.get("status")):
        issues.append("worker exit/summary mismatch")
    if not owned.get("owned_child_stopped"): issues.append("owned worker did not stop")
    if owned.get("supervisor_reason"): issues.append(owned["supervisor_reason"])
    attempts = summary.get("submitted_transformation_attempts")
    if type(attempts) is not int or not 0 <= attempts <= 2000:
        issues.append("invalid or unknown submitted-attempt count"); attempts = None
    reason = summary.get("incomplete_reason")
    if issues: reason = "; ".join(dict.fromkeys(([str(reason)] if reason else []) + issues))
    status = "FAIL" if failed or summary.get("status") == "FAIL" else "INCOMPLETE" if reason or summary.get("status") != "PASS" else "PASS"
    return {**summary, "schema": HARNESS_VERSION, "mode": mode, "status": status,
            "incomplete_reason": reason, "cases": records, "passed": passed, "failed": failed,
            "submitted_transformation_attempts": attempts if not issues else None,
            "audit_issues": issues, "interrupted_cases": list(pending)}
