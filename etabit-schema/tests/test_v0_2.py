#!/usr/bin/env python3
"""Non-executing Etabit schema v0.2 descriptor checks. Requires jsonschema.

Run from repository root:
    python -m pip install jsonschema
    python etabit-schema/tests/test_v0_2.py

These checks validate only the *documented draft* and declared graph links.
They do not verify storage access isolation, authorization, or cryptography.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((BASE / "schema" / "etabit-project.v0.2.schema.json").read_text(encoding="utf-8"))
EXAMPLE = json.loads((BASE / "examples" / "four-symbol-source.v0.2.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def validate_graph(data: dict) -> list[str]:
    """Additional candidate descriptor integrity checks (not wire grammar)."""
    errors: list[str] = []
    drives = data.get("drives", [])
    drive_ids = [d["id"] for d in drives]
    if len(set(drive_ids)) != len(drive_ids):
        errors.append("duplicate drive id")
    lookup = {d["id"]: d for d in drives}
    object_ids = []
    for d in drives:
        ids = [o["id"] for o in d["objects"]]
        if len(set(ids)) != len(ids):
            errors.append("duplicate object id in drive " + d["id"])
        object_ids.extend((d["id"], obj_id) for obj_id in ids)
    for r in data.get("references", []):
        if r["from_drive"] not in lookup or r["to_drive"] not in lookup:
            errors.append("missing reference endpoint")
        elif r["target_object_id"] != "SENTINEL_UNRESOLVED" and (
            r["to_drive"], r["target_object_id"]
        ) not in object_ids:
            errors.append("missing target object")
    for meta in data.get("out_of_band_meta_disks", []):
        if meta["for_drive"] not in lookup:
            errors.append("meta association missing drive")
    for page in data.get("codepages", []):
        for drive_id in page["referential_drive_ids"]:
            if drive_id not in lookup or "referential" not in lookup[drive_id]["roles"]:
                errors.append("codepage references nonreferential or missing drive")
    return errors


def assert_invalid(mutate, message: str) -> None:
    x = deepcopy(EXAMPLE)
    mutate(x)
    assert list(VALIDATOR.iter_errors(x)), message


def main() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    assert not list(VALIDATOR.iter_errors(EXAMPLE)), "v0.2 example must satisfy schema"
    assert not validate_graph(EXAMPLE), "v0.2 example must have valid local references"
    assert '"null"' not in json.dumps(EXAMPLE), "not required, but prohibit encoded JSON null marker"
    assert "null" not in EXAMPLE, "no synthetic null sentinel"
    tests = [
        (lambda x: x["system"].__setitem__("result", "Disk"), "fixed AE/EO nomenclature"),
        (lambda x: x["drives"][0].__setitem__("roles", ["source", "root"]), "unknown role"),
        (lambda x: x["security"].__setitem__("runtime_activated", True), "no runtime activation"),
        (lambda x: x["codepages"][0].__setitem__("execution_permission", True), "no codepage exec"),
        (lambda x: x["out_of_band_meta_disks"][0].__setitem__("reader_access", "ALLOWED"), "no metadata read"),
        (lambda x: x["out_of_band_meta_disks"][0].__setitem__("automatic_disclosure", True), "no implicit disclosure"),
        (lambda x: x["holonic_cooperation"].__setitem__("refusal_bypass_permitted", True), "no refusal bypass"),
        (lambda x: x["cypher_disk"]["responsibilities"].append("new_authority"), "no extra responsibility"),
        (lambda x: x["cypher_disk"]["responsibilities"].pop(), "all five responsibilities required"),
        (lambda x: x.__setitem__("drives", None), "JSON null not admissible for drives"),
    ]
    for mutation, label in tests:
        assert_invalid(mutation, label)
    reordered = deepcopy(EXAMPLE)
    reordered["cypher_disk"]["responsibilities"].reverse()
    assert not list(VALIDATOR.iter_errors(reordered)), "responsibility order is nonnormative"
    bad = deepcopy(EXAMPLE)
    bad["references"][0]["to_drive"] = "missing:drive"
    assert validate_graph(bad), "graph checker must flag missing endpoint"
    bad = deepcopy(EXAMPLE)
    bad["codepages"][0]["referential_drive_ids"] = ["drive:four-symbol"]
    assert validate_graph(bad), "graph checker must flag nonreferential codepage drive"
    print("ETABIT_SCHEMA_V0_2_TESTS=PASS (draft shape + local reference tests only)")


if __name__ == "__main__":
    main()
