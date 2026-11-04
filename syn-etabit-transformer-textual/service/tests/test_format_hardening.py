"""AUTH-15: explicit DOCX loss policy and pre-mutation Unicode rejection."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from uuid import uuid4

from docstream_cpu.docx_adapter import export_docx, import_docx
from docstream_cpu.errors import ModelError
from docstream_cpu.format_service import FormatService, ImportRequest
from docstream_cpu.models import Block, Properties, Snapshot
from docstream_cpu.rich import CellText, ImageRef, RichBlock, Snapshot2, Span, TableCell, TableRow
from docstream_cpu.service import DocumentService, IngestRequest, parse_request
from docstream_cpu.storage import Store
from docstream_cpu.harness.cases import execute_case
from docstream_cpu.harness.core import CheckFailed
from docstream_cpu.harness.generate import case
from docstream_cpu.format_common import Losses

ROOT = Path(__file__).resolve().parents[2] / ".docstream/format-hardening-runs/auth15-20261030"


def snapshot(text="A\rB"):
    return Snapshot2(properties=Properties(font_family="Arial"), blocks=(RichBlock(block_id="text", text=text, runs=(Span(text=text),)),))


def state(store):
    """Every application table plus in-memory semantic graph, excluding SQLite internals."""
    con = store.connection
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    durable = {name: [tuple(row) for row in con.execute('SELECT * FROM "' + name + '" ORDER BY rowid')] for name in tables}
    semantic = {name: dict(value) for name, value in vars(store.model).items() if isinstance(value, dict)}
    return durable, semantic


class FormatHardeningTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / ("case-" + uuid4().hex)
        self.store = Store(self.root)
        self.addCleanup(self.store.close)
        self.service = DocumentService(self.store)
        self.formats = FormatService(self.store)

    def ingest(self, source):
        response = self.service.ingest({"request_key": "initial", "snapshot": source.model_dump(mode="json")})
        self.assertTrue(response["ok"], response)
        return response["result"]

    def export(self, source, policy="reject", key="export"):
        return self.formats.export_document({"request_key": key, "stream_id": source["stream_id"], "format": "docx", "loss_policy": policy})

    def test_default_rejects_carriage_return_loss_without_artifact_or_head_change(self):
        original = snapshot(); info = self.ingest(original)
        before = self.store.model.materialize(info["stream_id"])
        head = self.store.model.head(info["document_id"])
        response = self.export(info)
        self.assertFalse(response["ok"], response)
        self.assertEqual(response["error"]["code"], "CONVERSION_LOSS")
        self.assertEqual({x["code"] for x in response["error"]["diagnostics"]}, {"DOCX_CARRIAGE_RETURN"})
        self.assertEqual(before, self.store.model.materialize(info["stream_id"]))
        self.assertEqual(head, self.store.model.head(info["document_id"]))
        self.assertFalse(list((self.root / "artifacts").rglob("*.docx")))
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM artifacts").fetchone()[0], 0)

    def test_explicit_allow_retains_loss_receipt_and_exact_original_after_restart(self):
        original = snapshot(); info = self.ingest(original)
        request = {"request_key": "allow", "stream_id": info["stream_id"], "format": "docx", "loss_policy": "allow"}
        response = self.formats.export_document(request)
        self.assertTrue(response["ok"], response)
        self.assertEqual({x["code"] for x in response["result"]["diagnostics"]}, {"DOCX_CARRIAGE_RETURN"})
        self.assertEqual(self.formats.export_document(request), response)
        self.store.close(); self.store = Store(self.root); self.addCleanup(self.store.close)
        self.assertEqual(FormatService(self.store).export_document(request), response)
        self.assertEqual(self.store.model.materialize(info["stream_id"]), original)
        row = self.store.connection.execute("SELECT response FROM requests WHERE request_key='allow'").fetchone()
        self.assertEqual(json.loads(row[0]), response)

    def test_line_break_mapping_is_explicit_and_does_not_mutate_source(self):
        for text, expected in (("A\rB", "A\nB"), ("A\r\nB", "A\n\nB"), ("A\nB", "A\nB"), ("A\tB", "A\tB")):
            with self.subTest(text=repr(text)):
                source = snapshot(text); digest = source.digest
                raw, losses = export_docx(source, lambda _: None)
                self.assertEqual({x["code"] for x in losses.items}, {"DOCX_CARRIAGE_RETURN"} if "\r" in text else set())
                result, _, imported = import_docx(raw)
                self.assertFalse(imported.items)
                self.assertEqual(result.blocks[0].text, expected)
                self.assertEqual(source.digest, digest)
                self.assertEqual(source.blocks[0].text, text)

    def test_title_table_and_legacy_plain_text_report_conversion_loss(self):
        title = Snapshot2(properties=Properties(title="A\rB", font_family="Arial"))
        cell = TableCell(paragraphs=(CellText(runs=(Span(text="A\rB"),)),))
        table = Snapshot2(properties=Properties(font_family="Arial"), blocks=(RichBlock(block_id="t", kind="table", rows=(TableRow(cells=(cell,)),)),))
        plain = Snapshot(properties=Properties(font_family="Arial"), blocks=(Block(block_id="p", text="A\rB"),))
        for source in (title, table, plain):
            with self.subTest(source=source.schema_version, title=source.properties.title):
                raw, losses = export_docx(source, lambda _: None)
                self.assertEqual({x["code"] for x in losses.items}, {"DOCX_CARRIAGE_RETURN"})
                result, _, imported = import_docx(raw)
                self.assertFalse(imported.items, imported.items)
                if source is title: self.assertEqual(result.properties.title, "A\nB")
                elif source is table: self.assertEqual("".join(r.text for r in result.blocks[0].rows[0].cells[0].paragraphs[0].runs), "A\nB")
                else: self.assertEqual(result.blocks[0].text, "A\nB")

    def test_all_xml_forbidden_scalars_reject_before_document_library(self):
        points = [*range(9), 11, 12, *range(14, 32), 0xFFFE, 0xFFFF]
        for point in points:
            with self.subTest(point=hex(point)), patch("docstream_cpu.docx_adapter.Document") as library:
                with self.assertRaises(ModelError) as caught: export_docx(snapshot(chr(point)), lambda _: None)
                self.assertEqual(caught.exception.code, "UNREPRESENTABLE_DOCX")
                self.assertIn(f"U+{point:04X}", str(caught.exception))
                library.assert_not_called()

    def test_xml_repertoire_boundaries_and_controls_are_accepted(self):
        text = "\t\n \u007f\u0085\ud7ff\ue000\ufffd\U00010000\U0010ffff"
        raw, losses = export_docx(snapshot(text), lambda _: None)
        result, _, imported = import_docx(raw)
        self.assertFalse(losses.items); self.assertFalse(imported.items)
        self.assertEqual(result.blocks[0].text, text)

    def test_unrepresentable_export_is_typed_under_both_policies_and_retains_head(self):
        original = snapshot("A\x00B"); info = self.ingest(original)
        head = self.store.model.head(info["document_id"])
        for policy in ("reject", "allow"):
            response = self.export(info, policy, "nul-" + policy)
            self.assertFalse(response["ok"], response)
            self.assertEqual(response["error"]["code"], "UNREPRESENTABLE_DOCX")
            self.assertFalse(response["error"]["retryable"])
            self.assertFalse(response["error"]["committed"])
            self.assertEqual(self.export(info, policy, "nul-" + policy), response)
        self.assertEqual(self.store.model.materialize(info["stream_id"]), original)
        self.assertEqual(self.store.model.head(info["document_id"]), head)

    def test_preflight_covers_metadata_links_images_and_nested_cells(self):
        base = snapshot("good").model_dump(mode="json")
        variants = []
        for key in ("title", "font_family"):
            value = deepcopy(base); value["properties"][key] = "bad\x00"; variants.append(value)
        value = deepcopy(base); value["blocks"][0]["runs"][0]["style"]["font_family"] = "bad\x00"; variants.append(value)
        value = deepcopy(base); value["blocks"][0]["runs"][0]["href"] = "https://example.com/\ufffe"; variants.append(value)
        cell = TableCell(paragraphs=(CellText(runs=(Span(text="bad\x00"),)),))
        variants.append(Snapshot2(blocks=(RichBlock(block_id="t", kind="table", rows=(TableRow(cells=(cell,)),)),)).model_dump(mode="json"))
        image = ImageRef(sha256="0"*64, media_type="image/png", alt="bad\x00", width_mpt=1000, height_mpt=1000)
        variants.append(Snapshot2(blocks=(RichBlock(block_id="i", kind="image", image=image),)).model_dump(mode="json"))
        for value in variants:
            with self.subTest(value=value), patch("docstream_cpu.docx_adapter.Document") as library:
                with self.assertRaises(ModelError) as caught: export_docx(Snapshot2.model_validate_json(json.dumps(value)), lambda _: None)
                self.assertEqual(caught.exception.code, "UNREPRESENTABLE_DOCX"); library.assert_not_called()

    def test_dictionary_surrogates_reject_before_serialization_and_all_store_state(self):
        self.ingest(snapshot("retained")); before = state(self.store)
        variants = [{"request_key": "bad", "text": "\ud800"}, {"request_key": "bad", "text": "ok", "title": "\udfff"},
                    {"request_key": "bad", "snapshot": {"blocks": [{"block_id": "a", "text": "\ud800"}]}},
                    {"request_key": "bad", "text": "ok", "extra": {"\udfff": "bad key"}}]
        for payload in variants:
            with self.subTest(payload=repr(payload)), patch("docstream_cpu.service.dumps") as serializer:
                with self.assertRaises(ModelError) as caught: self.service.ingest(payload)
                self.assertEqual(caught.exception.code, "VALIDATION_ERROR"); serializer.assert_not_called()
                self.assertEqual(state(self.store), before)

    def test_format_request_nested_surrogate_rejects_before_serialization(self):
        payload = {"request_key": "bad", "format": "markdown", "data_base64": "QQ==", "assets": {"a": "\ud800"}}
        with patch("docstream_cpu.service.dumps") as serializer:
            with self.assertRaises(ModelError) as caught: parse_request(ImportRequest, payload)
            self.assertEqual(caught.exception.code, "VALIDATION_ERROR"); serializer.assert_not_called()

    def test_typed_format_request_mapping_surrogate_is_rejected_at_entry(self):
        payload = ImportRequest(request_key="bad", format="markdown", data_base64="QQ==", assets={"a": "\ud800"})
        before = state(self.store)
        with patch("docstream_cpu.service.dumps") as serializer:
            with self.assertRaises(ModelError) as caught: self.formats.import_document(payload)
            self.assertEqual(caught.exception.code, "VALIDATION_ERROR"); serializer.assert_not_called()
        self.assertEqual(state(self.store), before)

    def test_partial_constructed_request_keeps_typed_missing_field_rejection(self):
        payload = IngestRequest.model_construct(text="valid text")
        before = state(self.store)
        with self.assertRaises(ModelError) as caught: self.service.ingest(payload)
        self.assertEqual(caught.exception.code, "VALIDATION_ERROR")
        self.assertEqual(state(self.store), before)

    def test_valid_unicode_remains_exact_including_supplementary_and_combining_text(self):
        text = "A\r\nB e\u0301 café 🙂 \U0010ffff"
        response = self.service.ingest({"request_key": "valid", "text": text})
        self.assertTrue(response["ok"], response)
        result = response["result"]
        material = self.store.model.materialize(result["stream_id"])
        self.assertEqual(material.blocks[0].text, text)
        self.assertEqual(self.store.model.source(result["document_id"]).original_sha256, sha256(text.encode()).hexdigest())

    def test_harness_requires_the_specific_declared_error(self):
        value = case("docx_roundtrip", {"snapshot": snapshot("\x00").model_dump(mode="json"), "allowed_losses": [], "expected_error": "UNREPRESENTABLE_DOCX"}, 20261029)
        self.assertEqual(execute_case(value, self.root)["expected_rejection"], "UNREPRESENTABLE_DOCX")
        for error in (ModelError("OTHER", "wrong code"), ValueError("unclassified")):
            with self.subTest(error=type(error).__name__), patch("docstream_cpu.harness.cases.export_docx", side_effect=error):
                with self.assertRaises(CheckFailed): execute_case(value, self.root)

    def test_harness_checks_all_remaining_text_even_when_cr_loss_is_allowed(self):
        value = case("docx_roundtrip", {"snapshot": snapshot().model_dump(mode="json"), "allowed_losses": ["DOCX_CARRIAGE_RETURN"]}, 20261029)
        result = execute_case(value, self.root)
        self.assertEqual(result["expected_losses"], ["DOCX_CARRIAGE_RETURN"])
        self.assertFalse(result["meaning_preserved"])
        wrong, _ = export_docx(snapshot("A\nWRONG"), lambda _: None)
        losses = Losses(); losses.add("DOCX_CARRIAGE_RETURN", "synthetic", "deliberate wrong export")
        with patch("docstream_cpu.harness.cases.export_docx", return_value=(wrong, losses)):
            with self.assertRaises(CheckFailed): execute_case(value, self.root)
        with patch("docstream_cpu.harness.cases.export_docx", return_value=(wrong, Losses())):
            with self.assertRaises(CheckFailed): execute_case(value, self.root)


if __name__ == "__main__": unittest.main()
