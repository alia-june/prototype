from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import random
import time
import unittest
from unittest.mock import patch

from docstream_cpu.native import (AssemblyRef, Edit, Layer, Limits, NativeError,
                                 NativeModel, SymbolRef, ascii_symbols)


FIXTURE = Path(__file__).parent / "fixtures" / "native" / "assemblies.json"


def fixture_model():
    model, refs = NativeModel(), {}
    records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for entry in records["definitions"]:
        children = tuple(SymbolRef(x) if type(x) is int else refs[x] for x in entry["children"])
        ref = model.define(Layer[entry["layer"]], children)
        refs[entry["label"]] = ref
    return model, refs, records


def literal_model(value=b"abc", limits=None):
    model = NativeModel(limits)
    root = model.define(Layer.DOCUMENT, ascii_symbols(value))
    return model, model.create_stream(root)


class NativeRigidTests(unittest.TestCase):
    def assert_code(self, code, action):
        with self.assertRaises(NativeError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_all_128_symbols_have_distinct_exact_values(self):
        model = NativeModel()
        self.assertEqual(len(model.alphabet.symbols), 128)
        self.assertEqual(len(set(model.alphabet.symbols)), 128)
        self.assertEqual(b"".join(model.expand(ref) for ref in model.alphabet.symbols), bytes(range(128)))

    def test_full_alphabet_round_trip_including_every_control(self):
        model, stream = literal_model(bytes(range(128)))
        self.assertEqual(model.expand_stream(stream.stream_id), bytes(range(128)))
        self.assertEqual(ast.literal_eval(model.escaped(stream.stream_id)).encode("ascii"), bytes(range(128)))
        self.assertFalse(any(ord(c) < 32 or ord(c) == 127 for c in model.escaped(stream.stream_id)))

    def test_fixture_has_fixed_external_expectations(self):
        model, refs, records = fixture_model()
        for entry in records["definitions"]:
            with self.subTest(label=entry["label"]):
                self.assertEqual(model.expand(refs[entry["label"]]), bytes.fromhex(entry["expected_hex"]))

    def test_hyphen_is_an_emitted_symbol(self):
        model, refs, _ = fixture_model()
        self.assertEqual(model.expand(refs["hyphen_ette"]), b"-ette")
        self.assertNotEqual(refs["hyphen_ette"], refs["ette"])
        self.assertEqual(model.expand(SymbolRef(45)), b"-")

    def test_unchanged_content_has_distinct_structural_layers(self):
        model, refs, _ = fixture_model()
        self.assertEqual(model.expand(refs["er"]), model.expand(refs["component_er"]))
        self.assertNotEqual(refs["er"], refs["component_er"])
        self.assertEqual(model.expand(refs["un"]), model.expand(refs["component_un"]))

    def test_case_whitespace_and_return_bytes_are_not_normalized(self):
        data = b" A\ta\r\nB\n\r \x00\x7f"
        model, stream = literal_model(data)
        self.assertEqual(model.expand_stream(stream.stream_id), data)
        self.assertNotEqual(model.expand(SymbolRef(10)), model.expand(SymbolRef(13)))

    def test_reject_non_ascii_without_substitution(self):
        for value in ["caf\u00e9", "\u20ac", "\ud800", b"\x80", b"\xff"]:
            with self.subTest(value=repr(value)):
                self.assert_code("VALIDATION_ERROR", lambda: ascii_symbols(value))

    def test_strict_values_reject_coercions_and_mutable_containers(self):
        for value in [-1, 128, True, 65.0, "65", None]:
            self.assert_code("VALIDATION_ERROR", lambda: SymbolRef(value))
        model = NativeModel()
        for layer, children in [(1, (SymbolRef(65),)), ("glyph", ()), (Layer.GLYPH, []), (Layer.GLYPH, (65,))]:
            self.assert_code("VALIDATION_ERROR", lambda: model.define(layer, children))
        for value in [bytearray(b"a"), [65], None]:
            self.assert_code("VALIDATION_ERROR", lambda: ascii_symbols(value))

    def test_catalog_and_values_are_immutable_through_public_views(self):
        model, stream = literal_model()
        definition = model.definition(stream.root)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            definition.children = ()
        with self.assertRaises(TypeError):
            model.definitions[stream.root.definition_id] = definition
        snapshot = model.definitions
        model.define(Layer.GLYPH, ascii_symbols("xy"))
        self.assertEqual(len(snapshot), 1)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            model.alphabet.symbols = ()

    def test_detached_records_and_stats_cannot_modify_payload(self):
        model, stream = literal_model()
        record = model.definition(stream.root).to_record()
        self.assertEqual(set(record), {"schema_version", "profile", "layer", "children"})
        record["children"][0]["value"] = 90
        stats = model.stats()
        stats["streams"] = 0
        self.assertEqual(model.expand_stream(stream.stream_id), b"abc")
        self.assertEqual(model.stats()["streams"], 1)

    def test_identical_definitions_share_but_streams_do_not(self):
        a, first = literal_model()
        duplicate = a.define(Layer.DOCUMENT, ascii_symbols("abc"))
        second = a.create_stream(duplicate)
        b, other = literal_model()
        self.assertEqual(a.stats()["definitions"], 1)
        self.assertEqual(first.root, duplicate)
        self.assertEqual(first.root, other.root)
        self.assertNotEqual(first.stream_id, second.stream_id)
        self.assertNotEqual(first.stream_id, other.stream_id)
        self.assertEqual(b.expand_stream(other.stream_id), b"abc")

    def test_missing_reference_does_not_publish_a_definition(self):
        model = NativeModel()
        before = model.stats()
        self.assert_code("UNKNOWN_REFERENCE", lambda: model.define(Layer.GLYPH, (AssemblyRef("0" * 64),)))
        self.assertEqual(model.stats(), before)

    def test_equal_or_upward_edges_are_rejected_preventing_cycles(self):
        model = NativeModel()
        glyph = model.define(Layer.GLYPH, ascii_symbols("ab"))
        component = model.define(Layer.COMPONENT, (glyph,))
        before = model.stats()
        for layer, child in [(Layer.GLYPH, glyph), (Layer.GLYPH, component), (Layer.COMPONENT, component)]:
            self.assert_code("LAYER_MISMATCH", lambda: model.define(layer, (child,)))
            self.assertEqual(model.stats(), before)

    def test_each_layer_can_explicitly_reference_lower_layers(self):
        model = NativeModel()
        ref = model.define(Layer.GLYPH, ascii_symbols("x"))
        for layer in list(Layer)[1:]:
            ref = model.define(layer, (ref,))
        stream = model.create_stream(ref)
        self.assertEqual(model.expand_stream(stream.stream_id), b"x")
        self.assertEqual(model.inspect(stream.stream_id, (0,) * 8).reference, SymbolRef(120))

    def test_shared_word_edit_changes_only_selected_occurrence(self):
        model, refs, _ = fixture_model()
        base = model.create_stream(refs["document"])
        result = model.apply_batch(base.stream_id, (Edit("capital", "replace", (0, 0, 0, 0), 0, 1, ascii_symbols("M")),))
        self.assertEqual(model.expand_stream(result.result_stream_id), b"Marionette marionette.\r\n")
        self.assertEqual(model.expand_stream(base.stream_id), b"marionette marionette.\r\n")
        self.assertEqual(model.expand(refs["marionette"]), b"marionette")
        self.assertEqual(model.inspect(result.result_stream_id, (0, 0, 2)).reference, refs["marionette"])

    def test_insert_remove_replace_are_ordered_and_intermediates_addressable(self):
        model, base = literal_model()
        operations = (Edit("insert", "insert", (), 1, 0, ascii_symbols("XY")),
                      Edit("remove", "remove", (), 3, 1),
                      Edit("replace", "replace", (), 0, 1, ascii_symbols("Z")))
        result = model.apply_batch(base.stream_id, operations)
        expected = [b"aXYbc", b"aXYc", b"ZXYc"]
        for i in (2, 0, 1):
            self.assertEqual(model.expand_stream(result.output_stream_ids[i]), expected[i])
        self.assertEqual(model.batch(result.batch_id).operations, operations)
        self.assertEqual([s.operation_id for s in model.history(result.result_stream_id)], [None, "insert", "remove", "replace"])

    def test_noop_and_return_to_original_reuse_definition_keep_occurrences(self):
        model, base = literal_model()
        operations = (Edit("same", "replace", (), 0, 1, ascii_symbols("a")),
                      Edit("change", "replace", (), 0, 1, ascii_symbols("z")),
                      Edit("restore", "replace", (), 0, 1, ascii_symbols("a")))
        result = model.apply_batch(base.stream_id, operations)
        self.assertEqual(model.stream(result.output_stream_ids[0]).root, base.root)
        self.assertEqual(model.stream(result.result_stream_id).root, base.root)
        self.assertEqual(len(set(result.output_stream_ids)), 3)
        self.assertEqual(len(model.history(result.result_stream_id)), 4)
        self.assertEqual(model.stats()["definitions"], 2)

    def test_branches_do_not_advance_an_implicit_head(self):
        model, base = literal_model()
        left = model.apply_batch(base.stream_id, (Edit("a", "replace", (), 0, 1, ascii_symbols("L")),))
        right = model.apply_batch(base.stream_id, (Edit("b", "replace", (), 0, 1, ascii_symbols("R")),))
        self.assertEqual(model.expand_stream(left.result_stream_id), b"Lbc")
        self.assertEqual(model.expand_stream(right.result_stream_id), b"Rbc")
        self.assertEqual(model.history(left.result_stream_id)[0], base)
        self.assertEqual(model.history(right.result_stream_id)[0], base)

    def test_empty_assembly_and_empty_batch_have_explicit_identity(self):
        model, base = literal_model(b"")
        result = model.apply_batch(base.stream_id, ())
        self.assertEqual(model.expand_stream(result.result_stream_id), b"")
        self.assertEqual(model.stream(result.result_stream_id).root, base.root)
        self.assertNotEqual(result.result_stream_id, base.stream_id)
        self.assertEqual(len(model.history(result.result_stream_id)), 2)

    def test_invalid_late_operation_publishes_nothing(self):
        model, base = literal_model()
        before, view = model.stats(), model.definitions
        operations = (Edit("first", "replace", (), 0, 1, ascii_symbols("z")),
                      Edit("late", "remove", (), 9, 1))
        self.assert_code("INVALID_RANGE", lambda: model.apply_batch(base.stream_id, operations))
        self.assertEqual(model.stats(), before)
        self.assertIs(model.definitions, view)
        self.assertEqual(model.expand_stream(base.stream_id), b"abc")
        recovered = model.apply_batch(base.stream_id, (operations[0],))
        self.assertTrue(recovered.result_stream_id.endswith(":stream:2"))
        self.assertTrue(recovered.batch_id.endswith(":batch:1"))

    def test_publication_preparation_failure_publishes_nothing(self):
        from docstream_cpu.native import model as implementation
        model, base = literal_model()
        before = model.stats()
        original, calls = implementation.frozen_map, 0

        def fail_during_preparation(value):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise MemoryError("controlled publication preparation failure")
            return original(value)

        with patch.object(implementation, "frozen_map", side_effect=fail_during_preparation):
            with self.assertRaises(MemoryError):
                model.apply_batch(base.stream_id, (Edit("change", "replace", (), 0, 1, ascii_symbols("z")),))
        self.assertEqual(model.stats(), before)
        result = model.apply_batch(base.stream_id, ())
        self.assertTrue(result.result_stream_id.endswith(":stream:2"))

    def test_duplicate_and_malformed_operations_are_rejected(self):
        model, base = literal_model()
        edit = Edit("same", "remove", (), 0, 1)
        before = model.stats()
        self.assert_code("DUPLICATE_OPERATION", lambda: model.apply_batch(base.stream_id, (edit, edit)))
        for value in [[], [edit], ({},)]:
            self.assert_code("VALIDATION_ERROR", lambda: model.apply_batch(base.stream_id, value))
        for args in [("x", "execute"), ("x", "insert"), ("x", "remove"), ("x", "replace")]:
            self.assert_code("VALIDATION_ERROR", lambda: Edit(*args))
        self.assert_code("VALIDATION_ERROR", lambda: Edit("\ud800", "remove", (), 0, 1))
        self.assertEqual(model.stats(), before)

    def test_invalid_paths_and_symbol_targets_reject_atomically(self):
        model, base = literal_model()
        for path in [(9,), (0, 0)]:
            self.assert_code("INVALID_PATH", lambda: model.inspect(base.stream_id, path))
        self.assert_code("INVALID_PATH", lambda: model.apply_batch(base.stream_id, (Edit("x", "remove", (0,), 0, 1),)))
        for path in [[], (True,), (-1,), (0,) * 9]:
            with self.assertRaises(NativeError):
                model.inspect(base.stream_id, path)
        self.assertEqual(model.stats()["streams"], 1)
        self.assertEqual(model.inspect(base.stream_id, (1,)).expanded_bytes, 1)

    def test_replacement_cannot_change_parent_layer_or_leak_definitions(self):
        model = NativeModel()
        glyph = model.define(Layer.GLYPH, ascii_symbols("x"))
        word = model.define(Layer.WORD, (glyph,))
        base = model.create_stream(word)
        before = model.stats()
        self.assert_code("LAYER_MISMATCH", lambda: model.apply_batch(base.stream_id,
            (Edit("up", "replace", (0,), 0, 1, (word,)),)))
        self.assertEqual(model.stats(), before)

    def test_definition_budget_failure_rolls_back_all_prefixes(self):
        model, base = literal_model(limits=Limits(max_definitions=2))
        before = model.stats()
        self.assert_code("LIMIT_EXCEEDED", lambda: model.apply_batch(base.stream_id, (
            Edit("one", "replace", (), 0, 1, ascii_symbols("x")),
            Edit("two", "replace", (), 0, 1, ascii_symbols("y")))))
        self.assertEqual(model.stats(), before)

    def test_children_reference_and_expanded_byte_budgets(self):
        for limits in [Limits(max_children=3), Limits(max_total_references=5), Limits(max_expanded_bytes=3)]:
            model, base = literal_model(limits=limits)
            before = model.stats()
            self.assert_code("LIMIT_EXCEEDED", lambda: model.apply_batch(base.stream_id,
                (Edit("more", "insert", (), 0, 0, ascii_symbols("x")),)))
            self.assertEqual(model.stats(), before)

    def test_zero_byte_graph_has_independent_traversal_budget(self):
        model = NativeModel(Limits(max_expansion_steps=10))
        empty = model.define(Layer.GLYPH, ())
        before = model.stats()
        self.assert_code("LIMIT_EXCEEDED", lambda: model.define(Layer.COMPONENT, (empty,) * 10))
        self.assertEqual(model.stats(), before)

    def test_stream_batch_and_operation_budgets(self):
        model, base = literal_model(limits=Limits(max_streams=2))
        before = model.stats()
        operations = tuple(Edit(str(n), "replace", (), 0, 1, ascii_symbols("a")) for n in range(2))
        self.assert_code("LIMIT_EXCEEDED", lambda: model.apply_batch(base.stream_id, operations))
        self.assertEqual(model.stats(), before)
        model, base = literal_model(limits=Limits(max_batches=1))
        model.apply_batch(base.stream_id, ())
        before = model.stats()
        self.assert_code("LIMIT_EXCEEDED", lambda: model.apply_batch(base.stream_id, ()))
        self.assertEqual(model.stats(), before)
        model, base = literal_model()
        self.assert_code("LIMIT_EXCEEDED", lambda: model.apply_batch(base.stream_id,
            tuple(Edit(str(n), "remove", (), 0, 1) for n in range(257))))

    def test_unknown_stream_and_batch_are_explicit_errors(self):
        model = NativeModel()
        self.assert_code("UNKNOWN_STREAM", lambda: model.stream("missing"))
        self.assert_code("UNKNOWN_BATCH", lambda: model.batch("missing"))
        self.assert_code("VALIDATION_ERROR", lambda: model.stream("\ud800"))
        self.assert_code("VALIDATION_ERROR", lambda: AssemblyRef("not-a-digest"))

    def test_limits_and_literal_size_are_strict(self):
        for limits in [dict(max_children=True), dict(max_operations=257), dict(max_streams=0)]:
            self.assert_code("VALIDATION_ERROR", lambda: Limits(**limits))
        self.assert_code("LIMIT_EXCEEDED", lambda: ascii_symbols(b"x" * 10_001))


class NativeGeneratedTests(unittest.TestCase):
    def test_seeded_200_cases_against_independent_byte_sequence_oracle(self):
        randomizer = random.Random(20261029)
        accepted, rejected = 0, 0
        for case in range(200):
            with self.subTest(case=case):
                model = NativeModel()
                # The oracle carries literal byte pieces separately from native definitions.
                pieces = []
                for _ in range(randomizer.randint(1, 7)):
                    data = bytes(randomizer.randrange(128) for _ in range(randomizer.randint(1, 4)))
                    ref = model.define(Layer.GLYPH, ascii_symbols(data))
                    pieces.append((ref, data))
                original_parts = [randomizer.choice(pieces) for _ in range(randomizer.randint(1, 6))]
                word = model.define(Layer.WORD, tuple(ref for ref, _ in original_parts))
                base = model.create_stream(model.define(Layer.DOCUMENT, (word, word, SymbolRef(13), SymbolRef(10))))
                oracle = [list(original_parts), list(original_parts)]
                original = b"".join(data for _, data in original_parts) * 2 + b"\r\n"
                operations, expected = [], []
                for step in range(randomizer.randint(2, 8)):
                    occurrence = randomizer.randrange(2)
                    parts = oracle[occurrence]
                    kind = randomizer.choice(["insert", "remove", "replace"] if parts else ["insert"])
                    index = randomizer.randrange(len(parts) + 1) if kind == "insert" else randomizer.randrange(len(parts))
                    count = 0 if kind == "insert" else randomizer.randint(1, len(parts) - index)
                    incoming = [] if kind == "remove" else [randomizer.choice(pieces) for _ in range(randomizer.randint(1, 3))]
                    operations.append(Edit(f"op{step}", kind, (occurrence,), index, count, tuple(ref for ref, _ in incoming)))
                    parts[index:index + count] = incoming
                    expected.append(b"".join(data for part in oracle for _, data in part) + b"\r\n")
                before = model.stats()
                if case % 5 == 0:
                    operations.append(Edit("invalid-tail", "remove", (99,), 0, 1))
                    with self.assertRaises(NativeError) as caught:
                        model.apply_batch(base.stream_id, tuple(operations))
                    self.assertEqual(caught.exception.code, "INVALID_PATH")
                    self.assertEqual(model.stats(), before)
                    rejected += 1
                else:
                    result = model.apply_batch(base.stream_id, tuple(operations))
                    for i in reversed(range(len(expected))):
                        self.assertEqual(model.expand_stream(result.output_stream_ids[i]), expected[i])
                    self.assertEqual(len(model.history(result.result_stream_id)), len(operations) + 1)
                    accepted += 1
                self.assertEqual(model.expand_stream(base.stream_id), original)
                self.assertEqual(model.expand(word), original[:-2][:len(original[:-2]) // 2])
        print("NATIVE_GENERATED_RESULT " + json.dumps({"seed": 20261029, "cases": 200,
              "accepted_batches": accepted, "expected_atomic_rejections": rejected, "failed": 0}))


class NativeTortureTests(unittest.TestCase):
    def test_10000_references_and_500_retained_transformations(self):
        started = time.perf_counter()
        model, base = literal_model(b"A" * 10_000)
        expected = bytearray(b"A" * 10_000)
        current = base.stream_id
        selected = {}
        for n in range(500):
            index = (n * 17) % 10_000
            value = 66 + n % 25
            expected[index] = value
            result = model.apply_batch(current, (Edit(f"edit{n}", "replace", (), index, 1, (SymbolRef(value),)),))
            current = result.result_stream_id
            self.assertEqual(model.expand_stream(current), bytes(expected))
            if n in (0, 249, 499):
                selected[current] = bytes(expected)
        self.assertEqual(model.expand_stream(base.stream_id), b"A" * 10_000)
        for stream_id, data in reversed(tuple(selected.items())):
            self.assertEqual(model.expand_stream(stream_id), data)
        history = model.history(current)
        self.assertEqual(len(history), 501)
        self.assertEqual(model.stats()["batches"], 500)
        self.assertEqual(model.stats()["definitions"], 501)
        self.assertEqual(model.stats()["reference_slots"], 5_010_000)
        print("NATIVE_TORTURE_RESULT " + json.dumps({"references_per_root": 10_000,
              "transformations": 500, "retained_streams": len(history),
              "elapsed_seconds": round(time.perf_counter() - started, 3), "stats": model.stats()}))


if __name__ == "__main__":
    unittest.main()
