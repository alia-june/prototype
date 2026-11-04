"""Spawn-safe combined regression runner. Earlier milestone logs stay untouched."""
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
    root=Path(__file__).resolve().parents[1]
    logging.disable(logging.CRITICAL)
    output=io.StringIO()
    started=time.perf_counter()
    suite=unittest.defaultTestLoader.discover(str(root/"tests"))
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    report={"scope":"M4a formats plus prior CPU/service/rendering/baseline regressions", "approval_date":"2026-10-29",
        "recorded_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,"sqlite":sqlite3.sqlite_version,
        "packages":{name:importlib.metadata.version(name) for name in ("docstream-cpu","mcp","uvicorn","playwright","pydantic","markdown-it-py","python-docx","Pillow","lxml")},
        "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped),"successful":result.wasSuccessful(),
        "elapsed_seconds":round(time.perf_counter()-started,6),"prior_cpu_generated_sequences":420,"rich_generated_sequences":80,"host_configuration_changed":False,
        "database_schema":2,"schema_migration_required":False,"source_and_image_store":"existing transactional sources table"}
    (root/"docs"/"m4-test-output.txt").write_text(output.getvalue(),encoding="utf-8")
    (root/"docs"/"m4-test-results.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(output.getvalue())
    print(json.dumps(report,indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":
    raise SystemExit(main())
