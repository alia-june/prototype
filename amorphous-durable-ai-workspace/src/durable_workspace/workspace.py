from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import time
import uuid
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import INT64_MAX, dumps, loads, normalize, sha256 as canonical_sha256
from .formats import bundle, read_jsonl, read_sqlite, read_xml, write_jsonl, write_sqlite, write_xml

ZERO_HASH = "0" * 64
SCHEMA_VERSION = "DWSK-1"
RECOVERY_MARKER = ".dwsk-recovery.json"
RECOVERY_GUARD = "workspace has incomplete recovery; operator review required"

class WorkspaceError(RuntimeError): pass
class SnapshotError(WorkspaceError): pass
class RecoveryError(WorkspaceError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details


def _recovery_identity(path: Path) -> tuple[int, int]:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()) or not path.is_file():
        raise RecoveryError("recovery marker ownership cannot be verified")
    info = path.stat(follow_symlinks=False)
    return info.st_dev, info.st_ino


def _recovery_marker_present(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    return True


def _read_recovery_record(path: Path) -> dict[str, Any]:
    _recovery_identity(path)
    if path.stat().st_size > 65536:
        raise RecoveryError("recovery marker exceeds its size limit")
    record = json.loads(path.read_text(encoding="utf-8"))
    if type(record) is not dict:
        raise RecoveryError("recovery marker is not an object")
    return record


def _recovery_error_record(error: BaseException) -> dict[str, str]:
    return {"error_type": type(error).__name__, "message": str(error)[:2048]}


def _write_failed_recovery_record(path: Path, record: dict[str, Any], identity: tuple[int, int],
                                  require_id: bool) -> None:
    if _recovery_identity(path) != identity:
        raise RecoveryError("recovery marker ownership changed")
    if require_id and _read_recovery_record(path).get("recovery_id") != record["recovery_id"]:
        raise RecoveryError("recovery marker ownership changed")
    temporary = path.with_name(path.name + "." + record["recovery_id"] + ".tmp")
    with temporary.open("xb") as handle:
        handle.write((json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    # A failed temporary record remains evidence; the original claim is retained.
    os.replace(temporary, path)


def _record_key(key: Any) -> str:
    if not isinstance(key, str) or not key:
        raise WorkspaceError("key must be a non-empty string")
    return normalize(key)


def _snapshot_key(key: Any, label: str) -> None:
    try:
        _record_key(key)
    except WorkspaceError as exc:
        raise SnapshotError(f"{label} must be a non-empty string") from exc


def _snapshot_counter(value: Any, label: str, minimum: int) -> int:
    if type(value) is not int or not minimum <= value <= INT64_MAX:
        domain = "nonnegative" if minimum == 0 else "positive"
        raise SnapshotError(f"{label} must be a {domain} signed 64-bit integer")
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _fsync_file(path: Path) -> None:
    # Windows _commit/os.fsync needs a write-capable descriptor. r+b preserves
    # the completed file bytes and does not truncate or append to the file.
    with path.open("r+b") as f:
        os.fsync(f.fileno())


def _fsync_dir(path: Path) -> None:
    # This standard-library implementation does not flush directory handles on
    # Windows. File fsync still runs; directory-entry power-loss durability is
    # not established on Windows by this helper or the readiness checks.
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def _replace_latest(source: Path, target: Path) -> None:
    """Retry only Windows pointer-sharing failures, without removing target.

    The caller retains ownership of the fully written/fsynced source. Each
    attempt is the same atomic replacement; a complete generation is never
    rolled back. A persistent error escapes with its original exception.
    """
    deadline = time.monotonic() + 2.0
    delay = 0.01
    while True:
        try:
            os.replace(source, target)
            return
        except OSError as exc:
            if os.name != "nt" or getattr(exc, "winerror", None) not in (5, 32, 33):
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise
            time.sleep(min(delay, remaining))
            # Do not start another replacement after the retry deadline.
            if time.monotonic() >= deadline:
                raise
            delay = min(delay * 2, 0.1)


def _windows_mutex_api():
    """Load typed Win32 bindings without adding a package dependency."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    declarations = [
        (kernel.CreateMutexW, [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
        (kernel.WaitForSingleObject, [wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
        (kernel.ReleaseMutex, [wintypes.HANDLE], wintypes.BOOL),
        (kernel.CloseHandle, [wintypes.HANDLE], wintypes.BOOL),
        (kernel.GetCurrentProcess, [], wintypes.HANDLE),
        (kernel.LocalFree, [ctypes.c_void_p], ctypes.c_void_p),
        (security.OpenProcessToken, [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)], wintypes.BOOL),
        (security.GetTokenInformation, [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
        (security.ConvertSidToStringSidW, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)], wintypes.BOOL),
    ]
    for function, arguments, result in declarations:
        function.argtypes = arguments
        function.restype = result
    return ctypes, wintypes, kernel, security


def _publication_mutex_name(snapshots_dir: Path) -> str:
    ctypes, wintypes, kernel, security = _windows_mutex_api()
    token = wintypes.HANDLE()
    if not security.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008, ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        needed = wintypes.DWORD()
        security.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        if ctypes.get_last_error() != 122 or not needed.value:
            raise ctypes.WinError(ctypes.get_last_error())
        buffer = ctypes.create_string_buffer(needed.value)
        if not security.GetTokenInformation(token, 1, buffer, needed.value, ctypes.byref(needed)):
            raise ctypes.WinError(ctypes.get_last_error())
        sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
        text = ctypes.c_void_p()
        if not security.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            identity = ctypes.wstring_at(text)
        finally:
            kernel.LocalFree(text)
    finally:
        if not kernel.CloseHandle(token):
            raise ctypes.WinError(ctypes.get_last_error())
    path = os.path.normcase(str(snapshots_dir.resolve()))
    digest = hashlib.sha256((identity + "\0" + path).encode("utf-8")).hexdigest()
    return "Local\\DWSK.Publication.v1." + digest


def _validate_abandoned_publication(snapshots_dir: Path) -> None:
    """An abandoned owner is a reason to inspect, never a success signal."""
    pointer = snapshots_dir / "LATEST"
    if pointer.is_symlink():
        raise SnapshotError("abandoned publication mutex: existing LATEST is inconsistent")
    if not pointer.exists():
        return  # Valid when the first publisher died before pointer promotion.
    try:
        generation = pointer.read_text(encoding="utf-8").strip()
        if (not generation or generation in (".", "..") or generation.startswith(".")
                or any(char in generation for char in ("/", "\\", ":"))):
            raise ValueError("invalid generation name")
        snapshot = snapshots_dir / generation
        if snapshot.is_symlink() or snapshot.resolve().parent != snapshots_dir.resolve():
            raise ValueError("generation escapes snapshot directory")
        manifest_path = snapshot / "manifest.json"
        if manifest_path.is_symlink():
            raise ValueError("manifest is a symbolic link")
        manifest = loads(manifest_path.read_text(encoding="utf-8"))
        expected_files = {"sqlite": "snapshot.sqlite3", "jsonl": "snapshot.jsonl", "xml": "snapshot.xml"}
        if (manifest.get("generation") != generation
                or set(manifest["representations"]) != set(expected_files)):
            raise ValueError("referenced generation identity is inconsistent")
        for kind, filename in expected_files.items():
            if manifest["representations"][kind]["file"] != filename or (snapshot / filename).is_symlink():
                raise ValueError("representation path is inconsistent")
        report = DurableWorkspace.inspect_snapshot(snapshot)
        if (set(report["representations"]) != {"sqlite", "jsonl", "xml"}
                or not all(value["valid"] is True for value in report["representations"].values())
                or report["manifest_digest_matches_quorum"] is not True):
            raise ValueError("referenced generation is not complete and valid")
    except Exception as exc:
        raise SnapshotError("abandoned publication mutex: existing LATEST is inconsistent") from exc


@contextmanager
def _publication_mutex(snapshots_dir: Path):
    if os.name != "nt":
        yield
        return
    ctypes, _, kernel, _ = _windows_mutex_api()
    handle = kernel.CreateMutexW(None, False, _publication_mutex_name(snapshots_dir))
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    owned = False
    try:
        outcome = kernel.WaitForSingleObject(handle, 5000)
        if outcome == 258:
            raise SnapshotError("publication mutex acquisition timed out")
        if outcome not in (0, 0x80):
            if outcome == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
            raise SnapshotError("unexpected publication mutex wait result")
        owned = True
        if outcome == 0x80:
            _validate_abandoned_publication(snapshots_dir)
        yield
    finally:
        active_error = sys.exc_info()[1]
        cleanup_error = None
        if owned and not kernel.ReleaseMutex(handle):
            cleanup_error = ctypes.WinError(ctypes.get_last_error())
        if not kernel.CloseHandle(handle) and cleanup_error is None:
            cleanup_error = ctypes.WinError(ctypes.get_last_error())
        if cleanup_error is not None:
            if active_error is not None:
                active_error.add_note("publication mutex cleanup failed: " + str(cleanup_error))
            else:
                raise cleanup_error


class DurableWorkspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.db_path = self.root / "workspace.sqlite3"
        self.snapshots_dir = self.root / "snapshots"
        self._recovery_claim = None
        self._recovery_identity = None

    def _check_recovery_guard(self) -> None:
        marker = self.root / RECOVERY_MARKER
        try:
            present = _recovery_marker_present(marker)
        except OSError as error:
            raise WorkspaceError(RECOVERY_GUARD) from error
        if not present:
            if self._recovery_claim is not None:
                raise WorkspaceError(RECOVERY_GUARD)
            return
        if self._recovery_claim is not None:
            try:
                record = _read_recovery_record(marker)
                if (_recovery_identity(marker) == self._recovery_identity
                        and record.get("recovery_id") == self._recovery_claim
                        and record.get("schema") == "DWSK-RECOVERY-1"
                        and record.get("status") == "IN_PROGRESS"):
                    return
            except Exception:
                pass
        raise WorkspaceError(RECOVERY_GUARD)

    @classmethod
    def init(cls, root: str | Path) -> "DurableWorkspace":
        ws = cls(root)
        ws._check_recovery_guard()
        ws.root.mkdir(parents=True, exist_ok=True)
        ws.snapshots_dir.mkdir(exist_ok=True)
        if ws.db_path.exists():
            raise WorkspaceError(f"workspace already exists: {ws.db_path}")
        conn = sqlite3.connect(ws.db_path)
        try:
            conn.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=FULL;
            PRAGMA foreign_keys=ON;
            CREATE TABLE workspace_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE records(key TEXT PRIMARY KEY, value_json TEXT NOT NULL, revision INTEGER NOT NULL);
            CREATE TABLE journal(
                seq INTEGER PRIMARY KEY,
                event_id TEXT NOT NULL UNIQUE,
                timestamp_utc TEXT NOT NULL,
                kind TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_event_sha256 TEXT NOT NULL,
                event_sha256 TEXT NOT NULL UNIQUE
            );
            """)
            wid = str(uuid.uuid4())
            conn.executemany("INSERT INTO workspace_meta VALUES (?,?)", [
                ("schema_version", SCHEMA_VERSION), ("workspace_id", wid), ("created_at", _utc_now())
            ])
            conn.commit()
        finally:
            conn.close()
        return ws

    def _connect(self) -> sqlite3.Connection:
        self._check_recovery_guard()
        if not self.db_path.exists(): raise WorkspaceError("workspace is not initialized")
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _append_event(self, conn: sqlite3.Connection, kind: str, payload: Any) -> dict[str, Any]:
        row = conn.execute("SELECT seq,event_sha256 FROM journal ORDER BY seq DESC LIMIT 1").fetchone()
        seq = 1 if row is None else row[0] + 1
        previous = ZERO_HASH if row is None else row[1]
        core = normalize({
            "seq": seq,
            "event_id": str(uuid.uuid4()),
            "timestamp_utc": _utc_now(),
            "kind": kind,
            "payload": payload,
            "previous_event_sha256": previous,
        })
        event_hash = canonical_sha256(core)
        event = {**core, "event_sha256": event_hash}
        conn.execute(
            "INSERT INTO journal VALUES (?,?,?,?,?,?,?)",
            (seq, event["event_id"], event["timestamp_utc"], kind, dumps(payload), previous, event_hash),
        )
        return event

    def set(self, key: str, value: Any) -> dict[str, Any]:
        key = _record_key(key)
        value = normalize(value)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT revision FROM records WHERE key=?", (key,)).fetchone()
            revision = 1 if row is None else row[0] + 1
            conn.execute(
                "INSERT INTO records(key,value_json,revision) VALUES (?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,revision=excluded.revision",
                (key, dumps(value), revision),
            )
            event = self._append_event(conn, "record.set", {"key": key, "value": value, "revision": revision})
            conn.commit(); return event
        except Exception:
            conn.rollback(); raise
        finally: conn.close()

    def delete(self, key: str) -> dict[str, Any]:
        key = _record_key(key)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT revision FROM records WHERE key=?", (key,)).fetchone()
            revision = 1 if row is None else row[0] + 1
            conn.execute("DELETE FROM records WHERE key=?", (key,))
            event = self._append_event(conn, "record.delete", {"key": key, "revision": revision})
            conn.commit(); return event
        except Exception:
            conn.rollback(); raise
        finally: conn.close()

    def get(self, key: str) -> Any:
        key = _record_key(key)
        conn = self._connect()
        try:
            row = conn.execute("SELECT value_json FROM records WHERE key=?", (key,)).fetchone()
            if row is None: raise KeyError(key)
            return loads(row[0])
        finally: conn.close()

    def _export_bundle(self) -> dict[str, Any]:
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            meta = {k: v for k, v in conn.execute("SELECT key,value FROM workspace_meta ORDER BY key")}
            records = {k: loads(v) for k, v in conn.execute("SELECT key,value_json FROM records ORDER BY key")}
            events = []
            for seq,eid,ts,kind,payload,prev,ehash in conn.execute(
                "SELECT seq,event_id,timestamp_utc,kind,payload_json,previous_event_sha256,event_sha256 FROM journal ORDER BY seq"
            ):
                events.append(normalize({"seq": seq,"event_id": eid,"timestamp_utc": ts,"kind": kind,
                                         "payload": loads(payload),"previous_event_sha256": prev,"event_sha256": ehash}))
            head = events[-1]["event_sha256"] if events else ZERO_HASH
            b = bundle(records, events, {**meta, "journal_head": head, "event_count": len(events)})
            conn.rollback()
            return b
        finally: conn.close()

    @staticmethod
    def _verified_replay(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
        """Check the chain and declared values, returning the replayed state.

        The event interpretation is the existing recovery interpretation. Values
        are compared as canonical JSON so booleans and integers remain distinct.
        This does not add a new snapshot format or higher-level record schema.
        """
        meta = data.get("meta")
        if not isinstance(meta, dict):
            raise SnapshotError("snapshot metadata must be an object")
        event_count = _snapshot_counter(meta.get("event_count"), "snapshot event_count", 0)
        events = data["events"]
        for record in data["records"]:
            if not isinstance(record, dict):
                raise SnapshotError("snapshot record must be an object")
            _snapshot_key(record.get("key"), "snapshot record key")
        prev = ZERO_HASH
        expected_seq = 1
        for event in events:
            if not isinstance(event, dict):
                raise SnapshotError("journal event must be an object")
            sequence = _snapshot_counter(event.get("seq"), "journal sequence", 1)
            if sequence != expected_seq: raise SnapshotError("journal sequence gap")
            if event.get("kind") in ("record.set", "record.delete"):
                payload = event.get("payload")
                if not isinstance(payload, dict):
                    raise SnapshotError("journal record payload must be an object")
                _snapshot_key(payload.get("key"), "journal record key")
                _snapshot_counter(payload.get("revision"), "journal revision", 1)
            if event["previous_event_sha256"] != prev: raise SnapshotError("journal previous hash mismatch")
            core = {k: event[k] for k in ("seq","event_id","timestamp_utc","kind","payload","previous_event_sha256")}
            calculated = canonical_sha256(core)
            if calculated != event["event_sha256"]: raise SnapshotError("journal event hash mismatch")
            prev = calculated; expected_seq += 1
        if meta.get("journal_head") != prev: raise SnapshotError("journal head mismatch")
        if event_count != len(events): raise SnapshotError("event count mismatch")
        state = {}
        revisions = {}
        for event in events:
            payload = event["payload"]
            if event["kind"] == "record.set":
                state[payload["key"]] = payload["value"]
                revisions[payload["key"]] = payload["revision"]
            elif event["kind"] == "record.delete":
                state.pop(payload["key"], None)
                revisions[payload["key"]] = payload["revision"]
        declared = {record["key"]: record["value"] for record in data["records"]}
        if dumps(state) != dumps(declared):
            raise SnapshotError("journal replay state disagrees with snapshot records")
        return state, revisions

    @staticmethod
    def verify_bundle(data: dict[str, Any]) -> None:
        DurableWorkspace._verified_replay(data)

    def verify(self) -> dict[str, Any]:
        conn = self._connect()
        try:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok": raise WorkspaceError(f"SQLite integrity check failed: {integrity}")
        finally: conn.close()
        data = self._export_bundle(); self.verify_bundle(data)
        return {"ok": True, "logical_digest": canonical_sha256(data), "event_count": len(data["events"]), "record_count": len(data["records"])}

    def checkpoint(self) -> Path:
        data = self._export_bundle(); self.verify_bundle(data)
        generation = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid.uuid4().hex[:12]
        staging = self.snapshots_dir / f".staging-{generation}"
        final = self.snapshots_dir / generation
        latest_tmp = self.snapshots_dir / f".LATEST-{generation}.tmp"
        latest_tmp_created = False
        staging.mkdir(parents=False, exist_ok=False)
        try:
            paths = {
                "sqlite": staging / "snapshot.sqlite3",
                "jsonl": staging / "snapshot.jsonl",
                "xml": staging / "snapshot.xml",
            }
            write_sqlite(paths["sqlite"], data); write_jsonl(paths["jsonl"], data); write_xml(paths["xml"], data)
            for p in paths.values(): _fsync_file(p)
            logical = canonical_sha256(data)
            manifest = normalize({
                "format": "DWSK-SNAPSHOT-1", "generation": generation, "created_at": _utc_now(),
                "logical_digest": logical,
                "representations": {name: {"file": p.name, "sha256": _hash_file(p), "size": p.stat().st_size} for name,p in paths.items()},
            })
            manifest_path = staging / "manifest.json"
            manifest_path.write_text(dumps(manifest) + "\n", encoding="utf-8", newline="\n"); _fsync_file(manifest_path)
            _fsync_dir(staging)
            os.replace(staging, final); _fsync_dir(self.snapshots_dir)
            with latest_tmp.open("x", encoding="utf-8", newline="\n") as f:
                latest_tmp_created = True
                f.write(generation + "\n")
            _fsync_file(latest_tmp)
            with _publication_mutex(self.snapshots_dir):
                _replace_latest(latest_tmp, self.snapshots_dir / "LATEST")
                latest_tmp_created = False
                _fsync_dir(self.snapshots_dir)
            return final
        except Exception:
            # Only this generation's staging directory and owned pointer file
            # are eligible for cleanup. A published generation is preserved.
            if staging.resolve().parent == self.snapshots_dir.resolve():
                shutil.rmtree(staging, ignore_errors=True)
            if latest_tmp_created:
                latest_tmp.unlink(missing_ok=True)
            raise

    @staticmethod
    def _read_snapshot_representation(path: Path, kind: str) -> dict[str, Any]:
        if kind == "sqlite": return read_sqlite(path)
        if kind == "jsonl": return read_jsonl(path)
        if kind == "xml": return read_xml(path)
        raise SnapshotError(f"unknown representation: {kind}")

    @classmethod
    def inspect_snapshot(cls, snapshot_dir: str | Path) -> dict[str, Any]:
        sd = Path(snapshot_dir)
        manifest_path = sd / "manifest.json"
        if not manifest_path.exists(): raise SnapshotError("snapshot manifest missing")
        manifest = loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("format") != "DWSK-SNAPSHOT-1": raise SnapshotError("unsupported snapshot format")
        results = {}
        groups: dict[str, list[str]] = {}
        parsed = {}
        for kind, spec in manifest["representations"].items():
            p = sd / spec["file"]
            try:
                file_hash_ok = p.exists() and _hash_file(p) == spec["sha256"] and p.stat().st_size == spec["size"]
                if not file_hash_ok: raise SnapshotError("file hash/size mismatch")
                data = cls._read_snapshot_representation(p, kind); cls.verify_bundle(data)
                digest = canonical_sha256(data)
                parsed[kind] = data; groups.setdefault(digest, []).append(kind)
                results[kind] = {"valid": True, "logical_digest": digest}
            except Exception as exc:
                results[kind] = {"valid": False, "error": str(exc)}
        quorum_digest = None
        quorum_kinds = []
        for digest, kinds in groups.items():
            if len(kinds) >= 2 and len(kinds) > len(quorum_kinds): quorum_digest, quorum_kinds = digest, kinds
        if len([d for d,k in groups.items() if len(k) >= 2]) > 1:
            raise RecoveryError("multiple conflicting quorums")
        return {"manifest": manifest, "representations": results, "quorum_digest": quorum_digest, "quorum_kinds": quorum_kinds,
                "manifest_digest_matches_quorum": quorum_digest == manifest.get("logical_digest") if quorum_digest else False,
                "_parsed": parsed}

    @classmethod
    def recover(cls, snapshot_dir: str | Path, target_root: str | Path) -> "DurableWorkspace":
        report = cls.inspect_snapshot(snapshot_dir)
        digest = report["quorum_digest"]
        if digest is None: raise RecoveryError("automatic recovery requires at least two agreeing valid representations")
        if digest != report["manifest"].get("logical_digest"):
            raise RecoveryError("quorum logical digest disagrees with published manifest")
        source_kind = report["quorum_kinds"][0]
        data = report["_parsed"][source_kind]
        # Complete consistency validation before creating or changing a target.
        state, revisions = cls._verified_replay(data)
        target = Path(target_root).resolve()
        if target.exists() and (not target.is_dir() or any(target.iterdir())):
            raise RecoveryError("recovery target must be absent or empty")
        ws = cls(target)
        marker = target / RECOVERY_MARKER
        recovery_id = uuid.uuid4().hex
        receipt = {"schema": "DWSK-RECOVERY-1", "recovery_id": recovery_id,
                   "status": "IN_PROGRESS", "phase": "claimed", "expected_logical_digest": digest}
        phase = "create_target"
        claimed = False
        claim_confirmed = False
        identity = None
        conn = None
        connection_closed = True
        verified = False
        try:
            target.mkdir(parents=True, exist_ok=True)
            phase = "claim"
            with marker.open("xb") as handle:
                claimed = True
                info = os.fstat(handle.fileno())
                identity = (info.st_dev, info.st_ino)
                ws._recovery_claim = recovery_id
                ws._recovery_identity = identity
                handle.write((json.dumps(receipt, sort_keys=True) + "\n").encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
                claim_confirmed = True
            phase = "destination_check"
            if set(path.name for path in target.iterdir()) != {RECOVERY_MARKER}:
                raise RecoveryError("recovery target changed after claim")
            ws.snapshots_dir.mkdir(exist_ok=False)
            phase = "database_open"
            conn = sqlite3.connect(ws.db_path)
            connection_closed = False
            phase = "schema"
            conn.executescript("""
            PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
            CREATE TABLE workspace_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE records(key TEXT PRIMARY KEY, value_json TEXT NOT NULL, revision INTEGER NOT NULL);
            CREATE TABLE journal(seq INTEGER PRIMARY KEY,event_id TEXT NOT NULL UNIQUE,timestamp_utc TEXT NOT NULL,kind TEXT NOT NULL,payload_json TEXT NOT NULL,previous_event_sha256 TEXT NOT NULL,event_sha256 TEXT NOT NULL UNIQUE);
            """)
            phase = "metadata"
            for k,v in data["meta"].items():
                if k not in ("journal_head","event_count"): conn.execute("INSERT INTO workspace_meta VALUES (?,?)", (k, str(v)))
            # Preserve the checked chain exactly and use its replayed state.
            phase = "events"
            for event in data["events"]:
                p = event["payload"]; kind = event["kind"]
                conn.execute("INSERT INTO journal VALUES (?,?,?,?,?,?,?)", (event["seq"],event["event_id"],event["timestamp_utc"],kind,dumps(p),event["previous_event_sha256"],event["event_sha256"]))
            phase = "records"
            for key,value in state.items(): conn.execute("INSERT INTO records VALUES (?,?,?)", (key,dumps(value),revisions[key]))
            phase = "commit"
            conn.commit()
            phase = "database_close"
            conn.close()
            conn = None
            connection_closed = True
            phase = "verify"
            if ws.verify()["logical_digest"] != digest:
                raise RecoveryError("recovered logical digest differs from snapshot")
            verified = True
            phase = "complete"
            ws._check_recovery_guard()
            marker.unlink()
            return ws
        except BaseException as primary:
            secondary = []
            if conn is not None:
                for attempt in range(2):
                    try:
                        conn.close()
                        connection_closed = True
                        conn = None
                        break
                    except Exception as error:
                        secondary.append({"stage": "builder_connection_close", **_recovery_error_record(error)})
            failure_record = {**receipt, "status": "FAILED", "phase": phase,
                              "primary_error": _recovery_error_record(primary),
                              "secondary_errors": list(secondary), "builder_connection_closed": connection_closed,
                              "verification_completed": verified, "claim_confirmed": claim_confirmed}
            if claimed:
                try:
                    if _recovery_marker_present(marker):
                        _write_failed_recovery_record(marker, failure_record, identity, claim_confirmed)
                    else:
                        # A namespace error may have removed the claim. Recreate exclusively,
                        # never replace somebody else's claim; report failure if this is uncertain.
                        with marker.open("xb") as handle:
                            handle.write((json.dumps(failure_record, sort_keys=True) + "\n").encode("utf-8"))
                            handle.flush()
                            os.fsync(handle.fileno())
                except Exception as error:
                    secondary.append({"stage": "failure_receipt", **_recovery_error_record(error)})
            marker_state = "ABSENT"
            present = None
            try:
                present = _recovery_marker_present(marker)
                if present:
                    current = _read_recovery_record(marker)
                    marker_state = current.get("status", "UNRECOGNIZED") if current.get("recovery_id") == recovery_id else "FOREIGN"
            except Exception as error:
                marker_state = "UNREADABLE_OR_UNVERIFIED"
                secondary.append({"stage": "marker_state", **_recovery_error_record(error)})
            if present is None:
                target_state = "GUARD_UNCERTAIN"
            elif present:
                target_state = "RETAINED_INCOMPLETE" if claimed else "UNCLAIMED_OCCUPIED"
            elif verified:
                target_state = "VERIFIED_UNACKNOWLEDGED"
            elif claimed:
                target_state = "GUARD_UNCERTAIN"
            else:
                try:
                    target_state = "EMPTY_UNCLAIMED" if target.is_dir() and not any(target.iterdir()) else "UNCLAIMED_OCCUPIED_OR_ABSENT"
                except OSError:
                    target_state = "UNCLAIMED_STATE_UNVERIFIED"
            details = {"status": "RECOVERY_INCOMPLETE", "phase": phase, "recovery_id": recovery_id,
                       "target_name": target.name, "claimed": claimed, "claim_confirmed": claim_confirmed,
                       "marker_state": marker_state, "target_state": target_state,
                       "builder_connection_closed": connection_closed, "verification_completed": verified,
                       "primary_error": _recovery_error_record(primary), "secondary_errors": secondary}
            if not isinstance(primary, Exception):
                primary.add_note("Recovery did not return success; retained state requires operator review")
                raise
            error = RecoveryError("recovery incomplete; retained destination requires operator review", details)
            if conn is not None:
                error.resource_owner = conn
            raise error from primary
        finally:
            ws._recovery_claim = None
            ws._recovery_identity = None
