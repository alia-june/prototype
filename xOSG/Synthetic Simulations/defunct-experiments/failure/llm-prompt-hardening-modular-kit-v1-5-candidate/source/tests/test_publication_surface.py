"""Publication-surface checks for the sanitized candidate."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class PublicationSurfaceTests(unittest.TestCase):
    def test_excluded_payload_types_are_absent(self) -> None:
        forbidden_directories = {"parent", "sources", "vendor", "__pycache__"}
        forbidden_suffixes = {".zip", ".docx", ".pyc", ".log"}
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            self.assertFalse(forbidden_directories.intersection(relative.parts), relative)
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, relative)

    def test_source_receipts_are_structured(self) -> None:
        receipts = json.loads((ROOT / "SOURCE_RECEIPTS.json").read_text(encoding="utf-8"))
        self.assertEqual(1, receipts["schema_version"])
        self.assertTrue(SHA256.fullmatch(receipts["source_archive"]["sha256"]))
        self.assertEqual(16, len(receipts["omitted_payloads"]))
        paths = set()
        for record in receipts["omitted_payloads"]:
            self.assertNotIn(record["path"], paths)
            paths.add(record["path"])
            self.assertTrue(SHA256.fullmatch(record["sha256"]), record["path"])
            self.assertTrue(record["reason"].strip(), record["path"])


if __name__ == "__main__":
    unittest.main()
