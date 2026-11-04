"""Rigid, deterministic fuzzy, and bounded torture tests for the pilot.

Run with:
    python -m unittest -v test_reference_occurrence.py

The torture lane is intentionally bounded so it is repeatable on an ordinary
development machine. It is not a denial-of-service or security certification.
"""

from __future__ import annotations

import copy
import json
import random
import unittest
from pathlib import Path
from typing import Any, Callable

from validate_reference_occurrence import (
    StrictJSONError,
    canonical_payload_sha256,
    load_contract,
    load_json_bytes_strict,
    load_json_file_strict,
    parse_json_strict,
    validate_document,
)


BASE = Path(__file__).resolve().parent
CONTRACT_PATH = BASE / "reference_occurrence_contract.json"
FIXTURE_PATH = BASE / "reference_occurrence_fixture.json"


def _load() -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_contract(CONTRACT_PATH)
    fixture = load_json_file_strict(
        FIXTURE_PATH,
        max_bytes=contract["limits"]["max_document_bytes"],
    )
    return contract, fixture


def _find(records: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
    return next(record for record in records if record["id"] == identifier)


def _rehash(target: dict[str, Any]) -> None:
    target["payload_sha256"] = canonical_payload_sha256(target["payload"])


class RigidConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.fixture = _load()

    def test_rigid_fixture_conforms_without_findings(self) -> None:
        self.assertEqual([], validate_document(self.fixture, self.contract))

    def test_rigid_expected_views_reference_same_occurrences_in_exact_orders(self) -> None:
        views = {view["id"]: view["occurrence_refs"] for view in self.fixture["views"]}
        self.assertEqual(
            ["occurrence:O0", "occurrence:O1", "occurrence:O2"],
            views["view:V0"],
        )
        self.assertEqual(
            ["occurrence:O2", "occurrence:O1", "occurrence:O0"],
            views["view:V1"],
        )
        self.assertEqual(set(views["view:V0"]), set(views["view:V1"]))

    def test_rigid_occurrences_are_reference_only(self) -> None:
        expected_fields = {"id", "kind", "target_ref", "relationship_ref", "metadata_ref"}
        for occurrence in self.fixture["occurrences"]:
            with self.subTest(occurrence=occurrence["id"]):
                self.assertEqual(expected_fields, set(occurrence))
                self.assertTrue(all(isinstance(value, str) for value in occurrence.values()))

    def test_rigid_payload_digests_are_reproducible(self) -> None:
        for target in self.fixture["targets"]:
            with self.subTest(target=target["id"]):
                self.assertEqual(
                    target["payload_sha256"],
                    canonical_payload_sha256(target["payload"]),
                )

    def test_rigid_validation_is_deterministic(self) -> None:
        snapshots = [validate_document(self.fixture, self.contract) for _ in range(25)]
        self.assertTrue(all(snapshot == snapshots[0] for snapshot in snapshots))
        self.assertEqual([], snapshots[0])

    def test_rigid_loader_rejects_duplicate_properties(self) -> None:
        with self.assertRaises(StrictJSONError):
            parse_json_strict('{"a":1,"a":2}')

    def test_rigid_loader_rejects_nonstandard_numbers_malformed_json_and_invalid_utf8(self) -> None:
        rejected = (
            lambda: parse_json_strict('{"a":NaN}'),
            lambda: parse_json_strict('{"a":1} trailing'),
            lambda: load_json_bytes_strict(b'{"a":"\xff"}'),
        )
        for index, operation in enumerate(rejected):
            with self.subTest(case=index), self.assertRaises(StrictJSONError):
                operation()


Mutation = tuple[str, Callable[[dict[str, Any]], None]]


class DeterministicFuzzyErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.fixture = _load()

    def _mutations(self) -> list[Mutation]:
        def missing_target(document: dict[str, Any]) -> None:
            document["targets"] = [target for target in document["targets"] if target["id"] != "target:B0"]

        def wrong_target_reference(document: dict[str, Any]) -> None:
            document["occurrences"][0]["target_ref"] = "metadata:M1"

        def malformed_id(document: dict[str, Any]) -> None:
            document["occurrences"][0]["id"] = "occurrence:bad/id"

        def duplicate_id(document: dict[str, Any]) -> None:
            document["occurrences"][1]["id"] = "occurrence:O0"

        def unknown_root_field(document: dict[str, Any]) -> None:
            document["surprise"] = "not contracted"

        def unknown_occurrence_field(document: dict[str, Any]) -> None:
            document["occurrences"][0]["embedded"] = "not allowed"

        def missing_relationship_ref(document: dict[str, Any]) -> None:
            del document["occurrences"][0]["relationship_ref"]

        def missing_metadata_ref(document: dict[str, Any]) -> None:
            del document["occurrences"][0]["metadata_ref"]

        def embedded_target(document: dict[str, Any]) -> None:
            document["occurrences"][0]["target_ref"] = {"id": "target:B0"}

        def altered_chronological_order(document: dict[str, Any]) -> None:
            document["views"][0]["occurrence_refs"].reverse()

        def inconsistent_view_set(document: dict[str, Any]) -> None:
            document["views"][1]["occurrence_refs"].pop()

        def digest_tamper(document: dict[str, Any]) -> None:
            document["targets"][0]["payload_sha256"] = "0" * 64

        def native_null(document: dict[str, Any]) -> None:
            document["metadata"][0]["provenance"] = None

        def oversized_string(document: dict[str, Any]) -> None:
            document["metadata"][0]["provenance"] = "x" * 8193

        def transformation_input_mismatch(document: dict[str, Any]) -> None:
            transform = _find(document["targets"], "target:T1")
            transform["payload"]["input_ref"] = "target:B1"
            _rehash(transform)

        def relationship_result_mismatch(document: dict[str, Any]) -> None:
            document["relationships"][0]["result_ref"] = "target:B0"

        def embedded_reference_array(document: dict[str, Any]) -> None:
            document["occurrences"][1]["metadata_ref"] = ["metadata:M1"]

        def wrong_kind(document: dict[str, Any]) -> None:
            document["metadata"][0]["kind"] = "relationship"

        def duplicate_occurrence_in_view(document: dict[str, Any]) -> None:
            document["views"][0]["occurrence_refs"][2] = "occurrence:O1"

        def malformed_digest(document: dict[str, Any]) -> None:
            document["targets"][2]["payload_sha256"] = "ABC"

        return [
            ("missing target", missing_target),
            ("wrong target family", wrong_target_reference),
            ("malformed identifier", malformed_id),
            ("duplicate identifier", duplicate_id),
            ("unknown root field", unknown_root_field),
            ("unknown occurrence field", unknown_occurrence_field),
            ("missing relationship reference", missing_relationship_ref),
            ("missing metadata reference", missing_metadata_ref),
            ("embedded target object", embedded_target),
            ("altered chronological order", altered_chronological_order),
            ("inconsistent view set", inconsistent_view_set),
            ("digest tamper", digest_tamper),
            ("native null", native_null),
            ("oversized string", oversized_string),
            ("transformation input mismatch", transformation_input_mismatch),
            ("relationship result mismatch", relationship_result_mismatch),
            ("embedded reference array", embedded_reference_array),
            ("wrong kind", wrong_kind),
            ("duplicate occurrence in view", duplicate_occurrence_in_view),
            ("malformed digest", malformed_digest),
        ]

    def test_fuzzy_twenty_semantic_mutations_are_rejected_deterministically(self) -> None:
        mutations = self._mutations()
        self.assertEqual(20, len(mutations))
        for name, mutate in mutations:
            with self.subTest(mutation=name):
                candidate = copy.deepcopy(self.fixture)
                mutate(candidate)
                first = validate_document(candidate, self.contract)
                second = validate_document(candidate, self.contract)
                self.assertTrue(first, f"mutation was unexpectedly accepted: {name}")
                self.assertEqual(first, second)

    def test_fuzzy_malformed_byte_streams_are_rejected(self) -> None:
        cases = (
            b'{"format":',
            b'{"a":1,"a":2}',
            b'{"n":Infinity}',
            b'\xff\xfe\xfd',
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(StrictJSONError):
                load_json_bytes_strict(data)
        with self.assertRaises(StrictJSONError):
            load_json_bytes_strict(b" " * 129, max_bytes=128)


def _large_occurrence_document(fixture: dict[str, Any], count: int, view_count: int = 2) -> dict[str, Any]:
    document = copy.deepcopy(fixture)
    document["pilot_id"] = f"pilot:torture:occurrences:{count}:views:{view_count}"
    occurrences = []
    for index in range(count):
        occurrences.append(
            {
                "id": f"occurrence:L{index:04d}",
                "kind": "occurrence",
                "target_ref": "target:B0",
                "relationship_ref": "relationship:R1",
                "metadata_ref": "metadata:M1",
            }
        )
    document["occurrences"] = occurrences
    ids = [record["id"] for record in occurrences]
    rng = random.Random(20261101)
    views = []
    for index in range(view_count):
        order = list(ids)
        if index == 1:
            order.reverse()
        elif index > 1:
            rng.shuffle(order)
        views.append(
            {
                "id": f"view:L{index:03d}",
                "kind": "view",
                "purpose": f"bounded_torture_view_{index}",
                "order_semantics": "inspection_permutation_only",
                "occurrence_refs": order,
            }
        )
    document["views"] = views
    return document


def _chain_document(length: int) -> dict[str, Any]:
    metadata = {
        "id": "metadata:Chain",
        "kind": "metadata",
        "scope": "whole_block",
        "provenance": f"deterministic bounded chain of {length} append operations",
    }
    targets: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []

    source = {
        "id": "target:B0000",
        "kind": "target",
        "role": "immutable_text_block",
        "payload": {"encoding": "utf-8", "text": ""},
        "payload_sha256": "",
    }
    _rehash(source)
    targets.append(source)

    for index in range(1, length + 1):
        input_ref = f"target:B{index - 1:04d}"
        result_ref = f"target:B{index:04d}"
        operation_ref = f"target:T{index:04d}"
        relationship_ref = f"relationship:R{index:04d}"

        operation = {
            "id": operation_ref,
            "kind": "target",
            "role": "transformation",
            "payload": {
                "operation": "append_text",
                "argument": "x",
                "input_ref": input_ref,
                "result_ref": result_ref,
                "scope_ref": "metadata:Chain",
            },
            "payload_sha256": "",
        }
        result = {
            "id": result_ref,
            "kind": "target",
            "role": "immutable_text_block",
            "payload": {"encoding": "utf-8", "text": "x" * index},
            "payload_sha256": "",
        }
        _rehash(operation)
        _rehash(result)
        targets.extend((operation, result))
        relationships.append(
            {
                "id": relationship_ref,
                "kind": "relationship",
                "meaning": "transforms_input_to_result",
                "operation_ref": operation_ref,
                "input_ref": input_ref,
                "result_ref": result_ref,
            }
        )
        for suffix, target_ref in (("I", input_ref), ("T", operation_ref), ("R", result_ref)):
            occurrences.append(
                {
                    "id": f"occurrence:C{index:04d}{suffix}",
                    "kind": "occurrence",
                    "target_ref": target_ref,
                    "relationship_ref": relationship_ref,
                    "metadata_ref": "metadata:Chain",
                }
            )

    ids = [record["id"] for record in occurrences]
    return {
        "format": "strmdocx-reference-occurrence/0.1-pilot",
        "pilot_id": f"pilot:torture:chain:{length}",
        "targets": targets,
        "relationships": relationships,
        "metadata": [metadata],
        "occurrences": occurrences,
        "views": [
            {
                "id": "view:ChainForward",
                "kind": "view",
                "purpose": "chain_forward_inspection",
                "order_semantics": "input_transformation_result_per_step",
                "occurrence_refs": ids,
            },
            {
                "id": "view:ChainReverse",
                "kind": "view",
                "purpose": "chain_reverse_inspection",
                "order_semantics": "reverse_inspection_without_mutation",
                "occurrence_refs": list(reversed(ids)),
            },
        ],
    }


class BoundedTortureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.fixture = _load()

    def test_torture_repeats_accepted_validation_one_thousand_times(self) -> None:
        for iteration in range(1000):
            findings = validate_document(self.fixture, self.contract)
            if findings:
                self.fail(f"iteration {iteration} failed: {findings}")

    def test_torture_large_forward_and_reverse_orders(self) -> None:
        document = _large_occurrence_document(self.fixture, 2048, 2)
        self.assertEqual([], validate_document(document, self.contract, enforce_profile=False))

    def test_torture_sixty_four_deterministic_permutation_views(self) -> None:
        document = _large_occurrence_document(self.fixture, 128, 64)
        first = validate_document(document, self.contract, enforce_profile=False)
        second = validate_document(document, self.contract, enforce_profile=False)
        self.assertEqual([], first)
        self.assertEqual(first, second)

    def test_torture_one_hundred_twenty_eight_step_transformation_chain(self) -> None:
        document = _chain_document(128)
        self.assertEqual([], validate_document(document, self.contract, enforce_profile=False))

    def test_torture_unresolved_reference_storm_is_error_bounded(self) -> None:
        document = _large_occurrence_document(self.fixture, 512, 2)
        for index, occurrence in enumerate(document["occurrences"]):
            occurrence["target_ref"] = f"target:Missing{index:04d}"
        findings = validate_document(document, self.contract, enforce_profile=False)
        self.assertEqual(self.contract["limits"]["max_errors"], len(findings))
        self.assertTrue(all("unresolved target reference" in finding for finding in findings))

    def test_torture_deeply_nested_embedded_reference_is_rejected_without_recursion(self) -> None:
        document = copy.deepcopy(self.fixture)
        nested: dict[str, Any] = {"leaf": "target:B0"}
        for _ in range(1000):
            nested = {"nested": nested}
        document["occurrences"][0]["target_ref"] = nested
        findings = validate_document(document, self.contract)
        self.assertTrue(findings)
        self.assertTrue(any("target_ref: must be a string" in finding for finding in findings))

    def test_torture_non_json_payload_value_is_a_finding_not_a_validator_crash(self) -> None:
        document = copy.deepcopy(self.fixture)
        document["targets"][0]["payload"]["text"] = {"not_json": {1, 2, 3}}
        findings = validate_document(document, self.contract)
        self.assertTrue(findings)
        self.assertTrue(any("cannot be canonically serialized" in finding for finding in findings))

    def test_torture_rejected_packets_do_not_contaminate_accepted_fixture(self) -> None:
        before = json.dumps(self.fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        for index in range(500):
            candidate = copy.deepcopy(self.fixture)
            candidate["occurrences"][index % 3]["target_ref"] = f"target:Missing{index:04d}"
            self.assertTrue(validate_document(candidate, self.contract))
        after = json.dumps(self.fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(before, after)
        self.assertEqual([], validate_document(self.fixture, self.contract))


if __name__ == "__main__":
    unittest.main(verbosity=2)
