"""Run the six original tests that do not start an HTTP server.

This keeps old source bytes unchanged. The native DOCX round-trip test checks
structure/text only; no renderer, installer, service or external converter runs.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "baseline" / "docstream-0.1.0"
sys.path.insert(0, str(BASELINE / "src"))
spec = spec_from_file_location("docstream_baseline_tests", BASELINE / "tests" / "test_docstream.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)


def load_tests(loader, tests, pattern):
    names = (
        "test_new_inspect_and_guarded_edit",
        "test_inspect_ignores_headings_inside_code_fences",
        "test_match_guard_prevents_write",
        "test_capture_replacement_and_newline",
        "test_native_round_trip",
        "test_service_root_containment",
    )
    return unittest.TestSuite(module.DocstreamTests(name) for name in names)
