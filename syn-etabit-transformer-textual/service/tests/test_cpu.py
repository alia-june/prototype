from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
import random
import unittest

from pydantic import ValidationError

from docstream_cpu import (Block, CpuModel, ModelError, Properties, Snapshot,
                          Style, execute, parse_batch, plan, reference_execute, text_digest)


def document(mixed=False):
    return Snapshot(properties=Properties(font_family="A"), blocks=(
        Block(block_id="a", text="First", style=Style(font_family="Different", bold=True) if mixed else Style()),
        Block(block_id="b", text="Second"),
    ))


def batch(base, *operations):
    return parse_batch({"base_sha256": base.digest, "operations": [dict(operation_id=f"op{i}", **op) for i, op in enumerate(operations)]})


def font(value):
    return {"kind": "set_font", "font_family": value}


class ReductionTests(unittest.TestCase):
    def assert_equivalent(self, base, request):
        compiled = plan(base, request)
        reduced, reference = execute(base, compiled), reference_execute(base, request)
        self.assertEqual(reduced.snapshot, reference.snapshot)
        return compiled, reduced, reference

    def test_font_return_to_original_executes_zero_writes(self):
        base = document()
        request = batch(base, font("B"), font("A"), font("C"), font("A"))
        compiled, reduced, reference = self.assert_equivalent(base, request)
        self.assertEqual(reduced.snapshot, base)
        self.assertEqual(reduced.property_writes, 0)
        self.assertEqual(compiled.steps, ())
        self.assertEqual(len(compiled.batch.operations), 4)
        self.assertEqual(reference.property_writes, 12)
        self.assertIn("RED-03", {r.rule_id for r in compiled.reductions})

    def test_only_final_font_is_executed(self):
        compiled, reduced, _ = self.assert_equivalent(document(), batch(document(), font("B"), font("C")))
        self.assertEqual(reduced.snapshot.properties.font_family, "C")
        self.assertEqual(reduced.property_writes, 1)
        self.assertIn("RED-02", {r.rule_id for r in compiled.reductions})

    def test_exact_duplicate_assignment(self):
        base = document()
        compiled, reduced, _ = self.assert_equivalent(base, batch(base, font("C"), font("C")))
        self.assertEqual(reduced.property_writes, 1)
        self.assertIn("RED-01", {r.rule_id for r in compiled.reductions})

    def test_mixed_fonts_restore_exact_inheritance_and_other_properties(self):
        base = document(mixed=True)
        compiled, reduced, _ = self.assert_equivalent(base, batch(base, font("B"), {"kind": "restore_font"}))
        self.assertEqual(reduced.snapshot, base)
        self.assertEqual(reduced.property_writes, 0)
        self.assertEqual(reduced.snapshot.block("a").style.font_family, "Different")
        self.assertIsNone(reduced.snapshot.block("b").style.font_family)

    def test_same_effective_font_is_not_same_explicit_style_state(self):
        base = Snapshot(properties=Properties(font_family="A"), blocks=(Block(block_id="a", style=Style(font_family="A")),))
        _, reduced, _ = self.assert_equivalent(base, batch(base, font("A")))
        self.assertNotEqual(reduced.snapshot.digest, base.digest)
        self.assertIsNone(reduced.snapshot.block("a").style.font_family)
        self.assertEqual(reduced.property_writes, 1)

    def test_restore_all_block_style_fields(self):
        base = document(mixed=True)
        request = batch(base, {"kind": "set_style", "targets": ["a"], "property": "italic", "value": True},
                        {"kind": "set_style", "targets": ["a"], "property": "font_size_mpt", "value": 24000},
                        {"kind": "restore_style", "targets": ["a"]})
        _, reduced, _ = self.assert_equivalent(base, request)
        self.assertEqual(reduced.snapshot, base)
        self.assertEqual(reduced.property_writes, 0)

    def test_disjoint_grouping_red04(self):
        base = document()
        compiled, reduced, _ = self.assert_equivalent(base, batch(base,
            {"kind": "set_style", "targets": ["a"], "property": "bold", "value": True},
            {"kind": "set_style", "targets": ["b"], "property": "italic", "value": True}))
        self.assertEqual(len(compiled.steps), 1)
        self.assertEqual(reduced.property_writes, 2)
        self.assertIn("RED-04", {r.rule_id for r in compiled.reductions})

    def test_partial_scope_supersession_preserves_other_target(self):
        base = document()
        _, reduced, _ = self.assert_equivalent(base, batch(base,
            {"kind": "set_style", "targets": ["a", "b"], "property": "font_family", "value": "B"},
            {"kind": "set_style", "targets": ["a"], "property": "font_family", "value": "C"}))
        self.assertEqual(reduced.snapshot.block("a").style.font_family, "C")
        self.assertEqual(reduced.snapshot.block("b").style.font_family, "B")

    def test_structural_boundary_preserves_prior_assignment(self):
        base = document()
        compiled, reduced, _ = self.assert_equivalent(base, batch(base, font("B"),
            {"kind": "insert_block", "block": {"block_id": "new", "text": "Inserted"}, "after": "a"}, font("A")))
        self.assertEqual([b.block_id for b in reduced.snapshot.blocks], ["a", "new", "b"])
        self.assertEqual(reduced.property_writes, 2)
        self.assertEqual(reduced.structural_operations, 1)
        self.assertTrue(any(d.reason == "source-order barrier" for d in compiled.dependencies))

    def test_text_preconditions_are_evaluated_in_original_order(self):
        base = document()
        request = batch(base,
            {"kind": "replace_text", "target": "a", "text": "Changed", "expected_text_sha256": text_digest("First")},
            {"kind": "replace_text", "target": "a", "text": "First", "expected_text_sha256": text_digest("Changed")})
        _, reduced, _ = self.assert_equivalent(base, request)
        self.assertEqual(reduced.snapshot, base)
        self.assertEqual(reduced.structural_operations, 2)

    def test_move_and_remove_are_immutable(self):
        base = document()
        _, reduced, _ = self.assert_equivalent(base, batch(base,
            {"kind": "insert_block", "block": {"block_id": "new", "text": "Inserted"}, "after": "b"},
            {"kind": "move_block", "target": "new", "after": None},
            {"kind": "remove_block", "target": "a"}))
        self.assertEqual([b.block_id for b in reduced.snapshot.blocks], ["new", "b"])
        self.assertEqual([b.block_id for b in base.blocks], ["a", "b"])

    def test_document_properties(self):
        base = document()
        _, reduced, _ = self.assert_equivalent(base, batch(base,
            {"kind": "set_property", "property": "title", "value": "New title"},
            {"kind": "set_property", "property": "page_width_mpt", "value": 595000}))
        self.assertEqual(reduced.snapshot.properties.title, "New title")
        self.assertEqual(reduced.snapshot.properties.page_width_mpt, 595000)

    def test_empty_batch(self):
        base = document()
        _, reduced, _ = self.assert_equivalent(base, batch(base))
        self.assertEqual(reduced.snapshot, base)
        self.assertEqual(reduced.property_writes, 0)

    def test_plan_is_deterministic_and_bound_to_input(self):
        base = document()
        request = batch(base, font("B"))
        first, second = plan(base, request), plan(base, request)
        self.assertEqual(first.seal, second.seal)
        different = Snapshot(properties=Properties(font_family="Z"), blocks=base.blocks)
        with self.assertRaises(ModelError) as failure:
            execute(different, first)
        self.assertEqual(failure.exception.code, "STALE_BASE")

    def test_modified_plan_and_optimizer_version_are_rejected(self):
        compiled = plan(document(), batch(document(), font("B")))
        for corrupt in (replace(compiled, steps=()), replace(compiled, optimizer_version="different")):
            with self.subTest(corrupt=corrupt.optimizer_version), self.assertRaises(ModelError) as failure:
                execute(document(), corrupt)
            self.assertEqual(failure.exception.code, "INVALID_PLAN")


class ValidationTests(unittest.TestCase):
    def test_unknown_target_cannot_be_hidden_by_later_reversal(self):
        base = document()
        request = batch(base, {"kind": "set_style", "targets": ["missing"], "property": "bold", "value": True}, font("A"))
        for evaluate in (lambda: plan(base, request), lambda: reference_execute(base, request)):
            with self.assertRaises(ModelError) as failure:
                evaluate()
            self.assertEqual((failure.exception.code, failure.exception.operation_id), ("UNKNOWN_TARGET", "op0"))

    def test_failed_text_guard_survives_later_replacement(self):
        base = document()
        request = batch(base, {"kind": "replace_text", "target": "a", "text": "x", "expected_text_sha256": "0" * 64},
                        {"kind": "remove_block", "target": "a"})
        with self.assertRaises(ModelError) as failure:
            plan(base, request)
        self.assertEqual(failure.exception.code, "PRECONDITION_FAILED")

    def test_inserted_block_cannot_restore_nonexistent_baseline(self):
        base = document()
        request = batch(base, {"kind": "insert_block", "block": {"block_id": "new"}}, {"kind": "restore_font"})
        for evaluator in (plan, reference_execute):
            with self.assertRaises(ModelError) as failure:
                evaluator(base, request)
            self.assertEqual(failure.exception.code, "RESTORE_BASE_MISSING")

    def test_block_id_cannot_be_reused_after_removal(self):
        base = document()
        for ops in (({"kind": "remove_block", "target": "a"}, {"kind": "insert_block", "block": {"block_id": "a"}}),
                    ({"kind": "insert_block", "block": {"block_id": "new"}}, {"kind": "remove_block", "target": "new"}, {"kind": "insert_block", "block": {"block_id": "new"}})):
            for evaluator in (plan, reference_execute):
                with self.assertRaises(ModelError) as failure:
                    evaluator(base, batch(base, *ops))
                self.assertEqual(failure.exception.code, "DUPLICATE_TARGET")

    def test_invalid_position(self):
        with self.assertRaises(ModelError) as failure:
            plan(document(), batch(document(), {"kind": "move_block", "target": "a", "after": "a"}))
        self.assertEqual(failure.exception.code, "INVALID_POSITION")

    def test_json_and_dictionary_callers_have_same_scalar_strictness(self):
        invalid = [
            {"kind": "set_style", "targets": ["a"], "property": "bold", "value": "false"},
            {"kind": "set_style", "targets": ["a"], "property": "bold", "value": 1},
            {"kind": "set_property", "property": "font_size_mpt", "value": True},
            {"kind": "set_property", "property": "font_size_mpt", "value": "12000"},
            {"kind": "set_property", "property": "font_size_mpt", "value": -2},
            {"kind": "set_font", "font_family": " "},
            {"kind": "set_font", "font_family": "B", "version": True},
            {"kind": "set_font", "font_family": "B", "version": 1.0},
            {"kind": "set_font", "font_family": "B", "exec": "anything"},
            {"kind": "unknown", "font_family": "B"},
            {"kind": "set_style", "targets": [], "property": "bold", "value": True},
            {"kind": "set_style", "targets": ["a", "a"], "property": "bold", "value": True},
        ]
        for item in invalid:
            payload = {"base_sha256": document().digest, "operations": [{"operation_id": "bad", **item}]}
            for input_value in (payload, json.dumps(payload)):
                with self.subTest(item=item, encoding=type(input_value).__name__), self.assertRaises(ModelError):
                    parse_batch(input_value)

    def test_duplicate_operations_and_batch_limit(self):
        payload = {"base_sha256": document().digest, "operations": [{"operation_id": "same", **font("B")} for _ in range(2)]}
        with self.assertRaises(ModelError):
            parse_batch(payload)
        payload["operations"] = [{"operation_id": f"op{i}", **font("B")} for i in range(257)]
        with self.assertRaises(ModelError):
            parse_batch(payload)

    def test_snapshot_contract_and_deep_immutability(self):
        for invalid in ({"block_id": "x", "kind": "heading"}, {"block_id": "x", "heading_level": 1},
                        {"block_id": "x", "kind": "list_item"}, {"block_id": "x", "style": {"bold": "false"}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                Block.model_validate(invalid)
        base = document()
        with self.assertRaises(ValidationError):
            base.blocks[0].style.bold = True
        with self.assertRaises(ValidationError):
            Snapshot(blocks=(base.blocks[0], base.blocks[0]))

    def test_unpaired_surrogate_cannot_enter_semantic_content(self):
        with self.assertRaises(ValidationError):
            Block(block_id="bad", text="\ud800")
        with self.assertRaises(ModelError):
            batch(document(), {"kind": "set_property", "property": "title", "value": "\udfff"})


class CatalogTests(unittest.TestCase):
    def test_removed_block_identity_cannot_be_resurrected_in_later_batch(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        removal = model.stage(head.stream_id, batch(base, {"kind": "remove_block", "target": "a"}))
        committed = model.commit_semantic(removal.candidate_id)
        current = model.materialize(committed.stream_id)
        with self.assertRaises(ModelError) as failure:
            model.stage(committed.stream_id, batch(current, {"kind": "insert_block", "block": {"block_id": "a"}}))
        self.assertEqual(failure.exception.code, "DUPLICATE_TARGET")
        with self.assertRaises(ModelError) as failure:
            model.stage(committed.stream_id, batch(current,
                {"kind": "remove_block", "target": "missing"},
                {"kind": "insert_block", "block": {"block_id": "a"}}))
        self.assertEqual(failure.exception.code, "UNKNOWN_TARGET")

    def test_history_and_out_of_order_materialization_do_not_change_head(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        candidate = model.stage(head.stream_id, batch(base, font("B"), font("C"), font("A")))
        self.assertEqual(len(model.history(candidate.result_stream_id)), 4)
        for index, expected in ((1, "C"), (0, "B"), (2, "A")):
            record = model.inspect(candidate.output_stream_ids[index], content=True)
            self.assertEqual(record["content"]["properties"]["font_family"], expected)
            self.assertEqual(record["visual_state"], "not_rendered")
            self.assertEqual(model.head(head.document_id), head)

    def test_noop_result_has_distinct_lineage_and_shared_payload(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        candidate = model.stage(head.stream_id, batch(base, font("B"), font("A")))
        self.assertNotEqual(candidate.result_stream_id, head.stream_id)
        self.assertEqual(model.inspect(candidate.result_stream_id)["state"], "logical")
        final = model.commit_semantic(candidate.candidate_id)
        self.assertEqual(final.revision, 1)
        self.assertEqual(model.payload_count, 1)
        self.assertEqual(model.materialize(final.stream_id), base)
        self.assertEqual(model.commit_semantic(candidate.candidate_id), final)

    def test_empty_batch_still_has_new_stream_identity(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        candidate = model.stage(head.stream_id, batch(base))
        self.assertNotEqual(candidate.result_stream_id, head.stream_id)
        self.assertEqual(model.materialize(candidate.result_stream_id), base)

    def test_competing_candidates_fail_stale_head_without_losing_candidate(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        first = model.stage(head.stream_id, batch(base, font("B")))
        second = model.stage(head.stream_id, batch(base, font("C")))
        committed = model.commit_semantic(first.candidate_id)
        with self.assertRaises(ModelError) as failure:
            model.commit_semantic(second.candidate_id)
        self.assertEqual(failure.exception.code, "STALE_HEAD")
        self.assertEqual(model.materialize(second.result_stream_id).properties.font_family, "C")
        self.assertEqual(model.head(head.document_id), committed)

    def test_invalid_batch_does_not_advance_head(self):
        model, base = CpuModel(), document()
        head = model.ingest(base)
        with self.assertRaises(ModelError):
            model.stage(head.stream_id, batch(base, {"kind": "remove_block", "target": "missing"}))
        self.assertEqual(model.history(head.stream_id), (model.stream(head.stream_id),))
        self.assertEqual(model.head(head.document_id), head)

    def test_original_bytes_bom_crlf_unicode_and_semantic_identity_are_separate(self):
        model = CpuModel()
        for raw in (b"one\r\ntwo\r\n", b"\xef\xbb\xbfone\r\n", "e\u0301 👩‍💻\n".encode("utf-8")):
            head = model.ingest_text(raw)
            source = model.source(head.document_id)
            snapshot = model.materialize(head.stream_id)
            self.assertEqual(source.original_bytes, raw)
            self.assertEqual(source.original_sha256, sha256(raw).hexdigest())
            self.assertEqual(snapshot.block("text").text, raw.decode("utf-8-sig"))
        composed, decomposed = "é", "e\u0301"
        self.assertNotEqual(text_digest(composed), text_digest(decomposed))

    def test_unknown_identifiers_and_unsupported_encoding(self):
        model = CpuModel()
        for call in (lambda: model.stream("missing"), lambda: model.head("missing"), lambda: model.source("missing"),
                     lambda: model.candidate("missing"), lambda: model.ingest_text(b"\xff")):
            with self.assertRaises(ModelError):
                call()


class GeneratedConformanceTests(unittest.TestCase):
    assert_equivalent = ReductionTests.assert_equivalent
    # Seed and bounded workloads are fixed, not a performance benchmark.
    def test_300_generated_assignment_sequences(self):
        rng = random.Random(20261029)
        for case in range(300):
            base = document(mixed=bool(case % 2))
            operations = []
            for _ in range(rng.randrange(0, 25)):
                choice = rng.randrange(5)
                if choice == 0:
                    operations.append(font(rng.choice(("A", "B", "C"))))
                elif choice == 1:
                    operations.append({"kind": "restore_font"})
                elif choice == 2:
                    operations.append({"kind": "set_style", "targets": [rng.choice(("a", "b"))], "property": "bold", "value": rng.choice((True, False, None))})
                elif choice == 3:
                    operations.append({"kind": "restore_style", "targets": [rng.choice(("a", "b"))]})
                else:
                    operations.append({"kind": "set_property", "property": "title", "value": rng.choice(("", "Report", "Revised"))})
            with self.subTest(case=case):
                self.assert_equivalent(base, batch(base, *operations))

    def test_60_generated_structural_sequences(self):
        rng = random.Random(12345)
        for case in range(60):
            base = document(mixed=bool(case % 2))
            operations = [font("B")]
            for index in range(5):
                key = f"new{index}"
                operations.extend((
                    {"kind": "insert_block", "block": {"block_id": key, "text": "fresh"}, "after": rng.choice((None, "a", "b"))},
                    {"kind": "set_style", "targets": [key], "property": "italic", "value": True},
                    {"kind": "replace_text", "target": key, "text": "changed", "expected_text_sha256": text_digest("fresh")},
                    {"kind": "move_block", "target": key, "after": "b"},
                    {"kind": "remove_block", "target": key}, font(rng.choice(("A", "B", "C"))),
                ))
            with self.subTest(case=case):
                self.assert_equivalent(base, batch(base, *operations))

    def test_60_generated_invalid_sequences_preserve_first_error(self):
        rng = random.Random(98765)
        for case in range(60):
            base = document(mixed=bool(case % 2))
            operations = [font(rng.choice(("B", "C"))) for _ in range(rng.randrange(0, 8))]
            index = len(operations)
            operations.extend((
                {"kind": "set_style", "targets": [f"missing{case}"], "property": "bold", "value": True},
                font("A"), {"kind": "restore_font"},
            ))
            request = batch(base, *operations)
            outcomes = []
            for evaluator in (plan, reference_execute):
                with self.assertRaises(ModelError) as failure:
                    evaluator(base, request)
                outcomes.append((failure.exception.code, failure.exception.operation_id))
            self.assertEqual(outcomes, [("UNKNOWN_TARGET", f"op{index}")] * 2)


if __name__ == "__main__":
    unittest.main()
