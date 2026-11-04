"""Strict loader and bounded queries for the AUTH-18B study packet."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable


class TheoryInspectionError(ValueError):
    """A stable-code rejection raised before untrusted study data is exposed."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class InspectorLimits:
    max_file_bytes: int = 2 * 1024 * 1024
    max_total_bytes: int = 10 * 1024 * 1024
    max_records: int = 1000
    max_results: int = 1000
    max_trace_depth: int = 16
    max_trace_links: int = 128


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TheoryInspectionError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except TheoryInspectionError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TheoryInspectionError("INVALID_JSON", f"{label}: {exc}") from exc
    if not isinstance(value, dict):
        raise TheoryInspectionError("INVALID_DOCUMENT", f"{label}: root must be an object")
    return value


_FORBIDDEN_KEYS = frozenset({"command", "executable", "script", "eval", "shell", "plugin"})


def _reject_executable_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in _FORBIDDEN_KEYS:
                raise TheoryInspectionError("EXECUTABLE_FIELD", f"{label}: forbidden field {key}")
            _reject_executable_fields(child, label)
    elif isinstance(value, list):
        for child in value:
            _reject_executable_fields(child, label)


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True).lower()


class TheoryInspector:
    """Immutable in-memory view loaded only from a hash-pinned inspection index."""

    def __init__(self, root: Path | str, limits: InspectorLimits | None = None):
        self.root = Path(root).resolve()
        self.limits = limits or InspectorLimits()
        self._catalogs: dict[str, tuple[dict[str, Any], ...]] = {}
        self._records: dict[str, dict[str, Any]] = {}
        self._files: tuple[dict[str, Any], ...] = ()
        self._index: dict[str, Any] = {}
        self._load()

    @property
    def records(self):
        return MappingProxyType(self._records.copy())

    def _read_bounded(self, path: Path, expected_size: int | None = None) -> bytes:
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise TheoryInspectionError("MISSING_FILE", str(path)) from exc
        if size > self.limits.max_file_bytes:
            raise TheoryInspectionError("FILE_LIMIT", f"{path.name}: {size} bytes")
        if expected_size is not None and size != expected_size:
            raise TheoryInspectionError("SIZE_MISMATCH", f"{path.name}: expected {expected_size}, got {size}")
        return path.read_bytes()

    def _load(self) -> None:
        index_path = (self.root / "inspection_index.json").resolve()
        if not _inside(self.root, index_path):
            raise TheoryInspectionError("PATH_ESCAPE", str(index_path))
        index_bytes = self._read_bounded(index_path)
        index = _strict_json(index_bytes, "inspection_index.json")
        _reject_executable_fields(index, "inspection_index.json")
        if index.get("schema") != "docstream.theory-inspection-index/1":
            raise TheoryInspectionError("INDEX_SCHEMA", "unsupported inspection index schema")
        files = index.get("files")
        if not isinstance(files, list) or not files:
            raise TheoryInspectionError("INVALID_INDEX", "files must be a non-empty list")
        total_bytes = 0
        total_records = 0
        seen_paths: set[str] = set()
        catalogs: dict[str, tuple[dict[str, Any], ...]] = {}
        records: dict[str, dict[str, Any]] = {}
        for item in files:
            if not isinstance(item, dict):
                raise TheoryInspectionError("INVALID_INDEX", "file entry must be an object")
            relative = item.get("path")
            if not isinstance(relative, str) or not relative or relative in seen_paths:
                raise TheoryInspectionError("INVALID_INDEX", "file paths must be unique non-empty strings")
            seen_paths.add(relative)
            candidate = (self.root / relative).resolve()
            if not _inside(self.root, candidate) or candidate.suffix.lower() != ".json":
                raise TheoryInspectionError("PATH_ESCAPE", relative)
            expected_size = item.get("bytes")
            if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
                raise TheoryInspectionError("INVALID_INDEX", f"invalid byte size for {relative}")
            payload = self._read_bounded(candidate, expected_size)
            total_bytes += len(payload)
            if total_bytes > self.limits.max_total_bytes:
                raise TheoryInspectionError("TOTAL_LIMIT", "catalog bytes exceed configured total")
            digest = sha256(payload).hexdigest()
            if digest != item.get("sha256"):
                raise TheoryInspectionError("HASH_MISMATCH", relative)
            document = _strict_json(payload, relative)
            _reject_executable_fields(document, relative)
            if document.get("schema") != item.get("schema"):
                raise TheoryInspectionError("SCHEMA_MISMATCH", relative)
            rows = document.get("records")
            if not isinstance(rows, list):
                raise TheoryInspectionError("INVALID_DOCUMENT", f"{relative}: records must be a list")
            if len(rows) != item.get("record_count"):
                raise TheoryInspectionError("COUNT_MISMATCH", relative)
            total_records += len(rows)
            if total_records > self.limits.max_records:
                raise TheoryInspectionError("RECORD_LIMIT", "catalog records exceed configured total")
            catalog = item.get("catalog")
            if not isinstance(catalog, str) or not catalog or catalog in catalogs:
                raise TheoryInspectionError("INVALID_INDEX", "catalog names must be unique")
            detached: list[dict[str, Any]] = []
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
                    raise TheoryInspectionError("INVALID_RECORD", f"{relative}: every record needs an id")
                record_id = row["id"]
                if record_id in records:
                    raise TheoryInspectionError("DUPLICATE_RECORD_ID", record_id)
                clean = json.loads(json.dumps(row, ensure_ascii=True, sort_keys=True))
                clean["_catalog"] = catalog
                records[record_id] = clean
                detached.append(clean)
            catalogs[catalog] = tuple(detached)
        self._validate_links(records)
        self._index = index
        self._files = tuple(json.loads(json.dumps(item)) for item in files)
        self._catalogs = catalogs
        self._records = records

    @staticmethod
    def _validate_links(records: dict[str, dict[str, Any]]) -> None:
        reference_fields = ("source_id", "wordnet_id", "theory_id", "generic_relation_id")
        for record_id, row in records.items():
            for field in reference_fields:
                value = row.get(field)
                if value is not None and (not isinstance(value, str) or value not in records):
                    raise TheoryInspectionError("MISSING_LINK", f"{record_id}.{field}: {value}")
            links = row.get("links", [])
            if not isinstance(links, list) or any(not isinstance(link, str) for link in links):
                raise TheoryInspectionError("INVALID_LINK", record_id)
            for link in links:
                if link not in records:
                    raise TheoryInspectionError("MISSING_LINK", f"{record_id}.links: {link}")

    def validate(self) -> dict[str, Any]:
        return {"status": "PASS", "schema": self._index["schema"],
                "study_status": self._index.get("study_status"),
                "files": len(self._files), "records": len(self._records),
                "total_bytes": sum(item["bytes"] for item in self._files)}

    def summary(self) -> dict[str, Any]:
        return {**self.validate(),
                "catalogs": {name: len(rows) for name, rows in sorted(self._catalogs.items())}}

    def _query(self, catalogs: Iterable[str], query: str | None = None,
               status: str | None = None, domain: str | None = None,
               source: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        cap = self.limits.max_results if limit is None else limit
        if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0 or cap > self.limits.max_results:
            raise TheoryInspectionError("RESULT_LIMIT", str(cap))
        rows = [row for catalog in catalogs for row in self._catalogs.get(catalog, ())]
        if query:
            needle = query.lower()
            rows = [row for row in rows if needle in _text(row)]
        if status:
            rows = [row for row in rows if str(row.get("status", row.get("mapping_status", ""))).lower() == status.lower()]
        if domain:
            rows = [row for row in rows if str(row.get("domain", row.get("layer", ""))).lower() == domain.lower()]
        if source:
            rows = [row for row in rows if str(row.get("source_id", "")).lower() == source.lower()]
        return [json.loads(json.dumps(row)) for row in rows[:cap]]

    def sources(self, **filters) -> list[dict[str, Any]]:
        return self._query(("sources",), **filters)

    def relations(self, **filters) -> list[dict[str, Any]]:
        return self._query(("wordnet_relations", "generic_relations", "theory"), **filters)

    def crosswalk(self, **filters) -> list[dict[str, Any]]:
        return self._query(("crosswalk",), **filters)

    def sample(self, **filters) -> list[dict[str, Any]]:
        return self._query(("sample",), **filters)

    def one(self, record_id: str) -> dict[str, Any]:
        try:
            return json.loads(json.dumps(self._records[record_id]))
        except KeyError as exc:
            raise TheoryInspectionError("NOT_FOUND", record_id) from exc

    def gaps(self, **filters) -> list[dict[str, Any]]:
        rows = self._query(("theory",), **filters)
        return [row for row in rows if "GAP" in row["id"] or "BLOCK" in str(row.get("status", ""))]

    def conflicts(self, **filters) -> list[dict[str, Any]]:
        rows = self._query(("crosswalk", "generic_relations"), **filters)
        tokens = ("NON_EQUIVALENT", "BLOCKED", "UNRESOLVED", "PLACEHOLDER")
        return [row for row in rows if any(token in str(row.get("mapping_status", row.get("status", ""))) for token in tokens)]

    def trace(self, record_id: str, depth: int = 4) -> dict[str, Any]:
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0 or depth > self.limits.max_trace_depth:
            raise TheoryInspectionError("TRACE_DEPTH", str(depth))
        self.one(record_id)
        queue: list[tuple[str, int]] = [(record_id, 0)]
        visited: set[str] = set()
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        while queue:
            current, level = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            row = self._records[current]
            nodes.append({"id": current, "depth": level, "catalog": row["_catalog"]})
            if level >= depth:
                continue
            targets: list[tuple[str, str]] = []
            for field in ("source_id", "wordnet_id", "theory_id", "generic_relation_id"):
                value = row.get(field)
                if isinstance(value, str):
                    targets.append((field, value))
            targets.extend(("links", value) for value in row.get("links", []))
            for field, target in targets:
                if len(edges) >= self.limits.max_trace_links:
                    return {"root": record_id, "nodes": nodes, "edges": edges,
                            "truncated": True, "reason": "TRACE_LINK_LIMIT"}
                edges.append({"from": current, "field": field, "to": target})
                if target not in visited:
                    queue.append((target, level + 1))
        return {"root": record_id, "nodes": nodes, "edges": edges, "truncated": False}
