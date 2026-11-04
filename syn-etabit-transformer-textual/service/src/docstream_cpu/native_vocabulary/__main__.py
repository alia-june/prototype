"""Maintained command entry point for the bounded AUTH-17 pilot."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time
import tracemalloc

from . import (MAX_APPROVED_MEMORY_BYTES, MAX_APPROVED_SECONDS, VocabularyError,
               build_pilot, verify_run, write_run)


def _peak_working_set() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        import win32api
        import win32process
        return int(win32process.GetProcessMemoryInfo(
            win32api.GetCurrentProcess())["PeakWorkingSetSize"])
    except (ImportError, KeyError, OSError):
        pass
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    process = ctypes.windll.kernel32.GetCurrentProcess()
    if not ctypes.windll.psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
        return None
    return int(counters.PeakWorkingSetSize)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded AUTH-17 WordNet native pilot")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true",
                        help="verify an existing retained run without writing")
    args = parser.parse_args(argv)
    if args.verify:
        try:
            print(json.dumps(verify_run(args.source, args.output), sort_keys=True))
            return 0
        except (VocabularyError, ValueError, OSError) as exc:
            code = getattr(exc, "code", "EVIDENCE_ERROR")
            print(json.dumps({"status": "ERROR", "code": code, "message": str(exc)},
                             sort_keys=True), file=sys.stderr)
            return 1
    started = time.perf_counter()
    tracemalloc.start()
    try:
        result, _model = build_pilot(args.source)
        elapsed = time.perf_counter() - started
        _current, allocation_peak = tracemalloc.get_traced_memory()
        working_set_peak = _peak_working_set()
        if elapsed > MAX_APPROVED_SECONDS:
            raise VocabularyError("RUNTIME_LIMIT", "pilot exceeded the approved ten-minute ceiling")
        if working_set_peak is not None and working_set_peak > MAX_APPROVED_MEMORY_BYTES:
            raise VocabularyError("MEMORY_LIMIT", "pilot exceeded the approved 512 MiB ceiling")
        runtime = {"elapsed_seconds": elapsed,
                   "python_allocation_peak_bytes": allocation_peak,
                   "process_peak_working_set_bytes": working_set_peak,
                   "approved_seconds": MAX_APPROVED_SECONDS,
                   "approved_memory_bytes": MAX_APPROVED_MEMORY_BYTES}
        write_run(args.output, result, runtime)
        print(json.dumps({"status": result.status, "output": str(args.output),
                          "summary": result.to_summary(), "runtime": runtime},
                         sort_keys=True))
        return 0 if result.status == "COMPLETE" else 2
    except VocabularyError as exc:
        print(json.dumps({"status": "ERROR", "code": exc.code, "message": str(exc)},
                         sort_keys=True), file=sys.stderr)
        return 1
    finally:
        tracemalloc.stop()


if __name__ == "__main__":
    raise SystemExit(main())
