from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen

from docstream.conversion import import_docx, publish_docx
from docstream.core import DocumentError, create_markdown, inspect_markdown, regex_edit
from docstream.service import DocumentService, make_handler
from http.server import ThreadingHTTPServer


SAMPLE = """# Service Test Document

Status: Draft

## Summary

This is **bold**, *italic*, and `code`.

- First item
- Second item

| Field | Value |
| --- | --- |
| State | Draft |
"""


class DocstreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_new_inspect_and_guarded_edit(self) -> None:
        path = self.root / "new.md"
        created = create_markdown(path, "A Clear Title")
        self.assertEqual(created["title"], "A Clear Title")
        path.write_text(SAMPLE, encoding="utf-8")
        dry = regex_edit(
            path,
            r"(?m)^Status:\s+Draft$",
            "Status: Final",
            expected=1,
            dry_run=True,
        )
        self.assertEqual(dry.replacements, 1)
        self.assertIn("Status: Draft", path.read_text(encoding="utf-8"))
        changed = regex_edit(
            path,
            r"(?m)^Status:\s+Draft$",
            "Status: Final",
            expected=1,
            backup=True,
        )
        self.assertTrue(changed.changed)
        self.assertTrue(Path(changed.backup).is_file())
        report = inspect_markdown(path)
        self.assertEqual(report["headings"][0]["text"], "Service Test Document")

    def test_inspect_ignores_headings_inside_code_fences(self) -> None:
        path = self.root / "fences.md"
        path.write_text("# Real Heading\n\n```powershell\n# Code Comment\n```\n", encoding="utf-8")
        report = inspect_markdown(path)
        self.assertEqual([item["text"] for item in report["headings"]], ["Real Heading"])
        self.assertEqual(report["code_blocks"], 1)
        self.assertFalse(report["unclosed_code_fence"])

    def test_match_guard_prevents_write(self) -> None:
        path = self.root / "guard.md"
        path.write_text("one one", encoding="utf-8")
        with self.assertRaises(DocumentError):
            regex_edit(path, "one", "two", expected=1)
        self.assertEqual(path.read_text(encoding="utf-8"), "one one")

    def test_capture_replacement_and_newline(self) -> None:
        path = self.root / "captures.md"
        path.write_text("# Captured Title\n", encoding="utf-8")
        result = regex_edit(
            path,
            r"(?m)^# (.+)$",
            "# \\g<1>\n\nStatus: Draft",
            expected=1,
        )
        self.assertEqual(result.replacements, 1)
        self.assertEqual(path.read_text(encoding="utf-8"), "# Captured Title\n\nStatus: Draft\n")

    def test_native_round_trip(self) -> None:
        markdown = self.root / "sample.md"
        docx = self.root / "sample.docx"
        recovered = self.root / "recovered.md"
        markdown.write_text(SAMPLE, encoding="utf-8")
        publish = publish_docx(markdown, docx, backend="native")
        self.assertEqual(publish.backend, "native")
        self.assertGreater(docx.stat().st_size, 1000)
        importing = import_docx(docx, recovered, backend="native")
        self.assertEqual(importing.backend, "native")
        recovered_text = recovered.read_text(encoding="utf-8")
        self.assertIn("# Service Test Document", recovered_text)
        self.assertIn("Status: Draft", recovered_text)
        self.assertIn("| Field | Value |", recovered_text)

    def test_service_root_containment(self) -> None:
        service = DocumentService(self.root)
        with self.assertRaises(DocumentError):
            service.resolve("..\\escape.md")
        status, result = service.execute("/v1/health", {})
        self.assertEqual(status, 200)
        self.assertTrue(result["ok"])

    def test_http_edit_endpoint(self) -> None:
        path = self.root / "http.md"
        path.write_text("Status: Draft\n", encoding="utf-8")
        service = DocumentService(self.root)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            payload = json.dumps(
                {
                    "path": "http.md",
                    "pattern": "Draft",
                    "replacement": "Final",
                    "expected": 1,
                }
            ).encode("utf-8")
            request = Request(
                f"http://127.0.0.1:{server.server_port}/v1/edit",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
            self.assertTrue(result["ok"])
            self.assertEqual(result["result"]["replacements"], 1)
            self.assertEqual(path.read_text(encoding="utf-8"), "Status: Final\n")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()

