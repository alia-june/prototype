import ast
import copy
import json
from pathlib import Path
import unittest

from code_lexigraph import ConstructionError, rehydrate

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples" / "safe_fallthrough.bundle.json"
REFERENCE = ROOT / "examples" / "reference.py"
REQUIRED = '{"items":[{"value":1}],"meta":{"revision":1}}'
BASELINE = {"items": [{"value": 1}], "meta": {"revision": 1}}


class RehydrationTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))

    def example(self):
        result = rehydrate(self.bundle)
        namespace = {}
        exec(compile(result["python"], "<declared-example>", "exec"), namespace)
        return namespace

    def test_three_constructions_and_input_preservation(self):
        original = copy.deepcopy(self.bundle)
        first = rehydrate(self.bundle)
        second = rehydrate(copy.deepcopy(self.bundle))
        third = rehydrate(json.loads(json.dumps(self.bundle, sort_keys=True)))
        self.assertEqual(first, second)
        self.assertEqual(first, third)
        self.assertEqual(self.bundle, original)

    def test_reference_python_syntax_structure(self):
        rebuilt = rehydrate(self.bundle)["python"]
        reference = REFERENCE.read_text(encoding="utf-8")
        self.assertEqual(
            ast.dump(ast.parse(rebuilt), include_attributes=False),
            ast.dump(ast.parse(reference), include_attributes=False),
        )

    def test_locations_inverse_mappings_and_construction_coverage(self):
        result = rehydrate(self.bundle)
        tree = ast.parse(result["python"])
        functions = {
            node.name: node for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }
        system = functions["system_run"]
        locations = {
            "C01": next(node.lineno for node in tree.body
                        if isinstance(node, ast.ClassDef) and node.name == "State"),
            "C02": functions["decode_working_json"].lineno,
            "C03": system.lineno,
            "C04": next(node.lineno for node in ast.walk(system)
                        if isinstance(node, ast.If)
                        and ast.unparse(node.test) == "gate is State.ERROR"),
            "C05": next(node.lineno for node in ast.walk(system)
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "working"
                                for target in node.targets)),
            "C06": next(node.lineno for node in ast.walk(system)
                        if isinstance(node, ast.Expr)
                        and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Name)
                        and node.value.func.id == "operation"),
            "C07": next(node.lineno for node in ast.walk(system)
                        if isinstance(node, ast.ExceptHandler)),
            "C08": functions["make_report"].lineno,
        }
        self.assertEqual(len(result["spans"]), 22)
        self.assertEqual(len(result["trace"]), 8)
        for link in result["trace"]:
            self.assertEqual(link["generated"]["start"], locations[link["code"]])
            for ref in [link["code"]] + link["meanings"]:
                self.assertIn(link["blueprint"], result["inverse"][ref])
        for support in self.bundle["supporting_declarations"]:
            for ref in support["supports"]:
                self.assertIn(support["blueprint"], result["inverse"][ref])

    def test_successful_nested_mutation_preserves_selected_survivor(self):
        namespace, views = self.example(), []

        def operation(working):
            views.append(working)
            working["items"][0]["value"] = 2
            working["meta"]["revision"] = 2

        report = namespace["system_run"](REQUIRED, namespace["State"].READY, operation)
        self.assertEqual(report["state"], "complete")
        self.assertIs(report["survivor"], REQUIRED)
        self.assertEqual(json.loads(report["survivor"]), BASELINE)
        self.assertEqual(views[0]["items"][0]["value"], 2)

    def test_mutation_then_exception_preserves_survivor_and_system_response(self):
        namespace, views = self.example(), []

        def operation(working):
            views.append(working)
            working["items"][0]["value"] = 99
            working["meta"]["revision"] = 99
            raise RuntimeError("deliberate example exception")

        report = namespace["system_run"](REQUIRED, namespace["State"].READY, operation)
        self.assertEqual(report["state"], "exception")
        self.assertEqual(report["response"], "RuntimeError")
        self.assertIs(report["survivor"], REQUIRED)
        self.assertEqual(json.loads(REQUIRED), BASELINE)
        self.assertEqual(views[0]["items"][0]["value"], 99)
        self.assertEqual(views[0]["meta"]["revision"], 99)

    def test_error_gate_blocks_decoder_and_operation(self):
        namespace = self.example()
        counts = {"decode": 0, "operation": 0}
        original_decode = namespace["decode_working_json"]

        def decoder(text):
            counts["decode"] += 1
            return original_decode(text)

        def operation(working):
            counts["operation"] += 1
            raise RuntimeError("must not execute")

        namespace["decode_working_json"] = decoder
        report = namespace["system_run"](REQUIRED, namespace["State"].ERROR, operation)
        self.assertEqual(report["state"], "error")
        self.assertEqual(report["response"], "operation skipped")
        self.assertIs(report["survivor"], REQUIRED)
        self.assertEqual(counts, {"decode": 0, "operation": 0})

    def test_independent_nested_working_representations(self):
        namespace, views = self.example(), []

        def operation(working):
            views.append(working)

        for _ in range(2):
            report = namespace["system_run"](
                REQUIRED, namespace["State"].READY, operation
            )
            self.assertEqual(report["state"], "complete")
            self.assertIs(report["survivor"], REQUIRED)
        self.assertIsNot(views[0], views[1])
        self.assertIsNot(views[0]["items"], views[1]["items"])
        self.assertIsNot(views[0]["items"][0], views[1]["items"][0])
        self.assertIsNot(views[0]["meta"], views[1]["meta"])
        views[0]["items"][0]["value"] = 999
        self.assertEqual(views[1]["items"][0]["value"], 1)
        self.assertEqual(json.loads(REQUIRED), BASELINE)

    def test_missing_survivor_binding_refused(self):
        del self.bundle["bindings"]["survivor"]
        with self.assertRaisesRegex(ConstructionError, "missing binding: survivor"):
            rehydrate(self.bundle)

    def test_unresolved_survivor_binding_refused(self):
        self.bundle["bindings"]["survivor"]["status"] = "unresolved"
        with self.assertRaisesRegex(ConstructionError, "unresolved binding: survivor"):
            rehydrate(self.bundle)

    def test_missing_construction_target_refused(self):
        self.bundle["construction_links"][0]["blueprint"] = "B-MISSING"
        with self.assertRaisesRegex(
            ConstructionError, "unresolved construction: B-MISSING"
        ):
            rehydrate(self.bundle)

    def test_unknown_construction_instruction_refused(self):
        self.bundle["module"][0]["op"] = "invent_default"
        with self.assertRaisesRegex(
            ConstructionError, "unknown statement: invent_default"
        ):
            rehydrate(self.bundle)


if __name__ == "__main__":
    unittest.main()
