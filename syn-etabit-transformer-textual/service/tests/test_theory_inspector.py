from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import random
import shutil
import tempfile
import unittest

from docstream_cpu.theory_inspector import (InspectorLimits, TheoryInspectionError,
                                             TheoryInspector)
from docstream_cpu.theory_inspector.__main__ import main


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STUDY_ROOT = PROJECT_ROOT / "research" / "relative-theory" / "auth18b-source-study"


def tree_hashes(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def refresh_index_entry(root: Path, relative: str) -> None:
    index_path = root / "inspection_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    payload = (root / relative).read_bytes()
    document = json.loads(payload.decode("utf-8"))
    for item in index["files"]:
        if item["path"] == relative:
            item["bytes"] = len(payload)
            item["sha256"] = sha256(payload).hexdigest()
            item["record_count"] = len(document["records"])
            break
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


class StudyCopy(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "study"
        shutil.copytree(STUDY_ROOT, self.root)

    def tearDown(self):
        self.temp.cleanup()

    def assert_code(self, code: str, action) -> None:
        with self.assertRaises(TheoryInspectionError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)


class TheoryInspectorRigidTests(StudyCopy):
    def test_checked_packet_loads_with_expected_counts_and_partial_status(self):
        inspector = TheoryInspector(self.root)
        summary = inspector.summary()
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["study_status"], "PARTIAL_GOVERNING_SOURCE_MISSING")
        self.assertEqual(summary["files"], 6)
        self.assertEqual(summary["records"], 77)
        self.assertEqual(summary["catalogs"]["wordnet_relations"], 16)

    def test_queries_keep_source_defined_and_proposed_statuses_distinct(self):
        inspector = TheoryInspector(self.root)
        defined = inspector.relations(status="SOURCE_DEFINED")
        proposed = inspector.relations(status="PROPOSED_NOT_ADOPTED")
        self.assertEqual(len(defined), 16)
        self.assertEqual(len(proposed), 17)
        self.assertTrue(all(row["_catalog"] == "wordnet_relations" for row in defined))
        self.assertTrue(all(row["_catalog"] == "generic_relations" for row in proposed))

    def test_trace_crosses_catalogs_without_interpreting_external_record_hash(self):
        trace = TheoryInspector(self.root).trace("XW-ADJECTIVE-MARKER-A", depth=4)
        ids = {node["id"] for node in trace["nodes"]}
        self.assertTrue({"WN-MARKER-A", "THEORY-MAP-SYNTAX", "SAMPLE-ALL-AROUND"} <= ids)
        self.assertFalse(trace["truncated"])
        self.assertFalse(any(edge["field"] == "source_record_id" for edge in trace["edges"]))

    def test_missing_id_and_invalid_query_limits_have_exact_codes(self):
        inspector = TheoryInspector(self.root)
        self.assert_code("NOT_FOUND", lambda: inspector.one("absent"))
        self.assert_code("RESULT_LIMIT", lambda: inspector.sources(limit=1001))
        self.assert_code("TRACE_DEPTH", lambda: inspector.trace("WN-MARKER-A", 17))

    def test_cli_supports_json_and_text_without_writing_study(self):
        before = tree_hashes(self.root)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["--root", str(self.root), "--format", "json", "validate"])
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertEqual(json.loads(stdout.getvalue())["status"], "PASS")
        self.assertEqual(tree_hashes(self.root), before)


class TheoryInspectorHardeningTests(StudyCopy):
    def test_hash_tamper_rejects(self):
        path = self.root / "source_register.json"
        path.write_bytes(path.read_bytes() + b" ")
        self.assert_code("SIZE_MISMATCH", lambda: TheoryInspector(self.root))

    def test_index_path_escape_rejects(self):
        index = json.loads((self.root / "inspection_index.json").read_text())
        index["files"][0]["path"] = "../source_register.json"
        (self.root / "inspection_index.json").write_text(json.dumps(index), encoding="utf-8")
        self.assert_code("PATH_ESCAPE", lambda: TheoryInspector(self.root))

    def test_duplicate_json_key_rejects_even_when_hash_and_size_match_index(self):
        path = self.root / "source_register.json"
        text = path.read_text(encoding="utf-8").replace(
            '"schema": "docstream.relative-theory.sources/1",',
            '"schema": "docstream.relative-theory.sources/1",\n  "schema": "docstream.relative-theory.sources/1",', 1)
        path.write_text(text, encoding="utf-8")
        payload = path.read_bytes()
        index_path = self.root / "inspection_index.json"
        index = json.loads(index_path.read_text())
        index["files"][0]["bytes"] = len(payload)
        index["files"][0]["sha256"] = sha256(payload).hexdigest()
        index_path.write_text(json.dumps(index), encoding="utf-8")
        self.assert_code("DUPLICATE_JSON_KEY", lambda: TheoryInspector(self.root))

    def test_executable_field_rejects(self):
        path = self.root / "generic_relation_catalog.json"
        doc = json.loads(path.read_text())
        doc["records"][0]["command"] = "ignored"
        path.write_text(json.dumps(doc), encoding="utf-8")
        refresh_index_entry(self.root, path.name)
        self.assert_code("EXECUTABLE_FIELD", lambda: TheoryInspector(self.root))

    def test_missing_link_rejects(self):
        path = self.root / "wordnet_theory_crosswalk.json"
        doc = json.loads(path.read_text())
        doc["records"][0]["links"] = ["ABSENT"]
        path.write_text(json.dumps(doc), encoding="utf-8")
        refresh_index_entry(self.root, path.name)
        self.assert_code("MISSING_LINK", lambda: TheoryInspector(self.root))

    def test_duplicate_record_id_rejects(self):
        path = self.root / "generic_relation_catalog.json"
        doc = json.loads(path.read_text())
        doc["records"][1]["id"] = doc["records"][0]["id"]
        path.write_text(json.dumps(doc), encoding="utf-8")
        refresh_index_entry(self.root, path.name)
        self.assert_code("DUPLICATE_RECORD_ID", lambda: TheoryInspector(self.root))

    def test_file_total_and_record_caps_reject_exactly(self):
        self.assert_code("FILE_LIMIT", lambda: TheoryInspector(
            self.root, InspectorLimits(max_file_bytes=100)))
        self.assert_code("TOTAL_LIMIT", lambda: TheoryInspector(
            self.root, InspectorLimits(max_total_bytes=10_000)))
        self.assert_code("RECORD_LIMIT", lambda: TheoryInspector(
            self.root, InspectorLimits(max_records=5)))


class TheoryInspectorFuzzyErrorTests(StudyCopy):
    def test_seeded_120_bad_query_controls_reject_without_mutating_packet(self):
        inspector = TheoryInspector(self.root)
        before = tree_hashes(self.root)
        rng = random.Random(20261030)
        counts = {"limit": 0, "depth": 0, "missing": 0}
        for _case in range(120):
            family = rng.choice(tuple(counts))
            counts[family] += 1
            if family == "limit":
                self.assert_code("RESULT_LIMIT", lambda: inspector.relations(limit=rng.randint(1001, 5000)))
            elif family == "depth":
                self.assert_code("TRACE_DEPTH", lambda: inspector.trace("WN-REL-SIMILAR", rng.randint(17, 100)))
            else:
                self.assert_code("NOT_FOUND", lambda: inspector.one(f"missing-{rng.getrandbits(64):016x}"))
        self.assertTrue(all(counts.values()))
        self.assertEqual(tree_hashes(self.root), before)

    def test_seeded_200_arbitrary_search_strings_remain_bounded(self):
        inspector = TheoryInspector(self.root)
        rng = random.Random(18_200)
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789 !&+;:_-/"
        for _case in range(200):
            query = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 80)))
            rows = inspector.relations(query=query, limit=25)
            self.assertLessEqual(len(rows), 25)


class TheoryInspectorTortureTests(StudyCopy):
    def test_repeated_full_queries_and_traces_are_deterministic_and_read_only(self):
        inspector = TheoryInspector(self.root)
        before = tree_hashes(self.root)
        expected = inspector.trace("XW-SIMILAR", depth=16)
        for _ in range(500):
            self.assertEqual(inspector.trace("XW-SIMILAR", depth=16), expected)
            self.assertEqual(len(inspector.relations(limit=1000)), 44)
        self.assertEqual(tree_hashes(self.root), before)

    def test_trace_link_ceiling_returns_explicit_truncation(self):
        inspector = TheoryInspector(self.root, InspectorLimits(max_trace_links=1))
        trace = inspector.trace("XW-ADJECTIVE-MARKER-A", depth=16)
        self.assertTrue(trace["truncated"])
        self.assertEqual(trace["reason"], "TRACE_LINK_LIMIT")
        self.assertEqual(len(trace["edges"]), 1)


if __name__ == "__main__":
    unittest.main()
