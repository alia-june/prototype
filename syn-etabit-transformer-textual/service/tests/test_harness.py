from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from docstream_cpu.harness.cases import execute_case
from docstream_cpu.harness.core import BudgetExceeded, CheckFailed, Journal, RUNS_ROOT, encoded, load_case, semantic_meaning
from docstream_cpu.harness.generate import case, generate
from docstream_cpu.harness.runner import OwnedProcess, main, prestart_result, recover_interrupted
from docstream_cpu.harness.worker import Context, minimize, regression_ids
from docstream_cpu.models import Properties, Style
from docstream_cpu.rich import RichBlock, Snapshot2, Span

RUNS_ROOT.mkdir(parents=True,exist_ok=True)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="harness-selftest-",dir=RUNS_ROOT)
        self.root=Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_generator_is_seeded_and_covers_eight_categories(self):
        first=list(generate(52,80))
        self.assertEqual(encoded(first),encoded(list(generate(52,80))))
        self.assertNotEqual(encoded(first),encoded(list(generate(53,80))))
        self.assertEqual(len({v["kind"] for v in first}),6)  # eight categories, three batch variants

    def test_closed_regression_selection_is_the_existing_117(self):
        ids=list(regression_ids())
        self.assertEqual(len(ids),117)
        self.assertFalse(any("test_harness" in ident for ident in ids))

    def test_preserved_baseline_alias_is_replayable(self):
        result=execute_case(case("regression",{"test_id":"docstream_baseline_tests.DocstreamTests.test_match_guard_prevents_write"},1),self.root)
        self.assertEqual(result["tests_run"],1)

    def test_projection_ignores_only_span_fragmentation_and_inheritance(self):
        props=Properties(font_family="Arial")
        a=Snapshot2(properties=props,blocks=(RichBlock(block_id="a",text="onetwo",runs=(Span(text="one"),Span(text="two"))),))
        b=Snapshot2(properties=props,blocks=(RichBlock(block_id="b",text="onetwo",runs=(Span(text="onetwo",style=Style(font_family="Arial",bold=False)),)),))
        c=Snapshot2(properties=props,blocks=(RichBlock(block_id="b",text="onetwo",runs=(Span(text="onetwo",style=Style(bold=True)),)),))
        self.assertEqual(semantic_meaning(a),semantic_meaning(b))
        self.assertNotEqual(semantic_meaning(a),semantic_meaning(c))

    def test_replay_rejects_unknown_kind_and_nondata_fields(self):
        path=self.root/"bad.json"
        for value in (case("execute_shell",{},1),{**case("batch",{},1),"command":"no"}):
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                load_case(path)

    def test_replay_is_bounded_and_regression_id_is_closed(self):
        path=self.root/"large.json"
        path.write_bytes(b"x"*(2*1024*1024+1))
        with self.assertRaises(ValueError):
            load_case(path)
        with self.assertRaises(ValueError):
            execute_case(case("regression",{"test_id":"os.system"},1),self.root)

    def test_case_files_preserve_surrogates_as_json_data(self):
        value=case("invalid_request",{"request":{"text":"\ud800"}},1)
        path=self.root/"case.json"
        path.write_bytes(encoded(value))
        self.assertEqual(load_case(path),value)

    def test_failure_is_retained_and_replayable(self):
        journal=Journal(self.root/"run","fuzzy",1)
        value=case("batch",{},1)
        def fail():
            raise CheckFailed("retained failure")
        item=journal.record("case",value,fail)
        result=journal.finish()
        self.assertEqual(result["status"],"failed")
        self.assertEqual(load_case(item["replay_file"]),value)

    def test_passing_case_input_is_also_retained(self):
        journal=Journal(self.root/"passing","fuzzy",1)
        value=case("batch",{},1)
        item=journal.record("pass",value,lambda:{"checked":True})
        self.assertEqual(load_case(item["input_file"]),value)
        self.assertEqual(journal.finish()["status"],"passed")

    def test_replay_mode_cannot_bypass_torture_accounting(self):
        path=self.root/"replay.json"
        path.write_bytes(encoded(case("network_load",{"requests":4},1)))
        self.assertEqual(main(["fuzzy","--replay",str(path)]),3)

    def test_time_and_byte_cutoffs_are_incomplete(self):
        for name,kwargs in (("time",{"seconds":-1}),("bytes",{"max_bytes":1})):
            journal=Journal(self.root/name,"fuzzy",1,**kwargs)
            try:
                journal.check_budget()
            except BudgetExceeded as exc:
                journal.incomplete.append(str(exc))
            self.assertEqual(journal.finish()["status"],"incomplete")

    def test_budget_counter_never_executes_above_limit(self):
        journal=Journal(self.root/"budget","torture",1)
        context=Context(journal,render_budget=1,api_budget=2)
        context.spend("render")
        with self.assertRaises(BudgetExceeded):
            context.spend("render")
        self.assertEqual(context.render_calls,1)
        self.assertEqual(journal.finish()["status"],"incomplete")

    def test_interrupted_result_recovers_completed_events(self):
        journal=Journal(self.root/"interrupt","fuzzy",1)
        journal.record("completed",case("batch",{},1),lambda:{"checked":True})
        journal._journal.close()
        result=recover_interrupted(journal.root,"fuzzy",1,"test interruption")
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["counts"],{"passed":1})

    def test_interruption_does_not_hide_an_earlier_failure(self):
        journal=Journal(self.root/"partial","fuzzy",1)
        def fail():
            raise CheckFailed("real failure")
        journal.record("failed",case("batch",{},1),fail)
        journal._journal.close()
        result=recover_interrupted(journal.root,"fuzzy",1,"interrupted")
        self.assertEqual(result["status"],"failed")
        self.assertFalse(result["coverage_complete"])

    def test_shrinker_preserves_the_failure_signature(self):
        value=case("batch",{"batch":{"operations":[{"x":1},{"x":7},{"x":2},{"x":3}]}},1)
        def oracle(candidate):
            if any(op["x"]==7 for op in candidate["input"]["batch"]["operations"]):
                raise CheckFailed("same issue")
        reduced,report=minimize(value,oracle,max_attempts=20)
        self.assertEqual(reduced["input"]["batch"]["operations"],[{"x":7}])
        self.assertTrue(report["reproduced"])
        self.assertLessEqual(report["attempts"],20)

    def test_owned_process_cleanup_terminates_only_its_child(self):
        with (self.root/"output.txt").open("wb") as log:
            owned=OwnedProcess([sys.executable,"-c","import time; time.sleep(30)"],log)
            self.assertIsNone(owned.process.poll())
            owned.close()
            self.assertIsNotNone(owned.process.poll())

    def test_cli_rejects_scope_expansion_before_creating_run(self):
        self.assertEqual(main(["fuzzy","--cases","501"]),3)
        self.assertEqual(main(["torture","--max-seconds","1201"]),3)

    def test_unknown_cli_option_is_a_configuration_error(self):
        self.assertEqual(main(["fuzzy","--unknown-option"]),3)

    def test_supervisor_deadline_produces_incomplete_and_stops_child(self):
        with patch("docstream_cpu.harness.runner.RUNS_ROOT",self.root/"runs"):
            self.assertEqual(main(["fuzzy","--cases","8","--max-seconds","0.05","--run-id","deadline"]),2)
        summary=json.loads((self.root/"runs"/"deadline"/"summary.json").read_text())
        self.assertEqual(summary["status"],"incomplete")
        self.assertTrue(summary["modes"][0]["owned_worker_stopped"])
        result=prestart_result("fuzzy",17,"controlled pre-start budget")
        self.assertFalse(result["owned_worker_started"])
        self.assertIsNone(result["owned_worker_pid"])
        self.assertIsNone(result["owned_worker_stopped"])
        self.assertEqual(result["owned_cleanup"]["status"],"not_started")
        self.assertEqual(result["cases"],[])
        with patch("docstream_cpu.harness.runner.RUNS_ROOT",self.root/"prestart-runs"):
            self.assertEqual(main(["fuzzy","--max-mib","0.000001","--run-id","prestart"]),2)
        summary=json.loads((self.root/"prestart-runs"/"prestart"/"summary.json").read_text())
        self.assertEqual(summary["modes"][0],prestart_result("fuzzy",20261029,"combined run budget reached before mode start"))


if __name__=="__main__":
    unittest.main()
