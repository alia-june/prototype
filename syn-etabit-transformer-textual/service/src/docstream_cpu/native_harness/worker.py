"""Owned mode worker and deliberately stalled cleanup probe."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from .cases import fuzzy_cases, hardening_cases, torture_cases
from .core import Budget, Incomplete, Journal, RUNS, load_case, reject_link, save
from .workloads import execute


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--mode", choices=("hardening", "fuzzy-error", "torture"))
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--fuzzy-cases", type=int, default=1000)
    parser.add_argument("--seconds", type=float, default=900)
    parser.add_argument("--max-bytes", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--max-attempts", type=int, default=2000)
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--stall-ready", type=Path)
    args = parser.parse_args(argv)
    target = args.stall_ready if args.stall_ready else args.root
    if target is None or not target.absolute().is_relative_to(RUNS.absolute()):
        parser.error("worker output must stay in the native harness run tree")
    reject_link(target)
    if args.stall_ready:
        save(args.stall_ready, {"status": "STARTED", "pid": os.getpid(), "expected_outcome": "INCOMPLETE"})
        while True:
            time.sleep(30)
    if args.mode is None:
        parser.error("mode is required")
    budget = Budget(args.seconds, args.max_bytes, args.max_attempts)
    journal = Journal(args.root, args.mode, budget)
    reason = None
    try:
        if args.replay:
            cases = (load_case(args.replay),)
            if cases[0]["mode"] != args.mode:
                raise ValueError("mode/replay mismatch")
        elif args.mode == "hardening":
            cases = hardening_cases(args.seed)
        elif args.mode == "fuzzy-error":
            cases = fuzzy_cases(args.seed, args.fuzzy_cases)
        else:
            cases = torture_cases(args.seed)
        for case in cases:
            journal.record(case, execute)
    except (Incomplete, KeyboardInterrupt) as exc:
        reason = str(exc) or "worker interrupted"
    except Exception as exc:
        reason = f"worker infrastructure exception: {type(exc).__name__}: {exc}"
        journal.event("worker_error", reason=reason)
    finally:
        result = journal.finish(reason)
    print(json.dumps({"status": result["status"], "passed": result["passed"], "failed": result["failed"]}), flush=True)
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
