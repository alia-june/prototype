"""Sequential owned-worker supervision with independent evidence and replay."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys
import time

from ..harness.runner import OwnedProcess
from . import HARNESS_VERSION
from .core import MODES, RUNS, SERVICE, WORKSPACE, footprint, load_case, reject_link, save
from .audit import recovered, reconcile, strict_json


def source_hashes():
    root = SERVICE / "src" / "docstream_cpu"
    return {p.relative_to(WORKSPACE).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py")) if not {"native_harness", "native_harness_meta"}.intersection(p.parts)}


def harness_hashes():
    paths = [*Path(__file__).parent.glob("*.py"), SERVICE / "tests" / "test_native_harness.py",
             SERVICE / "tests" / "fixtures" / "native_harness" / "fixed-cases.json"]
    return {p.relative_to(WORKSPACE).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def stop_owned(child):
    """Use the shared owner to capture, terminate and wait exactly once."""
    child.close()


def recover_mode(root, mode, reason):
    """Reconcile finished events; retain observed failure precedence after termination."""
    return recovered(Path(root), mode, reason)


def supervise(command, log_path, seconds, evidence_root, max_bytes):
    started, reason, samples, memory = time.monotonic(), None, 0, None
    with log_path.open("xb") as log:
        child = OwnedProcess(command, log)
        pid = child.process.pid
        try:
            next_size_check = 0
            while child.process.poll() is None:
                now = time.monotonic()
                if now - started >= seconds:
                    reason = "supervisor wall-clock deadline"
                    break
                if now >= next_size_check:
                    if footprint(evidence_root) >= max_bytes:
                        reason = "retained-run byte budget"
                        break
                    next_size_check = now + 0.5
                peak = child.job_memory()
                if peak:
                    memory = peak
                samples += 1
                time.sleep(0.025)
            peak = child.job_memory()
            if peak:
                memory = peak
        finally:
            stop_owned(child)
        return {"owned_pid": pid, "exit_code": child.process.returncode,
                "owned_child_stopped": child.process.poll() is not None,
                "supervisor_reason": reason, "poll_samples": samples,
                "elapsed_seconds": round(time.monotonic() - started, 6),
                "windows_job_memory": memory,
                "memory_scope": "Windows job committed-memory peaks include owned descendants; no leak threshold or enforced RAM cap"}


def run(mode="all", *, seed=20261029, fuzzy_count=1000, seconds=900, run_id=None, replay=None):
    if mode not in ("all", *MODES) or type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("invalid mode or seed")
    if type(fuzzy_count) is not int or not 5 <= fuzzy_count <= 1000 or fuzzy_count % 5:
        raise ValueError("fuzzy-cases must be a multiple of five in 5..1000")
    if type(seconds) not in (int, float) or type(seconds) is bool or not math.isfinite(seconds) or not 0.01 <= seconds <= 900:
        raise ValueError("seconds must be in 0.01..900")
    if replay is not None:
        replay = Path(replay).absolute()
        item = load_case(replay)
        if mode != "all" and mode != item["mode"]:
            raise ValueError("explicit mode does not match replay")
        mode = item["mode"]
    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + secrets.token_hex(4)
    if type(run_id) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", run_id):
        raise ValueError("invalid run-id")
    reject_link(RUNS)
    RUNS.mkdir(parents=True, exist_ok=True)
    root = RUNS / run_id
    root.mkdir(exist_ok=False)
    before, implementation = source_hashes(), harness_hashes()
    deadline = time.monotonic() + seconds
    max_bytes, max_attempts = 512 * 1024 * 1024, 2000
    modes = MODES if mode == "all" else (mode,)
    summaries, remaining_attempts = [], max_attempts
    save(root / "RUN.json", {"schema": HARNESS_VERSION, "mode": mode, "seed": seed,
         "fuzzy_cases": fuzzy_count, "seconds": seconds, "max_retained_bytes": max_bytes,
         "max_submitted_attempts": max_attempts, "replay": str(replay) if replay else None,
         "recorded_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
         "executable": sys.executable, "product_hashes_before": before, "harness_hashes": implementation})
    for selected in modes:
        remaining = deadline - time.monotonic()
        if remaining < 0.01 or remaining_attempts <= 0:
            summaries.append({"mode": selected, "status": "INCOMPLETE", "passed": 0, "failed": 0,
                              "incomplete_reason": "combined workload budget exhausted", "cases": []})
            continue
        command = [sys.executable, "-m", "docstream_cpu.native_harness.worker", "--root", str(root / selected),
                   "--mode", selected, "--seed", str(seed), "--fuzzy-cases", str(fuzzy_count),
                   "--seconds", str(remaining), "--max-bytes", str(max_bytes - footprint(root) - 1024 * 1024),
                   "--max-attempts", str(remaining_attempts)]
        if replay: command += ["--replay", str(replay)]
        owned = supervise(command, root / (selected + ".log"), remaining, root, max_bytes)
        mode_root = root / selected
        summary_path = mode_root / "summary.json"
        if summary_path.exists():
            try:
                reject_link(summary_path)
                result = strict_json(summary_path.read_text(encoding="utf-8"))
            except (ValueError, UnicodeError, OSError, RecursionError):
                result = None
        else:
            mode_root.mkdir(exist_ok=True)
            result = recover_mode(mode_root, selected, owned["supervisor_reason"] or "worker ended without summary")
            save(summary_path, result)
        from .cases import fuzzy_cases, hardening_cases, torture_cases
        planned = (load_case(replay),) if replay else tuple(hardening_cases(seed) if selected == "hardening"
            else fuzzy_cases(seed, fuzzy_count) if selected == "fuzzy-error" else torture_cases(seed))
        result = reconcile(mode_root, selected, result, planned, owned)
        save(mode_root / "audited-summary.json", result)
        result["supervisor"] = owned
        summaries.append(result)
        attempts = result.get("submitted_transformation_attempts")
        if attempts is None:
            remaining_attempts = 0  # Do not guess unjournaled consumption after interruption.
        else:
            remaining_attempts -= attempts
    after = source_hashes()
    changed = sorted(set(before) | set(after)) if before != after else []
    if changed: changed = [p for p in changed if before.get(p) != after.get(p)]
    status = "FAIL" if changed or any(s["status"] == "FAIL" for s in summaries) else "INCOMPLETE" if any(s["status"] == "INCOMPLETE" for s in summaries) else "PASS"
    result = {"schema": HARNESS_VERSION, "status": status, "seed": seed, "modes": summaries,
              "product_hashes_before": before, "product_hashes_after": after, "changed_product_files": changed,
              "harness_hashes": implementation, "retained_bytes_before_final_reports": footprint(root),
              "limits": {"seconds": seconds, "max_retained_bytes": max_bytes, "max_submitted_attempts": max_attempts}}
    save(root / "summary.json", result)
    lines = ["# Native hardening, fuzzy-error and torture run", "", f"Status: **{status}**. Harness: {HARNESS_VERSION}. Seed: {seed}.", "",
             "| Mode | Status | Passed | Failed | Submitted transformation attempts |", "| --- | --- | ---: | ---: | ---: |"]
    for s in summaries:
        lines.append(f"| {s['mode']} | {s['status']} | {s['passed']} | {s['failed']} | {s.get('submitted_transformation_attempts', 'unknown')} |")
    lines += ["", "Inputs are stored before execution. Replay selects only closed data families.",
              "Expected rejections pass only with the declared exception/code and an unchanged complete state fingerprint.",
              "The timeout scenario expects its deliberately stalled child to end INCOMPLETE; the parent scenario checks cleanup.",
              "Memory/timing are bounded-run observations, not leak-absence or production capacity evidence.", "",
              f"Changed product source files: {len(changed)}. See summary.json for identities, cases and supervisor evidence."]
    for s in summaries:
        if s.get("incomplete_reason"): lines += ["", f"Incomplete {s['mode']}: {s['incomplete_reason']}"]
        for item in s["cases"]:
            if item.get("status") == "FAIL":
                lines += ["", f"- {s['mode']} / {item['case_id']}: {item.get('error', {}).get('message', 'observed journal failure')}",
                          f"  Replay: {s['mode']}/{item.get('reduced_replay') or item.get('replay') or item.get('input', 'unavailable')}"]
    (root / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[status], root, result


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m docstream_cpu.native_harness")
    parser.add_argument("mode", choices=("all", *MODES))
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--fuzzy-cases", type=int, default=1000)
    parser.add_argument("--seconds", type=float, default=900)
    parser.add_argument("--run-id")
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args(argv)
    try:
        code, root, result = run(args.mode, seed=args.seed, fuzzy_count=args.fuzzy_cases,
                                 seconds=args.seconds, run_id=args.run_id, replay=args.replay)
        print(json.dumps({"status": result["status"], "report": str(root / "REPORT.md"), "summary": str(root / "summary.json")}), flush=True)
        return code
    except (ValueError, TypeError, OSError, RecursionError) as exc:
        print(json.dumps({"status": "CONFIG_ERROR", "message": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
