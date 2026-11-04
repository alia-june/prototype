"""Independent oracle checks; deliberate failures must never become passes."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import unittest
from uuid import uuid4

from docstream_cpu.native_harness import runner as target
from docstream_cpu.native_harness_meta.checks import (
    Context, HARDENING, TORTURE, RUNS, encode, execute_mutation, fake_report,
    mutation_cases, recover_failed_then_pass, run_hardening)
from docstream_cpu.native_harness_meta.runner import FIXTURE, aggregate, audit_outer, run


class NativeHarnessMetaTests(unittest.TestCase):
    def setUp(self):
        RUNS.mkdir(parents=True, exist_ok=True)
        self.root = RUNS / ("verification-" + uuid4().hex)
        self.root.mkdir()
        self.ctx = Context(self.root)

    def test_mutations_are_repeatable_unique_and_have_exact_controls(self):
        a = list(mutation_cases())
        self.assertEqual(encode(a), encode(list(mutation_cases())))
        self.assertEqual(len({x["id"] for x in a}), 1000)
        self.assertEqual(Counter(x["expected"] for x in a), {"CONFIG_ERROR": 680, "FAIL": 120, "PASS": 200})
        self.assertNotEqual(encode(a), encode(list(mutation_cases(7))))

    def test_reviewed_fixture_selects_all_closed_checks(self):
        fixture = json.loads(FIXTURE.read_text())
        self.assertEqual(tuple(fixture["hardening"]), HARDENING)
        self.assertEqual(tuple(fixture["torture"]), TORTURE)
        self.assertEqual(fixture["mutations"], 1000)

    def test_configuration_rejection_happens_before_writes(self):
        before = set(RUNS.iterdir())
        for options in ({"mode": "shell"}, {"seed": True}, {"seconds": float("nan")},
                        {"seconds": 601}, {"run_id": "../escape"}):
            with self.subTest(options=options), self.assertRaises(ValueError): run(**options)
        self.assertEqual(before, set(RUNS.iterdir()))

    def test_outer_failure_has_precedence_over_interruption(self):
        self.assertEqual(aggregate([{"status": "FAIL"}], "interrupted"), "FAIL")
        self.assertEqual(aggregate([{"status": "PASS"}], "interrupted"), "INCOMPLETE")

    def test_outer_audit_rejects_forged_counts_and_missing_coverage(self):
        path = self.root / "input.json"; path.write_bytes(b"{}\n")
        row = {"case_id": "one", "input": "input.json", "input_sha256": sha256(path.read_bytes()).hexdigest(), "status": "PASS"}
        (self.root / "events.jsonl").write_bytes(encode({"event": "started", **row}) + b"\n" + encode({"event": "finished", **row}) + b"\n")
        result = {"status": "PASS", "cases": [row], "passed": 1, "failed": 0, "completed": 1}
        self.assertEqual(audit_outer(self.root, result, 1), [])
        self.assertTrue(audit_outer(self.root, result, 2))
        result["passed"] = 99
        self.assertIn("meta count mismatch: passed", audit_outer(self.root, result, 1))

    def test_real_journal_input_is_retained_before_actor_runs(self):
        self.assertEqual(run_hardening("preexecution_input", self.ctx)["observed"], "PASS")

    def test_clean_worker_control_retains_verified_input_hashes(self):
        code, root, result = fake_report(self.ctx)
        self.assertEqual((code, result["status"]), (0, "PASS"))
        for row in result["modes"][0]["cases"]:
            self.assertEqual(sha256((root / "fuzzy-error" / row["input"]).read_bytes()).hexdigest(), row["input_sha256"])

    def test_contradictory_journal_failure_is_not_lost(self):
        code, _, result = fake_report(self.ctx, "failure_journal")
        self.assertEqual((code, result["status"]), (1, "FAIL"))
        self.assertEqual(result["modes"][0]["failed"], 1)

    def test_invalid_summary_and_input_evidence_cannot_pass(self):
        for mutation in ("wrong_counts", "wrong_schema", "wrong_identity", "outside_input", "duplicate_row",
                         "tampered_input", "missing_input", "pending_journal", "bad_middle_event"):
            with self.subTest(mutation=mutation):
                code, _, result = fake_report(self.ctx, mutation)
                self.assertNotEqual(code, 0)
                self.assertNotEqual(result["status"], "PASS")

    def test_recovery_failure_is_sticky_after_later_pass(self):
        self.assertEqual(recover_failed_then_pass(self.ctx)["observed"], "FAIL")

    def test_wrong_error_expectation_is_a_detected_failure(self):
        item = next(x for x in mutation_cases() if x["input"]["kind"] == "oracle")
        self.assertEqual(execute_mutation(item, self.ctx)["observed"], "FAIL")


if __name__ == "__main__": unittest.main()
