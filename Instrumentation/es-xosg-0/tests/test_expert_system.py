from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import expert_system


class ExpertSystemTests(unittest.TestCase):
    expected = {
        "creation-known-valid.json": "AWAIT_HUMAN_REVIEW",
        "verification-known-valid.json": "AWAIT_HUMAN_REVIEW",
        "gate-known-valid.json": "AWAIT_HUMAN_REVIEW",
        "authority-mismatch.json": "NEEDS_AUTHORITY",
        "structural-failure.json": "STOP_AND_RETAIN",
        "partial-or-unknown.json": "STOP_AND_RETAIN",
    }

    def fixture(self, name: str) -> Path:
        return ROOT / "fixtures" / name

    def test_declared_fixture_outcomes(self):
        for name, outcome in self.expected.items():
            with self.subTest(name=name):
                before = hashlib.sha256(self.fixture(name).read_bytes()).hexdigest()
                result = expert_system.evaluate(json.loads(self.fixture(name).read_text(encoding="utf-8")))
                after = hashlib.sha256(self.fixture(name).read_bytes()).hexdigest()
                self.assertEqual(outcome, result["outcome"])
                self.assertEqual("not_performed", result["execution"])
                self.assertEqual("human_decision_required", result["authority"])
                self.assertEqual(before, after)

    def test_unknown_tool_is_refused(self):
        result = expert_system.evaluate({"envelope_schema": "es-xosg-0/receipt-envelope/v1", "tool_kind": "unknown.tool", "receipt": {}})
        self.assertEqual("UNMAPPED_OR_INSUFFICIENT_RECEIPT", result["outcome"])

    def test_missing_receipt_fields_are_refused(self):
        result = expert_system.evaluate({"envelope_schema": "es-xosg-0/receipt-envelope/v1", "tool_kind": "mill.gate", "receipt": {"admission": "permitted"}})
        self.assertEqual("UNMAPPED_OR_INSUFFICIENT_RECEIPT", result["outcome"])

    def test_no_execution_or_network_imports(self):
        tree = ast.parse((ROOT / "expert_system.py").read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        self.assertFalse(imports & {"subprocess", "socket", "urllib", "http", "requests", "openai", "anthropic", "importlib"})

    def test_source_has_no_declared_write_or_execution_calls(self):
        tree = ast.parse((ROOT / "expert_system.py").read_text(encoding="utf-8"))
        called_attributes = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        direct_calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertFalse(called_attributes & {
            "write", "write_text", "write_bytes", "mkdir", "unlink", "rename",
            "replace", "rmdir", "touch", "system", "popen", "run", "Popen",
            "connect", "send", "sendall", "request", "urlopen",
        })
        self.assertFalse(direct_calls & {"open", "exec", "eval", "compile"})


if __name__ == "__main__":
    unittest.main()
