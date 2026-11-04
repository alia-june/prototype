from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from docstream_cpu.errors import ModelError
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store

VALIDATION_ROOT = Path(__file__).resolve().parents[2] / ".docstream" / "validation"
VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=VALIDATION_ROOT)
        self.root = Path(self.folder.name)
        self.store = Store(self.root)
        self.service = DocumentService(self.store)

    def tearDown(self):
        self.store.close()
        self.folder.cleanup()

    def ingest(self, key="initial"):
        reply = self.service.ingest({"request_key": key, "text": "Preserved\r\ntext"})
        self.assertTrue(reply["ok"], reply)
        return reply["result"]

    def transformation(self, source, key="change", mode="commit", fonts=("B", "Aptos")):
        return {"request_key": key, "base_stream_id": source["stream_id"], "mode": mode,
                "batch": {"base_sha256": source["semantic_sha256"], "operations": [
                    {"operation_id": f"op{i}", "kind": "set_font", "font_family": value}
                    for i, value in enumerate(fonts)]}}

    def restart(self):
        self.store.close()
        self.store = Store(self.root)
        self.service = DocumentService(self.store)

    def test_ingest_retry_survives_restart(self):
        payload = {"request_key": "same", "text": "Original"}
        first = self.service.ingest(payload)
        self.restart()
        self.assertEqual(self.service.ingest(payload), first)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM documents").fetchone()[0], 1)

    def test_changed_payload_reuse_rejected(self):
        self.service.ingest({"request_key": "same", "text": "Original"})
        with self.assertRaises(ModelError) as failure:
            self.service.ingest({"request_key": "same", "text": "Changed"})
        self.assertEqual(failure.exception.code, "IDEMPOTENCY_CONFLICT")

    def test_committed_noop_and_intermediates_survive_restart(self):
        source = self.ingest()
        payload = self.transformation(source, fonts=("B", "Aptos", "C", "Aptos"))
        first = self.service.transform(payload)
        self.assertTrue(first["ok"], first)
        self.assertEqual(first["result"]["property_writes"], 0)
        result = first["result"]
        self.restart()
        self.assertEqual(self.service.transform(payload), first)
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 1)
        self.assertEqual(len(self.store.model.history(result["result_stream_id"])), 5)
        prefix = result["output_stream_ids"][0]
        inspected = self.service.inspect({"target_id": prefix, "section": "content"})
        self.assertEqual(inspected["result"]["properties"]["font_family"], "B")
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 1)
        self.restart()
        self.assertIsNotNone(self.store.model.stream(prefix).semantic_sha256)

    def test_plan_then_separate_commit(self):
        source = self.ingest()
        response = self.service.transform(self.transformation(source, mode="plan", fonts=("B",)))
        self.assertTrue(response["ok"])
        self.assertFalse(response["result"]["committed"])
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 0)
        self.restart()
        committed = self.service.commit({"request_key": "commit-it", "candidate_id": response["result"]["candidate_id"]})
        self.assertTrue(committed["ok"], committed)
        self.assertEqual(committed["result"]["head"]["revision"], 1)

    def test_two_clients_cannot_lose_updates(self):
        source = self.ingest()
        first = self.service.transform(self.transformation(source, key="one", mode="plan", fonts=("B",)))
        second = self.service.transform(self.transformation(source, key="two", mode="plan", fonts=("C",)))
        def commit(item):
            return self.service.commit({"request_key": item[0], "candidate_id": item[1]})
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(commit, [("commit-one", first["result"]["candidate_id"]), ("commit-two", second["result"]["candidate_id"])]))
        self.assertEqual(sum(result["ok"] for result in results), 1)
        failed = next(result for result in results if not result["ok"])
        self.assertEqual(failed["error"]["code"], "STALE_HEAD")
        self.restart()
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 1)

    def test_rollback_restores_sql_and_in_memory_model(self):
        source = self.ingest()
        def fail(phase):
            if phase == "after_flush":
                raise RuntimeError("injected write failure")
        self.store.fault = fail
        reply = self.service.transform(self.transformation(source, fonts=("B",)))
        self.assertFalse(reply["ok"])
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 0)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM batches").fetchone()[0], 0)
        self.store.fault = lambda _: None
        self.restart()
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 0)
        self.assertEqual(self.service.job(reply["job_id"])["state"], "failed")
        self.assertEqual(self.service.transform(self.transformation(source, fonts=("B",))), reply)

    def test_inline_conflict_retains_candidate_and_receipt(self):
        source = self.ingest()
        first = self.service.transform(self.transformation(source, key="first", fonts=("B",)))
        stale = self.service.transform(self.transformation(source, key="stale", fonts=("C",)))
        self.assertFalse(stale["ok"])
        self.assertEqual(stale["error"]["code"], "STALE_HEAD")
        self.restart()
        candidate = self.store.model.candidate(stale["result"]["candidate_id"])
        self.assertEqual(self.store.model.materialize(candidate.result_stream_id).properties.font_family, "C")
        self.assertEqual(self.store.model.head(source["document_id"]).stream_id, first["result"]["result_stream_id"])

    def test_source_limit_rejects_without_partial_document(self):
        reply = self.service.ingest({"request_key": "large", "text": "x" * (1_048_576 + 1)})
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["error"]["code"], "LIMIT_EXCEEDED")
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM documents").fetchone()[0], 0)

    def test_lost_response_after_commit_replays_receipt(self):
        source = self.ingest()
        payload = self.transformation(source, fonts=("B",))
        def fail(phase):
            if phase == "after_commit":
                raise RuntimeError("lost response")
        self.store.fault = fail
        with self.assertRaises(RuntimeError):
            self.service.transform(payload)
        self.restart()
        reply = self.service.transform(payload)
        self.assertTrue(reply["ok"])
        self.assertEqual(self.store.model.head(source["document_id"]).revision, 1)

    def test_real_process_crash_recovery_at_three_boundaries(self):
        self.store.close()
        worker = Path(__file__).with_name("crash_worker.py")
        for phase in ("after_reserved", "after_flush", "after_commit"):
            root = self.root / phase
            process = subprocess.run([sys.executable, str(worker), str(root), phase], capture_output=True, timeout=20,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            self.assertEqual(process.returncode, 71, process.stderr)
            with Store(root) as recovered:
                service = DocumentService(recovered)
                row = recovered.connection.execute("SELECT * FROM requests").fetchone()
                if phase != "after_commit":
                    self.assertEqual(service.job(row["job_id"])["state"], "interrupted")
                    self.assertEqual(recovered.connection.execute("SELECT count(*) FROM documents").fetchone()[0], 0)
                reply = service.ingest({"request_key": "crash", "text": "recover"})
                self.assertTrue(reply["ok"], reply)
                self.assertEqual(recovered.connection.execute("SELECT count(*) FROM documents").fetchone()[0], 1)
                self.assertEqual(recovered.connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.store = Store(self.root)
        self.service = DocumentService(self.store)

    def test_owner_lock_rejects_second_writer(self):
        with self.assertRaises(ModelError) as failure:
            Store(self.root)
        self.assertEqual(failure.exception.code, "OWNER_BUSY")

    def test_invalid_fields_do_not_create_receipts(self):
        for payload in ({"request_key": "bad", "text": "x", "title": False},
                        {"request_key": "bad", "text": "x", "snapshot": {}},
                        {"request_key": "bad", "text": "x", "exec": "code"}):
            with self.assertRaises(ModelError):
                self.service.ingest(payload)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM requests").fetchone()[0], 0)

    def test_source_bytes_and_bounded_content_inspection(self):
        import base64
        raw = b"\xef\xbb\xbfOriginal\r\n"
        reply = self.service.ingest({"request_key": "raw", "source_base64": base64.b64encode(raw).decode()})
        source = self.store.model.source(reply["result"]["document_id"])
        self.assertEqual(source.original_bytes, raw)
        result = self.service.inspect({"target_id": reply["result"]["stream_id"], "section": "content", "block_id": "text", "offset": 2, "limit": 4})
        self.assertEqual(result["result"]["text"], "igin")

    def test_schema_and_digest_corruption_are_rejected(self):
        self.ingest()
        self.store.close()
        with closing(sqlite3.connect(self.root / "state.sqlite3")) as con:
            con.execute("UPDATE snapshots SET payload='{}'")
            con.commit()
        with self.assertRaises(ModelError):
            Store(self.root)
        # Restore a valid empty store for teardown without rewriting corrupt evidence.
        self.store = Store(self.root / "fresh")

    def test_failed_reload_disables_future_mutations(self):
        self.ingest()
        self.store.connection.execute("UPDATE snapshots SET payload='{}'")
        with self.assertRaises(ModelError):
            self.store._load()
        self.assertFalse(self.service.status()["storage_ready"])
        with self.assertRaises(ModelError) as failure:
            self.service.ingest({"request_key": "must-not-run", "text": "New"})
        self.assertEqual(failure.exception.code, "STORE_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
