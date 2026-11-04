"""SQLite owner and atomic persistence for the existing CPU model.

All SQL values are bound parameters. One OS-held byte-range lock owns a root;
rollback journaling and synchronous FULL protect database transactions.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import json
import os
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Callable

from .catalog import Candidate, CpuModel, Head, Source, Stream
from .errors import ModelError
from .models import Snapshot, canonical_bytes, digest
from .rich import parse_snapshot
from .operations import parse_batch
from .planner import plan

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS snapshots(digest TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, payload BLOB NOT NULL, encoding TEXT NOT NULL, digest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, head_id TEXT NOT NULL REFERENCES streams(id) DEFERRABLE INITIALLY DEFERRED, revision INTEGER NOT NULL, source_id TEXT REFERENCES sources(id));
CREATE TABLE IF NOT EXISTS streams(id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) DEFERRABLE INITIALLY DEFERRED, parent_id TEXT REFERENCES streams(id) DEFERRABLE INITIALLY DEFERRED, batch_id TEXT REFERENCES batches(id) DEFERRABLE INITIALLY DEFERRED, prefix_length INTEGER NOT NULL, producer_id TEXT, digest TEXT REFERENCES snapshots(digest));
CREATE TABLE IF NOT EXISTS batches(id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id), base_id TEXT NOT NULL REFERENCES streams(id), expected_revision INTEGER NOT NULL, request TEXT NOT NULL, plan TEXT NOT NULL, plan_digest TEXT NOT NULL, output_ids TEXT NOT NULL, result_id TEXT NOT NULL REFERENCES streams(id) DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS transformations(batch_id TEXT NOT NULL REFERENCES batches(id), operation_id TEXT NOT NULL, position INTEGER NOT NULL, payload TEXT NOT NULL, stream_id TEXT NOT NULL REFERENCES streams(id), PRIMARY KEY(batch_id,operation_id), UNIQUE(batch_id,position));
CREATE TABLE IF NOT EXISTS commits(batch_id TEXT PRIMARY KEY REFERENCES batches(id), head TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS requests(principal TEXT NOT NULL, family TEXT NOT NULL, request_key TEXT NOT NULL, digest TEXT NOT NULL, payload TEXT NOT NULL, job_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL, response TEXT, PRIMARY KEY(principal,family,request_key));
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, principal TEXT NOT NULL, family TEXT NOT NULL, request_key TEXT NOT NULL, state TEXT NOT NULL, FOREIGN KEY(principal,family,request_key) REFERENCES requests(principal,family,request_key));
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, detail TEXT NOT NULL, created TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')));
"""

ARTIFACT_SCHEMA = """
CREATE TABLE IF NOT EXISTS render_sets(cache_key TEXT PRIMARY KEY, content_digest TEXT NOT NULL REFERENCES snapshots(digest), profile TEXT NOT NULL, metadata TEXT NOT NULL, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, digest TEXT NOT NULL, relative_path TEXT NOT NULL UNIQUE, media_type TEXT NOT NULL, bytes INTEGER NOT NULL, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS render_artifacts(cache_key TEXT NOT NULL REFERENCES render_sets(cache_key), format TEXT NOT NULL, artifact_id TEXT NOT NULL REFERENCES artifacts(id), PRIMARY KEY(cache_key,format));
CREATE TABLE IF NOT EXISTS stream_renders(stream_id TEXT NOT NULL REFERENCES streams(id), cache_key TEXT NOT NULL REFERENCES render_sets(cache_key), PRIMARY KEY(stream_id,cache_key));
"""


def dumps(value):
    return canonical_bytes(value).decode("utf-8")


class OwnerLock:
    def __init__(self, path: Path):
        self.handle = path.open("a+b")
        if path.stat().st_size == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            raise ModelError("OWNER_BUSY", "another process owns this store") from exc

    def close(self):
        if self.handle.closed:
            return
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()


class Store:
    def __init__(self, root: Path, *, fault: Callable[[str], None] | None = None):
        root = Path(root).absolute()
        # This store only accepts managed roots, never per-request paths.
        for part in (root, *root.parents):
            if part.exists() and (part.is_symlink() or part.is_junction()):
                raise ModelError("UNSAFE_ROOT", "linked/reparse roots are not supported")
        root.mkdir(parents=True, exist_ok=True)
        for name in ("owner.lock", "state.sqlite3", "state.sqlite3-journal"):
            target = root / name
            if target.is_symlink() or target.is_junction():
                raise ModelError("UNSAFE_ROOT", "linked managed files are not supported")
        self.root = root.resolve()
        self.owner = OwnerLock(self.root / "owner.lock")
        self.lock = RLock()
        self.fault = fault or (lambda phase: None)
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.root / "state.sqlite3", isolation_level=None, check_same_thread=False, timeout=5)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys=ON")
            self.connection.execute("PRAGMA journal_mode=DELETE")
            self.connection.execute("PRAGMA synchronous=FULL")
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2):
                raise ModelError("SCHEMA_VERSION", "unsupported database schema")
            if version == 0:
                self.connection.executescript("BEGIN IMMEDIATE;" + SCHEMA + ARTIFACT_SCHEMA + "PRAGMA user_version=2; COMMIT;")
            elif version == 1:
                backup_path = self.root / "before-schema-v2.sqlite3"
                if backup_path.is_symlink() or backup_path.is_junction() or backup_path.exists():
                    raise ModelError("MIGRATION_BACKUP", "migration backup destination already exists; inspect before retry")
                backup = sqlite3.connect(backup_path)
                try:
                    self.connection.backup(backup)
                finally:
                    backup.close()
                self.connection.executescript("BEGIN IMMEDIATE;" + ARTIFACT_SCHEMA + "PRAGMA user_version=2; COMMIT;")
            with self.transaction():
                self.connection.execute("UPDATE requests SET state='interrupted' WHERE state='pending'")
                self.connection.execute("UPDATE jobs SET state='interrupted' WHERE state='pending'")
                self.connection.execute("UPDATE render_sets SET state='failed' WHERE state='pending'")
            self._load()
        except BaseException:
            self.close()
            raise

    @contextmanager
    def transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.execute("COMMIT")
        except BaseException:
            if self.connection.in_transaction:
                self.connection.execute("ROLLBACK")
            raise

    def event(self, kind: str, detail: dict):
        self.connection.execute("INSERT INTO events(kind,detail) VALUES(?,?)", (kind, dumps(detail)))

    def _load(self):
        self.healthy = False
        model = CpuModel()
        for row in self.connection.execute("SELECT * FROM snapshots"):
            value = parse_snapshot(row["payload"])
            if value.digest != row["digest"]:
                raise ModelError("STORE_CORRUPT", "snapshot digest mismatch")
            model._payloads[row["digest"]] = value
        for row in self.connection.execute("SELECT * FROM sources"):
            value = Source(row["id"], row["payload"], row["encoding"])
            if value.original_sha256 != row["digest"]:
                raise ModelError("STORE_CORRUPT", "source digest mismatch")
            model._sources[row["id"]] = value
        for row in self.connection.execute("SELECT * FROM streams"):
            model._streams[row["id"]] = Stream(row["id"], row["document_id"], row["parent_id"], row["batch_id"], row["prefix_length"], row["producer_id"], row["digest"])
        for row in self.connection.execute("SELECT * FROM documents"):
            model._heads[row["id"]] = Head(row["id"], row["head_id"], row["revision"])
            if row["source_id"]:
                model._document_sources[row["id"]] = row["source_id"]
        for row in self.connection.execute("SELECT * FROM batches"):
            base_record = model._streams[row["base_id"]]
            base = model._payloads[base_record.semantic_sha256]
            request = parse_batch(row["request"])
            saved = json.loads(row["plan"])
            compiled = plan(base, request, reserved_block_ids=frozenset(saved["reserved_block_ids"]))
            if compiled.seal != row["plan_digest"] or compiled.payload() != saved:
                raise ModelError("PLAN_VERSION", "stored plan differs from current CPU semantics")
            model._candidates[row["id"]] = Candidate(row["id"], row["document_id"], row["base_id"], row["expected_revision"], request, compiled, tuple(json.loads(row["output_ids"])), row["result_id"])
        for row in self.connection.execute("SELECT * FROM commits"):
            model._committed[row["batch_id"]] = Head(**json.loads(row["head"]))
        self.model = model
        self._saved: dict[tuple, str] = {}
        self.healthy = True

    def flush(self):
        """Upsert changed records only; return cache deltas after SQL commit succeeds."""
        pending = {}

        def changed(kind, key, value):
            identity = (kind, key)
            signature = dumps(value)
            pending[identity] = signature
            return self._saved.get(identity) != signature

        for key, value in self.model._payloads.items():
            if changed("snapshot", key, value.model_dump(mode="json")):
                self.connection.execute("INSERT OR IGNORE INTO snapshots VALUES(?,?)", (key, value.model_dump_json()))
        for key, value in self.model._sources.items():
            if changed("source", key, [value.original_sha256, value.encoding]):
                self.connection.execute("INSERT OR IGNORE INTO sources VALUES(?,?,?,?)", (key, value.original_bytes, value.encoding, value.original_sha256))
        for key, value in self.model._heads.items():
            if changed("head", key, asdict(value)):
                self.connection.execute("INSERT INTO documents VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET head_id=excluded.head_id,revision=excluded.revision,source_id=excluded.source_id", (key, value.stream_id, value.revision, self.model._document_sources.get(key)))
        for key, value in self.model._streams.items():
            if changed("stream", key, asdict(value)):
                self.connection.execute("INSERT INTO streams VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET digest=excluded.digest", (key, value.document_id, value.parent_id, value.batch_id, value.prefix_length, value.producer_operation_id, value.semantic_sha256))
        for key, value in self.model._candidates.items():
            if changed("batch", key, value.compiled.seal):
                self.connection.execute("INSERT OR IGNORE INTO batches VALUES(?,?,?,?,?,?,?,?,?)", (key, value.document_id, value.base_stream_id, value.expected_revision, value.batch.model_dump_json(), dumps(value.compiled.payload()), value.compiled.seal, dumps(list(value.output_stream_ids)), value.result_stream_id))
                for index, op in enumerate(value.batch.operations):
                    self.connection.execute("INSERT OR IGNORE INTO transformations VALUES(?,?,?,?,?)", (key, op.operation_id, index, op.model_dump_json(), value.output_stream_ids[index]))
        for key, value in self.model._committed.items():
            if changed("commit", key, asdict(value)):
                self.connection.execute("INSERT OR IGNORE INTO commits VALUES(?,?)", (key, dumps(asdict(value))))
        return pending

    def close(self):
        self.healthy = False
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
