#!/usr/bin/env python3
"""xOSG-0 consolidated local runtime — v0.5.0.

Standard-library-only stateful workspace runtime for the xOSG-0 overlay.
It is intentionally bounded: no hidden agents, privilege escalation, external
account access, or fabricated execution claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
STATE = WORKSPACE / "runtime_state.json"
REG = WORKSPACE / "registers.json"
JOURNAL = WORKSPACE / ".transaction.json"
LOCK = WORKSPACE / ".runtime.lock"
MACHINE = ROOT / "machine" / "xOSG-0_machine_v1.2.0.json"

REVISION = "0.5.0"
PIPELINE = ["INTAKE", "DECOMPOSE", "ASSIGN", "EXECUTE", "RECONCILE", "VERIFY", "DELIVER", "LOG"]
STATES = ["IDLE", *PIPELINE, "BLOCKED"]
REGISTERS = ["NOTES", "TODO", "ERROR-LOG", "AGENDA", "ROADMAP"]
VERIFICATION_STATUSES = {"NOT_RUN", "PASS", "FAIL"}
MAX_OBJECTIVE_CHARS = 16384
MAX_JSON_BYTES = 1024 * 1024
MAX_HISTORY = 512
LOCK_TIMEOUT_SECONDS = 0.75
LOCK_STALE_SECONDS = 30.0

ALLOWED_TRANSITIONS = {
    "IDLE": {"INTAKE"},
    "INTAKE": {"DECOMPOSE", "BLOCKED", "IDLE"},
    "DECOMPOSE": {"ASSIGN", "BLOCKED", "INTAKE", "IDLE"},
    "ASSIGN": {"EXECUTE", "BLOCKED", "INTAKE", "IDLE"},
    "EXECUTE": {"RECONCILE", "BLOCKED", "INTAKE", "IDLE"},
    "RECONCILE": {"VERIFY", "BLOCKED", "INTAKE", "IDLE"},
    "VERIFY": {"DELIVER", "RECONCILE", "BLOCKED", "INTAKE", "IDLE"},
    "DELIVER": {"LOG", "INTAKE", "IDLE"},
    "LOG": {"IDLE", "INTAKE"},
    "BLOCKED": {"IDLE", "INTAKE", "DECOMPOSE"},
}


class XOSGError(Exception):
    code = "XOSG_ERROR"


class DataCorruptionError(XOSGError):
    code = "DATA_CORRUPTION"


class ValidationError(XOSGError):
    code = "VALIDATION_ERROR"


class LockTimeoutError(XOSGError):
    code = "LOCK_TIMEOUT"


@dataclass
class LoadResult:
    ok: bool
    data: Any = None
    code: str | None = None
    detail: str | None = None


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def provenance(source: str, actor: str, claim_type: str) -> dict[str, str]:
    return {"source": source, "timestamp": now(), "actor": actor, "claim_type": claim_type}


def _check_regular_file(path: Path, *, may_absent: bool = True) -> None:
    if not path.exists() and may_absent:
        return
    if path.is_symlink():
        raise DataCorruptionError(f"refusing symlink: {path.name}")
    if path.exists() and not path.is_file():
        raise DataCorruptionError(f"not a regular file: {path.name}")


def load_json(path: Path, *, required: bool = False) -> LoadResult:
    try:
        _check_regular_file(path, may_absent=not required)
        if not path.exists():
            return LoadResult(False, code="MISSING", detail=f"{path.name} missing")
        size = path.stat().st_size
        if size > MAX_JSON_BYTES:
            return LoadResult(False, code="OVERSIZE", detail=f"{path.name} exceeds {MAX_JSON_BYTES} bytes")
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            return LoadResult(False, code="BOM", detail=f"{path.name} contains UTF-8 BOM")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            return LoadResult(False, code="ENCODING", detail=f"{path.name}: {e}")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            return LoadResult(False, code="MALFORMED_JSON", detail=f"{path.name}: {e.msg} at line {e.lineno} column {e.colno}")
        return LoadResult(True, data=data)
    except XOSGError as e:
        return LoadResult(False, code=e.code, detail=str(e))
    except OSError as e:
        return LoadResult(False, code="IO_ERROR", detail=f"{path.name}: {e}")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _check_regular_file(path, may_absent=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        try:
            dirfd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except (AttributeError, OSError):
            pass
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def save_json(path: Path, obj: Any) -> None:
    encoded = (json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise ValidationError(f"serialized {path.name} exceeds {MAX_JSON_BYTES} bytes")
    _atomic_write(path, encoded)


def _journal_payload(state: dict[str, Any], regs: dict[str, Any]) -> dict[str, Any]:
    body = {"revision": REVISION, "created_at": now(), "state": state, "registers": regs}
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**body, "sha256": hashlib.sha256(canonical).hexdigest()}


def _verify_journal(j: dict[str, Any]) -> bool:
    if not isinstance(j, dict) or not isinstance(j.get("sha256"), str):
        return False
    body = {k: v for k, v in j.items() if k != "sha256"}
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest() == j["sha256"]


def commit_pair(state: dict[str, Any], regs: dict[str, Any]) -> None:
    journal = _journal_payload(state, regs)
    save_json(JOURNAL, journal)
    save_json(STATE, state)
    save_json(REG, regs)
    try:
        JOURNAL.unlink()
    except FileNotFoundError:
        pass


def recover_if_needed() -> tuple[bool, str | None]:
    if not JOURNAL.exists():
        return False, None
    r = load_json(JOURNAL, required=True)
    if not r.ok:
        raise DataCorruptionError(f"transaction journal unreadable: {r.code}: {r.detail}")
    if not _verify_journal(r.data):
        raise DataCorruptionError("transaction journal checksum mismatch")
    state = r.data.get("state")
    regs = r.data.get("registers")
    state_errors = validate_state_obj(state)
    reg_errors = validate_registers_obj(regs)
    if state_errors or reg_errors:
        raise DataCorruptionError("transaction journal contains invalid state/registers")
    save_json(STATE, state)
    save_json(REG, regs)
    JOURNAL.unlink(missing_ok=True)
    return True, "recovered incomplete transaction"


@contextmanager
def runtime_lock(timeout: float = LOCK_TIMEOUT_SECONDS):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    while True:
        if LOCK.is_symlink():
            raise DataCorruptionError("refusing symlink lock file")
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps({"pid": os.getpid(), "created_at": time.time()}) + "\n")
            break
        except FileExistsError:
            try:
                age = time.time() - LOCK.stat().st_mtime
                if age > LOCK_STALE_SECONDS:
                    LOCK.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise LockTimeoutError("runtime mutation lock timed out")
            time.sleep(0.025)
    try:
        yield
    finally:
        try:
            if not LOCK.is_symlink():
                LOCK.unlink(missing_ok=True)
        except OSError:
            pass


def default_state() -> dict[str, Any]:
    return {
        "system": "xOSG-0",
        "artifact_revision": REVISION,
        "state": "IDLE",
        "task": None,
        "verification": {"status": "NOT_RUN", "checks": []},
        "last_transition": None,
        "history": [],
    }


def default_registers() -> dict[str, list[Any]]:
    return {k: [] for k in REGISTERS}


def validate_state_obj(state: Any) -> list[str]:
    e: list[str] = []
    if not isinstance(state, dict):
        return ["STATE_TYPE: runtime state root must be an object"]
    if state.get("system") != "xOSG-0":
        e.append("STATE_SYSTEM: system must equal xOSG-0")
    if not isinstance(state.get("artifact_revision"), str):
        e.append("STATE_REVISION: artifact_revision must be string")
    st = state.get("state")
    if st not in STATES:
        e.append("STATE_ENUM: invalid state")
    ver = state.get("verification")
    if not isinstance(ver, dict):
        e.append("STATE_VERIFICATION_TYPE: verification must be object")
    else:
        if ver.get("status") not in VERIFICATION_STATUSES:
            e.append("STATE_VERIFICATION_STATUS: invalid verification status")
        if not isinstance(ver.get("checks", []), list):
            e.append("STATE_VERIFICATION_CHECKS: checks must be list")
        if ver.get("status") == "PASS" and st not in {"VERIFY", "DELIVER", "LOG"}:
            e.append("STATE_VERIFICATION_GATE: PASS incompatible with current state")
    hist = state.get("history")
    if not isinstance(hist, list):
        e.append("STATE_HISTORY_TYPE: history must be list")
    elif len(hist) > MAX_HISTORY:
        e.append("STATE_HISTORY_BOUND: history exceeds bound")
    return e


def validate_registers_obj(regs: Any) -> list[str]:
    if not isinstance(regs, dict):
        return ["REG_ROOT_TYPE: register store must be object"]
    e: list[str] = []
    if set(regs) != set(REGISTERS):
        e.append("REG_SET: register set mismatch")
    for name in REGISTERS:
        if name in regs and not isinstance(regs[name], list):
            e.append(f"REG_TYPE:{name}: register must be list")
    return e


def transition(state: dict[str, Any], new: str, *, reason: str = "workflow") -> None:
    old = state.get("state")
    if old not in ALLOWED_TRANSITIONS or new not in ALLOWED_TRANSITIONS[old]:
        raise ValidationError(f"illegal transition {old!r} -> {new!r}")
    record = {"from": old, "to": new, "timestamp": now(), "reason": reason}
    state["state"] = new
    state["last_transition"] = record
    history = state.setdefault("history", [])
    if not isinstance(history, list):
        raise ValidationError("history is not a list")
    history.append(record)
    if len(history) > MAX_HISTORY:
        del history[:-MAX_HISTORY]


def _load_workspace_or_raise() -> tuple[dict[str, Any], dict[str, Any]]:
    recover_if_needed()
    sr, rr = load_json(STATE, required=True), load_json(REG, required=True)
    if not sr.ok:
        raise DataCorruptionError(f"runtime state unavailable: {sr.code}: {sr.detail}")
    if not rr.ok:
        raise DataCorruptionError(f"register store unavailable: {rr.code}: {rr.detail}")
    se, re = validate_state_obj(sr.data), validate_registers_obj(rr.data)
    if se or re:
        raise DataCorruptionError("; ".join(se + re))
    return sr.data, rr.data


def initialize(*, quiet: bool = False) -> None:
    with runtime_lock():
        commit_pair(default_state(), default_registers())
    if not quiet:
        print("initialized xOSG-0 runtime workspace")


def accept_task(text: str) -> None:
    if not isinstance(text, str):
        raise ValidationError("task objective must be text")
    if len(text) > MAX_OBJECTIVE_CHARS:
        raise ValidationError(f"task objective exceeds {MAX_OBJECTIVE_CHARS} characters")
    with runtime_lock():
        if not STATE.exists() and not REG.exists():
            commit_pair(default_state(), default_registers())
        state, regs = _load_workspace_or_raise()
        if state["state"] != "IDLE":
            if "INTAKE" not in ALLOWED_TRANSITIONS.get(state["state"], set()):
                transition(state, "IDLE", reason="new_task_reset")
        transition(state, "INTAKE", reason="task_received")
        state["task"] = {
            "objective": text,
            "requested_at": now(),
            "status": "REQUESTED",
            "provenance": provenance("user_request", "user", "action"),
        }
        state["verification"] = {"status": "NOT_RUN", "checks": []}
        regs["AGENDA"].append({"objective": text, "next_action": "decompose", "open_questions": [], "timestamp": now()})
        regs["NOTES"].append({
            "type": "context",
            "content": "Task received; intake does not imply external execution.",
            "timestamp": now(),
            "provenance": provenance("runtime", "assistant", "fact"),
        })
        transition(state, "DECOMPOSE", reason="intake_complete")
        commit_pair(state, regs)
    print("task accepted: INTAKE -> DECOMPOSE")
    print("No external action was executed.")


def status() -> int:
    try:
        recovered, note = recover_if_needed()
    except XOSGError as e:
        print(json.dumps({"status": "INVALID", "code": e.code, "detail": str(e)}, indent=2))
        return 1
    sr, rr = load_json(STATE), load_json(REG)
    if not sr.ok or not rr.ok:
        print(json.dumps({
            "status": "INVALID",
            "state_error": None if sr.ok else {"code": sr.code, "detail": sr.detail},
            "register_error": None if rr.ok else {"code": rr.code, "detail": rr.detail},
        }, indent=2))
        return 1
    errs = validate_state_obj(sr.data) + validate_registers_obj(rr.data)
    out = {
        "status": "VALID" if not errs else "INVALID",
        "recovery": note if recovered else None,
        "runtime": sr.data,
        "register_counts": {k: len(v) if isinstance(v, list) else None for k, v in rr.data.items()} if isinstance(rr.data, dict) else {},
        "errors": errs,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if not errs else 1


def validate() -> int:
    errors: list[str] = []
    try:
        recovered, note = recover_if_needed()
        if recovered and note:
            print(f"RECOVERY: {note}")
    except XOSGError as e:
        errors.append(f"JOURNAL:{e.code}: {e}")

    sr, rr, mr = load_json(STATE), load_json(REG), load_json(MACHINE, required=True)
    if not sr.ok:
        errors.append(f"STATE_LOAD:{sr.code}: {sr.detail}")
    else:
        errors.extend(validate_state_obj(sr.data))
    if not rr.ok:
        errors.append(f"REG_LOAD:{rr.code}: {rr.detail}")
    else:
        errors.extend(validate_registers_obj(rr.data))
    if not mr.ok:
        errors.append(f"MACHINE_LOAD:{mr.code}: {mr.detail}")
    elif not isinstance(mr.data, dict) or mr.data.get("system", {}).get("id") != "xOSG-0":
        errors.append("MACHINE_SCHEMA: machine configuration identity invalid")

    print("VALID" if not errors else "INVALID")
    for e in errors:
        print(" -", e)
    return 0 if not errors else 1


def recover_command() -> int:
    try:
        recovered, note = recover_if_needed()
        print(note if recovered else "no recovery needed")
        return 0
    except XOSGError as e:
        print(f"INVALID - {e.code}: {e}")
        return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="xosg")
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("init")
    s.add_parser("status")
    t = s.add_parser("task")
    t.add_argument("text")
    s.add_parser("validate")
    s.add_parser("recover")
    a = p.parse_args(argv)
    try:
        if a.cmd == "init":
            initialize(); return 0
        if a.cmd == "status":
            return status()
        if a.cmd == "task":
            accept_task(a.text); return 0
        if a.cmd == "validate":
            return validate()
        if a.cmd == "recover":
            return recover_command()
    except XOSGError as e:
        print(f"ERROR [{e.code}]: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
