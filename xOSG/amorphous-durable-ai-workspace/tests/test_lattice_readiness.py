"""Focused readiness checks; retained fixtures are synthetic and opt-in."""
from __future__ import annotations

import concurrent.futures
import errno
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from durable_workspace import DurableWorkspace, RecoveryError, SnapshotError
from durable_workspace.canonical import dumps, sha256
from durable_workspace.formats import read_jsonl, write_jsonl, write_xml
import durable_workspace.workspace as implementation


def fingerprint(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


class LatticeReadinessTests(unittest.TestCase):
    def setUp(self):
        retained = os.environ.get("DWSK_READINESS_FIXTURE_ROOT")
        self.temporary = None
        if retained:
            base = Path(retained).resolve()
            approved = Path(__file__).resolve().parents[2] / "fixtures"
            self.assertTrue(base.is_relative_to(approved))
            self.case = base / self._testMethodName
            self.case.mkdir(parents=True, exist_ok=False)
        else:
            self.temporary = tempfile.TemporaryDirectory()
            self.case = Path(self.temporary.name)
        self.observations = {}
        self.ws = DurableWorkspace.init(self.case / "workspace")

    def tearDown(self):
        if self.temporary is None:
            (self.case / "observations.json").write_text(
                json.dumps(self.observations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            self.temporary.cleanup()

    @staticmethod
    def alter_value(ws: DurableWorkspace, key: str, value) -> None:
        connection = sqlite3.connect(ws.db_path)
        try:
            connection.execute("UPDATE records SET value_json=? WHERE key=?", (dumps(value), key))
            connection.commit()
        finally:
            connection.close()

    def assert_replay_error(self, operation):
        with self.assertRaises(SnapshotError) as caught:
            operation()
        self.assertIs(type(caught.exception), SnapshotError)
        self.assertEqual(str(caught.exception), "journal replay state disagrees with snapshot records")

    def test_verify_rejects_unjournaled_value_and_preserves_files(self):
        self.ws.set("task", {"phase": "review", "sequence": 1})
        self.alter_value(self.ws, "task", {"phase": "unrecorded", "sequence": 2})
        before = fingerprint(self.ws.root)
        self.assert_replay_error(self.ws.verify)
        after = fingerprint(self.ws.root)
        self.assertEqual(after, before)
        self.observations = {"expected_exception": "SnapshotError", "before": before, "after": after,
                             "all_input_file_hashes_preserved": True}

    def test_checkpoint_rejects_disagreement_before_publication(self):
        self.ws.set("task", {"phase": "review", "sequence": 1})
        initial = self.ws.checkpoint()
        self.alter_value(self.ws, "task", {"phase": "unrecorded", "sequence": 2})
        before = fingerprint(self.ws.root)
        self.assert_replay_error(self.ws.checkpoint)
        after = fingerprint(self.ws.root)
        self.assertEqual(after, before)
        self.assertEqual((self.ws.snapshots_dir / "LATEST").read_text().strip(), initial.name)
        self.observations = {"expected_exception": "SnapshotError", "before": before, "after": after,
                             "all_input_file_hashes_preserved": True, "new_generations": 0}

    def test_replay_comparison_distinguishes_boolean_and_integer(self):
        cases = [(1, True), (False, 0), ({"nested": [True, 1]}, {"nested": [1, True]})]
        observed = []
        for index, (recorded, changed) in enumerate(cases):
            with self.subTest(index=index):
                ws = DurableWorkspace.init(self.case / f"typed-{index}")
                ws.set("value", recorded)
                self.alter_value(ws, "value", changed)
                before = fingerprint(ws.root)
                self.assert_replay_error(ws.verify)
                self.assert_replay_error(ws.checkpoint)
                self.assertEqual(fingerprint(ws.root), before)
                observed.append({"journal_value": recorded, "declared_value": changed,
                                 "expected_exception": "SnapshotError", "file_hashes_preserved": True})
        self.observations = {"typed_mismatch_cases": observed}

    def test_recovery_rejects_forged_quorum_before_changing_targets(self):
        self.ws.set("task", {"phase": "review", "sequence": 1})
        snapshot = self.ws.checkpoint()
        forged = read_jsonl(snapshot / "snapshot.jsonl")
        forged["records"][0]["value"] = {"phase": "unrecorded", "sequence": 2}
        write_jsonl(snapshot / "snapshot.jsonl", forged)
        write_xml(snapshot / "snapshot.xml", forged)
        manifest_path = snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["logical_digest"] = sha256(forged)
        for kind, name in (("jsonl", "snapshot.jsonl"), ("xml", "snapshot.xml")):
            data = (snapshot / name).read_bytes()
            manifest["representations"][kind].update(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
        manifest_path.write_text(dumps(manifest) + "\n", encoding="utf-8")
        before = fingerprint(snapshot)
        report = DurableWorkspace.inspect_snapshot(snapshot)
        self.assertIsNone(report["quorum_digest"])
        self.assertIs(report["representations"]["sqlite"]["valid"], True)
        for kind in ("jsonl", "xml"):
            self.assertIs(report["representations"][kind]["valid"], False)
            self.assertEqual(report["representations"][kind]["error"],
                             "journal replay state disagrees with snapshot records")
        absent = self.case / "absent-recovery-target"
        empty = self.case / "empty-recovery-target"
        empty.mkdir()
        for target in (absent, empty):
            with self.assertRaises(RecoveryError) as caught:
                DurableWorkspace.recover(snapshot, target)
            self.assertIs(type(caught.exception), RecoveryError)
            self.assertEqual(str(caught.exception), "automatic recovery requires at least two agreeing valid representations")
        self.assertFalse(absent.exists())
        self.assertEqual(list(empty.iterdir()), [])
        self.assertEqual(fingerprint(snapshot), before)
        self.observations = {"forged_formats": ["jsonl", "xml"], "hashes_and_manifest_recomputed": True,
                             "expected_exception": "RecoveryError", "absent_target_remains_absent": True,
                             "empty_target_remains_empty": True, "before": before, "after": fingerprint(snapshot)}

    def test_valid_replay_preserves_delete_recreate_and_recovery(self):
        self.ws.set("x", 1)
        self.ws.set("x", 2)
        self.ws.delete("x")
        self.ws.delete("missing")
        self.ws.set("x", False)
        self.ws.set("x", True)
        self.ws.set("y", {"nested": [1, None]})
        self.ws.delete("y")
        before = self.ws.verify()
        snapshot = self.ws.checkpoint()
        source_files = fingerprint(self.ws.root)
        recovered = DurableWorkspace.recover(snapshot, self.case / "recovered")
        self.assertIs(recovered.get("x"), True)
        self.assertEqual(recovered.verify(), before)
        self.assertEqual(dumps(recovered._export_bundle()), dumps(self.ws._export_bundle()))
        connection = sqlite3.connect(recovered.db_path)
        try:
            self.assertEqual(connection.execute("SELECT revision FROM records WHERE key='x'").fetchone()[0], 2)
        finally:
            connection.close()
        self.assertEqual(fingerprint(self.ws.root), source_files)
        self.observations = {"events": 8, "complete_logical_bundle_preserved": True,
                             "boolean_type_preserved": True, "source_file_hashes_preserved": True}

    def test_overlapping_checkpoint_publishers_complete_without_collision(self):
        self.ws.set("project", {"name": "synthetic-lattice-pilot", "phase": 1})
        before = self.ws.verify()
        barrier = threading.Barrier(2, timeout=20)
        first_finished = threading.Event()
        lock = threading.Lock()
        first_thread = []
        temporary_names = []
        original_sync = implementation._fsync_file

        def synchronize(path: Path) -> None:
            original_sync(path)
            if path.name.startswith(".LATEST") and path.suffix == ".tmp":
                with lock:
                    if not first_thread:
                        first_thread.append(threading.get_ident())
                    temporary_names.append(path.name)
                barrier.wait()
                if threading.get_ident() != first_thread[0]:
                    self.assertTrue(first_finished.wait(20))

        def publish() -> Path:
            try:
                return self.ws.checkpoint()
            finally:
                if first_thread and threading.get_ident() == first_thread[0]:
                    first_finished.set()

        with patch.object(implementation, "_fsync_file", synchronize):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                snapshots = [future.result() for future in [pool.submit(publish), pool.submit(publish)]]
        self.assertEqual(len(set(temporary_names)), 2)
        for snapshot in snapshots:
            report = DurableWorkspace.inspect_snapshot(snapshot)
            self.assertEqual(set(report["quorum_kinds"]), {"sqlite", "jsonl", "xml"})
            self.assertIs(report["manifest_digest_matches_quorum"], True)
        latest = (self.ws.snapshots_dir / "LATEST").read_text().strip()
        self.assertIn(latest, {snapshot.name for snapshot in snapshots})
        self.assertEqual(list(self.ws.snapshots_dir.glob(".LATEST*.tmp")), [])
        self.assertEqual(list(self.ws.snapshots_dir.glob(".staging-*")), [])
        self.assertEqual(self.ws.verify(), before)
        self.observations = {"publishers": 2, "forced_overlap": True, "both_returned": True,
                             "observed_temporary_names": temporary_names, "runtime_logical_state_unchanged": True,
                             "all_three_formats_valid": True, "temporary_files_remaining": 0}

    def test_manifest_sync_failure_preserves_entire_existing_tree(self):
        self.ws.set("project", {"name": "synthetic-lattice-pilot", "phase": 1})
        self.ws.checkpoint()
        before = fingerprint(self.ws.root)
        failure = OSError(errno.EIO, "synthetic manifest flush failure")
        original_sync = implementation._fsync_file

        def fail_manifest(path: Path) -> None:
            if path.name == "manifest.json":
                raise failure
            original_sync(path)

        with patch.object(implementation, "_fsync_file", fail_manifest):
            with self.assertRaises(OSError) as caught:
                self.ws.checkpoint()
        self.assertIs(caught.exception, failure)
        self.assertEqual(fingerprint(self.ws.root), before)
        self.assertEqual(list(self.ws.snapshots_dir.glob(".staging-*")), [])
        self.observations = {"injected_exception": "OSError", "errno": errno.EIO,
                             "before": before, "after": fingerprint(self.ws.root),
                             "all_existing_file_hashes_preserved": True, "new_generations": 0}

    def test_pointer_sync_failure_keeps_prior_latest_and_complete_generation(self):
        self.ws.set("project", {"name": "synthetic-lattice-pilot", "phase": 1})
        initial = self.ws.checkpoint()
        before = fingerprint(self.ws.root)
        runtime = self.ws.verify()
        failure = OSError(errno.EIO, "synthetic pointer flush failure")
        original_sync = implementation._fsync_file

        def fail_pointer(path: Path) -> None:
            if path.name.startswith(".LATEST") and path.suffix == ".tmp":
                raise failure
            original_sync(path)

        with patch.object(implementation, "_fsync_file", fail_pointer):
            with self.assertRaises(OSError) as caught:
                self.ws.checkpoint()
        self.assertIs(caught.exception, failure)
        after = fingerprint(self.ws.root)
        self.assertEqual({name: after[name] for name in before}, before)
        self.assertNotEqual(after, before)
        self.assertEqual((self.ws.snapshots_dir / "LATEST").read_text().strip(), initial.name)
        generations = [p for p in self.ws.snapshots_dir.iterdir() if p.is_dir()]
        self.assertEqual(len(generations), 2)
        for generation in generations:
            report = DurableWorkspace.inspect_snapshot(generation)
            self.assertEqual(set(report["quorum_kinds"]), {"sqlite", "jsonl", "xml"})
            self.assertIs(report["manifest_digest_matches_quorum"], True)
        self.assertEqual(list(self.ws.snapshots_dir.glob(".LATEST*.tmp")), [])
        self.assertEqual(self.ws.verify(), runtime)
        self.observations = {"injected_exception": "OSError", "errno": errno.EIO,
                             "before": before, "after": after, "prior_files_unchanged": True,
                             "prior_latest_preserved": True, "new_complete_unreferenced_generation_retained": True,
                             "full_tree_unchanged": False, "temporary_files_remaining": 0}


if __name__ == "__main__":
    unittest.main()
