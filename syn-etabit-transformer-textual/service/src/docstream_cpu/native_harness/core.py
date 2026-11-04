"""Closed replay data, pre-execution evidence, explicit budgets and outcomes."""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import re
import threading
import time
import traceback

from . import HARNESS_VERSION

SERVICE = Path(__file__).resolve().parents[3]
WORKSPACE = SERVICE.parent
RUNS = WORKSPACE / ".docstream" / "native-harness-runs"
SCHEMA = "docstream.native-harness.case/1"
MODES = ("hardening", "fuzzy-error", "torture")
FAMILIES = ("error", "valid", "probe", "scenario")
ERROR_CODES = {"VALIDATION_ERROR", "UNKNOWN_REFERENCE", "LAYER_MISMATCH", "LIMIT_EXCEEDED",
               "UNKNOWN_STREAM", "UNKNOWN_BATCH", "INVALID_PATH", "INVALID_RANGE", "DUPLICATE_OPERATION"}


class CheckFailed(AssertionError):
    def __init__(self, tag, message, **details):
        self.tag, self.details = tag, details
        super().__init__(message)


class Incomplete(RuntimeError):
    pass


def check(condition, tag, message, **details):
    if not condition:
        raise CheckFailed(tag, message, **details)


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(value):
    return sha256(encoded(value)).hexdigest()


def save(path, value, *, new=True):
    with Path(path).open("xb" if new else "wb") as target:
        target.write(encoded(value) + b"\n")


def footprint(root):
    total = 0
    for p in Path(root).rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def reject_link(path):
    p = Path(path).absolute()
    for parent in (p, *p.parents):
        if parent.exists():
            st = parent.lstat()
            if parent.is_symlink() or getattr(st, "st_file_attributes", 0) & 0x400:
                raise ValueError("linked or reparse-point evidence paths are not supported")


def validate_case(case):
    expected_keys = {"schema", "case_id", "mode", "family", "seed", "input", "expected"}
    if type(case) is not dict or set(case) != expected_keys or case["schema"] != SCHEMA:
        raise ValueError("invalid native replay schema")
    if type(case["case_id"]) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", case["case_id"]):
        raise ValueError("invalid case ID")
    if case["mode"] not in MODES or case["family"] not in FAMILIES:
        raise ValueError("unknown mode or replay family")
    if type(case["seed"]) is not int or not 0 <= case["seed"] <= 0xFFFFFFFF:
        raise ValueError("invalid seed")
    if type(case["input"]) is not dict or type(case["expected"]) is not dict:
        raise ValueError("case input/expected must be objects")
    expected = case["expected"]
    if case["family"] == "error":
        if set(expected) != {"exception", "code"} or expected["exception"] not in ("NativeError", "TypeError"):
            raise ValueError("invalid expected rejection")
        if expected["exception"] == "NativeError" and expected["code"] not in ERROR_CODES:
            raise ValueError("unknown expected NativeError code")
        if expected["exception"] == "TypeError" and expected["code"] is not None:
            raise ValueError("TypeError has no NativeError code")
        if case["mode"] not in ("hardening", "fuzzy-error"):
            raise ValueError("error family/mode mismatch")
    elif expected != {"outcome": "pass"}:
        raise ValueError("invalid positive expectation")
    if case["family"] == "scenario" and case["mode"] != "torture":
        raise ValueError("scenario/mode mismatch")
    if case["family"] == "probe" and case["mode"] != "hardening":
        raise ValueError("probe/mode mismatch")
    # Family-specific names and input fields are checked before dispatch too.
    from .cases import validate_input
    validate_input(case)
    if len(encoded(case)) > 2 * 1024 * 1024:
        raise ValueError("replay case exceeds 2 MiB")
    return case


def load_case(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("replay requires a file of at most 2 MiB")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate replay JSON key")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                       parse_constant=lambda text: (_ for _ in ()).throw(ValueError("non-finite JSON literal")))
    return validate_case(value)


def fingerprint(model):
    """White-box state audit: content, ancestry, requests, derived accounts and counters."""
    with model._lock:
        s = model._state
        return digest({"definitions": {key: value.to_record() for key, value in s.definitions.items()},
            "lengths": dict(s.lengths), "costs": dict(s.costs),
            "streams": {key: asdict(value) for key, value in s.streams.items()},
            "batches": {key: asdict(value) for key, value in s.batches.items()},
            "slots": s.reference_slots, "next_stream": s.next_stream, "next_batch": s.next_batch})


class Budget:
    def __init__(self, seconds=900, max_bytes=512 * 1024 * 1024, max_attempts=2000):
        self.started = time.monotonic()
        self.deadline = self.started + seconds
        self.max_bytes = max_bytes
        self.max_attempts = max_attempts
        self.attempts = 0
        self.lock = threading.Lock()

    def tick(self):
        if time.monotonic() >= self.deadline:
            raise Incomplete("worker wall-clock budget reached")

    def apply(self, model, base, operations):
        self.tick()
        # Empty/malformed submissions count as at least one attempt. No credit
        # is refunded when validation rejects a submitted batch.
        amount = max(1, len(operations)) if type(operations) in (tuple, list) else 1
        with self.lock:
            if self.attempts + amount > self.max_attempts:
                raise Incomplete("submitted transformation-attempt budget reached")
            self.attempts += amount
        return model.apply_batch(base, operations)


class Journal:
    def __init__(self, root, mode, budget):
        self.root, self.mode, self.budget = Path(root), mode, budget
        self.root.mkdir(exist_ok=False)
        (self.root / "inputs").mkdir()
        (self.root / "failures").mkdir()
        self.events = (self.root / "events.jsonl").open("xb", buffering=0)
        self.records = []
        self.bytes_written = 0

    def event(self, kind, **details):
        line = encoded({"event": kind, "elapsed_seconds": round(time.monotonic() - self.budget.started, 6), **details}) + b"\n"
        self.events.write(line)
        self.bytes_written += len(line)

    def record(self, case, execute):
        self.budget.tick()
        validate_case(case)
        payload = encoded(case) + b"\n"
        if self.bytes_written + len(payload) + 65536 > self.budget.max_bytes:
            raise Incomplete("retained evidence budget reached")
        name = f"{len(self.records):04d}-{case['case_id']}.json"
        path = self.root / "inputs" / name
        save(path, case)
        self.bytes_written += len(payload)
        record = {"case_id": case["case_id"], "family": case["family"], "input": "inputs/" + name,
                  "input_sha256": sha256(payload).hexdigest(), "status": "STARTED"}
        self.event("case_started", **record)
        started = time.monotonic()
        retained_failure = False
        try:
            record["details"] = execute(case, self.budget, self.root)
            record["status"] = "PASS"
        except Incomplete:
            raise
        except Exception as exc:
            record.update(status="FAIL", error={"type": type(exc).__name__, "tag": getattr(exc, "tag", None),
                "message": str(exc), "details": getattr(exc, "details", {}), "traceback": traceback.format_exc()})
            save(self.root / "failures" / name, case)
            record["replay"] = "failures/" + name
            # Publish the observed failure before optional shrinking can time out.
            self.records.append(record)
            retained_failure = True
            self.event("case_failed", **record)
            record["reduced_replay"] = self.reduce_failure(case, record, execute, name)
        record["elapsed_seconds"] = round(time.monotonic() - started, 6)
        if not retained_failure:
            self.records.append(record)
        self.event("case_finished", **record)

    def reduce_failure(self, case, record, execute, name):
        if case["mode"] != "fuzzy-error":
            return None
        from .cases import reductions
        current = case
        details = record["error"]["details"]
        signature = (record["error"]["type"], record["error"]["tag"], details.get("actual_type"), details.get("actual_code"))
        trials = 0
        for candidate in reductions(case):
            if trials >= 12:
                break
            self.budget.tick()
            trials += 1
            try:
                validate_case(candidate)
            except (ValueError, TypeError):
                continue
            if len(encoded(candidate)) >= len(encoded(current)):
                continue
            try:
                execute(candidate, self.budget, self.root)
            except Incomplete:
                raise
            except Exception as exc:
                actual = getattr(exc, "details", {})
                if (type(exc).__name__, getattr(exc, "tag", None), actual.get("actual_type"), actual.get("actual_code")) == signature:
                    current = candidate
        record["shrink_trials"] = trials
        if current == case:
            return None
        target = "reduced-" + name
        save(self.root / "failures" / target, current)
        return "failures/" + target

    def finish(self, reason=None):
        status = "FAIL" if any(x["status"] == "FAIL" for x in self.records) else "INCOMPLETE" if reason else "PASS"
        result = {"schema": HARNESS_VERSION, "mode": self.mode, "status": status,
                  "incomplete_reason": reason, "cases": self.records,
                  "passed": sum(x["status"] == "PASS" for x in self.records),
                  "failed": sum(x["status"] == "FAIL" for x in self.records),
                  "submitted_transformation_attempts": self.budget.attempts,
                  "elapsed_seconds": round(time.monotonic() - self.budget.started, 6)}
        self.event("mode_finished", status=status, incomplete_reason=reason)
        self.events.close()
        save(self.root / "summary.json", result)
        return result
