"""Retained evidence writer and deterministic verifier for AUTH-18A."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
from uuid import uuid4

from .probe import ProbeResult, build_probe
from .values import MapError, canonical, require


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("ascii")


def _jsonl_bytes(values) -> bytes:
    return b"".join(canonical(value) + b"\n" for value in values)


def deterministic_payloads(result: ProbeResult, store) -> dict[str, bytes]:
    source_rows = []
    score_by_id = {record.record_id: score
                   for record, score in zip(result.pull.selected_records,
                                            result.pull.selected_scores, strict=True)}
    for record in result.pull.selected_records:
        source_rows.append({"role": "selected", "selection_score": score_by_id[record.record_id],
                            "record_id": record.record_id, **record.to_record()})
    for record in result.pull.target_records:
        source_rows.append({"role": "resolved-target", "selection_score": None,
                            "record_id": record.record_id, **record.to_record()})
    maps = [{"map_id": definition.map_id, **definition.to_record()}
            for definition in sorted(store.definitions.values(), key=lambda item: item.map_id)]
    return {
        "aliases.json": _json_bytes(dict(result.aliases)),
        "maps.jsonl": _jsonl_bytes(maps),
        "source-records.jsonl": _jsonl_bytes(source_rows),
        "relations.jsonl": _jsonl_bytes(result.relation_records),
    }


def write_probe(output_dir: str | Path, result: ProbeResult, store, runtime: dict) -> Path:
    output = Path(output_dir)
    require(not output.exists(), "OUTPUT_EXISTS", "probe output already exists")
    require(type(runtime) is dict, "VALIDATION_ERROR", "runtime evidence must be exact dict")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent / f".{output.name}.tmp-{uuid4().hex}"
    temporary.mkdir()
    try:
        files = deterministic_payloads(result, store)
        files["result.json"] = _json_bytes({**result.to_summary(), "runtime": runtime})
        for name, payload in files.items():
            (temporary / name).write_bytes(payload)
        manifest = {"schema": "docstream.relative-maps.evidence-manifest/1",
                    "files": [{"path": name, "bytes": len(payload),
                               "sha256": sha256(payload).hexdigest()}
                              for name, payload in sorted(files.items())]}
        (temporary / "manifest.json").write_bytes(_json_bytes(manifest))
        temporary.rename(output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return output


def verify_probe(source_path: str | Path, output_dir: str | Path,
                 expected_sha256: str | None = None) -> dict:
    output = Path(output_dir)
    require(output.is_dir(), "EVIDENCE_NOT_FOUND", "probe evidence directory is absent")
    try:
        manifest = json.loads((output / "manifest.json").read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MapError("EVIDENCE_MANIFEST_INVALID", "cannot read evidence manifest") from exc
    expected = {"aliases.json", "maps.jsonl", "source-records.jsonl",
                "relations.jsonl", "result.json"}
    listed = {row.get("path") for row in manifest.get("files", [])}
    require(listed == expected, "EVIDENCE_MANIFEST_MISMATCH", "manifest file set is not exact")
    for row in manifest["files"]:
        name = row["path"]
        require(Path(name).name == name, "EVIDENCE_MANIFEST_MISMATCH",
                "manifest path must be a plain file name")
        payload = (output / name).read_bytes()
        require(len(payload) == row["bytes"] and sha256(payload).hexdigest() == row["sha256"],
                "EVIDENCE_HASH_MISMATCH", f"hash mismatch for {name}")
    replay, store = (build_probe(source_path) if expected_sha256 is None
                     else build_probe(source_path, expected_sha256=expected_sha256))
    payloads = deterministic_payloads(replay, store)
    for name, payload in payloads.items():
        require((output / name).read_bytes() == payload, "REPLAY_MISMATCH",
                f"deterministic replay mismatch for {name}")
    stored = json.loads((output / "result.json").read_text(encoding="ascii"))
    runtime = stored.pop("runtime", None)
    require(stored == replay.to_summary(), "REPLAY_MISMATCH", "result summary mismatch")
    require(type(runtime) is dict, "EVIDENCE_MANIFEST_MISMATCH", "runtime evidence is absent")
    for definition in store.definitions.values():
        for input_map_id in definition.input_map_ids:
            require(input_map_id in store.definitions, "DANGLING_MAP_REFERENCE",
                    "replayed map graph has a dangling input")
    aliases = replay.aliases
    require(replay.context_resolutions["context-a-v1"] == aliases["adjective.a"],
            "CONTEXT_RESOLUTION_MISMATCH", "context A v1 did not retain composition A")
    require(replay.context_resolutions["context-a-v2"] == aliases["adjective.b"],
            "CONTEXT_RESOLUTION_MISMATCH", "context A v2 did not select composition B")
    require(replay.context_resolutions["context-b-v1"] == aliases["adjective.a"],
            "CONTEXT_RESOLUTION_MISMATCH", "context B changed with context A")
    return {"status": "PASS", "manifest_hashes_verified": len(expected),
            "deterministic_payloads_verified": len(payloads) + 1,
            "map_inputs_verified": sum(len(item.input_map_ids) for item in store.definitions.values()),
            "source_records_verified": (len(replay.pull.selected_records)
                                        + len(replay.pull.target_records)),
            "relations_verified": len(replay.relation_records),
            "summary": replay.to_summary(), "runtime": runtime}
