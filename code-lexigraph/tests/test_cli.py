import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from code_lexigraph import rehydrate

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples" / "safe_fallthrough.bundle.json"


class CliTests(unittest.TestCase):
    def setUp(self):
        qa_root = (ROOT / "build" / "qa").resolve()
        qa_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=qa_root, prefix="cli-")
        self.scratch = Path(self.temporary.name).resolve()
        if not self.scratch.is_relative_to(qa_root):
            raise RuntimeError("Temporary test path escaped the approved QA directory")
        self.addCleanup(self.temporary.cleanup)

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", "-m", "code_lexigraph", *map(str, arguments)],
            cwd=ROOT, capture_output=True, encoding="utf-8", timeout=15,
            check=False,
        )

    def expected(self):
        return rehydrate(json.loads(BUNDLE.read_text(encoding="utf-8")))

    def assert_input_error(self, result):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stderr.startswith("code-lexigraph: "), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_stdout_returns_complete_construction_result(self):
        result = self.run_cli(BUNDLE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), self.expected())

    def test_output_directory_contains_the_three_declared_outputs(self):
        directory = self.scratch / "output"
        result = self.run_cli(BUNDLE, "--out", directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            {entry.name for entry in directory.iterdir()},
            {"example.py", "CONTRACT.md", "TRACE.json"},
        )
        expected = self.expected()
        self.assertEqual(
            (directory / "example.py").read_text(encoding="utf-8"),
            expected["python"],
        )
        self.assertEqual(
            (directory / "CONTRACT.md").read_text(encoding="utf-8"),
            "# Rehydrated example contract\n\n" + expected["human"] + "\n",
        )
        self.assertEqual(
            json.loads((directory / "TRACE.json").read_text(encoding="utf-8")),
            {key: expected[key] for key in ("trace", "inverse", "spans")},
        )

    def test_existing_output_is_preserved_without_partial_new_outputs(self):
        directory = self.scratch / "output"
        directory.mkdir()
        original = "existing source must remain intact\n"
        (directory / "example.py").write_text(original, encoding="utf-8")
        result = self.run_cli(BUNDLE, "--out", directory)
        self.assert_input_error(result)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(
            (directory / "example.py").read_text(encoding="utf-8"), original
        )
        self.assertEqual({entry.name for entry in directory.iterdir()}, {"example.py"})

    def test_missing_input_does_not_create_output_directory(self):
        directory = self.scratch / "output"
        result = self.run_cli(self.scratch / "missing.json", "--out", directory)
        self.assert_input_error(result)
        self.assertFalse(directory.exists())

    def test_invalid_json_does_not_create_output_directory(self):
        source = self.scratch / "invalid.json"
        source.write_text("{invalid", encoding="utf-8")
        directory = self.scratch / "output"
        result = self.run_cli(source, "--out", directory)
        self.assert_input_error(result)
        self.assertFalse(directory.exists())

    def test_unresolved_binding_does_not_create_output_directory(self):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        bundle["bindings"]["survivor"]["status"] = "unresolved"
        source = self.scratch / "unresolved.json"
        source.write_text(json.dumps(bundle), encoding="utf-8")
        directory = self.scratch / "output"
        result = self.run_cli(source, "--out", directory)
        self.assert_input_error(result)
        self.assertIn("unresolved binding: survivor", result.stderr)
        self.assertFalse(directory.exists())

    def test_paths_containing_spaces(self):
        source_dir = self.scratch / "input with spaces"
        source_dir.mkdir()
        source = source_dir / "example bundle.json"
        source.write_bytes(BUNDLE.read_bytes())
        directory = self.scratch / "output with spaces"
        result = self.run_cli(source, "--out", directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (directory / "example.py").read_text(encoding="utf-8"),
            self.expected()["python"],
        )

    def test_wrong_json_shape_is_reported_without_output(self):
        source = self.scratch / "wrong-shape.json"
        source.write_text("[]", encoding="utf-8")
        directory = self.scratch / "output"
        result = self.run_cli(source, "--out", directory)
        self.assert_input_error(result)
        self.assertFalse(directory.exists())


if __name__ == "__main__":
    unittest.main()
