"""Durable synchronous application operations, independent of MCP transport."""
from __future__ import annotations

import base64
from dataclasses import asdict
import json
import sqlite3
from typing import Annotated, Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from .catalog import new_id
from .errors import ModelError
from .models import Identifier, Snapshot, Value, canonical_bytes, digest
from .rich import Snapshot2, parse_snapshot
from .operations import Batch, parse_batch
from .storage import Store, dumps

RequestKey = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")]
MAX_TEXT_BYTES = 1_048_576
MAX_REPLY_BYTES = 131_072


class IngestRequest(Value):
    request_key: RequestKey
    text: str | None = None
    source_base64: str | None = None
    snapshot: Snapshot | Snapshot2 | None = None
    title: str = ""

    @field_validator("snapshot", mode="before")
    @classmethod
    def json_snapshot(cls, value):
        return parse_snapshot(value) if type(value) is dict else value

    @model_validator(mode="after")
    def one_source(self):
        if sum(v is not None for v in (self.text, self.source_base64, self.snapshot)) != 1:
            raise ValueError("supply exactly one of text, source_base64 or snapshot")
        return self


class TransformRequest(Value):
    request_key: RequestKey
    base_stream_id: Identifier
    batch: Batch
    mode: Literal["plan", "materialize", "commit"] = "plan"

    @field_validator("batch", mode="before")
    @classmethod
    def json_batch(cls, value):
        # The SDK validates Python dictionaries decoded from JSON. Explicitly
        # normalize array containers, retaining the core's strict scalar rules.
        return parse_batch(value) if type(value) is dict else value


class CommitRequest(Value):
    request_key: RequestKey
    candidate_id: Identifier


class InspectRequest(Value):
    target_id: Identifier
    section: Literal["head", "stream", "history", "plan", "content", "source", "structure"] = "stream"
    block_id: Identifier | None = None
    path: tuple[str | int, ...] = ()
    offset: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=100)] = 50


def validate_request_unicode(payload):
    """Check request strings before the strict UTF-8 serializer is invoked."""
    pending, seen = [payload], set()
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise ModelError("VALIDATION_ERROR", "request contains an unpaired Unicode surrogate") from exc
        elif type(value) in (dict, list, tuple) and id(value) not in seen:
            seen.add(id(value))
            if type(value) is dict:
                pending.extend(value.keys())
                pending.extend(value.values())
            else:
                pending.extend(value)
        elif isinstance(value, Value) and id(value) not in seen:
            seen.add(id(value))
            # model_construct can omit required fields. Leave their rejection
            # to the normal model validator rather than raising AttributeError.
            pending.extend(getattr(value, name, None) for name in type(value).model_fields)


def parse_request(kind, payload):
    try:
        if isinstance(payload, kind):
            validate_request_unicode(payload)
            return kind.model_validate(payload)
        if type(payload) is dict:
            validate_request_unicode(payload)
            return kind.model_validate_json(dumps(payload))
        raise ModelError("VALIDATION_ERROR", "request must be an object")
    except ValidationError as exc:
        fields = [{"field": ".".join(map(str, error["loc"])), "type": error["type"]} for error in exc.errors(include_input=False)[:8]]
        raise ModelError("VALIDATION_ERROR", dumps(fields)) from exc


class DocumentService:
    def __init__(self, store: Store):
        self.store = store

    def status(self):
        return {"ok": self.store.healthy, "storage_ready": self.store.healthy, "service_version": "0.2.0.dev4", "schema_version": self.store.connection.execute("PRAGMA user_version").fetchone()[0] if self.store.connection else None,
                "cpu_schema": "docstream.snapshot/1", "durability": "sqlite",
                "cpu_schemas": ["docstream.snapshot/1", "docstream.snapshot/2"],
                "visual_state": "unavailable", "gpu": False,
                "limits": {"operations_per_batch": 256, "text_bytes": MAX_TEXT_BYTES,
                           "reply_bytes": MAX_REPLY_BYTES, "history_page": 100},
                "capabilities": ["ingest", "inspect", "plan", "materialize", "semantic_commit", "durable_receipt", "job_inspect"],
                "sqlite_version": sqlite3.sqlite_version}

    def _mutate(self, family, request, action, principal="local"):
        if not self.store.healthy:
            raise ModelError("STORE_UNAVAILABLE", "store requires recovery before further requests")
        payload = request.model_dump(mode="json")
        payload_digest = digest(payload)
        identity = (principal, family, request.request_key)
        if not self.store.lock.acquire(timeout=5):
            raise ModelError("BUSY", "service writer is busy; retry with the same key")
        try:
            if not self.store.healthy:
                raise ModelError("STORE_UNAVAILABLE", "store requires recovery before further requests")
            con = self.store.connection
            row = con.execute("SELECT * FROM requests WHERE principal=? AND family=? AND request_key=?", identity).fetchone()
            if row:
                if row["digest"] != payload_digest:
                    raise ModelError("IDEMPOTENCY_CONFLICT", "request key already belongs to another payload")
                if row["state"] in ("completed", "failed", "conflicted"):
                    return json.loads(row["response"])
                job_id = row["job_id"]
                with self.store.transaction():
                    con.execute("UPDATE requests SET state='pending' WHERE principal=? AND family=? AND request_key=?", identity)
                    con.execute("UPDATE jobs SET state='pending' WHERE id=?", (job_id,))
            else:
                job_id = new_id("job")
                with self.store.transaction():
                    con.execute("INSERT INTO requests VALUES(?,?,?,?,?,?,?,?)", (*identity, payload_digest, dumps(payload), job_id, "pending", None))
                    con.execute("INSERT INTO jobs VALUES(?,?,?,?,?)", (job_id, *identity, "pending"))
                    self.store.event("request_reserved", {"job_id": job_id, "family": family})
            self.store.fault("after_reserved")
            try:
                with self.store.transaction():
                    data = action(self.store.model)
                    self.store.fault("after_model")
                    changed = self.store.flush()
                    self.store.fault("after_flush")
                    application_error = data.pop("_application_error", None)
                    terminal = "conflicted" if application_error else "completed"
                    reply = {"ok": not bool(application_error), "job_id": job_id, "state": terminal, "result": data}
                    if application_error:
                        reply["error"] = application_error
                    if len(canonical_bytes(reply)) > MAX_REPLY_BYTES:
                        raise ModelError("RESPONSE_LIMIT", "response exceeds limit; request a smaller section")
                    con.execute("UPDATE requests SET state=?,response=? WHERE principal=? AND family=? AND request_key=?", (terminal, dumps(reply), *identity))
                    con.execute("UPDATE jobs SET state=? WHERE id=?", (terminal, job_id))
                    self.store.event("request_" + terminal, {"job_id": job_id, "family": family})
                    self.store.fault("before_commit")
                self.store._saved.update(changed)
            except Exception as exc:
                self.store._load()  # Discard every uncommitted in-memory effect.
                code = exc.code if isinstance(exc, ModelError) else "INTERNAL_ERROR"
                state = "conflicted" if code in ("STALE_HEAD", "STALE_BASE") else "failed"
                message = str(exc)[:800] if isinstance(exc, ModelError) else "operation failed; database changes were rolled back"
                reply = {"ok": False, "job_id": job_id, "state": state,
                         "error": {"code": code, "message": message,
                                   "operation_id": getattr(exc, "operation_id", None),
                                   "retryable": False, "committed": False}}
                if hasattr(exc, "diagnostics"):
                    reply["error"]["diagnostics"] = exc.diagnostics
                with self.store.transaction():
                    con.execute("UPDATE requests SET state=?,response=? WHERE principal=? AND family=? AND request_key=?", (state, dumps(reply), *identity))
                    con.execute("UPDATE jobs SET state=? WHERE id=?", (state, job_id))
                    self.store.event("request_failed", {"job_id": job_id, "code": code})
            self.store.fault("after_commit")  # A lost response cannot overwrite its receipt.
            return reply
        finally:
            self.store.lock.release()

    def ingest(self, payload):
        request = parse_request(IngestRequest, payload)

        def action(model):
            if request.snapshot is not None:
                if len(canonical_bytes(request.snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                    raise ModelError("LIMIT_EXCEEDED", "snapshot exceeds 1 MiB")
                head = model.ingest(request.snapshot)
                from .assets import AssetStore, validate_references
                validate_references(request.snapshot, AssetStore(self.store).get)
            else:
                if request.source_base64 is not None:
                    try:
                        raw = base64.b64decode(request.source_base64, validate=True)
                    except (ValueError, base64.binascii.Error) as exc:
                        raise ModelError("VALIDATION_ERROR", "source_base64 is invalid") from exc
                else:
                    raw = request.text.encode("utf-8")
                if len(raw) > MAX_TEXT_BYTES:
                    raise ModelError("LIMIT_EXCEEDED", "text source exceeds 1 MiB")
                head = model.ingest_text(raw, title=request.title)
            snapshot = model.materialize(head.stream_id)
            return {**asdict(head), "semantic_sha256": snapshot.digest,
                    "block_ids": [b.block_id for b in snapshot.blocks[:100]],
                    "total_blocks": len(snapshot.blocks), "visual_state": "not_rendered"}

        return self._mutate("ingest", request, action)

    def transform(self, payload):
        request = parse_request(TransformRequest, payload)

        def action(model):
            candidate = model.stage(request.base_stream_id, request.batch)
            report = candidate.compiled.to_dict()
            result = {"candidate_id": candidate.candidate_id, "result_stream_id": candidate.result_stream_id,
                      "output_stream_ids": list(candidate.output_stream_ids), "plan_sha256": candidate.compiled.seal,
                      "requested_operations": report["requested_operations"], "property_writes": report["property_writes"],
                      "structural_operations": report["structural_operations"], "reduction_count": len(candidate.compiled.reductions),
                      "committed": False, "visual_state": "not_rendered"}
            if request.mode in ("materialize", "commit"):
                snapshot = model.materialize(candidate.result_stream_id)
                from .assets import AssetStore, validate_references
                validate_references(snapshot, AssetStore(self.store).get)
                if len(canonical_bytes(snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                    raise ModelError("LIMIT_EXCEEDED", "result exceeds 1 MiB")
                result["semantic_sha256"] = snapshot.digest
            if request.mode == "commit":
                try:
                    result["head"] = asdict(model.commit_semantic(candidate.candidate_id))
                    result["committed"] = True
                except ModelError as exc:
                    if exc.code != "STALE_HEAD":
                        raise
                    result["_application_error"] = {**exc.to_dict(), "committed": False, "retryable": False}
            return result

        return self._mutate("transform", request, action)

    def commit(self, payload):
        request = parse_request(CommitRequest, payload)

        def action(model):
            candidate = model.candidate(request.candidate_id)
            snapshot = model.materialize(candidate.result_stream_id)
            from .assets import AssetStore, validate_references
            validate_references(snapshot, AssetStore(self.store).get)
            if len(canonical_bytes(snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                raise ModelError("LIMIT_EXCEEDED", "result exceeds 1 MiB")
            return {"head": asdict(model.commit_semantic(request.candidate_id)), "committed": True, "visual_state": "not_rendered"}

        return self._mutate("commit", request, action)

    def inspect(self, payload):
        request = parse_request(InspectRequest, payload)
        with self.store.lock:
            if not self.store.healthy:
                raise ModelError("STORE_UNAVAILABLE", "store requires recovery")
            model = self.store.model
            if request.section == "head":
                result = asdict(model.head(request.target_id))
            elif request.section == "source":
                source = model.source(request.target_id)
                result = {"source_id": source.source_id, "original_sha256": source.original_sha256,
                          "bytes": len(source.original_bytes), "encoding": source.encoding}
            elif request.section == "plan":
                candidate = model.candidate(request.target_id)
                items = candidate.compiled.reductions[request.offset:request.offset + request.limit]
                result = {"plan_sha256": candidate.compiled.seal, "reductions": [item.to_dict() for item in items],
                          "total": len(candidate.compiled.reductions), "offset": request.offset}
            elif request.section == "history":
                history = model.history(request.target_id)
                result = {"streams": [asdict(r) for r in history[request.offset:request.offset + request.limit]], "total": len(history), "offset": request.offset}
            elif request.section == "stream":
                # The in-memory inspect result can include a large original operation.
                record = model.stream(request.target_id)
                result = {**asdict(record), "visual_state": "not_rendered", "durability": "sqlite"}
            else:
                # Materialization is a durable cache mutation, never a head mutation.
                try:
                    with self.store.transaction():
                        snapshot = model.materialize(request.target_id)
                        if len(canonical_bytes(snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                            raise ModelError("LIMIT_EXCEEDED", "result exceeds 1 MiB")
                        if request.section == "structure":
                            from .format_service import inspect_structure
                            result = inspect_structure(snapshot, request)
                        elif request.block_id is None:
                            result = {"properties": snapshot.properties.model_dump(),
                                      "blocks": [{"block_id": b.block_id, "kind": b.kind, "text_length": len(b.text), "style": b.style.model_dump()} for b in snapshot.blocks[request.offset:request.offset + request.limit]],
                                      "total_blocks": len(snapshot.blocks), "semantic_sha256": snapshot.digest}
                        else:
                            block = snapshot.block(request.block_id)
                            result = {"block_id": block.block_id, "text": block.text[request.offset:request.offset + request.limit],
                                      "offset": request.offset, "total_codepoints": len(block.text), "coordinate_units": "unicode_codepoints"}
                        changes = self.store.flush()
                    self.store._saved.update(changes)
                except KeyError as exc:
                    self.store._load()
                    raise ModelError("UNKNOWN_TARGET", "unknown block") from exc
                except Exception:
                    self.store._load()
                    raise
            if len(canonical_bytes(result)) > MAX_REPLY_BYTES:
                raise ModelError("RESPONSE_LIMIT", "request a smaller page")
            return {"ok": True, "result": result}

    def job(self, job_id: str):
        with self.store.lock:
            if not self.store.healthy:
                raise ModelError("STORE_UNAVAILABLE", "store requires recovery")
            row = self.store.connection.execute("SELECT r.* FROM requests r WHERE job_id=? AND principal='local'", (job_id,)).fetchone()
            if row is None:
                raise ModelError("UNKNOWN_JOB", "unknown job")
            return {"ok": True, "job_id": job_id, "state": row["state"],
                    "retryable": row["state"] == "interrupted",
                    "receipt": json.loads(row["response"]) if row["response"] else None}
