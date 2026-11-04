from __future__ import annotations

import asyncio
import base64
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
import urllib.error
import urllib.request

from pypdf import PdfReader

from docstream_cpu.cli import client_call
from docstream_cpu.errors import ModelError
from docstream_cpu.models import Block, Properties, Snapshot
from docstream_cpu.rendering import RenderProfile, Renderer
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import SCHEMA, Store
from docstream_cpu.visual_service import VisualService
from test_mcp import RunningServer

ROOT = Path(__file__).resolve().parents[2] / ".docstream" / "validation"
ROOT.mkdir(parents=True, exist_ok=True)


def snapshot(text="A reusable rendering."):
    return Snapshot(properties=Properties(title="Docstream rendering test", font_family="Arial"),
                    blocks=(Block(block_id="body", text=text),))


class RenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = Renderer()

    @classmethod
    def tearDownClass(cls):
        cls.renderer.close()

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.folder.name)
        self.store = Store(self.root)
        self.service = DocumentService(self.store)
        self.visual = VisualService(self.store, self.renderer)
        self.source = self.service.ingest({"request_key": "source", "snapshot": snapshot().model_dump(mode="json")})["result"]

    def tearDown(self):
        self.store.close()
        self.folder.cleanup()

    def render(self, key="render", **extra):
        return self.visual.render({"request_key": key, "stream_id": self.source["stream_id"], "profile": {"formats": ["png"]}, **extra})

    def candidate(self, font="Times New Roman"):
        reply = self.service.transform({"request_key": "candidate", "base_stream_id": self.source["stream_id"], "mode": "plan",
            "batch": {"base_sha256": self.source["semantic_sha256"], "operations": [{"operation_id": "font", "kind": "set_font", "font_family": font}]}})
        self.assertTrue(reply["ok"], reply)
        return reply["result"]["candidate_id"]

    def test_preview_cache_and_profile_invalidation(self):
        before = self.renderer.render_count
        first = self.render()
        self.assertTrue(first["ok"], first)
        second = self.render("same-content")
        self.assertTrue(second["result"]["cache_hit"])
        self.assertEqual(self.renderer.render_count, before + 1)
        third = self.render("changed-profile", profile={"formats": ["png"], "margin_mpt": 48000})
        self.assertFalse(third["result"]["cache_hit"])
        self.assertEqual(self.renderer.render_count, before + 2)
        self.assertEqual(self.store.model.head(self.source["document_id"]).revision, 0)

    def test_warm_worker_reused_for_changed_content(self):
        self.render()
        starts = self.renderer.starts
        candidate = self.candidate()
        result = self.visual.render({"request_key": "changed", "candidate_id": candidate, "profile": {"formats": ["png"]}})
        self.assertTrue(result["ok"], result)
        self.assertEqual(self.renderer.starts, starts)

    def test_font_cycle_reuses_render_and_retains_logical_outputs(self):
        self.render()
        before = self.renderer.render_count
        reply = self.service.transform({"request_key": "cycle", "base_stream_id": self.source["stream_id"], "mode": "plan",
            "batch": {"base_sha256": self.source["semantic_sha256"], "operations": [
                {"operation_id": f"f{i}", "kind": "set_font", "font_family": font}
                for i, font in enumerate(("Times New Roman", "Arial", "Consolas", "Arial"))]}})
        self.assertEqual(reply["result"]["property_writes"], 0)
        result = self.visual.render({"request_key": "cycle-commit", "candidate_id": reply["result"]["candidate_id"], "commit": True, "profile": {"formats": ["png"]}})
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["result"]["cache_hit"])
        self.assertTrue(result["result"]["committed"])
        self.assertEqual(len(reply["result"]["output_stream_ids"]), 4)
        self.assertEqual(self.renderer.render_count, before)

    def test_missing_font_leaves_head_unchanged(self):
        candidate = self.candidate("Not-A-Registered-Font")
        reply = self.visual.render({"request_key": "missing-font", "candidate_id": candidate, "commit": True})
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["error"]["code"], "FONT_UNAVAILABLE")
        self.assertEqual(self.store.model.head(self.source["document_id"]).revision, 0)

    def test_actual_renderer_limit_failure_keeps_head_and_worker_recovers(self):
        candidate = self.candidate()
        reply = self.visual.render({"request_key": "renderer-limit", "candidate_id": candidate, "commit": True,
                                    "profile": {"formats": ["png"], "max_height_px": 500}})
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["error"]["code"], "RENDER_LIMIT")
        self.assertEqual(self.store.model.head(self.source["document_id"]).revision, 0)
        recovered = self.visual.render({"request_key": "after-limit", "candidate_id": candidate, "commit": True, "profile": {"formats": ["png"]}})
        self.assertTrue(recovered["ok"], recovered)

    def test_dead_worker_is_replaced_for_next_uncached_result(self):
        self.assertTrue(self.render()["ok"])
        starts = self.renderer.starts
        self.renderer.process.terminate()
        self.renderer.process.join(5)
        candidate = self.candidate()
        reply = self.visual.render({"request_key": "after-worker-exit", "candidate_id": candidate, "profile": {"formats": ["png"]}})
        self.assertTrue(reply["ok"], reply)
        self.assertEqual(self.renderer.starts, starts + 1)

    def test_artifact_retrieval_and_damage_recovery(self):
        first = self.render()
        self.assertTrue(first["ok"], first)
        meta = first["result"]["artifacts"]["png"]
        chunk = self.visual.artifact({"artifact_id": meta["artifact_id"], "mode": "chunk", "length": 8})
        self.assertEqual(base64.b64decode(chunk["result"]["data_base64"]), b"\x89PNG\r\n\x1a\n")
        self.visual.artifacts.path(meta["relative_path"]).write_bytes(b"damaged managed test artifact")
        unavailable = self.render()
        self.assertFalse(unavailable["ok"])
        self.assertEqual(unavailable["error"]["code"], "ARTIFACT_UNAVAILABLE")
        before = self.renderer.render_count
        repaired = self.render("repair")
        self.assertTrue(repaired["ok"], repaired)
        self.assertFalse(repaired["result"]["cache_hit"])
        self.assertEqual(self.renderer.render_count, before + 1)
        self.assertTrue(list((self.root / "staging").glob("quarantine-*")))

    def test_published_files_without_metadata_cannot_advance_head(self):
        candidate = self.candidate()
        def fault(phase):
            if phase == "after_artifact_files":
                raise RuntimeError("injected publication crash")
        self.store.fault = fault
        reply = self.visual.render({"request_key": "publish-fail", "candidate_id": candidate, "commit": True, "profile": {"formats": ["png"]}})
        self.assertFalse(reply["ok"])
        self.assertEqual(self.store.model.head(self.source["document_id"]).revision, 0)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM artifacts").fetchone()[0], 0)
        self.assertEqual(self.store.connection.execute("SELECT state FROM render_sets").fetchone()[0], "failed")
        self.assertTrue(list((self.root / "artifacts").glob("*.png")))
        self.store.close()
        self.store = Store(self.root)
        self.assertEqual(self.store.connection.execute("SELECT state FROM render_sets").fetchone()[0], "failed")

    def test_failure_before_final_commit_keeps_head_but_cache_is_reusable(self):
        candidate = self.candidate()
        def fault(phase):
            if phase == "before_visual_commit":
                raise RuntimeError("injected final transaction failure")
        self.store.fault = fault
        reply = self.visual.render({"request_key": "commit-fail", "candidate_id": candidate, "commit": True, "profile": {"formats": ["png"]}})
        self.assertFalse(reply["ok"])
        self.assertEqual(self.store.model.head(self.source["document_id"]).revision, 0)
        self.store.fault = lambda _: None
        again = self.visual.render({"request_key": "commit-retry", "candidate_id": candidate, "commit": True, "profile": {"formats": ["png"]}})
        self.assertTrue(again["ok"], again)
        self.assertTrue(again["result"]["cache_hit"])

    def test_restart_cache_and_receipt(self):
        first = self.render()
        before = self.renderer.render_count
        self.store.close()
        self.store = Store(self.root)
        self.visual = VisualService(self.store, self.renderer)
        self.assertEqual(self.render(), first)
        self.assertTrue(self.render("after-restart")["result"]["cache_hit"])
        self.assertEqual(self.renderer.render_count, before)

    def test_pdf_multipage_and_full_text(self):
        content = Snapshot(properties=Properties(title="Multi-page validation", font_family="Arial"), blocks=tuple(
            Block(block_id=f"p{i}", text=f"Paragraph {i}. " + "Readable text with a stable margin and line spacing. " * 8)
            for i in range(35)))
        source = self.service.ingest({"request_key": "long", "snapshot": content.model_dump(mode="json")})["result"]
        result = self.visual.render({"request_key": "long-pdf", "stream_id": source["stream_id"], "profile": {"formats": ["pdf"], "max_height_px": 16000}})
        self.assertTrue(result["ok"], result)
        pdf = result["result"]["artifacts"]["pdf"]
        reader = PdfReader(self.visual.artifacts.path(pdf["relative_path"]))
        self.assertGreater(len(reader.pages), 1)
        self.assertIn("Paragraph 34", "".join(page.extract_text() for page in reader.pages))

    def test_html_is_escaped_and_profile_is_strict(self):
        value = snapshot('<script>window.notAllowed=true</script> & text')
        spec = self.renderer.prepare(value, RenderProfile(formats=("png",)))
        self.assertNotIn("<script>", spec.html)
        self.assertIn("&lt;script&gt;", spec.html)
        with self.assertRaises(ModelError):
            self.visual.render({"request_key": "bad-profile", "stream_id": self.source["stream_id"], "profile": {"show_title": "false"}})


class MigrationTests(unittest.TestCase):
    def test_v1_data_is_preserved_and_backup_is_v1(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder)
            with closing(sqlite3.connect(root / "state.sqlite3")) as con:
                con.executescript(SCHEMA + "PRAGMA user_version=1;")
                value = snapshot("Version-one source content")
                con.execute("INSERT INTO snapshots VALUES(?,?)", (value.digest, value.model_dump_json()))
                con.execute("INSERT INTO documents VALUES(?,?,?,?)", ("document:migration", "stream:migration", 0, None))
                con.execute("INSERT INTO streams VALUES(?,?,?,?,?,?,?)", ("stream:migration", "document:migration", None, None, 0, None, value.digest))
                con.commit()
            with Store(root) as store:
                self.assertEqual(store.connection.execute("PRAGMA user_version").fetchone()[0], 2)
                self.assertEqual(store.connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(store.model.materialize("stream:migration"), value)
            with closing(sqlite3.connect(root / "before-schema-v2.sqlite3")) as backup:
                self.assertEqual(backup.execute("PRAGMA user_version").fetchone()[0], 1)


class RenderNetworkTests(unittest.TestCase):
    def test_real_render_artifact_download_and_lifecycle(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            renderer = Renderer()
            server = RunningServer(Path(folder), renderer=renderer)
            try:
                async def calls():
                    source = await client_call(server.url, server.token, "docstream_ingest", {"request_key": "net-source", "snapshot": snapshot().model_dump(mode="json")})
                    reply = await client_call(server.url, server.token, "docstream_render", {"request_key": "net-render", "stream_id": source["result"]["stream_id"], "profile": {"formats": ["png"]}})
                    self.assertTrue(reply["ok"], reply)
                    meta = reply["result"]["artifacts"]["png"]
                    read = await client_call(server.url, server.token, "docstream_artifact", {"artifact_id": meta["artifact_id"]})
                    self.assertTrue(read["ok"])
                    return meta
                meta = asyncio.run(calls())
                url = server.url.removesuffix("/mcp") + meta["download_path"]
                request = urllib.request.Request(url, headers={"Authorization": "Bearer " + server.token})
                with urllib.request.urlopen(request, timeout=5) as response:
                    self.assertEqual(response.headers.get_content_type(), "image/png")
                    self.assertEqual(response.read(8), b"\x89PNG\r\n\x1a\n")
                with self.assertRaises(urllib.error.HTTPError) as failure:
                    urllib.request.urlopen(url, timeout=5)
                self.assertEqual(failure.exception.code, 401)
                failure.exception.close()
            finally:
                server.close()
            self.assertIsNone(renderer.process)
