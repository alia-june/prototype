"""Managed immutable artifact publication and checked cache lookup."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from .errors import ModelError
from .storage import Store, dumps

MEDIA = {"png": "image/png", "pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "zip": "application/zip"}


class ArtifactStore:
    def __init__(self, store: Store):
        self.store = store
        self.root = store.root / "artifacts"
        self.staging = store.root / "staging"
        for folder in (self.root, self.staging):
            if folder.is_symlink() or folder.is_junction():
                raise ModelError("UNSAFE_ROOT", "linked artifact directories are not supported")
            folder.mkdir(exist_ok=True)

    def path(self, relative: str):
        if not re.fullmatch(r"[0-9a-f]{64}\.(png|pdf|docx|zip)", relative):
            raise ModelError("ARTIFACT_PATH", "invalid managed artifact location")
        if self.root.is_symlink() or self.root.is_junction():
            raise ModelError("ARTIFACT_PATH", "artifact directory changed")
        result = self.root / relative
        if result.is_symlink() or result.is_junction():
            raise ModelError("ARTIFACT_PATH", "linked artifact is not supported")
        return result

    def metadata(self, artifact_id: str):
        row = self.store.connection.execute("SELECT * FROM artifacts WHERE id=? AND state='ready'", (artifact_id,)).fetchone()
        if row is None:
            raise ModelError("UNKNOWN_ARTIFACT", "artifact is not ready")
        value = dict(row)
        path = self.path(value["relative_path"])
        if not path.is_file() or path.stat().st_size != value["bytes"] or sha256(path.read_bytes()).hexdigest() != value["digest"]:
            raise ModelError("ARTIFACT_INTEGRITY", "artifact bytes do not match ready metadata")
        return {"artifact_id": value["id"], "sha256": value["digest"], "bytes": value["bytes"],
                "media_type": value["media_type"], "download_path": "/artifacts/" + value["id"],
                "relative_path": value["relative_path"]}

    def cached(self, key: str):
        row = self.store.connection.execute("SELECT * FROM render_sets WHERE cache_key=? AND state='ready'", (key,)).fetchone()
        if row is None:
            return None
        ids = self.store.connection.execute("SELECT format,artifact_id FROM render_artifacts WHERE cache_key=? ORDER BY format", (key,)).fetchall()
        try:
            expected = json.loads(row["profile"])["formats"]
            if {item["format"] for item in ids} != set(expected):
                raise ModelError("ARTIFACT_INTEGRITY", "render set is incomplete")
            return {"cache_key": key, "artifacts": {item["format"]: self.metadata(item["artifact_id"]) for item in ids},
                    "renderer_metadata": json.loads(row["metadata"])}
        except ModelError:
            with self.store.transaction():
                self.store.connection.execute("UPDATE render_sets SET state='failed' WHERE cache_key=?", (key,))
            return None

    def begin(self, spec):
        with self.store.transaction():
            self.store.connection.execute("INSERT INTO render_sets VALUES(?,?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET state='pending'", (spec.cache_key, spec.metadata["semantic_sha256"], dumps(spec.profile.model_dump(mode="json")), dumps(spec.metadata), "pending"))

    def publish_blob(self, raw, format_name):
        """Caller owns the receipt transaction; orphaned immutable files are harmless."""
        if format_name not in ("zip", "docx") or not raw or len(raw) > 32*1024*1024:
            raise ModelError("ARTIFACT_LIMIT", "invalid export format or size")
        content_hash = sha256(raw).hexdigest()
        relative = content_hash + "." + format_name
        destination = self.path(relative)
        temporary = self.staging / (uuid4().hex + ".part")
        with temporary.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if destination.exists() and sha256(destination.read_bytes()).hexdigest() != content_hash:
            os.replace(destination, self.staging / ("quarantine-"+uuid4().hex+"."+format_name))
        os.replace(temporary, destination)
        self.store.fault("after_export_files")
        key = "artifact:" + content_hash
        self.store.connection.execute("INSERT INTO artifacts VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET state='ready'", (key, content_hash, relative, MEDIA[format_name], len(raw), "ready"))
        return self.metadata(key)

    def publish(self, spec, rendered):
        files = rendered["files"]
        if set(files) != set(spec.profile.formats):
            raise ModelError("ARTIFACT_PUBLICATION", "renderer output set differs from requested formats")
        entries = []
        for format_name, raw in files.items():
            if not raw or len(raw) > 32 * 1024 * 1024:
                raise ModelError("ARTIFACT_LIMIT", "rendered artifact is empty or exceeds 32 MiB")
            if format_name == "png" and not raw.startswith(b"\x89PNG\r\n\x1a\n") or format_name == "pdf" and not raw.startswith(b"%PDF-"):
                raise ModelError("ARTIFACT_PUBLICATION", "renderer output signature is invalid")
            content_hash = sha256(raw).hexdigest()
            relative = content_hash + "." + format_name
            destination = self.path(relative)
            temporary = self.staging / (uuid4().hex + ".part")
            with temporary.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            if destination.exists() and sha256(destination.read_bytes()).hexdigest() != content_hash:
                # Preserve damaged managed bytes for inspection, rather than delete.
                os.replace(destination, self.staging / ("quarantine-" + uuid4().hex + "." + format_name))
            os.replace(temporary, destination)
            entries.append(("artifact:" + content_hash, content_hash, relative, MEDIA[format_name], len(raw), "ready", format_name))
        self.store.fault("after_artifact_files")
        metadata = {**spec.metadata, **rendered["metadata"]}
        with self.store.transaction():
            for entry in entries:
                self.store.connection.execute("INSERT INTO artifacts VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET state='ready'", entry[:6])
                self.store.connection.execute("INSERT INTO render_artifacts VALUES(?,?,?) ON CONFLICT(cache_key,format) DO UPDATE SET artifact_id=excluded.artifact_id", (spec.cache_key, entry[6], entry[0]))
            self.store.connection.execute("UPDATE render_sets SET metadata=?,state='ready' WHERE cache_key=?", (dumps(metadata), spec.cache_key))
        return self.cached(spec.cache_key)
