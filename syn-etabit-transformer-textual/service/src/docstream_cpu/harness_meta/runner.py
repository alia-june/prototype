"""Retained three-mode AUTH-19A meta runner."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import secrets
import sys
import time
import traceback

from . import CASE_SCHEMA, HARNESS_VERSION
from .audit import encode
from .cases import HARDENING, TORTURE, fuzzy_cases, meta_case
from .checks import SERVICE, WORKSPACE, run_hardening, run_torture


RUNS = WORKSPACE / ".docstream" / "harness-meta-runs"
FIXTURE = SERVICE / "tests/fixtures/harness_meta/contract.json"


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle: handle.write(encode(value) + b"\n")


def _footprint(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        try:
            if path.is_file() and not path.is_symlink(): total += path.stat().st_size
        except FileNotFoundError: pass
    return total


def target_hashes() -> dict[str, str]:
    paths = [*SERVICE.joinpath("src/docstream_cpu/harness").glob("*.py"),
             *SERVICE.joinpath("src/docstream_cpu/native_harness").glob("*.py"),
             *SERVICE.joinpath("src/docstream_cpu/native_harness_meta").glob("*.py"),
             SERVICE / "tests/test_harness.py", SERVICE / "tests/test_harness_cleanup.py",
             SERVICE / "tests/test_native_harness.py", SERVICE / "tests/test_native_harness_meta.py",
             SERVICE / "tests/fixtures/harness/reviewed-m4.json"]
    return {path.relative_to(WORKSPACE).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths) if path.is_file()}


def implementation_hashes() -> dict[str, str]:
    paths = [*Path(__file__).parent.glob("*.py"), FIXTURE,
             SERVICE / "tests/test_harness_meta.py"]
    return {path.relative_to(WORKSPACE).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths) if path.is_file()}


class MetaJournal:
    def __init__(self, root: Path, mode: str, deadline: float, max_bytes: int):
        self.root, self.mode = root, mode
        self.inputs = root / "inputs"; self.inputs.mkdir(parents=True)
        self.events = (root / "events.jsonl").open("xb")
        self.deadline, self.max_bytes = deadline, max_bytes
        self.rows: list[dict] = []
        self._size_check_at = 0
        self.event({"event": "mode_started", "mode": mode})

    def event(self, value):
        self.events.write(encode(value) + b"\n"); self.events.flush()

    def record(self, case: dict, action):
        if time.monotonic() >= self.deadline: raise TimeoutError("meta deadline")
        # A full recursive scan on every one of 1,000 packet mutations becomes
        # quadratic as evidence accumulates. Sample every 50 retained cases and
        # perform an exact final scan in run(); this remains a guard, not a quota.
        if len(self.rows) >= self._size_check_at:
            if _footprint(self.root.parent) >= self.max_bytes: raise RuntimeError("meta evidence limit")
            self._size_check_at = len(self.rows) + 50
        number = len(self.rows)
        payload = encode(case) + b"\n"
        path = self.inputs / f"{number:04d}-{case['case_id']}.json"
        with path.open("xb") as handle: handle.write(payload)
        row = {"case_id": case["case_id"], "mode": self.mode,
               "input": path.relative_to(self.root).as_posix(),
               "input_sha256": sha256(payload).hexdigest(), "expected": case["expected"]}
        self.event({"event": "case_started", **row})
        try:
            result = action()
            observed = result.get("observed", result.get("status", "PASS"))
            row.update(status="PASS" if observed == case["expected"] else "FAIL",
                       observed=observed, result=result)
            if row["status"] == "FAIL":
                row["error"] = {"type": "ExpectationMismatch",
                                "message": f"expected {case['expected']}, observed {observed}"}
        except Exception as exc:
            row.update(status="FAIL", observed="EXCEPTION",
                       error={"type": type(exc).__name__, "message": str(exc)[:2000]},
                       traceback=traceback.format_exc()[-16000:])
        self.rows.append(row); self.event({"event": "case_finished", **row})
        return row

    def finish(self, incomplete_reason=None):
        counts = Counter(row["status"] for row in self.rows)
        status = "FAIL" if counts["FAIL"] else "INCOMPLETE" if incomplete_reason else "PASS"
        result = {"schema": HARNESS_VERSION, "mode": self.mode, "status": status,
                  "counts": dict(counts), "cases": self.rows,
                  "coverage_complete": incomplete_reason is None,
                  "incomplete_reason": incomplete_reason}
        self.event({"event": "mode_finished", "status": status, "counts": dict(counts)})
        self.events.close(); _write(self.root / "summary.json", result)
        return result


def _validate(mode, seed, seconds, run_id, fuzzy_count):
    if mode not in ("all", "hardening", "fuzzy", "torture"):
        raise ValueError("invalid mode")
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("invalid seed")
    if type(seconds) not in (int, float) or type(seconds) is bool or not math.isfinite(seconds) or not 1 <= seconds <= 900:
        raise ValueError("seconds outside approved range")
    if type(fuzzy_count) is not int or not 5 <= fuzzy_count <= 1000 or fuzzy_count % 5:
        raise ValueError("fuzzy count outside approved range")
    if type(run_id) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", run_id):
        raise ValueError("invalid run id")


def audit_outer(root: Path, result: dict, planned: int) -> list[str]:
    issues = []
    rows = result.get("cases", [])
    if len(rows) != planned: issues.append("planned coverage mismatch")
    counts = Counter(row.get("status") for row in rows)
    if result.get("counts") != dict(counts): issues.append("outer count mismatch")
    seen = set()
    for row in rows:
        if row.get("case_id") in seen: issues.append("duplicate meta case")
        seen.add(row.get("case_id"))
        path = root / row.get("input", "")
        try:
            if not path.resolve().is_relative_to(root.resolve()): issues.append("escaped meta input")
            payload = path.read_bytes()
            if sha256(payload).hexdigest() != row.get("input_sha256"): issues.append("meta input hash mismatch")
            value = json.loads(payload)
            if value.get("schema") != CASE_SCHEMA: issues.append("meta input schema")
        except Exception: issues.append("missing or invalid meta input")
    if any(row.get("status") == "FAIL" for row in rows) and result.get("status") == "PASS":
        issues.append("outer failure demoted")
    return sorted(set(issues))


def run(mode="all", *, seed=20261031, seconds=900, run_id="auth19a-20261031-before",
        fuzzy_count=1000):
    _validate(mode, seed, seconds, run_id, fuzzy_count)
    RUNS.mkdir(parents=True, exist_ok=True)
    root = RUNS / run_id; root.mkdir(exist_ok=False)
    started = time.monotonic(); deadline = started + seconds; max_bytes = 512 * 1024 * 1024
    before = target_hashes()
    _write(root / "RUN.json", {"schema": HARNESS_VERSION, "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(), "seed": seed,
        "seconds": seconds, "fuzzy_cases": fuzzy_count, "max_retained_bytes": max_bytes,
        "target_hashes_before": before, "implementation_hashes": implementation_hashes()})
    selected = ("hardening", "fuzzy", "torture") if mode == "all" else (mode,)
    summaries = []
    for selected_mode in selected:
        journal = MetaJournal(root / selected_mode, selected_mode, deadline, max_bytes)
        incomplete = None
        try:
            if selected_mode == "hardening":
                for name in HARDENING:
                    expected = "PASS" if name in ("clean_control", "input_retained_before_actor") else "REJECT"
                    case = meta_case("hardening-" + name, "hardening", "fixed", name, expected)
                    journal.record(case, lambda n=name: run_hardening(n, journal.root / "artifacts"))
            elif selected_mode == "fuzzy":
                from .checks import check_packet
                for case in fuzzy_cases(seed, fuzzy_count):
                    journal.record(case, lambda c=case: check_packet(
                        journal.root / "artifacts", c["mutation"], c["case_id"]))
            else:
                for name in TORTURE:
                    case = meta_case("torture-" + name, "torture", "scenario", name, "PASS")
                    journal.record(case, lambda n=name: run_torture(n, journal.root / "artifacts" / n))
        except (TimeoutError, RuntimeError) as exc: incomplete = str(exc)
        summary = journal.finish(incomplete)
        problems = audit_outer(journal.root, summary,
            len(HARDENING) if selected_mode == "hardening" else fuzzy_count if selected_mode == "fuzzy" else len(TORTURE))
        summary["outer_audit_issues"] = problems
        if problems: summary["status"] = "FAIL"
        summaries.append(summary)
    after = target_hashes(); changed = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
    status = "FAIL" if changed or any(row["status"] == "FAIL" for row in summaries) else "INCOMPLETE" if any(
        row["status"] != "PASS" for row in summaries) else "PASS"
    result = {"schema": HARNESS_VERSION, "status": status, "run_id": run_id,
              "elapsed_seconds": round(time.monotonic() - started, 6),
              "retained_bytes": _footprint(root), "target_files_changed": changed,
              "modes": summaries, "target_hashes_after": after}
    _write(root / "summary.json", result)
    lines = ["# Service-harness meta-verification", "", f"Status: **{status}**.", "",
             "| Mode | Status | Pass | Fail |", "| --- | --- | ---: | ---: |"]
    for row in summaries:
        lines.append(f"| {row['mode']} | {row['status']} | {row['counts'].get('PASS',0)} | {row['counts'].get('FAIL',0)} |")
    lines.extend(["", f"Elapsed seconds: {result['elapsed_seconds']}.",
                  f"Retained bytes: {result['retained_bytes']}.",
                  f"Target files changed: {changed}.", "", "Failed meta-cases:", ""])
    for mode_row in summaries:
        for case in mode_row["cases"]:
            if case["status"] == "FAIL": lines.append(
                f"- {case['case_id']}: {case.get('error',{}).get('message','target finding')}")
    (root / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[status], root, result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent service-harness meta-verification")
    parser.add_argument("mode", nargs="?", default="all", choices=("all", "hardening", "fuzzy", "torture"))
    parser.add_argument("--run-id", default="auth19a-20261031-before")
    parser.add_argument("--seconds", type=float, default=900)
    parser.add_argument("--seed", type=int, default=20261031)
    parser.add_argument("--fuzzy-cases", type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        code, root, result = run(args.mode, seed=args.seed, seconds=args.seconds,
                                 run_id=args.run_id, fuzzy_count=args.fuzzy_cases)
        print(json.dumps({"status": result["status"], "root": str(root),
                          "summary": str(root / "summary.json")}, sort_keys=True))
        return code
    except (ValueError, FileExistsError) as exc:
        print(json.dumps({"status": "CONFIG_ERROR", "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 3
