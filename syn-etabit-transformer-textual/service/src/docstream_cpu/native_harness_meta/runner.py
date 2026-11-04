"""Independent meta-test journal and bounded owned-worker supervision."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import traceback

from ..harness.runner import OwnedProcess
from . import HARNESS_VERSION
from .checks import Context, RUNS, SERVICE, HARDENING, TORTURE, encode, mutation_cases, execute_mutation, run_hardening, run_torture

FIXTURE = SERVICE / "tests/fixtures/native_harness_meta/contract.json"


def save(path, value):
    with path.open("xb") as file:
        file.write(encode(value) + b"\n")


def hashes():
    paths = [*Path(__file__).parent.glob("*.py"), *Path(__file__).parent.parent.joinpath("native_harness").glob("*.py"), FIXTURE,
             SERVICE / "tests/test_native_harness_meta.py", SERVICE / "tests/test_native_harness.py"]
    return {p.relative_to(SERVICE).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def footprint(root):
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def aggregate(records, reason=None):
    return "FAIL" if any(r["status"] == "FAIL" for r in records) else "INCOMPLETE" if reason else "PASS"


def audit_outer(root, result, planned):
    """Audit the meta worker too, independently of its reported counts."""
    problems, finished, started = [], {}, set()
    try:
        for line in (root / "events.jsonl").read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            key = event["case_id"]
            if event["event"] == "started":
                if key in started: problems.append("duplicate meta case start")
                started.add(key)
            elif event["event"] == "finished":
                if key not in started or key in finished: problems.append("meta journal ordering or duplicate outcome")
                finished[key] = {k: v for k, v in event.items() if k != "event"}
            else: problems.append("unknown meta event")
    except (OSError, ValueError, TypeError, KeyError): problems.append("unreadable meta journal")
    if list(finished.values()) != result["cases"]: problems.append("meta summary differs from journal")
    for status, key in (("PASS", "passed"), ("FAIL", "failed")):
        if result.get(key) != sum(r.get("status") == status for r in finished.values()): problems.append("meta count mismatch: " + key)
    if result.get("completed") != len(finished): problems.append("meta completed count mismatch")
    if result["status"] == "PASS" and (len(finished) != planned or started != set(finished)):
        problems.append("meta PASS lacks complete planned coverage")
    if any(r.get("status") == "FAIL" for r in finished.values()) and result["status"] != "FAIL":
        problems.append("meta summary lost an observed failure")
    for row in result["cases"]:
        relative = Path(row["input"])
        path = root / relative
        if relative.is_absolute() or not path.resolve().is_relative_to(root.resolve()):
            problems.append("meta input escaped root"); continue
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != row["input_sha256"]:
            problems.append("outer case input integrity mismatch: " + row["case_id"])
    return problems


def worker(root, modes, seed, seconds):
    contract = json.loads(FIXTURE.read_text())
    if tuple(contract["hardening"]) != HARDENING or tuple(contract["torture"]) != TORTURE:
        raise ValueError("fixture and closed dispatch disagree")
    deadline = time.monotonic() + seconds
    records, artifacts, terminations, reason = [], [], 0, None
    linked_bytes, retained, next_size_check = 0, 0, 0
    (root / "inputs").mkdir(); (root / "work").mkdir()
    items = []
    for mode in modes:
        if mode == "fuzzy": items.extend(mutation_cases(seed, contract["mutations"]))
        else:
            items.extend({"id": mode + "-" + name, "mode": mode, "input": {"name": name}, "expected": "PASS"}
                         for name in contract[mode])
    with (root / "events.jsonl").open("xb", buffering=0) as events:
        for item in items:
            if time.monotonic() >= deadline:
                reason = "meta-test wall-clock budget reached"; break
            if time.monotonic() >= next_size_check:
                retained = footprint(root) + linked_bytes
                next_size_check = time.monotonic() + .5
            if retained > 511 * 1024 * 1024:
                reason = "meta-test retained evidence budget reached"; break
            path = root / "inputs" / (item["id"] + ".json")
            save(path, item)
            record = {"case_id": item["id"], "mode": item["mode"], "input": path.relative_to(root).as_posix(),
                      "input_sha256": sha256(path.read_bytes()).hexdigest(), "expected": item["expected"], "status": "STARTED"}
            events.write(encode({"event": "started", **record}) + b"\n")
            folder = root / "work" / item["id"]; folder.mkdir()
            ctx = Context(folder, seed)
            started = time.monotonic()
            try:
                if item["mode"] == "hardening": details = run_hardening(item["input"]["name"], ctx)
                elif item["mode"] == "fuzzy": details = execute_mutation(item, ctx)
                else: details = run_torture(item["input"]["name"], ctx)
                record.update(status="PASS", details=details)
            except Exception as exc:
                record.update(status="FAIL", error={"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
            artifacts.extend(ctx.artifacts); terminations += ctx.terminations
            linked_bytes += sum(footprint(Path(p)) for p in ctx.artifacts)
            record.update(elapsed_seconds=round(time.monotonic()-started, 6), artifacts=ctx.artifacts, owned_termination_cycles=ctx.terminations)
            records.append(record)
            events.write(encode({"event": "finished", **record}) + b"\n")
    result = {"schema": HARNESS_VERSION, "status": aggregate(records, reason), "cases": records,
              "incomplete_reason": reason, "planned": len(items), "completed": len(records),
              "passed": sum(r["status"] == "PASS" for r in records), "failed": sum(r["status"] == "FAIL" for r in records),
              "artifacts": artifacts, "owned_termination_cycles": terminations,
              "retained_bytes": footprint(root) + sum(footprint(Path(p)) for p in artifacts)}
    save(root / "worker-summary.json", result)
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[result["status"]]


def stop(child):
    """Independent of the native harness cleanup function being tested."""
    try:
        if os.name == "nt" and child.job is not None:
            import win32job
            win32job.TerminateJobObject(child.job, 2)
            until = time.monotonic() + 5
            while win32job.QueryInformationJobObject(child.job, win32job.JobObjectBasicAccountingInformation)["ActiveProcesses"]:
                if time.monotonic() >= until: raise RuntimeError("meta-test descendants remained active")
                time.sleep(.01)
    finally:
        child.close()


def run(mode="all", *, seed=20261030, seconds=600, run_id="auth14-20261030-final"):
    if mode not in ("all", "hardening", "fuzzy", "torture", "before"):
        raise ValueError("unknown mode")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("invalid seed")
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or not .01 <= seconds <= 600:
        raise ValueError("invalid seconds")
    if type(run_id) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", run_id):
        raise ValueError("invalid run-id")
    for part in (RUNS, *RUNS.parents):
        if part.exists() and (part.is_symlink() or part.is_junction()): raise ValueError("linked evidence roots unsupported")
    RUNS.mkdir(parents=True, exist_ok=True)
    root = RUNS / run_id; root.mkdir(exist_ok=False)
    identity = hashes()
    modes = ["hardening", "fuzzy", "torture"] if mode == "all" else ["hardening", "fuzzy"] if mode == "before" else [mode]
    save(root / "RUN.json", {"schema": HARNESS_VERSION, "seed": seed, "modes": modes, "seconds": seconds,
         "max_retained_bytes": 512 * 1024 * 1024, "recorded_utc": datetime.now(timezone.utc).isoformat(),
         "python": sys.version, "source_hashes": identity})
    reason = None; started = time.monotonic()
    with (root / "worker.log").open("xb") as log:
        child = OwnedProcess([sys.executable, "-m", "docstream_cpu.native_harness_meta.runner", "--worker-root", str(root),
            "--modes", ",".join(modes), "--seed", str(seed), "--seconds", str(seconds)], log)
        try:
            while child.process.poll() is None:
                if time.monotonic() - started >= seconds:
                    reason = "independent supervisor deadline"; break
                if footprint(root) >= 512 * 1024 * 1024:
                    reason = "independent supervisor evidence limit"; break
                time.sleep(.1)
        finally: stop(child)
    path = root / "worker-summary.json"
    if path.exists(): result = json.loads(path.read_text())
    else:
        records = []
        if (root / "events.jsonl").exists():
            for line in (root / "events.jsonl").read_text().splitlines():
                try: event = json.loads(line)
                except ValueError: continue
                if event.get("event") == "finished": records.append(event)
        reason = reason or "worker ended without summary"
        result = {"schema": HARNESS_VERSION, "cases": records, "status": aggregate(records, reason), "incomplete_reason": reason}
    problems = []
    if child.process.returncode != {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[result["status"]] and not reason:
        problems.append("meta worker exit/summary mismatch")
    if identity != hashes(): problems.append("meta or target harness source changed during run")
    fixture = json.loads(FIXTURE.read_text())
    planned = sum(fixture["mutations"] if mode == "fuzzy" else len(fixture[mode]) for mode in modes)
    problems.extend(audit_outer(root, result, planned))
    if problems: result["status"] = "FAIL"
    if reason and result["status"] != "FAIL": result["status"] = "INCOMPLETE"
    result.update(supervisor_reason=reason, audit_problems=problems, elapsed_seconds=round(time.monotonic()-started, 6),
                  owned_worker_stopped=child.process.poll() is not None, owned_worker_exit_code=child.process.returncode)
    save(root / "summary.json", result)
    lines = ["# Native harness meta-test run", "", f"Status: **{result['status']}**. Seed: {seed}.", "",
             "| Mode | Passed | Failed |", "| --- | ---: | ---: |"]
    for selected in modes:
        rows = [r for r in result["cases"] if r["mode"] == selected]
        lines.append(f"| {selected} | {sum(r['status']=='PASS' for r in rows)} | {sum(r['status']=='FAIL' for r in rows)} |")
    lines += ["", "Synthetic faults deliberately contradict reports or actor outcomes; an outer PASS means detection matched its declared expectation.",
              f"Owned timeout/termination cycles: {result.get('owned_termination_cycles', 'unknown')}. Independent supervisor stopped: {result['owned_worker_stopped']}.",
              "Inputs, hashes, exact exception details and target-run links are retained in summary.json and events.jsonl."]
    for row in result["cases"]:
        if row["status"] == "FAIL": lines.append(f"- {row['case_id']}: {row['error']['type']}: {row['error']['message']}")
    (root / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[result["status"]], root, result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="all", choices=("all", "before", "hardening", "fuzzy", "torture"))
    parser.add_argument("--run-id", default="auth14-20261030-final")
    parser.add_argument("--seconds", type=float, default=600)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--worker-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--modes", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker_root:
        root = args.worker_root.resolve()
        if root.parent != RUNS.resolve() or not root.is_dir(): raise ValueError("worker root outside owned run area")
        return worker(root, args.modes.split(","), args.seed, args.seconds)
    code, root, result = run(args.mode, seed=args.seed, seconds=args.seconds, run_id=args.run_id)
    print(json.dumps({"status": result["status"], "report": str(root / "REPORT.md"), "completed": len(result["cases"])}), flush=True)
    return code


if __name__ == "__main__": raise SystemExit(main())
