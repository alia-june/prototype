#!/usr/bin/env python3
"""Deterministic receipt controller for the unchanged Mill Test-MillBatch.ps1 tool.

This deliberately controls one read-only verification operation.  It never calls
an LLM, does not alter a Mill batch, and does not grant authority.
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

REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
MAX_JSON_BYTES = 64 * 1024
MAX_CAPTURE_BYTES = 1024 * 1024
TOOL_TIMEOUT_SECONDS = 120
SOURCE_FILES = ("Test-MillBatch.ps1", "Update-MillManifest.ps1")
SQLITE_INITIALIZE_ATTEMPTS = 20
SQLITE_INITIALIZE_RETRY_SECONDS = 0.05


class ControllerError(Exception):
    """Raised where a controller boundary cannot be established."""


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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


def resolve_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ControllerError("A nonempty path string is required.")
    return Path(os.path.abspath(os.path.expanduser(value)))


def same_path(left: Path, right: Path) -> bool:
    if os.path.normcase(os.path.normpath(str(left))) == os.path.normcase(os.path.normpath(str(right))):
        return True
    try:
        return left.exists() and right.exists() and os.path.samefile(left, right)
    except OSError:
        return False


def is_within(child: Path, parent: Path) -> bool:
    try:
        child_text = os.path.normcase(os.path.normpath(str(child)))
        parent_text = os.path.normcase(os.path.normpath(str(parent)))
        return child_text == parent_text or os.path.commonpath((child_text, parent_text)) == parent_text
    except ValueError:
        return False


def load_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_JSON_BYTES:
            raise ControllerError(f"JSON file exceeds {MAX_JSON_BYTES} bytes: {path}")
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ControllerError(f"Cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ControllerError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def source_identity(tool_root: Path) -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    for name in SOURCE_FILES:
        path = tool_root / name
        if not path.is_file():
            raise ControllerError(f"Required Mill source file is unavailable: {path}")
        entries.append({"path": name, "sha256": digest_bytes(path.read_bytes())})
    return {
        "tool": "Test-MillBatch.ps1",
        "root": str(tool_root),
        "files": entries,
        "sha256": digest_bytes(canonical(entries)),
    }


def derive_request(request: dict[str, Any]) -> tuple[str, Path, list[str]]:
    problems: list[str] = []
    if len(canonical(request)) > MAX_JSON_BYTES:
        problems.append(f"request exceeds {MAX_JSON_BYTES} byte controller limit")
    if contains_nul(request):
        problems.append("request contains a NUL character")
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        problems.append("request_id must contain only letters, digits, dot, underscore or hyphen")
        request_id = "UNUSABLE_REQUEST_ID"
    batch_value = request.get("batch_path")
    try:
        batch_path = resolve_path(batch_value)
    except ControllerError as error:
        problems.append(str(error))
        batch_path = Path(".")
    return request_id, batch_path, problems


def validate_authority(
    authority: dict[str, Any], request: dict[str, Any], identity: dict[str, Any], batch_path: Path
) -> list[str]:
    problems: list[str] = []
    if len(canonical(authority)) > MAX_JSON_BYTES:
        problems.append(f"authority exceeds {MAX_JSON_BYTES} byte controller limit")
    if contains_nul(authority):
        problems.append("authority contains a NUL character")
    if not isinstance(authority.get("authority_id"), str) or not authority["authority_id"]:
        problems.append("authority_id is required")
    if not isinstance(authority.get("authorized_by"), str) or not authority["authorized_by"]:
        problems.append("authorized_by is required")
    if authority.get("request_digest") != request_digest(request):
        problems.append("authority does not bind this complete request digest")
    if authority.get("tool_identity_sha256") != identity["sha256"]:
        problems.append("authority tool identity does not match the current Mill verifier source")
    roots = authority.get("allowed_batch_roots")
    if not isinstance(roots, list) or not roots:
        problems.append("authority must declare one or more allowed_batch_roots")
    else:
        parsed: list[Path] = []
        for root in roots:
            try:
                parsed.append(resolve_path(root))
            except ControllerError:
                problems.append("authority has an invalid allowed batch root")
        if parsed and not any(is_within(batch_path, root) for root in parsed):
            problems.append("batch path is outside every authorized batch root")
    return problems


def initialize(state_root: Path) -> sqlite3.Connection:
    state_root.mkdir(parents=True, exist_ok=True)
    for attempt in range(SQLITE_INITIALIZE_ATTEMPTS):
        connection = sqlite3.connect(state_root / "controller.sqlite3", timeout=5, isolation_level=None)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=5000")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS operations (request_id TEXT PRIMARY KEY, request_digest TEXT NOT NULL, "
                "batch_path TEXT NOT NULL, status TEXT NOT NULL, receipt_json TEXT NOT NULL, created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL)"
            )
            connection.execute("CREATE TABLE IF NOT EXISTS leases (batch_path TEXT PRIMARY KEY, holder_request_id TEXT NOT NULL, acquired_utc TEXT NOT NULL)")
            return connection
        except sqlite3.OperationalError as error:
            connection.close()
            if "locked" not in str(error).lower() or attempt + 1 == SQLITE_INITIALIZE_ATTEMPTS:
                raise
            time.sleep(SQLITE_INITIALIZE_RETRY_SECONDS * (attempt + 1))
        except Exception:
            connection.close()
            raise


def receipt_base(request_id: str, digest: str, identity: dict[str, Any], batch_path: Path) -> dict[str, Any]:
    return {
        "receipt_schema": "mill-batch-verification-controller/v1",
        "receipt_id": uuid.uuid4().hex,
        "recorded_utc": utcnow(),
        "request_id": request_id,
        "request_digest": digest,
        "derived": {"batch_path": str(batch_path)},
        "tool_identity": identity,
        "admission": "not_permitted",
        "process": {"launched": False, "exit_code": None, "timed_out": False, "stdout": "", "stderr": "", "stdout_truncated": False, "stderr_truncated": False},
        "validator": {"reported_result": "not_run", "report": None},
        "retained_state": "none_observed",
        "authority": "assertion_not_accepted",
        "next_permitted_action": "correct_request_or_authority",
        "problems": [],
        "limitations": [
            "The authority assertion is local controller input, not user approval or cryptographic authorization.",
            "A PASS proves only the existing Mill validator's structure and internal-consistency checks at the observed time.",
            "The controller does not prevent direct batch changes or direct Mill invocation outside this controller.",
        ],
    }


def _reader(stream: Any, target: bytearray, truncated: list[bool]) -> None:
    while True:
        chunk = stream.read(65536)
        if not chunk:
            return
        remaining = MAX_CAPTURE_BYTES - len(target)
        if remaining > 0:
            target.extend(chunk[:remaining])
        if len(chunk) > remaining:
            truncated[0] = True


def bounded_run(command: list[str], cwd: Path, timeout: float = TOOL_TIMEOUT_SECONDS) -> dict[str, Any]:
    try:
        process = subprocess.Popen(command, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as error:
        return {"launched": False, "launch_error": str(error), "exit_code": None, "timed_out": False, "stdout": "", "stderr": "", "stdout_truncated": False, "stderr_truncated": False}
    stdout, stderr, stdout_truncated, stderr_truncated = bytearray(), bytearray(), [False], [False]
    readers = [
        threading.Thread(target=_reader, args=(process.stdout, stdout, stdout_truncated), daemon=True),
        threading.Thread(target=_reader, args=(process.stderr, stderr, stderr_truncated), daemon=True),
    ]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()
    for reader in readers:
        reader.join(timeout=2)
    process.stdout.close()
    process.stderr.close()
    return {
        "launched": True,
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "stdout": stdout.decode("utf-8", errors="replace"),
        "stderr": stderr.decode("utf-8", errors="replace"),
        "stdout_truncated": stdout_truncated[0],
        "stderr_truncated": stderr_truncated[0],
    }


def parse_report(stdout: str) -> dict[str, Any] | None:
    stripped = stdout.strip()
    candidates = [stripped] + list(reversed([line.strip() for line in stdout.splitlines() if line.strip()]))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "result" in parsed:
            return parsed
    return None


def persist(connection: sqlite3.Connection, receipt: dict[str, Any], status: str, new: bool) -> None:
    now = utcnow()
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    if new:
        connection.execute(
            "INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)",
            (receipt["request_id"], receipt["request_digest"], receipt["derived"]["batch_path"], status, encoded, now, now),
        )
    else:
        connection.execute(
            "UPDATE operations SET status = ?, receipt_json = ?, updated_utc = ? WHERE request_id = ?",
            (status, encoded, now, receipt["request_id"]),
        )
    write_json(Path(connection.execute("PRAGMA database_list").fetchone()[2]).parent / "receipts" / f"{receipt['request_id']}.json", receipt)


def emergency(state_root: Path, receipt: dict[str, Any], problem: str) -> dict[str, Any]:
    receipt["problems"].append(problem)
    receipt["retained_state"] = "emergency_receipt_retained"
    receipt["next_permitted_action"] = "await_recovery_authority"
    try:
        write_json(state_root / "emergency-receipts" / f"{receipt['request_id']}.json", receipt)
    except OSError:
        pass
    return receipt


def execute(request: dict[str, Any], authority: dict[str, Any], tool_root: Path, state_root: Path, powershell: str) -> dict[str, Any]:
    identity = source_identity(tool_root)
    request_id, batch_path, request_problems = derive_request(request)
    digest = request_digest(request)
    receipt = receipt_base(request_id, digest, identity, batch_path)
    problems = request_problems + validate_authority(authority, request, identity, batch_path)
    try:
        connection = initialize(state_root)
    except (OSError, sqlite3.Error) as error:
        return emergency(state_root, receipt, f"controller state is unavailable: {error}")
    try:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute("SELECT request_digest, receipt_json FROM operations WHERE request_id = ?", (request_id,)).fetchone()
        if existing:
            connection.execute("COMMIT")
            if existing[0] == digest:
                prior = json.loads(existing[1])
                prior["replayed_request"] = True
                return prior
            receipt["problems"].append("request_id is already bound to a different request digest")
            receipt["retained_state"] = "prior_request_preserved"
            receipt["next_permitted_action"] = "use_a_new_request_id_with_fresh_authority"
            return receipt
        if problems:
            receipt["problems"].extend(problems)
            persist(connection, receipt, "not_permitted", True)
            connection.execute("COMMIT")
            return receipt
        held = connection.execute("SELECT holder_request_id FROM leases WHERE batch_path = ?", (str(batch_path),)).fetchone()
        if held:
            receipt["problems"].append(f"verification lease held by request: {held[0]}")
            receipt["retained_state"] = "lease_preserved"
            receipt["next_permitted_action"] = "await_recovery_authority"
            persist(connection, receipt, "blocked", True)
            connection.execute("COMMIT")
            return receipt
        connection.execute("INSERT INTO leases VALUES (?, ?, ?)", (str(batch_path), request_id, utcnow()))
        receipt["admission"] = "permitted"
        receipt["authority"] = "assertion_accepted_for_verification_only"
        receipt["next_permitted_action"] = "invoke_existing_validator"
        persist(connection, receipt, "running", True)
        connection.execute("COMMIT")
    except (sqlite3.Error, OSError) as error:
        try:
            connection.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        return emergency(state_root, receipt, f"controller state transaction failed: {error}")
    finally:
        connection.close()

    process = bounded_run([powershell, "-NoProfile", "-NonInteractive", "-File", str(tool_root / "Test-MillBatch.ps1"), "-BatchPath", str(batch_path)], tool_root)
    report = parse_report(process["stdout"])
    receipt["process"] = process
    receipt["validator"] = {"reported_result": report.get("result", "unknown") if report else "unknown", "report": report}
    if report and report.get("result") == "PASS" and process["exit_code"] == 0 and not process["timed_out"]:
        receipt["retained_state"] = "receipt_retained"
        receipt["next_permitted_action"] = "await_user_review"
        status = "pass"
    elif report and report.get("result") == "FAIL":
        receipt["retained_state"] = "receipt_retained"
        receipt["next_permitted_action"] = "review_validator_failures"
        status = "fail"
    else:
        receipt["retained_state"] = "receipt_retained"
        receipt["next_permitted_action"] = "await_recovery_authority"
        if process.get("launch_error"):
            receipt["problems"].append(f"validator launch failed: {process['launch_error']}")
        elif process["timed_out"]:
            receipt["problems"].append("validator timed out before a reliable result was established")
        else:
            receipt["problems"].append("validator did not produce a reliable structured result")
        status = "unknown"

    try:
        connection = initialize(state_root)
        connection.execute("BEGIN IMMEDIATE")
        persist(connection, receipt, status, False)
        connection.execute("DELETE FROM leases WHERE batch_path = ? AND holder_request_id = ?", (str(batch_path), request_id))
        connection.execute("COMMIT")
        connection.close()
    except (sqlite3.Error, OSError) as error:
        try:
            connection.execute("ROLLBACK")
            connection.close()
        except (sqlite3.Error, UnboundLocalError):
            pass
        return emergency(state_root, receipt, f"post-validation retention failed: {error}")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-root", required=True, type=Path)
    parser.add_argument("--state-root", required=True, type=Path)
    parser.add_argument("--powershell", default="pwsh")
    parser.add_argument("request", type=Path)
    parser.add_argument("authority", type=Path)
    arguments = parser.parse_args()
    try:
        receipt = execute(load_json(arguments.request), load_json(arguments.authority), arguments.tool_root.resolve(), arguments.state_root.resolve(), arguments.powershell)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["admission"] == "permitted" and receipt["validator"]["reported_result"] == "PASS" else 2
    except ControllerError as error:
        print(json.dumps({"controller_error": str(error)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
