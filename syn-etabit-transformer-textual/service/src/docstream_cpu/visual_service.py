"""Two-phase rendered preview/commit over durable semantic candidates."""
from __future__ import annotations

import base64
from dataclasses import asdict
import json
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .artifacts import ArtifactStore
from .catalog import new_id
from .errors import ModelError
from .models import Identifier, Value, canonical_bytes, digest
from .rendering import RenderProfile, Renderer
from .service import DocumentService, RequestKey, MAX_TEXT_BYTES, parse_request
from .storage import dumps


class RenderRequest(Value):
    request_key: RequestKey
    stream_id: Identifier | None = None
    candidate_id: Identifier | None = None
    commit: bool = False
    profile: RenderProfile = Field(default_factory=RenderProfile)

    @model_validator(mode="after")
    def one_target(self):
        if (self.stream_id is None) == (self.candidate_id is None):
            raise ValueError("supply exactly one stream_id or candidate_id")
        if self.commit and self.candidate_id is None:
            raise ValueError("rendered commit requires candidate_id")
        return self


class ArtifactRequest(Value):
    artifact_id: Identifier
    mode: Literal["metadata", "chunk"] = "metadata"
    offset: Annotated[int, Field(ge=0)] = 0
    length: Annotated[int, Field(ge=1, le=65536)] = 65536


class VisualService:
    def __init__(self, store, renderer=None):
        self.store = store
        self.renderer = renderer if renderer is not None else Renderer()
        self.artifacts = ArtifactStore(store)

    def status(self):
        reply = DocumentService(self.store).status()
        try:
            identity = self.renderer.identity()
            reply["visual_state"] = "available"
            reply["renderer"] = identity
        except ModelError as exc:
            reply["visual_state"] = "unavailable"
            reply["render_error"] = exc.to_dict()
        reply["capabilities"] += ["render", "artifact", "rendered_commit", "import", "export", "structure_inspect"]
        reply["registered_fonts"] = sorted(self.renderer.fonts.fonts)
        reply["worker_starts"] = self.renderer.starts
        reply["actual_renders"] = self.renderer.render_count
        reply["schema_version"] = self.store.connection.execute("PRAGMA user_version").fetchone()[0]
        return reply

    def render(self, payload):
        request = parse_request(RenderRequest, payload)
        identity = ("local", "render", request.request_key)
        encoded = request.model_dump(mode="json")
        request_digest = digest(encoded)
        if not self.store.lock.acquire(timeout=5):
            raise ModelError("BUSY", "service writer is busy")
        try:
            if not self.store.healthy:
                raise ModelError("STORE_UNAVAILABLE", "store requires recovery")
            con = self.store.connection
            row = con.execute("SELECT * FROM requests WHERE principal=? AND family=? AND request_key=?", identity).fetchone()
            if row and row["digest"] != request_digest:
                raise ModelError("IDEMPOTENCY_CONFLICT", "render request key belongs to another payload")
            if row and row["state"] in ("completed", "failed", "conflicted"):
                saved_reply = json.loads(row["response"])
                if saved_reply.get("ok"):
                    try:
                        for metadata in saved_reply["result"]["artifacts"].values():
                            self.artifacts.metadata(metadata["artifact_id"])
                    except ModelError:
                        return {"ok": False, "job_id": row["job_id"], "state": row["state"], "error": {
                            "code": "ARTIFACT_UNAVAILABLE", "message": "original receipt is preserved, but its artifact is unavailable; use a new render request key",
                            "committed": saved_reply["result"]["committed"], "retryable": False}}
                return saved_reply
            job_id = row["job_id"] if row else new_id("job")
            with self.store.transaction():
                if row:
                    con.execute("UPDATE requests SET state='pending' WHERE principal=? AND family=? AND request_key=?", identity)
                    con.execute("UPDATE jobs SET state='pending' WHERE id=?", (job_id,))
                else:
                    con.execute("INSERT INTO requests VALUES(?,?,?,?,?,?,?,?)", (*identity, request_digest, dumps(encoded), job_id, "pending", None))
                    con.execute("INSERT INTO jobs VALUES(?,?,?,?,?)", (job_id, *identity, "pending"))
                    self.store.event("render_reserved", {"job_id": job_id})
            self.store.fault("after_render_reserved")
            spec = None
            try:
                model = self.store.model
                candidate = model.candidate(request.candidate_id) if request.candidate_id else None
                stream_id = candidate.result_stream_id if candidate else request.stream_id
                # Persist semantic construction first, without moving any head.
                with self.store.transaction():
                    snapshot = model.materialize(stream_id)
                    if len(canonical_bytes(snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                        raise ModelError("LIMIT_EXCEEDED", "rendered semantic input exceeds 1 MiB")
                    changes = self.store.flush()
                self.store._saved.update(changes)
                from .rich import Snapshot2
                from .assets import AssetStore
                spec = self.renderer.prepare(snapshot, request.profile, AssetStore(self.store).get) if isinstance(snapshot, Snapshot2) else self.renderer.prepare(snapshot, request.profile)
                bundle = self.artifacts.cached(spec.cache_key)
                cache_hit = bundle is not None
                if not cache_hit:
                    self.artifacts.begin(spec)
                    rendered = self.renderer.render(spec)  # No SQL transaction is open.
                    bundle = self.artifacts.publish(spec, rendered)
                if bundle is None:
                    raise ModelError("ARTIFACT_PUBLICATION", "published artifact set is not ready")
                committed = False
                error = None
                with self.store.transaction():
                    # Re-verify required bytes immediately before a head transition.
                    for metadata in bundle["artifacts"].values():
                        self.artifacts.metadata(metadata["artifact_id"])
                    con.execute("INSERT OR IGNORE INTO stream_renders VALUES(?,?)", (stream_id, spec.cache_key))
                    head = None
                    if request.commit:
                        try:
                            head = model.commit_semantic(candidate.candidate_id)
                            committed = True
                        except ModelError as exc:
                            if exc.code != "STALE_HEAD":
                                raise
                            error = {**exc.to_dict(), "committed": False, "retryable": False}
                    changes = self.store.flush()
                    result = {"stream_id": stream_id, "candidate_id": request.candidate_id,
                              "cache_hit": cache_hit, "visual_state": "ready", "committed": committed,
                              "semantic_sha256": snapshot.digest, **bundle,
                              "actual_renders": self.renderer.render_count, "worker_starts": self.renderer.starts}
                    if head is not None:
                        result["head"] = asdict(head)
                    terminal = "conflicted" if error else "completed"
                    reply = {"ok": error is None, "job_id": job_id, "state": terminal, "result": result}
                    if error:
                        reply["error"] = error
                    con.execute("UPDATE requests SET state=?,response=? WHERE principal=? AND family=? AND request_key=?", (terminal, dumps(reply), *identity))
                    con.execute("UPDATE jobs SET state=? WHERE id=?", (terminal, job_id))
                    self.store.event("render_" + terminal, {"job_id": job_id, "cache_key": spec.cache_key, "committed": committed})
                    self.store.fault("before_visual_commit")
                self.store._saved.update(changes)
            except Exception as exc:
                self.store._load()
                code = exc.code if isinstance(exc, ModelError) else "INTERNAL_ERROR"
                reply = {"ok": False, "job_id": job_id, "state": "failed", "error": {
                    "code": code, "message": str(exc)[:600] if isinstance(exc, ModelError) else "rendering failed; document head was not advanced",
                    "committed": False, "retryable": False}}
                with self.store.transaction():
                    if spec is not None:
                        con.execute("UPDATE render_sets SET state='failed' WHERE cache_key=? AND state='pending'", (spec.cache_key,))
                    con.execute("UPDATE requests SET state='failed',response=? WHERE principal=? AND family=? AND request_key=?", (dumps(reply), *identity))
                    con.execute("UPDATE jobs SET state='failed' WHERE id=?", (job_id,))
                    self.store.event("render_failed", {"job_id": job_id, "code": code})
            self.store.fault("after_visual_commit")
            return reply
        finally:
            self.store.lock.release()

    def artifact(self, payload):
        request = parse_request(ArtifactRequest, payload)
        with self.store.lock:
            metadata = self.artifacts.metadata(request.artifact_id)
            result = dict(metadata)
            if request.mode == "chunk":
                path = self.artifacts.path(metadata["relative_path"])
                with path.open("rb") as handle:
                    handle.seek(request.offset)
                    raw = handle.read(request.length)
                result.update({"offset": request.offset, "data_base64": base64.b64encode(raw).decode(),
                               "next_offset": request.offset + len(raw), "eof": request.offset + len(raw) >= metadata["bytes"]})
            return {"ok": True, "result": result}

    def artifact_file(self, artifact_id):
        with self.store.lock:
            metadata = self.artifacts.metadata(artifact_id)
            return self.artifacts.path(metadata["relative_path"]), metadata

    def close(self):
        self.renderer.close()
