"""Atomic retained evidence writer for an AUTH-17 pilot result."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
from uuid import uuid4

from .pilot import build_pilot
from .values import PilotResult, require


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("ascii")


def _jsonl_bytes(values) -> bytes:
    return b"".join((json.dumps(value, ensure_ascii=True, sort_keys=True,
                                separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")
                    for value in values)


def write_run(output_dir: str | Path, result: PilotResult, runtime: dict) -> Path:
    output = Path(output_dir)
    require(not output.exists(), "OUTPUT_EXISTS", "evidence output already exists")
    require(type(runtime) is dict, "VALIDATION_ERROR", "runtime evidence must be a dict")
    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = parent / f".{output.name}.tmp-{uuid4().hex}"
    temporary.mkdir()
    try:
        files = {
            "result.json": _json_bytes({**result.to_summary(), "runtime": runtime}),
            "forms.jsonl": _jsonl_bytes(row.to_record() for row in result.forms),
            "exceptions.jsonl": _jsonl_bytes(row.to_record() for row in result.exceptions),
            "fragments.json": _json_bytes([row.to_record() for row in result.fragments]),
            "constructions.jsonl": _jsonl_bytes(row.to_record() for row in result.constructions),
        }
        for name, payload in files.items():
            (temporary / name).write_bytes(payload)
        manifest = {
            "schema": "docstream.native-vocabulary.evidence-manifest/1",
            "files": [{"path": name, "bytes": len(payload),
                       "sha256": sha256(payload).hexdigest()}
                      for name, payload in sorted(files.items())],
        }
        (temporary / "manifest.json").write_bytes(_json_bytes(manifest))
        temporary.rename(output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return output


def verify_run(source_path: str | Path, output_dir: str | Path) -> dict:
    """Verify retained bytes, replay source intake and check every native expansion."""
    output = Path(output_dir)
    require(output.is_dir(), "EVIDENCE_NOT_FOUND", "evidence directory does not exist")
    try:
        manifest = json.loads((output / "manifest.json").read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid evidence manifest") from exc
    expected_names = {"result.json", "forms.jsonl", "exceptions.jsonl",
                      "fragments.json", "constructions.jsonl"}
    listed_names = {row.get("path") for row in manifest.get("files", [])}
    require(listed_names == expected_names, "EVIDENCE_MANIFEST_MISMATCH",
            "evidence manifest file set is not exact")
    for row in manifest["files"]:
        name = row["path"]
        require(Path(name).name == name, "EVIDENCE_MANIFEST_MISMATCH",
                "evidence manifest path must be a plain file name")
        payload = (output / name).read_bytes()
        require(len(payload) == row["bytes"] and sha256(payload).hexdigest() == row["sha256"],
                "EVIDENCE_HASH_MISMATCH", f"evidence hash mismatch for {name}")

    replay, model = build_pilot(source_path)
    deterministic = {
        "forms.jsonl": _jsonl_bytes(row.to_record() for row in replay.forms),
        "exceptions.jsonl": _jsonl_bytes(row.to_record() for row in replay.exceptions),
        "fragments.json": _json_bytes([row.to_record() for row in replay.fragments]),
        "constructions.jsonl": _jsonl_bytes(row.to_record() for row in replay.constructions),
    }
    for name, expected in deterministic.items():
        require((output / name).read_bytes() == expected, "REPLAY_MISMATCH",
                f"deterministic replay mismatch for {name}")
    stored_result = json.loads((output / "result.json").read_text(encoding="ascii"))
    runtime = stored_result.pop("runtime", None)
    require(stored_result == replay.to_summary(), "REPLAY_MISMATCH",
            "deterministic replay summary mismatch")
    require(type(runtime) is dict, "EVIDENCE_MANIFEST_MISMATCH",
            "runtime evidence is missing")
    for construction in replay.constructions:
        ref = model.definitions[construction.definition_id].ref
        require(model.expand(ref) == construction.text.encode("ascii"),
                "EXPANSION_MISMATCH", "native word expansion mismatch")
        require("".join(piece.text for piece in construction.pieces) == construction.text,
                "EXPANSION_MISMATCH", "construction trace mismatch")
    for form in replay.forms:
        require(model.expand(model.definitions[form.definition_id].ref) == form.form.encode("ascii"),
                "EXPANSION_MISMATCH", "form occurrence expansion mismatch")
    for relation in replay.exceptions:
        require(model.expand(model.definitions[relation.inflected_definition_id].ref)
                == relation.inflected.encode("ascii"), "EXPANSION_MISMATCH",
                "exception inflected expansion mismatch")
        require(model.expand(model.definitions[relation.base_definition_id].ref)
                == relation.base.encode("ascii"), "EXPANSION_MISMATCH",
                "exception base expansion mismatch")
    return {"status": "PASS", "manifest_hashes_verified": len(expected_names),
            "deterministic_payloads_verified": len(deterministic) + 1,
            "native_expansions_verified": (len(replay.constructions) + len(replay.forms)
                                           + len(replay.exceptions) * 2),
            "source_locators_verified": len(replay.forms) + len(replay.exceptions),
            "summary": replay.to_summary(), "runtime": runtime}
