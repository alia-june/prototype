from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from docstream_cpu.harness_meta.audit import AuditError, audit_run, strict_json
from docstream_cpu.harness_meta.cases import HARDENING, MUTATIONS, TORTURE, fuzzy_cases
from docstream_cpu.harness_meta.checks import clean_packet, check_packet
from docstream_cpu.harness_meta.runner import (FIXTURE, audit_outer, run,
                                                target_hashes)


class HarnessMetaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness-meta-test-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_reviewed_contract_matches_closed_case_sets(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(tuple(fixture["hardening"]), HARDENING)
        self.assertEqual(tuple(fixture["torture"]), TORTURE)
        self.assertEqual(fixture["fuzzy_cases"], 1000)

    def test_fuzzy_generation_is_reproducible_and_exactly_800_200(self):
        first, second = list(fuzzy_cases()), list(fuzzy_cases())
        self.assertEqual(first, second)
        self.assertEqual(Counter(row["family"] for row in first), {"invalid": 800, "control": 200})
        self.assertEqual(Counter(row["mutation"] for row in first if row["family"] == "invalid"),
                         {name: 40 for name in MUTATIONS})
        self.assertEqual(len({row["case_id"] for row in first}), 1000)

    def test_clean_packet_passes_and_all_closed_mutations_reject(self):
        self.assertEqual(check_packet(self.root, "clean_control", "clean")["observed"], "PASS")
        for number, mutation in enumerate(MUTATIONS):
            with self.subTest(mutation=mutation):
                result = check_packet(self.root, mutation, f"mutation-{number}")
                self.assertEqual(result["observed"], "REJECT")
                self.assertTrue(result["issues"])

    def test_strict_json_rejects_duplicate_keys_and_size(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"x":1,"x":2}', encoding="utf-8")
        with self.assertRaises(AuditError) as caught: strict_json(duplicate)
        self.assertEqual(caught.exception.code, "DUPLICATE_JSON_KEY")
        large = self.root / "large.json"; large.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        with self.assertRaises(AuditError) as caught: strict_json(large)
        self.assertEqual(caught.exception.code, "JSON_LIMIT")

    def test_failure_and_incomplete_cannot_be_demoted(self):
        failed = check_packet(self.root, "contradictory_event", "failed")
        incomplete = check_packet(self.root, "passed_without_coverage", "incomplete")
        self.assertTrue(any("FAILURE_DEMOTED" in issue for issue in failed["issues"]))
        self.assertTrue(any("INCOMPLETE_DEMOTED" in issue for issue in incomplete["issues"]))

    def test_incomplete_zero_case_mode_may_precede_event_journal(self):
        packet = clean_packet(self.root / "prejournal")
        summary = json.loads((packet / "summary.json").read_text())
        mode = summary["modes"][0]
        mode.update(status="incomplete", coverage_complete=False, cases=[], counts={},
                    owned_worker_started=False, owned_worker_pid=None,
                    owned_worker_stopped=None, owned_job_stopped=None,
                    owned_cleanup={"status":"not_started","scope":"none","job_assigned":False})
        (packet / "rigid/events.jsonl").unlink()
        (packet / "rigid/cleanup.json").unlink()
        (packet / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        issues = audit_run(packet)
        self.assertFalse(any("MISSING_EVENTS" in issue for issue in issues))

    def test_outer_audit_rejects_tampered_retained_input(self):
        mode = self.root / "mode"; (mode / "inputs").mkdir(parents=True)
        payload = b'{"schema":"docstream.harness-meta.case/1"}\n'
        path = mode / "inputs/case.json"; path.write_bytes(payload)
        row = {"case_id": "one", "status": "PASS", "input": "inputs/case.json",
               "input_sha256": sha256(payload).hexdigest()}
        result = {"status": "PASS", "counts": {"PASS": 1}, "cases": [row]}
        self.assertEqual(audit_outer(mode, result, 1), [])
        path.write_bytes(b"{}\n")
        self.assertIn("meta input hash mismatch", audit_outer(mode, result, 1))

    def test_small_hardening_and_fuzzy_runs_preserve_target(self):
        runs = self.root / "runs"; before = target_hashes()
        with patch("docstream_cpu.harness_meta.runner.RUNS", runs):
            hard_code, _, hard = run("hardening", run_id="hardening", seconds=120, fuzzy_count=20)
            fuzzy_code, _, fuzzy = run("fuzzy", run_id="fuzzy", seconds=120, fuzzy_count=20)
        self.assertEqual((hard_code, hard["status"]), (0, "PASS"))
        self.assertEqual((fuzzy_code, fuzzy["status"]), (0, "PASS"))
        self.assertEqual(target_hashes(), before)

    def test_configuration_rejects_before_run_creation(self):
        runs = self.root / "runs"
        with patch("docstream_cpu.harness_meta.runner.RUNS", runs):
            for kwargs in ({"seed": True}, {"seconds": 901}, {"fuzzy_count": 6},
                           {"run_id": "../escape"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): run(**kwargs)
        self.assertFalse(runs.exists())


if __name__ == "__main__":
    unittest.main()
