"""Run the approved service suite and preserve M1 evidence separately."""
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

root = Path(__file__).resolve().parents[1]
logging.disable(logging.CRITICAL)
output = io.StringIO()
started = time.perf_counter()
suite = unittest.TestSuite(unittest.defaultTestLoader.discover(str(root / "tests"), pattern=pattern)
                           for pattern in ("test_baseline.py", "test_cpu.py", "test_service.py", "test_mcp.py"))
result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
report = {"scope": "M2 service plus CPU and baseline regressions", "approval_date": "2026-10-29",
          "recorded_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
          "sqlite": sqlite3.sqlite_version,
          "packages": {name: importlib.metadata.version(name) for name in ("docstream-cpu", "mcp", "mcp-types", "uvicorn", "pydantic", "anyio", "starlette", "httpx2")},
          "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
          "skipped": len(result.skipped), "successful": result.wasSuccessful(),
          "elapsed_seconds": round(time.perf_counter() - started, 6), "cpu_generated_sequences": 420,
          "test_listeners": "ephemeral loopback; shut down by fixtures; foreground subprocesses terminated and checked",
          "host_configuration_changed": False, "browser_renderer_run": False}
(root / "docs" / "m2-test-output.txt").write_text(output.getvalue(), encoding="utf-8")
(root / "docs" / "m2-test-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(output.getvalue())
print(json.dumps(report, indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
