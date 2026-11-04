"""In-memory stream catalog for M1; intentionally no durable store or server.

Candidates and inspection do not advance a document head. Semantic commit is a
separate explicit method and never claims visual rendering occurred.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from threading import RLock
from uuid import uuid4

from .errors import ModelError
from .models import Block, Properties, Snapshot
from .rich import parse_snapshot
from .operations import Batch
from .operations import InsertBlock
from .planner import Plan, execute, plan


def new_id(prefix: str) -> str:
    return f"{prefix}:{uuid4().hex}"


@dataclass(frozen=True)
class Source:
    source_id: str
    original_bytes: bytes
    encoding: str

    @property
    def original_sha256(self):
        return sha256(self.original_bytes).hexdigest()


@dataclass(frozen=True)
class Stream:
    stream_id: str
    document_id: str
    parent_id: str | None
    batch_id: str | None
    prefix_length: int
    producer_operation_id: str | None
    semantic_sha256: str | None = None


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    document_id: str
    base_stream_id: str
    expected_revision: int
    batch: Batch
    compiled: Plan
    output_stream_ids: tuple[str, ...]
    result_stream_id: str


@dataclass(frozen=True)
class Head:
    document_id: str
    stream_id: str
    revision: int


class CpuModel:
    """An explicitly ephemeral reference catalog. All public mutations are locked."""

    def __init__(self):
        self._lock = RLock()
        self._heads: dict[str, Head] = {}
        self._streams: dict[str, Stream] = {}
        self._payloads: dict[str, Snapshot] = {}
        self._candidates: dict[str, Candidate] = {}
        self._sources: dict[str, Source] = {}
        self._document_sources: dict[str, str] = {}
        self._committed: dict[str, Head] = {}

    def ingest(self, snapshot: Snapshot, *, original_bytes: bytes | None = None) -> Head:
        # Revalidate rather than trust model_copy/model_construct from library callers.
        snapshot = parse_snapshot(snapshot)
        content_hash = snapshot.digest
        if original_bytes is not None and type(original_bytes) is not bytes:
            raise ModelError("VALIDATION_ERROR", "original_bytes must be immutable bytes")
        with self._lock:
            document_id, stream_id = new_id("document"), new_id("stream")
            self._payloads.setdefault(content_hash, snapshot)
            self._streams[stream_id] = Stream(stream_id, document_id, None, None, 0, None, content_hash)
            head = Head(document_id, stream_id, 0)
            self._heads[document_id] = head
            if original_bytes is not None:
                source = Source(new_id("source"), original_bytes, "opaque")
                self._sources[source.source_id] = source
                self._document_sources[document_id] = source.source_id
            return head

    def ingest_text(self, raw: bytes, *, title: str = "") -> Head:
        if type(raw) is not bytes:
            raise ModelError("VALIDATION_ERROR", "text source must be bytes")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ModelError("UNSUPPORTED_ENCODING", "initial text ingestion requires UTF-8 or UTF-8 BOM") from exc
        # One literal block; this is not a guessed Markdown parser.
        head = self.ingest(Snapshot(properties=Properties(title=title), blocks=(Block(block_id="text", text=text),)), original_bytes=raw)
        with self._lock:
            key = self._document_sources[head.document_id]
            self._sources[key] = replace(self._sources[key], encoding="utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8")
        return head

    def source(self, document_id: str) -> Source:
        with self._lock:
            try:
                return self._sources[self._document_sources[document_id]]
            except KeyError as exc:
                raise ModelError("UNKNOWN_SOURCE", document_id) from exc

    def head(self, document_id: str) -> Head:
        with self._lock:
            try:
                return self._heads[document_id]
            except KeyError as exc:
                raise ModelError("UNKNOWN_DOCUMENT", document_id) from exc

    def stream(self, stream_id: str) -> Stream:
        with self._lock:
            try:
                return self._streams[stream_id]
            except KeyError as exc:
                raise ModelError("UNKNOWN_STREAM", stream_id) from exc

    def stage(self, base_stream_id: str, batch: Batch) -> Candidate:
        with self._lock:
            base_record = self.stream(base_stream_id)
            base = self.materialize(base_stream_id)
            head = self.head(base_record.document_id)
            # Identity is stable along a lineage, even after a block is removed.
            # Standalone snapshots have no historical tombstones; the catalog does.
            lineage = self.history(base_stream_id)
            reserved = {block.block_id for block in self.materialize(lineage[0].stream_id).blocks}
            for record in lineage:
                if record.producer_operation_id is not None:
                    prior = self.candidate(record.batch_id).batch.operations[record.prefix_length - 1]
                    if isinstance(prior, InsertBlock):
                        reserved.add(prior.block.block_id)
            compiled = plan(base, batch, reserved_block_ids=frozenset(reserved))
            candidate_id = new_id("batch")
            records: list[Stream] = []
            parent = base_stream_id
            for index, op in enumerate(batch.operations, start=1):
                record = Stream(new_id("stream"), head.document_id, parent, candidate_id, index, op.operation_id)
                records.append(record)
                parent = record.stream_id
            # Empty batches also have a distinct result occurrence.
            if not records:
                records.append(Stream(new_id("stream"), head.document_id, parent, candidate_id, 0, None, base.digest))
            candidate = Candidate(candidate_id, head.document_id, base_stream_id, head.revision, batch, compiled, tuple(r.stream_id for r in records), records[-1].stream_id)
            self._candidates[candidate_id] = candidate
            self._streams.update({r.stream_id: r for r in records})
            return candidate

    def candidate(self, candidate_id: str) -> Candidate:
        with self._lock:
            try:
                return self._candidates[candidate_id]
            except KeyError as exc:
                raise ModelError("UNKNOWN_CANDIDATE", candidate_id) from exc

    def materialize(self, stream_id: str) -> Snapshot:
        with self._lock:
            record = self.stream(stream_id)
            if record.semantic_sha256 is not None:
                return self._payloads[record.semantic_sha256]
            candidate = self.candidate(record.batch_id)
            base = self.materialize(candidate.base_stream_id)
            if record.prefix_length == len(candidate.batch.operations):
                compiled = candidate.compiled
            else:
                prefix = Batch(base_sha256=base.digest, operations=candidate.batch.operations[:record.prefix_length])
                compiled = plan(base, prefix, reserved_block_ids=frozenset(candidate.compiled.reserved_block_ids))
            output = execute(base, compiled).snapshot
            self._payloads.setdefault(output.digest, output)
            self._streams[stream_id] = replace(record, semantic_sha256=output.digest)
            return self._payloads[output.digest]

    def commit_semantic(self, candidate_id: str) -> Head:
        """Explicit in-memory semantic commit. No render claim or durable receipt."""
        with self._lock:
            if candidate_id in self._committed:
                return self._committed[candidate_id]
            candidate = self.candidate(candidate_id)
            head = self.head(candidate.document_id)
            if head.stream_id != candidate.base_stream_id or head.revision != candidate.expected_revision:
                raise ModelError("STALE_HEAD", "candidate base is not the current document head")
            self.materialize(candidate.result_stream_id)
            updated = Head(head.document_id, candidate.result_stream_id, head.revision + 1)
            self._heads[head.document_id] = updated
            self._committed[candidate_id] = updated
            return updated

    def inspect(self, stream_id: str, *, content: bool = False) -> dict:
        with self._lock:
            if content:
                self.materialize(stream_id)
            record = self.stream(stream_id)
            result = {**vars(record), "state": "materialized" if record.semantic_sha256 else "logical",
                      "visual_state": "not_rendered", "durability": "memory_only"}
            if record.producer_operation_id is not None:
                candidate = self.candidate(record.batch_id)
                result["transformation"] = candidate.batch.operations[record.prefix_length - 1].model_dump(mode="json")
            if content:
                result["content"] = self._payloads[record.semantic_sha256].model_dump(mode="json")
            return result

    def history(self, stream_id: str) -> tuple[Stream, ...]:
        with self._lock:
            result = []
            current = self.stream(stream_id)
            while True:
                result.append(current)
                if current.parent_id is None:
                    break
                current = self.stream(current.parent_id)
            return tuple(reversed(result))

    @property
    def payload_count(self) -> int:
        with self._lock:
            return len(self._payloads)
