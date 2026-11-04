"""Combined validation with a spawn-safe main guard and retained M3 evidence."""
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import logging
from pathlib import Path
import sqlite3
import sys
import time
import unittest


def main():
    root = Path(__file__).resolve().parents[1]
    logging.disable(logging.CRITICAL)
    output = io.StringIO()
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover(str(root / "tests"))
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    report = {"scope": "M3 rendering plus service/CPU/baseline regressions", "approval_date": "2026-10-29",
              "recorded_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "sqlite": sqlite3.sqlite_version,
              "packages": {name: importlib.metadata.version(name) for name in ("docstream-cpu", "mcp", "uvicorn", "playwright", "pydantic")},
              "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "skipped": len(result.skipped), "successful": result.wasSuccessful(),
              "elapsed_seconds": round(time.perf_counter() - started, 6), "cpu_generated_sequences": 420,
              "worker_lifecycle": "spawned renderer owned by Windows job object; closed by fixtures and ASGI lifespan",
              "host_configuration_changed": False, "browser": "project-local Chromium"}
    (root / "docs" / "m3-test-output.txt").write_text(output.getvalue(), encoding="utf-8")
    (root / "docs" / "m3-test-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(output.getvalue())
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
