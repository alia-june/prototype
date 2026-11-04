from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import uuid4

from docstream_cpu.native import Edit, NativeError, ascii_symbols
from docstream_cpu.native_harness.cases import (PROBES, RECIPES, SCENARIOS, case,
                                              error_case, fuzzy_cases)
from docstream_cpu.native_harness.core import (Budget, CheckFailed, Incomplete,
    Journal, RUNS, encoded, fingerprint, load_case, save, validate_case)
from docstream_cpu.native_harness.runner import recover_mode, run, supervise
from docstream_cpu.native_harness.workloads import execute, make, rejection


class NativeHarnessTests(unittest.TestCase):
    def setUp(self):
        RUNS.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="selftest-", dir=RUNS)
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(RUNS.resolve()))
        self.addCleanup(self.cleanup_owned_temp)

    def cleanup_owned_temp(self):
        self.assertTrue(self.root.is_relative_to(RUNS.resolve()))
        self.temp.cleanup()

    def example(self):
        return next(fuzzy_cases(20261029, 5))

    def test_generation_is_repeatable_and_has_exact_800_200_distribution(self):
        a, b = list(fuzzy_cases(20261029)), list(fuzzy_cases(20261029))
        self.assertEqual(encoded(a), encoded(b))
        self.assertEqual(Counter(x["family"] for x in a), {"error": 800, "valid": 200})
        self.assertEqual(set(x["input"]["recipe"] for x in a if x["family"] == "error"), set(RECIPES))
        self.assertEqual(set(Counter(x["input"]["recipe"] for x in a if x["family"] == "error").values()), {40})
        self.assertEqual(len({x["case_id"] for x in a}), 1000)
        for item in a: validate_case(item)

    def test_changed_seed_changes_cases(self):
        self.assertNotEqual(encoded(list(fuzzy_cases(1, 5))), encoded(list(fuzzy_cases(2, 5))))

    def test_input_is_saved_before_execution_with_exact_hash(self):
        journal = Journal(self.root / "journal", "fuzzy-error", Budget())
        item = self.example()

        def checked(case_data, budget, root):
            inputs = list((root / "inputs").glob("*.json"))
            self.assertEqual(len(inputs), 1)
            self.assertEqual(load_case(inputs[0]), item)
            return execute(case_data, budget, root)

        journal.record(item, checked)
        result = journal.finish()
        path = journal.root / result["cases"][0]["input"]
        self.assertEqual(sha256(path.read_bytes()).hexdigest(), result["cases"][0]["input_sha256"])
        self.assertEqual(result["status"], "PASS")

    def test_invalid_unicode_is_retained_as_escaped_replay_data(self):
        import random
        item = error_case("literal_unicode", 1, random.Random(1))
        target = self.root / "surrogate.json"
        save(target, item)
        self.assertIn(b"\\ud800", target.read_bytes())
        self.assertEqual(load_case(target), item)
        self.assertTrue(execute(item, Budget(), self.root)["expected_rejection"])

    def test_replay_rejects_unknown_families_names_and_executable_fields(self):
        original = self.example()
        examples = []
        for field, value in [("family", "exec"), ("mode", "shell"), ("seed", True)]:
            altered = deepcopy(original); altered[field] = value; examples.append(altered)
        altered = deepcopy(original); altered["command"] = "ignored"; examples.append(altered)
        examples.append(case("unknown", "torture", "scenario", {"name": "os.system"}))
        examples.append(case("unknown", "hardening", "probe", {"name": "eval"}))
        for item in examples:
            with self.subTest(item=item):
                with self.assertRaises((ValueError, TypeError)): validate_case(item)

    def test_replay_rejects_duplicate_keys_and_oversized_files(self):
        target = self.root / "bad.json"
        target.write_text('{"schema":"x","schema":"y"}', encoding="utf-8")
        with self.assertRaises(ValueError): load_case(target)
        target.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        with self.assertRaises(ValueError): load_case(target)

    def test_replay_rejects_malformed_hex_and_expected_error_schema(self):
        item = self.example()
        item["input"] = {"recipe": "literal_highbyte", "variant": 0, "value": "x"}
        with self.assertRaises(ValueError): validate_case(item)
        item = self.example(); item["expected"]["code"] = "ANY_EXCEPTION"
        with self.assertRaises(ValueError): validate_case(item)

    def test_wrong_exception_type_and_code_are_failures(self):
        model, base = make()
        with self.assertRaises(CheckFailed) as caught:
            rejection(model, lambda: (_ for _ in ()).throw(KeyError("synthetic")),
                      {"exception": "NativeError", "code": "VALIDATION_ERROR"})
        self.assertEqual(caught.exception.tag, "wrong_error_type")
        with self.assertRaises(CheckFailed) as caught:
            rejection(model, lambda: (_ for _ in ()).throw(NativeError("INVALID_PATH", "synthetic")),
                      {"exception": "NativeError", "code": "VALIDATION_ERROR"})
        self.assertEqual(caught.exception.tag, "wrong_error_code")

    def test_state_change_is_detected_even_with_expected_exception(self):
        model, base = make()

        def corrupted():
            model.apply_batch(base.stream_id, (Edit("x", "replace", (), 0, 1, ascii_symbols("X")),))
            raise NativeError("VALIDATION_ERROR", "synthetic after publication")

        with self.assertRaises(CheckFailed) as caught:
            rejection(model, corrupted, {"exception": "NativeError", "code": "VALIDATION_ERROR"})
        self.assertEqual(caught.exception.tag, "state_changed")

    def test_failed_case_is_replayable_and_shrinking_preserves_failure(self):
        import random
        item = error_case("operation_id", 3, random.Random(1), case_id="synthetic")
        journal = Journal(self.root / "failure", "fuzzy-error", Budget())

        def fail(case_data, budget, root):
            raise CheckFailed("synthetic", "controlled harness self-test failure")

        journal.record(item, fail)
        result = journal.finish()
        self.assertEqual(result["status"], "FAIL")
        row = result["cases"][0]
        self.assertEqual(load_case(journal.root / row["replay"]), item)
        reduced = load_case(journal.root / row["reduced_replay"])
        self.assertEqual(reduced["input"]["value"], "")
        self.assertLessEqual(row["shrink_trials"], 12)

    def test_observed_failure_keeps_precedence_when_shrinking_is_interrupted(self):
        import random
        item = error_case("operation_id", 3, random.Random(1), case_id="interrupted")
        journal = Journal(self.root / "interrupted", "fuzzy-error", Budget())
        calls = 0

        def interrupted(case_data, budget, root):
            nonlocal calls
            calls += 1
            if calls > 1: raise Incomplete("controlled shrink timeout")
            raise CheckFailed("synthetic", "controlled initial failure")

        with self.assertRaises(Incomplete): journal.record(item, interrupted)
        result = journal.finish("controlled shrink timeout")
        self.assertEqual(result["status"], "FAIL")
        recovered = recover_mode(journal.root, "fuzzy-error", "supervisor stopped worker")
        self.assertEqual(recovered["status"], "FAIL")
        self.assertEqual(recovered["failed"], 1)

    def test_interrupted_journal_does_not_claim_a_pass(self):
        journal = Journal(self.root / "pending", "fuzzy-error", Budget())
        journal.event("case_started", case_id="pending")
        journal.events.close()
        with (journal.root / "events.jsonl").open("ab") as target: target.write(b'{"unfinished":')
        recovered = recover_mode(journal.root, "fuzzy-error", "controlled interruption")
        self.assertEqual(recovered["status"], "INCOMPLETE")
        self.assertEqual(recovered["interrupted_cases"], ["pending"])

    def test_attempt_budget_counts_rejected_submissions_without_publishing(self):
        model, base = make()
        budget = Budget(max_attempts=1)
        before = fingerprint(model)
        with self.assertRaises(Incomplete):
            budget.apply(model, base.stream_id, (Edit("a", "remove", (), 0, 1), Edit("b", "remove", (), 0, 1)))
        self.assertEqual(fingerprint(model), before)
        with self.assertRaises(NativeError): budget.apply(model, base.stream_id, [])
        self.assertEqual(budget.attempts, 1)
        self.assertEqual(fingerprint(model), before)

    def test_evidence_budget_returns_incomplete_before_case_execution(self):
        journal = Journal(self.root / "small", "fuzzy-error", Budget(max_bytes=10))
        with self.assertRaises(Incomplete): journal.record(self.example(), execute)
        result = journal.finish("controlled evidence cap")
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(list((journal.root / "inputs").iterdir()), [])

    def test_configuration_and_mode_mismatch_are_rejected_before_run_creation(self):
        for options in [dict(seed=True), dict(seed=-1), dict(fuzzy_count=6), dict(seconds=float("nan")), dict(run_id="../escape")]:
            with self.subTest(options=options):
                with self.assertRaises(ValueError): run(**options)
        target = self.root / "case.json"; save(target, self.example())
        with self.assertRaises(ValueError): run("torture", replay=target)

    def test_real_supervisor_timeout_stops_its_owned_child(self):
        command = [sys.executable, "-m", "docstream_cpu.native_harness.worker", "--stall-ready", str(self.root / "ready.json")]
        outcome = supervise(command, self.root / "child.log", 0.2, self.root, 512 * 1024 * 1024)
        self.assertEqual(outcome["supervisor_reason"], "supervisor wall-clock deadline")
        self.assertTrue(outcome["owned_child_stopped"])

    def test_smoke_run_replay_and_existing_run_refusal(self):
        run_id = "selftest-smoke-" + uuid4().hex
        code, root, summary = run("fuzzy-error", fuzzy_count=5, seconds=30, run_id=run_id)

        def cleanup_run():
            self.assertTrue(root.resolve().is_relative_to(RUNS.resolve()))
            shutil.rmtree(root)

        self.addCleanup(cleanup_run)
        self.assertEqual(code, 0)
        self.assertEqual(summary["modes"][0]["passed"], 5)
        path = root / "fuzzy-error" / summary["modes"][0]["cases"][0]["input"]
        before = (root / "REPORT.md").read_bytes()
        with self.assertRaises(FileExistsError): run("hardening", run_id=run_id)
        self.assertEqual((root / "REPORT.md").read_bytes(), before)
        replay_id = "selftest-replay-" + uuid4().hex
        code, replay_root, result = run("all", replay=path, run_id=replay_id, seconds=30)

        def cleanup_replay():
            self.assertTrue(replay_root.resolve().is_relative_to(RUNS.resolve()))
            shutil.rmtree(replay_root)

        self.addCleanup(cleanup_replay)
        self.assertEqual(code, 0)
        self.assertEqual(len(result["modes"]), 1)
        self.assertEqual(result["modes"][0]["mode"], "fuzzy-error")


if __name__ == "__main__":
    unittest.main()
