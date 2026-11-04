"""Run the bounded approved CPU suite and retain machine-readable evidence."""
from __future__ import annotations

import importlib.metadata
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = io.StringIO()
    started = time.perf_counter()
    suite = unittest.TestSuite((
        unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_cpu.py"),
        unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_baseline.py"),
    ))
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    elapsed = time.perf_counter() - started
    packages = ("docstream-cpu", "pydantic", "pydantic_core", "annotated-types", "typing_extensions", "typing-inspection", "python-docx", "setuptools", "pip")
    report = {
        "scope": "M0-M1 CPU model; no HTTP server or renderer started",
        "date": "2026-10-29", "timezone": "America/New_York",
        "python": sys.version, "executable": sys.executable,
        "base_prefix": sys.base_prefix, "platform": platform.platform(),
        "environment": "project venv inheriting bundled runtime site-packages; editable package",
        "packages": {name: importlib.metadata.version(name) for name in packages},
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "elapsed_seconds": round(elapsed, 6), "successful": result.wasSuccessful(),
        "generated_cases": {"assignment": 300, "structural": 60, "invalid": 60},
        "seeds": [20261029, 12345, 98765],
        "baseline": {"included": 6, "excluded": ["test_http_edit_endpoint (service startup deferred)"]},
    }
    (root / "docs" / "test-output.txt").write_text(output.getvalue(), encoding="utf-8")
    (root / "docs" / "test-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(output.getvalue())
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
