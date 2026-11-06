#!/usr/bin/env python3
"""Deterministic admission, execution, verification and receipt control for New-MillBatch.ps1.

This is deliberately single-tool code. It never calls an LLM and does not grant its own authority.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", re.IGNORECASE)
REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
REQUIRED_SOURCE = (
    "New-MillBatch.ps1",
    "Update-MillManifest.ps1",
    "Test-MillBatch.ps1",
)
REQUIRED_TEMPLATES = (
    "SOURCE_INVENTORY.csv", "CLAIM_LEDGER.csv", "GATE_LEDGER.csv",
    "DECISION_LEDGER.csv", "VALIDATION_PLAN.csv", "LIVE_RESULTS.csv",
    "ERROR_LOG.md", "SENTINEL_REGISTRY.json", "REFERENCE_REGISTRY.json",
    "GLUE_LEDGER.csv", "README.md.tmpl", "DECISION.md.tmpl", "ROLLBACK.md.tmpl",
)
MAX_JSON_BYTES = 64 * 1024
MAX_CAPTURE_BYTES = 1024 * 1024
TOOL_TIMEOUT_SECONDS = 120


class ControllerError(Exception):
    pass


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path, maximum_bytes: int = MAX_JSON_BYTES) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        if len(raw) > maximum_bytes:
            raise ControllerError(f"JSON file exceeds {maximum_bytes} bytes: {path}")
        data = json.loads(raw.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ControllerError(f"Cannot read JSON {path}: {error}") from error
    if not isinstance(data, dict):
        raise ControllerError(f"JSON object required: {path}")
    return data


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def resolved(path_value: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise ControllerError("A nonempty path string is required.")
    # Match the Mill tool's GetFullPath behavior. Resolving links here can turn an
    # initially absent Windows path into a later 8.3 spelling during contention.
    return Path(os.path.abspath(os.path.expanduser(path_value)))


def is_within(child: Path, parent: Path) -> bool:
    try:
        child_text = os.path.normcase(os.path.normpath(str(child)))
        parent_text = os.path.normcase(os.path.normpath(str(parent)))
        if child_text == parent_text:
            return True
        if child.exists() and parent.exists() and os.path.samefile(child, parent):
            return True
        return os.path.commonpath((child_text, parent_text)) == parent_text
    except ValueError:
        return False


def same_path(left: Path, right: Path) -> bool:
    left_text = os.path.normcase(os.path.normpath(str(left)))
    right_text = os.path.normcase(os.path.normpath(str(right)))
    if left_text == right_text:
        return True
    try:
        return left.exists() and right.exists() and os.path.samefile(left, right)
    except OSError:
        return False


def tree_identity(tool_root: Path) -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    required = [tool_root / name for name in REQUIRED_SOURCE]
    required.extend(tool_root / "templates" / name for name in REQUIRED_TEMPLATES)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ControllerError("Required Mill source files are unavailable: " + "; ".join(missing))
    for path in sorted(required, key=lambda item: item.relative_to(tool_root).as_posix()):
        entries.append({"path": path.relative_to(tool_root).as_posix(), "sha256": digest_bytes(path.read_bytes())})
    return {"tool": "New-MillBatch.ps1", "root": str(tool_root), "files": entries,
            "sha256": digest_bytes(canonical(entries))}


def request_digest(request: dict[str, Any]) -> str:
    return digest_bytes(canonical(request))


def contains_nul(value: Any) -> bool:
    if isinstance(value, str):
        return "\x00" in value
    if isinstance(value, dict):
        return any(contains_nul(key) or contains_nul(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_nul(item) for item in value)
    return False


def derive(request: dict[str, Any]) -> tuple[Path, Path, str, list[str]]:
    issues: list[str] = []
    if len(canonical(request)) > MAX_JSON_BYTES:
        issues.append(f"request exceeds {MAX_JSON_BYTES} byte controller limit")
    if contains_nul(request):
        issues.append("request contains a NUL character")
    for name in ("request_id", "slug", "title", "scope", "date", "workspace_root"):
        if name not in request:
            issues.append(f"missing {name}")
    if issues:
        return Path("."), Path("."), "", issues
    request_id = request["request_id"]
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        issues.append("request_id must contain only letters, digits, dot, underscore or hyphen")
    slug = request["slug"]
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        issues.append("slug fails the declared Mill pattern")
    for name in ("title", "scope"):
        if not isinstance(request[name], str) or request[name] == "":
            issues.append(f"{name} must be a nonempty string")
    date_text = request["date"]
    if not isinstance(date_text, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        issues.append("date must have yyyy-MM-dd shape")
    else:
        try:
            dt.date.fromisoformat(date_text)
        except ValueError:
            issues.append("date is not a real calendar date")
    try:
        workspace_root = resolved(request["workspace_root"])
        output_value = request.get("output_root")
        mill_root = resolved(output_value) if isinstance(output_value, str) and output_value.strip() else workspace_root / "mill"
    except ControllerError as error:
        issues.append(str(error))
        return Path("."), Path("."), "", issues
    batch_id = f"{slug}-{date_text}" if isinstance(slug, str) and isinstance(date_text, str) else ""
    batch_path = mill_root / batch_id
    if not is_within(batch_path, mill_root):
        issues.append("derived batch path is outside the effective output root")
    return mill_root, batch_path, batch_id, issues


def initialize(state_root: Path) -> sqlite3.Connection:
    state_root.mkdir(parents=True, exist_ok=True)
    last_error: sqlite3.DatabaseError | None = None
    for attempt in range(20):
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(state_root / "controller.sqlite3", isolation_level=None, timeout=15)
            connection.execute("PRAGMA busy_timeout=15000")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.executescript("""
      CREATE TABLE IF NOT EXISTS operations (
        request_id TEXT PRIMARY KEY, request_digest TEXT NOT NULL, batch_path TEXT NOT NULL,
        phase TEXT NOT NULL, receipt_json TEXT NOT NULL, created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS leases (
        batch_path TEXT PRIMARY KEY, request_id TEXT NOT NULL UNIQUE, acquired_utc TEXT NOT NULL,
        FOREIGN KEY(request_id) REFERENCES operations(request_id)
      );
            """)
            return connection
        except sqlite3.DatabaseError as error:
            last_error = error
            if connection is not None:
                connection.close()
            if "locked" not in str(error).lower() or attempt == 19:
                break
            time.sleep(min(0.05 * (attempt + 1), 0.5))
    raise ControllerError(f"controller state store is unavailable: {last_error}") from last_error


def save_receipt(connection: sqlite3.Connection, state_root: Path, receipt: dict[str, Any], phase: str) -> None:
    request_id = receipt["request_id"]
    now = utcnow()
    payload = json.dumps(receipt, sort_keys=True)
    connection.execute("BEGIN IMMEDIATE")
    try:
        existing = connection.execute("SELECT request_digest FROM operations WHERE request_id=?", (request_id,)).fetchone()
        if existing and existing[0] != receipt["request_digest"]:
            raise ControllerError("request_id is already bound to different request content")
        if existing:
            connection.execute("UPDATE operations SET phase=?, receipt_json=?, updated_utc=? WHERE request_id=?",
                               (phase, payload, now, request_id))
        else:
            connection.execute("INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (request_id, receipt["request_digest"], receipt["derived"]["batch_path"], phase,
                                payload, now, now))
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise
    write_json(state_root / "receipts" / f"{request_id}.json", receipt)


def receipt_base(request: dict[str, Any], identity: dict[str, Any], derived_data: dict[str, str]) -> dict[str, Any]:
    return {"receipt_version": 1, "request_id": request.get("request_id", "invalid-request"),
            "request_digest": request_digest(request), "recorded_utc": utcnow(), "tool_identity": identity,
            "controller_identity": {"path": str(Path(__file__).resolve()), "sha256": digest_bytes(Path(__file__).read_bytes())},
            "derived": derived_data, "admission": "needs_facts", "creation_reported": "unknown",
            "artifact_verification": "not_run", "retained_state": "unknown", "authority": "recovery_pending",
            "next_permitted_action": "request_facts", "problems": [], "references": {}}


def check_authority(authority: dict[str, Any], request: dict[str, Any], identity: dict[str, Any], mill_root: Path) -> list[str]:
    problems: list[str] = []
    if len(canonical(authority)) > MAX_JSON_BYTES:
        problems.append(f"authority exceeds {MAX_JSON_BYTES} byte controller limit")
    if contains_nul(authority):
        problems.append("authority contains a NUL character")
    for name in ("authority_id", "authorized_by", "request_digest", "tool_identity_sha256", "allowed_output_roots"):
        if name not in authority:
            problems.append(f"authority missing {name}")
    if authority.get("request_digest") != request_digest(request):
        problems.append("authority request digest does not match")
    if authority.get("tool_identity_sha256") != identity["sha256"]:
        problems.append("authority tool identity does not match")
    roots = authority.get("allowed_output_roots")
    if not isinstance(roots, list) or not roots:
        problems.append("authority requires at least one allowed output root")
    else:
        try:
            if not any(is_within(mill_root, resolved(root)) for root in roots):
                problems.append("effective output root is not inside an authority-allowed root")
        except ControllerError as error:
            problems.append(str(error))
    return problems


def bounded_run(command: list[str], cwd: Path, timeout_seconds: float = TOOL_TIMEOUT_SECONDS) -> dict[str, Any]:
    """Run a subprocess without retaining more than one MiB from either output stream."""
    process = subprocess.Popen(command, text=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    captured: dict[str, bytearray] = {"stdout": bytearray(), "stderr": bytearray()}
    truncated = {"stdout": False, "stderr": False}

    def drain(name: str, stream: Any) -> None:
        while True:
            data = stream.read(65536)
            if not data:
                break
            capacity = MAX_CAPTURE_BYTES - len(captured[name])
            if capacity > 0:
                captured[name].extend(data[:capacity])
            if len(data) > capacity:
                truncated[name] = True

    workers = [threading.Thread(target=drain, args=("stdout", process.stdout), daemon=True),
               threading.Thread(target=drain, args=("stderr", process.stderr), daemon=True)]
    for worker in workers:
        worker.start()
    timed_out = False
    try:
        exit_code = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        exit_code = process.wait()
    for worker in workers:
        worker.join(timeout=5)
    process.stdout.close()
    process.stderr.close()
    return {"command": command, "exit_code": exit_code, "timed_out": timed_out,
            "stdout": captured["stdout"].decode("utf-8", errors="replace"),
            "stderr": captured["stderr"].decode("utf-8", errors="replace"),
            "stdout_truncated": truncated["stdout"], "stderr_truncated": truncated["stderr"]}


def execute(request: dict[str, Any], authority: dict[str, Any], tool_root: Path, state_root: Path,
            powershell: str, admit_only: bool = False) -> dict[str, Any]:
    identity = tree_identity(tool_root)
    mill_root, batch_path, batch_id, problems = derive(request)
    derived_data = {"effective_output_root": str(mill_root), "batch_path": str(batch_path), "batch_id": batch_id}
    receipt = receipt_base(request, identity, derived_data)
    try:
        connection = initialize(state_root)
    except ControllerError as error:
        receipt.update(admission="not_permitted", retained_state="unknown", authority="recovery_pending",
                       next_permitted_action="await_recovery_authority", problems=[str(error)])
        emergency_path = state_root / "emergency-receipts" / f"{receipt['request_id']}.json"
        write_json(emergency_path, receipt)
        receipt["references"]["emergency_receipt"] = str(emergency_path)
        return receipt
    try:
        if problems:
            receipt.update(admission="not_permitted", retained_state="none_observed", authority="create_only",
                           next_permitted_action="request_facts", problems=problems)
            save_receipt(connection, state_root, receipt, "not_permitted")
            return receipt
        problems = check_authority(authority, request, identity, mill_root)
        if problems:
            receipt.update(admission="not_permitted", retained_state="none_observed", authority="create_only",
                           next_permitted_action="request_facts", problems=problems)
            save_receipt(connection, state_root, receipt, "not_permitted")
            return receipt
        if batch_path.exists():
            receipt.update(admission="not_permitted", retained_state="partial_observed", authority="recovery_pending",
                           next_permitted_action="await_recovery_authority", problems=["derived batch path already exists"])
            save_receipt(connection, state_root, receipt, "not_permitted")
            return receipt
        if admit_only:
            lease = connection.execute("SELECT request_id FROM leases WHERE batch_path=?", (str(batch_path),)).fetchone()
            if lease:
                receipt.update(admission="not_permitted", retained_state="unknown", authority="recovery_pending",
                               next_permitted_action="await_recovery_authority", problems=[f"destination lease held by {lease[0]}"])
                save_receipt(connection, state_root, receipt, "lease_blocked")
                return receipt
            receipt.update(admission="permitted", retained_state="none_observed", authority="create_only",
                           next_permitted_action="invoke")
            save_receipt(connection, state_root, receipt, "admitted")
            return receipt
        connection.execute("BEGIN IMMEDIATE")
        try:
            lease = connection.execute("SELECT request_id FROM leases WHERE batch_path=?", (str(batch_path),)).fetchone()
            if lease:
                receipt.update(admission="not_permitted", retained_state="unknown", authority="recovery_pending",
                               next_permitted_action="await_recovery_authority", problems=[f"destination lease held by {lease[0]}"])
                connection.execute("COMMIT")
                save_receipt(connection, state_root, receipt, "lease_blocked")
                return receipt
            if batch_path.exists():
                receipt.update(admission="not_permitted", retained_state="partial_observed", authority="recovery_pending",
                               next_permitted_action="await_recovery_authority", problems=["derived batch path appeared before lease acquisition"])
                connection.execute("COMMIT")
                save_receipt(connection, state_root, receipt, "not_permitted")
                return receipt
            connection.execute("INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (receipt["request_id"], receipt["request_digest"], str(batch_path), "running",
                                json.dumps(receipt), utcnow(), utcnow()))
            connection.execute("INSERT INTO leases VALUES (?, ?, ?)", (str(batch_path), receipt["request_id"], utcnow()))
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        receipt.update(admission="permitted", authority="create_only", next_permitted_action="inspect")
        command = [powershell, "-NoProfile", "-File", str(tool_root / "New-MillBatch.ps1"),
                   "-WorkspaceRoot", request["workspace_root"], "-Slug", request["slug"],
                   "-Title", request["title"], "-Scope", request["scope"], "-Date", request["date"],
                   "-OutputRoot", str(mill_root), "-Owner", request.get("owner", "UNASSIGNED")]
        try:
            completed = bounded_run(command, tool_root)
        except OSError as error:
            raw_path = state_root / "raw" / f"{receipt['request_id']}.json"
            write_json(raw_path, {"command": command, "launch_error": str(error)})
            receipt["references"]["raw_process"] = str(raw_path)
            receipt.update(creation_reported="unknown", artifact_verification="not_run", retained_state="unknown",
                           authority="recovery_pending", next_permitted_action="await_recovery_authority",
                           problems=[f"controller could not launch the tool: {error}"])
            save_receipt(connection, state_root, receipt, "recovery_pending")
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM leases WHERE request_id=?", (receipt["request_id"],))
            connection.execute("COMMIT")
            return receipt
        raw = completed
        raw_path = state_root / "raw" / f"{receipt['request_id']}.json"
        write_json(raw_path, raw)
        receipt["references"]["raw_process"] = str(raw_path)
        reported: dict[str, Any] | None = None
        if not completed["timed_out"] and completed["exit_code"] == 0:
            try:
                reported = json.loads(completed["stdout"])
            except json.JSONDecodeError:
                receipt["problems"].append("tool exited zero but did not emit one JSON result")
        if reported and reported.get("result") == "BATCH_CREATED" and same_path(resolved(reported.get("batch_path", "")), batch_path):
            receipt["creation_reported"] = "true"
            validator = bounded_run([powershell, "-NoProfile", "-File", str(tool_root / "Test-MillBatch.ps1"),
                                     "-BatchPath", str(batch_path)], tool_root)
            validation_raw = validator
            validation_path = state_root / "raw" / f"{receipt['request_id']}.validation.json"
            write_json(validation_path, validation_raw)
            receipt["references"]["structural_validation"] = str(validation_path)
            receipt["artifact_verification"] = "pass" if not validator["timed_out"] and validator["exit_code"] == 0 else "fail"
            receipt["retained_state"] = "none_observed" if receipt["artifact_verification"] == "pass" else "partial_observed"
            receipt["authority"] = "promotion_pending"
            receipt["next_permitted_action"] = "none" if receipt["artifact_verification"] == "pass" else "await_recovery_authority"
            if receipt["artifact_verification"] != "pass":
                receipt["problems"].append("structural validation failed")
        else:
            receipt["creation_reported"] = "false" if completed["exit_code"] else "unknown"
            receipt["artifact_verification"] = "not_run"
            receipt["retained_state"] = "partial_observed" if batch_path.exists() else "unknown"
            receipt["authority"] = "recovery_pending"
            receipt["next_permitted_action"] = "await_recovery_authority"
            receipt["problems"].append("tool did not return a matching BATCH_CREATED result")
        phase = "complete" if receipt["artifact_verification"] == "pass" else "recovery_pending"
        save_receipt(connection, state_root, receipt, phase)
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM leases WHERE request_id=?", (receipt["request_id"],))
        connection.execute("COMMIT")
        return receipt
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-root", required=True, type=Path)
    parser.add_argument("--state-root", required=True, type=Path)
    parser.add_argument("--powershell", default="pwsh")
    parser.add_argument("--admit-only", action="store_true", help="perform deterministic admission without invoking Mill")
    parser.add_argument("request", type=Path)
    parser.add_argument("authority", type=Path)
    args = parser.parse_args()
    try:
        receipt = execute(load_json(args.request), load_json(args.authority), args.tool_root.resolve(), args.state_root.resolve(), args.powershell, args.admit_only)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["admission"] == "permitted" and (args.admit_only or receipt["artifact_verification"] == "pass") else 2
    except ControllerError as error:
        print(json.dumps({"controller_error": str(error)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
