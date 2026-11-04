"""Maintained command entry point for the AUTH-18A vertical composition probe."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import tracemalloc

from . import MapError, build_probe, verify_probe, write_probe


MAX_SECONDS = 120.0
MAX_MEMORY_BYTES = 128 * 1024 * 1024


def _peak_working_set() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        import win32api
        import win32process
        return int(win32process.GetProcessMemoryInfo(
            win32api.GetCurrentProcess())["PeakWorkingSetSize"])
    except (ImportError, KeyError, OSError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or verify the AUTH-18A map probe")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        try:
            print(json.dumps(verify_probe(args.source, args.output), sort_keys=True))
            return 0
        except (MapError, OSError, ValueError) as exc:
            print(json.dumps({"status": "ERROR", "code": getattr(exc, "code", "EVIDENCE_ERROR"),
                              "message": str(exc)}, sort_keys=True), file=sys.stderr)
            return 1
    started = time.perf_counter()
    tracemalloc.start()
    try:
        result, store = build_probe(args.source)
        elapsed = time.perf_counter() - started
        _current, allocation_peak = tracemalloc.get_traced_memory()
        process_peak = _peak_working_set()
        if elapsed > MAX_SECONDS:
            raise MapError("RUNTIME_LIMIT", "probe exceeded two-minute ceiling")
        if process_peak is not None and process_peak > MAX_MEMORY_BYTES:
            raise MapError("MEMORY_LIMIT", "probe exceeded 128 MiB peak working-set ceiling")
        runtime = {"elapsed_seconds": elapsed,
                   "python_allocation_peak_bytes": allocation_peak,
                   "process_peak_working_set_bytes": process_peak,
                   "approved_seconds": MAX_SECONDS,
                   "approved_memory_bytes": MAX_MEMORY_BYTES}
        write_probe(args.output, result, store, runtime)
        print(json.dumps({"status": "COMPLETE", "output": str(args.output),
                          "summary": result.to_summary(), "runtime": runtime}, sort_keys=True))
        return 0
    except MapError as exc:
        print(json.dumps({"status": "ERROR", "code": exc.code, "message": str(exc)},
                         sort_keys=True), file=sys.stderr)
        return 1
    finally:
        tracemalloc.stop()


if __name__ == "__main__":
    raise SystemExit(main())
