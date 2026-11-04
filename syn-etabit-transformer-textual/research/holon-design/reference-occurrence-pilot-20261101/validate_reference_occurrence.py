"""Strict validator for the bounded Strmdocx reference-occurrence pilot.

This module intentionally uses only the Python standard library.  Its contract
is fixture-specific and must not be represented as the final native Holon
schema or as validation of the Strmdocx service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ID_RE = re.compile(r"^(target|relationship|metadata|occurrence|view):[A-Za-z][A-Za-z0-9._-]{0,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_CONTRACT_KEYS = {
    "contract_id",
    "contract_version",
    "status",
    "fixture_format",
    "root_schema",
    "record_schemas",
    "policies",
    "digest",
    "limits",
    "expected_profile",
}
EXPECTED_KINDS = ("target", "relationship", "metadata", "occurrence", "view")


class StrictJSONError(ValueError):
    """The byte stream is not accepted by the pilot's strict JSON loader."""


def _reject_constant(value: str) -> None:
    raise StrictJSONError(f"nonstandard JSON numeric constant: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON property: {key}")
        result[key] = value
    return result


def parse_json_strict(text: str) -> Any:
    """Parse standard JSON while rejecting duplicate object properties."""

    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except StrictJSONError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise StrictJSONError(f"invalid JSON: {exc}") from exc


def load_json_bytes_strict(data: bytes, *, max_bytes: int | None = None) -> Any:
    if max_bytes is not None and len(data) > max_bytes:
        raise StrictJSONError(f"document is {len(data)} bytes; limit is {max_bytes}")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise StrictJSONError(f"invalid UTF-8: {exc}") from exc
    return parse_json_strict(text)


def load_json_file_strict(path: Path, *, max_bytes: int | None = None) -> Any:
    return load_json_bytes_strict(path.read_bytes(), max_bytes=max_bytes)


def canonical_payload_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_payload_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload)).hexdigest()


def _exact_keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{label} keys differ; missing={missing}, extra={extra}")


def validate_contract(contract: Any) -> None:
    """Fail closed if the validator's own bounded contract is malformed."""

    _exact_keys(contract, EXPECTED_CONTRACT_KEYS, "contract")
    if contract["contract_id"] != "strmdocx:reference-occurrence-pilot:0.1":
        raise ValueError("unsupported contract_id")
    if contract["contract_version"] != "0.1":
        raise ValueError("unsupported contract_version")
    if contract["fixture_format"] != "strmdocx-reference-occurrence/0.1-pilot":
        raise ValueError("unsupported fixture_format")

    root_schema = contract["root_schema"]
    _exact_keys(root_schema, {"required_fields", "allowed_fields"}, "root_schema")
    if root_schema["required_fields"] != root_schema["allowed_fields"]:
        raise ValueError("pilot root required_fields and allowed_fields must be identical")
    if not all(isinstance(item, str) for item in root_schema["required_fields"]):
        raise ValueError("root field declarations must be strings")

    schemas = contract["record_schemas"]
    if not isinstance(schemas, dict) or tuple(schemas) != EXPECTED_KINDS:
        raise ValueError("record_schemas must declare the five supported kinds in contract order")
    schema_keys = {"collection", "id_prefix", "required_fields", "allowed_fields"}
    for kind, schema in schemas.items():
        _exact_keys(schema, schema_keys, f"record_schemas.{kind}")
        if schema["required_fields"] != schema["allowed_fields"]:
            raise ValueError(f"{kind} required_fields and allowed_fields must be identical")
        if schema["collection"] not in root_schema["required_fields"]:
            raise ValueError(f"{kind} collection is not a declared root field")
        if schema["id_prefix"] != f"{kind}:":
            raise ValueError(f"{kind} id_prefix is inconsistent")

    required_policy_values = {
        "reject_native_null": True,
        "reject_unknown_fields": True,
        "reject_duplicate_ids_globally": True,
        "reject_duplicate_occurrence_refs_within_view": True,
        "all_views_use_same_occurrence_set": True,
        "view_order_implies_ownership": False,
        "reverse_view_mutates_history": False,
        "occurrences_are_reference_only": True,
    }
    if contract["policies"] != required_policy_values:
        raise ValueError("unsupported policy set")
    if contract["digest"] != {
        "algorithm": "sha256",
        "payload_canonicalization": "json-sort-keys-compact-utf8",
    }:
        raise ValueError("unsupported digest policy")

    required_limits = {
        "max_document_bytes",
        "max_collection_records",
        "max_views",
        "max_occurrence_refs_per_view",
        "max_string_characters",
        "max_errors",
    }
    _exact_keys(contract["limits"], required_limits, "limits")
    for name, value in contract["limits"].items():
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"limit {name} must be a positive integer")
    if contract["limits"]["max_views"] > contract["limits"]["max_collection_records"]:
        raise ValueError("max_views cannot exceed max_collection_records")

    profile = contract["expected_profile"]
    required_profile_keys = {
        "pilot_id",
        "target_ids",
        "relationship_ids",
        "metadata_ids",
        "occurrence_bindings",
        "view_orders",
        "transformation",
        "relationship_meaning",
        "metadata_scope",
        "source_text",
        "result_text",
    }
    _exact_keys(profile, required_profile_keys, "expected_profile")


def load_contract(path: Path) -> dict[str, Any]:
    contract = load_json_file_strict(path)
    validate_contract(contract)
    return contract


class _Errors:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.items: list[str] = []

    def add(self, path: str, message: str) -> None:
        if len(self.items) < self.limit:
            self.items.append(f"{path}: {message}")


def _walk_scalars(root: Any) -> Iterable[tuple[str, Any]]:
    stack: list[tuple[str, Any]] = [("$", root)]
    while stack:
        path, value = stack.pop()
        if isinstance(value, dict):
            for key, child in reversed(list(value.items())):
                stack.append((f"{path}.{key}", child))
        elif isinstance(value, list):
            for index in range(len(value) - 1, -1, -1):
                stack.append((f"{path}[{index}]", value[index]))
        else:
            yield path, value


def _require_string(errors: _Errors, path: str, value: Any) -> bool:
    if not isinstance(value, str):
        errors.add(path, "must be a string")
        return False
    return True


def _check_record_shape(
    errors: _Errors,
    record: Any,
    path: str,
    kind: str,
    schema: dict[str, Any],
) -> bool:
    if not isinstance(record, dict):
        errors.add(path, "record must be an object")
        return False
    required = set(schema["required_fields"])
    actual = set(record)
    for field in sorted(required - actual):
        errors.add(path, f"missing required field {field}")
    for field in sorted(actual - set(schema["allowed_fields"])):
        errors.add(path, f"unknown field {field}")
    if record.get("kind") != kind:
        errors.add(f"{path}.kind", f"must be exactly {kind!r}")
    identifier = record.get("id")
    if _require_string(errors, f"{path}.id", identifier):
        if not ID_RE.fullmatch(identifier):
            errors.add(f"{path}.id", "malformed pilot identifier")
        if not identifier.startswith(schema["id_prefix"]):
            errors.add(f"{path}.id", f"must start with {schema['id_prefix']!r}")
    return not (required - actual)


def validate_document(
    document: Any,
    contract: dict[str, Any],
    *,
    enforce_profile: bool = True,
) -> list[str]:
    """Return deterministic errors. The input object is never modified."""

    validate_contract(contract)
    limits = contract["limits"]
    errors = _Errors(limits["max_errors"])

    for path, value in _walk_scalars(document):
        if value is None:
            errors.add(path, "native JSON null is forbidden")
        elif isinstance(value, str) and len(value) > limits["max_string_characters"]:
            errors.add(path, f"string exceeds {limits['max_string_characters']} characters")

    if not isinstance(document, dict):
        errors.add("$", "root must be an object")
        return errors.items

    root_schema = contract["root_schema"]
    root_required = set(root_schema["required_fields"])
    root_allowed = set(root_schema["allowed_fields"])
    actual_root = set(document)
    for field in sorted(root_required - actual_root):
        errors.add("$", f"missing required field {field}")
    for field in sorted(actual_root - root_allowed):
        errors.add("$", f"unknown field {field}")

    if document.get("format") != contract["fixture_format"]:
        errors.add("$.format", "does not match contract fixture_format")
    _require_string(errors, "$.pilot_id", document.get("pilot_id"))

    by_kind: dict[str, dict[str, dict[str, Any]]] = {kind: {} for kind in EXPECTED_KINDS}
    global_ids: dict[str, str] = {}

    for kind, schema in contract["record_schemas"].items():
        collection_name = schema["collection"]
        collection = document.get(collection_name)
        path = f"$.{collection_name}"
        if not isinstance(collection, list):
            errors.add(path, "must be an array")
            continue
        collection_limit = limits["max_views"] if kind == "view" else limits["max_collection_records"]
        if len(collection) > collection_limit:
            errors.add(path, f"contains {len(collection)} records; limit is {collection_limit}")
        for index, record in enumerate(collection):
            record_path = f"{path}[{index}]"
            _check_record_shape(errors, record, record_path, kind, schema)
            if not isinstance(record, dict):
                continue
            identifier = record.get("id")
            if isinstance(identifier, str):
                if identifier in global_ids:
                    errors.add(f"{record_path}.id", f"duplicate identifier also used at {global_ids[identifier]}")
                else:
                    global_ids[identifier] = record_path
                if identifier in by_kind[kind]:
                    errors.add(f"{record_path}.id", "duplicate identifier within collection")
                else:
                    by_kind[kind][identifier] = record

    for identifier, target in by_kind["target"].items():
        path = global_ids.get(identifier, "$.targets")
        role = target.get("role")
        if not _require_string(errors, f"{path}.role", role):
            continue
        payload = target.get("payload")
        if not isinstance(payload, dict):
            errors.add(f"{path}.payload", "must be an object")
        else:
            if role == "immutable_text_block":
                if set(payload) != {"encoding", "text"}:
                    errors.add(f"{path}.payload", "immutable_text_block payload must contain exactly encoding and text")
                if payload.get("encoding") != "utf-8":
                    errors.add(f"{path}.payload.encoding", "must be exactly 'utf-8'")
                _require_string(errors, f"{path}.payload.text", payload.get("text"))
            elif role == "transformation":
                transformation_fields = {"operation", "argument", "input_ref", "result_ref", "scope_ref"}
                if set(payload) != transformation_fields:
                    errors.add(f"{path}.payload", "transformation payload fields are not exact")
                for field in sorted(transformation_fields):
                    _require_string(errors, f"{path}.payload.{field}", payload.get(field))
                if payload.get("operation") != "append_text":
                    errors.add(f"{path}.payload.operation", "unsupported pilot transformation")
            else:
                errors.add(f"{path}.role", "unsupported target role")

        digest = target.get("payload_sha256")
        if not _require_string(errors, f"{path}.payload_sha256", digest):
            pass
        elif not SHA256_RE.fullmatch(digest):
            errors.add(f"{path}.payload_sha256", "must be 64 lowercase hexadecimal characters")
        elif isinstance(payload, dict):
            try:
                computed_digest = canonical_payload_sha256(payload)
            except (RecursionError, TypeError, ValueError) as exc:
                errors.add(f"{path}.payload", f"cannot be canonically serialized: {type(exc).__name__}")
            else:
                if computed_digest != digest:
                    errors.add(f"{path}.payload_sha256", "does not match canonical payload digest")

    for identifier, relationship in by_kind["relationship"].items():
        path = global_ids.get(identifier, "$.relationships")
        _require_string(errors, f"{path}.meaning", relationship.get("meaning"))
        for field in ("operation_ref", "input_ref", "result_ref"):
            reference = relationship.get(field)
            if _require_string(errors, f"{path}.{field}", reference) and reference not in by_kind["target"]:
                errors.add(f"{path}.{field}", "unresolved target reference")

    for identifier, metadata in by_kind["metadata"].items():
        path = global_ids.get(identifier, "$.metadata")
        _require_string(errors, f"{path}.scope", metadata.get("scope"))
        _require_string(errors, f"{path}.provenance", metadata.get("provenance"))

    for identifier, occurrence in by_kind["occurrence"].items():
        path = global_ids.get(identifier, "$.occurrences")
        reference_rules = (
            ("target_ref", "target"),
            ("relationship_ref", "relationship"),
            ("metadata_ref", "metadata"),
        )
        for field, expected_kind in reference_rules:
            reference = occurrence.get(field)
            if _require_string(errors, f"{path}.{field}", reference) and reference not in by_kind[expected_kind]:
                errors.add(f"{path}.{field}", f"unresolved {expected_kind} reference")

    view_sets: list[tuple[str, set[str]]] = []
    for identifier, view in by_kind["view"].items():
        path = global_ids.get(identifier, "$.views")
        _require_string(errors, f"{path}.purpose", view.get("purpose"))
        _require_string(errors, f"{path}.order_semantics", view.get("order_semantics"))
        references = view.get("occurrence_refs")
        if not isinstance(references, list):
            errors.add(f"{path}.occurrence_refs", "must be an array of scalar references")
            continue
        if len(references) > limits["max_occurrence_refs_per_view"]:
            errors.add(f"{path}.occurrence_refs", "exceeds occurrence-reference limit")
        valid_references: list[str] = []
        for index, reference in enumerate(references):
            reference_path = f"{path}.occurrence_refs[{index}]"
            if _require_string(errors, reference_path, reference):
                valid_references.append(reference)
                if reference not in by_kind["occurrence"]:
                    errors.add(reference_path, "unresolved occurrence reference")
        if len(valid_references) != len(set(valid_references)):
            errors.add(f"{path}.occurrence_refs", "duplicate occurrence reference within view")
        view_sets.append((identifier, set(valid_references)))

    if view_sets:
        baseline_id, baseline = view_sets[0]
        for identifier, current in view_sets[1:]:
            if current != baseline:
                errors.add(f"view:{identifier}", f"occurrence set differs from {baseline_id}")

    for identifier, target in by_kind["target"].items():
        if target.get("role") != "transformation" or not isinstance(target.get("payload"), dict):
            continue
        path = global_ids.get(identifier, "$.targets")
        payload = target["payload"]
        input_ref = payload.get("input_ref")
        result_ref = payload.get("result_ref")
        scope_ref = payload.get("scope_ref")
        if isinstance(input_ref, str) and input_ref not in by_kind["target"]:
            errors.add(f"{path}.payload.input_ref", "unresolved target reference")
        if isinstance(result_ref, str) and result_ref not in by_kind["target"]:
            errors.add(f"{path}.payload.result_ref", "unresolved target reference")
        if isinstance(scope_ref, str) and scope_ref not in by_kind["metadata"]:
            errors.add(f"{path}.payload.scope_ref", "unresolved metadata reference")

        matching_relationships = [
            relationship
            for relationship in by_kind["relationship"].values()
            if relationship.get("operation_ref") == identifier
        ]
        if not matching_relationships:
            errors.add(path, "transformation is not named by any relationship")
        for relationship in matching_relationships:
            if relationship.get("input_ref") != input_ref or relationship.get("result_ref") != result_ref:
                errors.add(path, "transformation input/result references disagree with relationship")

        source = by_kind["target"].get(input_ref) if isinstance(input_ref, str) else None
        result = by_kind["target"].get(result_ref) if isinstance(result_ref, str) else None
        if payload.get("operation") == "append_text" and source and result:
            source_payload = source.get("payload")
            result_payload = result.get("payload")
            argument = payload.get("argument")
            if (
                isinstance(source_payload, dict)
                and isinstance(result_payload, dict)
                and isinstance(source_payload.get("text"), str)
                and isinstance(result_payload.get("text"), str)
                and isinstance(argument, str)
                and source_payload["text"] + argument != result_payload["text"]
            ):
                errors.add(path, "append_text result does not equal source text plus argument")

    if enforce_profile:
        _validate_expected_profile(errors, document, contract, by_kind)

    return errors.items


def _validate_expected_profile(
    errors: _Errors,
    document: dict[str, Any],
    contract: dict[str, Any],
    by_kind: dict[str, dict[str, dict[str, Any]]],
) -> None:
    profile = contract["expected_profile"]
    if document.get("pilot_id") != profile["pilot_id"]:
        errors.add("$.pilot_id", "does not match expected pilot profile")

    for profile_key, kind in (
        ("target_ids", "target"),
        ("relationship_ids", "relationship"),
        ("metadata_ids", "metadata"),
    ):
        if set(by_kind[kind]) != set(profile[profile_key]):
            errors.add(f"$.{contract['record_schemas'][kind]['collection']}", f"IDs do not match expected {profile_key}")

    bindings = profile["occurrence_bindings"]
    if set(by_kind["occurrence"]) != set(bindings):
        errors.add("$.occurrences", "IDs do not match expected occurrence bindings")
    for occurrence_id, expected in bindings.items():
        actual = by_kind["occurrence"].get(occurrence_id)
        if actual is not None:
            for field, value in expected.items():
                if actual.get(field) != value:
                    errors.add(f"occurrence:{occurrence_id}.{field}", "does not match expected binding")

    view_orders = profile["view_orders"]
    if set(by_kind["view"]) != set(view_orders):
        errors.add("$.views", "IDs do not match expected inspection views")
    for view_id, expected_order in view_orders.items():
        actual = by_kind["view"].get(view_id)
        if actual is not None and actual.get("occurrence_refs") != expected_order:
            errors.add(f"view:{view_id}.occurrence_refs", "does not match expected profile order")

    transformation = profile["transformation"]
    target = by_kind["target"].get(transformation["target_ref"])
    relationship = by_kind["relationship"].get(transformation["relationship_ref"])
    metadata = by_kind["metadata"].get(transformation["metadata_ref"])
    source = by_kind["target"].get(transformation["input_ref"])
    result = by_kind["target"].get(transformation["result_ref"])
    if target and isinstance(target.get("payload"), dict):
        payload = target["payload"]
        for field in ("input_ref", "result_ref", "operation", "argument"):
            if payload.get(field) != transformation[field]:
                errors.add(f"target:{transformation['target_ref']}.payload.{field}", "does not match expected transformation")
        if payload.get("scope_ref") != transformation["metadata_ref"]:
            errors.add(f"target:{transformation['target_ref']}.payload.scope_ref", "does not match expected metadata reference")
    if relationship and relationship.get("meaning") != profile["relationship_meaning"]:
        errors.add("relationship:meaning", "does not match expected profile")
    if metadata and metadata.get("scope") != profile["metadata_scope"]:
        errors.add("metadata:scope", "does not match expected profile")
    if source and isinstance(source.get("payload"), dict) and source["payload"].get("text") != profile["source_text"]:
        errors.add("source:text", "does not match expected profile")
    if result and isinstance(result.get("payload"), dict) and result["payload"].get("text") != profile["result_text"]:
        errors.add("result:text", "does not match expected profile")


def main(argv: list[str] | None = None) -> int:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=base / "reference_occurrence_contract.json")
    parser.add_argument("--fixture", type=Path, default=base / "reference_occurrence_fixture.json")
    parser.add_argument("--structural-only", action="store_true", help="skip the exact fixture profile checks")
    args = parser.parse_args(argv)

    try:
        contract = load_contract(args.contract)
        document = load_json_file_strict(
            args.fixture,
            max_bytes=contract["limits"]["max_document_bytes"],
        )
        findings = validate_document(document, contract, enforce_profile=not args.structural_only)
    except (OSError, StrictJSONError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    if findings:
        print(f"FAIL: {len(findings)} finding(s)")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("PASS: reference-occurrence fixture satisfies the bounded pilot contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
