from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "runner" / "run_validation.py"


def run(path):
    return subprocess.run(
        [sys.executable, str(RUNNER), str(path)],
        capture_output=True,
        text=True,
    )


# Regression: user's exact usage pattern must validate the fixture, not crash.
fixture = run(ROOT / "fixtures" / "wb-002.json")
assert fixture.returncode == 0, fixture.stdout + fixture.stderr
fixture_report = json.loads(fixture.stdout)
assert fixture_report["document_type"] == "fixture"
assert fixture_report["fixture_id"] == "WB-002"
assert fixture_report["pass"] is True

# Existing good candidate must pass.
good = run(ROOT / "examples" / "wb001_candidate_good.json")
assert good.returncode == 0, good.stdout + good.stderr
good_report = json.loads(good.stdout)
assert good_report["document_type"] == "candidate_result"
assert good_report["pass"] is True

# Existing bad candidate must be graded and fail (exit 1), not crash.
bad = run(ROOT / "examples" / "wb001_candidate_bad.json")
assert bad.returncode == 1, bad.stdout + bad.stderr
bad_report = json.loads(bad.stdout)
assert bad_report["document_type"] == "candidate_result"
assert bad_report["pass"] is False
assert bad_report["forbidden_present"]

# Malformed candidate structure must produce a controlled exit 2 and JSON error.
with tempfile.TemporaryDirectory() as td:
    malformed = Path(td) / "malformed.json"
    malformed.write_text(json.dumps({"fixture_id": "WB-001", "claims": []}), encoding="utf-8")
    result = run(malformed)
    assert result.returncode == 2, result.stdout + result.stderr
    err = json.loads(result.stderr)
    assert err["pass"] is False
    assert "structurally invalid" in err["error"]

print("self-test: PASS")
