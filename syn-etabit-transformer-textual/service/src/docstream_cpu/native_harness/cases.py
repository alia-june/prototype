"""Explicit case families. Data never selects code, modules or shell commands."""
from __future__ import annotations

from copy import deepcopy
import json
import random

from .core import SCHEMA, SERVICE

RECIPES = ("symbol_high", "symbol_negative", "symbol_bool", "symbol_wrong", "literal_unicode",
           "literal_highbyte", "literal_mutable", "literal_long", "operation_id", "edit_type",
           "path_type", "edit_shape", "define_type", "reference_missing", "reference_layer",
           "duplicate_batch", "batch_container", "late_range", "late_path", "resource")
PROBES = ("all_ascii", "meaning_free_literals", "public_immutability", "detached_records",
          "shared_occurrence", "identity_and_history", "empty_noop", "request_identity",
          "fault_publish_1", "fault_publish_2", "fault_publish_3", "fault_publish_4", "fault_publish_5",
          "fault_define_1", "fault_define_2", "fault_define_3")
SCENARIOS = ("wide_history", "deep_shared", "empty_amplification", "near_expansion_limit",
             "resource_exhaustion", "four_callers", "publication_failures", "supervisor_timeout")


def case(case_id, mode, family, payload, expected=None, seed=20261029):
    return {"schema": SCHEMA, "case_id": case_id, "mode": mode, "family": family,
            "seed": seed, "input": payload, "expected": expected or {"outcome": "pass"}}


def validate_input(value):
    family, data = value["family"], value["input"]
    if family == "error":
        if set(data) != {"recipe", "variant", "value"} or data["recipe"] not in RECIPES:
            raise ValueError("unknown error recipe or fields")
        if type(data["variant"]) is not int or not 0 <= data["variant"] <= 10000:
            raise ValueError("invalid recipe variant")
        recipe, raw = data["recipe"], data["value"]
        if recipe in ("literal_highbyte", "literal_mutable"):
            if type(raw) is not str or len(raw) > 20002:
                raise ValueError("invalid literal byte encoding")
            bytes.fromhex(raw)
        if recipe == "reference_missing":
            import re
            if type(raw) is not str or not re.fullmatch(r"[0-9a-f]{64}", raw):
                raise ValueError("missing-reference case requires a well-formed digest")
        if recipe == "resource" and (type(raw) is not int or not 0 <= raw < 8):
            raise ValueError("unknown resource boundary")
        if recipe in ("late_path", "late_range") and (type(raw) is not int or not 0 <= raw < 10000):
            raise ValueError("invalid late-error coordinate")
        if recipe == "edit_shape" and raw not in ("execute", "insert-count", "remove-refs", "replace-empty"):
            raise ValueError("unknown edit-shape variant")
    elif family in ("probe", "scenario"):
        if set(data) != {"name"} or data["name"] not in (PROBES if family == "probe" else SCENARIOS):
            raise ValueError("unknown fixed probe/scenario")
    else:
        if set(data) != {"base_hex", "operations"} or type(data["base_hex"]) is not str or len(data["base_hex"]) > 128:
            raise ValueError("invalid valid-control base")
        raw = bytes.fromhex(data["base_hex"])
        if any(x >= 128 for x in raw) or type(data["operations"]) is not list or not 1 <= len(data["operations"]) <= 2:
            raise ValueError("invalid valid-control operations")
        for op in data["operations"]:
            if type(op) is not dict or set(op) != {"kind", "index", "count", "data_hex"}:
                raise ValueError("invalid control operation fields")
            if op["kind"] not in ("insert", "remove", "replace") or type(op["index"]) is not int or type(op["count"]) is not int:
                raise ValueError("invalid control operation scalars")
            if type(op["data_hex"]) is not str or len(op["data_hex"]) > 32 or any(x >= 128 for x in bytes.fromhex(op["data_hex"])):
                raise ValueError("invalid control operation bytes")


def error_case(recipe, variant, rnd, *, mode="fuzzy-error", case_id="error", seed=20261029):
    code = "VALIDATION_ERROR"
    if recipe == "symbol_high": value = rnd.randint(128, 65535)
    elif recipe == "symbol_negative": value = -rnd.randint(1, 10000)
    elif recipe == "symbol_bool": value = bool(variant % 2)
    elif recipe == "symbol_wrong": value = [None, "65", 65.0, [65]][variant % 4]
    elif recipe == "literal_unicode": value = ["\u00e9", "\ud800", "\u20ac", "A\udfffB"][variant % 4]
    elif recipe == "literal_highbyte": value = bytes([rnd.randint(128, 255)]).hex()
    elif recipe == "literal_mutable": value = "4142"
    elif recipe == "literal_long": value = "x" * 10001; code = "LIMIT_EXCEEDED"
    elif recipe == "operation_id": value = ["", "bad id", "\ud800", "x" * 129][variant % 4]
    elif recipe == "edit_type": value = [True, -1, "1", 1.5][variant % 4]
    elif recipe == "path_type": value = [True, -1, "0", 0.5][variant % 4]
    elif recipe == "edit_shape": value = ["execute", "insert-count", "remove-refs", "replace-empty"][variant % 4]
    elif recipe == "define_type": value = ["glyph", 1, True, None][variant % 4]
    elif recipe == "reference_missing": value = f"{rnd.getrandbits(256):064x}"; code = "UNKNOWN_REFERENCE"
    elif recipe == "reference_layer": value = "document-to-glyph"; code = "LAYER_MISMATCH"
    elif recipe == "duplicate_batch": value = "duplicate"; code = "DUPLICATE_OPERATION"
    elif recipe == "batch_container": value = [[], {}, None][variant % 3]
    elif recipe == "late_range": value = rnd.randint(5, 9999); code = "INVALID_RANGE"
    elif recipe == "late_path": value = rnd.randint(5, 9999); code = "INVALID_PATH"
    else: value = variant % 8; code = "LIMIT_EXCEEDED"
    return case(case_id, mode, "error", {"recipe": recipe, "variant": variant, "value": value},
                {"exception": "NativeError", "code": code}, seed)


def valid_case(rnd, case_id, seed):
    base = bytes(rnd.randrange(128) for _ in range(rnd.randint(1, 24)))
    oracle = bytearray(base)
    operations = []
    for _ in range(2):
        kind = rnd.choice(("insert", "remove", "replace")) if oracle else "insert"
        index = rnd.randrange(len(oracle) + 1) if kind == "insert" else rnd.randrange(len(oracle))
        count = 0 if kind == "insert" else rnd.randint(1, len(oracle) - index)
        data = b"" if kind == "remove" else bytes(rnd.randrange(128) for _ in range(rnd.randint(1, 5)))
        operations.append({"kind": kind, "index": index, "count": count, "data_hex": data.hex()})
        oracle[index:index + count] = data
    return case(case_id, "fuzzy-error", "valid", {"base_hex": base.hex(), "operations": operations}, seed=seed)


def fuzzy_cases(seed, count=1000):
    rnd, invalid = random.Random(seed), 0
    for n in range(count):
        if n % 5 == 4:
            yield valid_case(rnd, f"fuzz-{n:04d}", seed)
        else:
            recipe = RECIPES[invalid % len(RECIPES)]
            variant = invalid // len(RECIPES)
            yield error_case(recipe, variant, rnd, case_id=f"fuzz-{n:04d}", seed=seed)
            invalid += 1


def hardening_cases(seed):
    fixture = SERVICE / "tests" / "fixtures" / "native_harness" / "fixed-cases.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    rnd = random.Random(seed)
    for n, item in enumerate(data["errors"]):
        yield error_case(item["recipe"], item["variant"], rnd, mode="hardening", case_id=f"fixed-error-{n:03d}", seed=seed)
    for name in data["probes"]:
        yield case("probe-" + name, "hardening", "probe", {"name": name}, seed=seed)


def torture_cases(seed):
    for name in SCENARIOS:
        yield case("stress-" + name, "torture", "scenario", {"name": name}, seed=seed)


def reductions(value):
    # Closed data-only candidates, maximum twelve evaluations in the journal.
    data = value["input"]
    if value["family"] == "valid":
        for n in range(1, len(data["operations"])):
            reduced = deepcopy(value)
            reduced["input"]["operations"] = data["operations"][:n]
            yield reduced
    elif value["family"] == "error" and type(data["value"]) is str:
        for n in sorted({0, 1, 2, 4, 8, len(data["value"]) // 2}):
            if n < len(data["value"]):
                reduced = deepcopy(value)
                reduced["input"]["value"] = data["value"][:n]
                yield reduced
