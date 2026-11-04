from __future__ import annotations

import asyncio
import base64
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor
from PIL import Image

from docstream_cpu.assets import AssetStore, validate_image
from docstream_cpu.docx_adapter import export_docx, import_docx
from docstream_cpu.errors import ModelError
from docstream_cpu.executor import reference_execute
from docstream_cpu.format_common import deterministic_zip, read_package, xml
from docstream_cpu.format_service import FormatService
from docstream_cpu.markdown_adapter import import_markdown, export_markdown
from docstream_cpu.models import Block, Properties, Snapshot, Style, digest
from docstream_cpu.operations import parse_batch
from docstream_cpu.planner import plan, execute
from docstream_cpu.rendering import RenderProfile, Renderer
from docstream_cpu.rich import CellText, ImageRef, RichBlock, Snapshot2, Span, TableCell, TableRow, parse_snapshot
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store
from docstream_cpu.visual_service import VisualService
from docstream_cpu.cli import client_call
from test_mcp import RunningServer

ROOT = Path(__file__).resolve().parents[2]/".docstream"/"m4-validation"
ROOT.mkdir(parents=True, exist_ok=True)
MARKDOWN = b"# Document formats\n\nA **bold** and *italic* paragraph with `inline code` and [a link](https://example.com).\n\n3. First item\n   - Nested item\n4. Second item\n\n| Feature | State |\n| --- | --- |\n| Tables | Supported |\n\n```\nservice call\n```\n\n![A small blue sample](sample.png)\n"


def b64(raw):
    return base64.b64encode(raw).decode()


def picture():
    output = BytesIO()
    Image.new("RGB", (160,60), "#28659a").save(output,format="PNG")
    return output.getvalue()


def fixture():
    return import_markdown(MARKDOWN,{"sample.png":picture()})


def document_bytes(change=None):
    doc=Document()
    doc.styles["Normal"].font.name="Arial"
    doc.add_paragraph("A test document")
    if change:
        change(doc)
    output=BytesIO()
    doc.save(output)
    return output.getvalue()


class RichModelTests(unittest.TestCase):
    def test_version_one_bytes_and_digest_remain_exact(self):
        original=Snapshot(blocks=(Block(block_id="a",text="CR\r\nLF e\u0301"),))
        raw=original.model_dump_json()
        loaded=parse_snapshot(raw)
        self.assertEqual(raw,loaded.model_dump_json())
        self.assertEqual(original.digest,loaded.digest)
        self.assertNotIn("runs",loaded.model_dump()["blocks"][0])

    def test_rich_model_rejects_mismatched_text_and_skipped_nesting(self):
        with self.assertRaises(ValueError):
            RichBlock(block_id="a",text="one",runs=(Span(text="two"),))
        with self.assertRaises(ValueError):
            Snapshot2(blocks=(RichBlock(block_id="a",kind="list_item",list_kind="bullet",list_depth=1),))

    def test_table_header_is_explicit(self):
        cell=TableCell(paragraphs=(CellText(runs=(Span(text="data"),)),))
        b=RichBlock(block_id="t",kind="table",rows=(TableRow(cells=(cell,)),))
        self.assertFalse(b.rows[0].header)
        with self.assertRaises(ValueError):
            RichBlock(block_id="t",kind="table",rows=(TableRow(cells=(cell,)),TableRow(cells=(cell,cell))))

    def test_font_reduction_covers_runs_and_cells_and_restore(self):
        s,_,_=fixture()
        blocks=list(s.blocks)
        p=blocks[1]
        runs=list(p.runs)
        runs[0]=Span(**{**runs[0].model_dump(),"style":Style(font_family="Times New Roman")})
        blocks[1]=RichBlock(**{**p.model_dump(),"runs":tuple(runs)})
        s=Snapshot2(properties=s.properties,blocks=tuple(blocks))
        batch=parse_batch({"base_sha256":s.digest,"operations":[
            {"kind":"set_font","operation_id":"one","font_family":"Consolas"},
            {"kind":"restore_font","operation_id":"restore"}]})
        compiled=plan(s,batch)
        self.assertEqual(compiled.to_dict()["property_writes"],0)
        self.assertEqual(execute(s,compiled).snapshot.digest,s.digest)
        self.assertEqual(reference_execute(s,batch).snapshot.digest,s.digest)

    def test_plain_text_cannot_erase_runs(self):
        s,_,_=fixture()
        p=s.blocks[1]
        batch=parse_batch({"base_sha256":s.digest,"operations":[{"kind":"replace_text","operation_id":"bad","target":p.block_id,"text":"lost","expected_text_sha256":sha256(p.text.encode()).hexdigest()}]})
        with self.assertRaisesRegex(ModelError,"replace_block"):
            plan(s,batch)

    def test_guarded_rich_replacement(self):
        s,_,_=fixture()
        p=s.blocks[1]
        updated=RichBlock(block_id=p.block_id,text="Changed",runs=(Span(text="Changed",style=Style(bold=True)),))
        payload={"base_sha256":s.digest,"operations":[{"kind":"replace_block","operation_id":"change","target":p.block_id,"block":updated.model_dump(mode="json"),"expected_block_sha256":digest(p.model_dump(mode="json"))}]}
        result=execute(s,plan(s,parse_batch(payload))).snapshot
        self.assertEqual(result.block(p.block_id),updated)
        payload["operations"][0]["expected_block_sha256"]="0"*64
        with self.assertRaises(ModelError):
            plan(s,parse_batch(payload))

    def test_unsafe_links_are_rejected(self):
        for href in ("javascript:alert(1)","file:///a","https://name:secret@example.com","https://example.com\n"):
            with self.assertRaises(ValueError):
                Span(href=href,text="x")

    def test_structural_edit_cannot_leave_orphaned_list_prefix(self):
        s=Snapshot2(blocks=(RichBlock(block_id="parent",kind="list_item",list_kind="bullet"),RichBlock(block_id="child",kind="list_item",list_kind="bullet",list_depth=1)))
        batch=parse_batch({"base_sha256":s.digest,"operations":[{"kind":"remove_block","operation_id":"remove-parent","target":"parent"},{"kind":"remove_block","operation_id":"remove-child","target":"child"}]})
        with self.assertRaisesRegex(ModelError,"orphaned"):
            plan(s,batch)

    def test_rich_insert_and_reference_agree(self):
        s=Snapshot2(properties=Properties(font_family="Arial"),blocks=(RichBlock(block_id="one",text="First"),))
        inserted=RichBlock(block_id="two",text="Second",runs=(Span(text="Second",style=Style(italic=True)),))
        batch=parse_batch({"base_sha256":s.digest,"operations":[{"kind":"insert_block","operation_id":"insert","block":inserted.model_dump(mode="json"),"after":"one"},{"kind":"set_font","operation_id":"font","font_family":"Consolas"}]})
        self.assertEqual(execute(s,plan(s,batch)).snapshot,reference_execute(s,batch).snapshot)

    def test_generated_rich_assignments_match_reference(self):
        import random
        rng=random.Random(421029)
        s,_,_=fixture()
        for case in range(80):
            operations=[]
            for index in range(rng.randrange(0,20)):
                choice=rng.randrange(3)
                if choice==0:
                    op={"kind":"set_font","font_family":rng.choice(["Arial","Consolas","Times New Roman"])}
                elif choice==1:
                    op={"kind":"restore_font"}
                else:
                    op={"kind":"set_style","targets":[rng.choice(s.blocks).block_id],"property":"bold","value":rng.choice([True,False,None])}
                operations.append({"operation_id":f"op{index}",**op})
            batch=parse_batch({"base_sha256":s.digest,"operations":operations})
            with self.subTest(case=case):
                self.assertEqual(execute(s,plan(s,batch)).snapshot,reference_execute(s,batch).snapshot)


class MarkdownTests(unittest.TestCase):
    def test_supported_parse_and_source_levels(self):
        s,assets,losses=fixture()
        self.assertFalse(losses.items,losses.items)
        self.assertEqual(s.blocks[0].heading_level,1)
        self.assertEqual([b.list_depth for b in s.blocks if b.kind=="list_item"],[0,1,0])
        self.assertEqual([b.list_start for b in s.blocks if b.kind=="list_item"],[3,1,3])
        self.assertTrue(next(b for b in s.blocks if b.kind=="table").rows[0].header)
        self.assertEqual(next(iter(assets.values())),picture())

    def test_markdown_bundle_roundtrip_content(self):
        s,assets,_=fixture()
        raw,losses=export_markdown(s,assets.__getitem__)
        self.assertFalse(losses.items,losses.items)
        package=read_package(raw)
        manifest=json.loads(package["docstream.json"])
        again,images,losses=import_markdown(package["document.md"],package,properties=Properties(**manifest["properties"]),image_metadata=manifest["images"])
        self.assertFalse(losses.items,losses.items)
        self.assertEqual(s.model_dump(),again.model_dump())
        self.assertEqual(images,assets)

    def test_html_quotes_code_metadata_and_missing_images_reported(self):
        _,_,losses=import_markdown(b'> quoted\n\n<script>bad()</script>\n\n```python\nx\n```\n\n![x](https://example.com/a.png)',{})
        self.assertTrue({"BLOCK_QUOTE","BLOCK_HTML_BLOCK","CODE_LANGUAGE","IMAGE_SOURCE"}.issubset({d["code"] for d in losses.items}))

    def test_nonheader_table_does_not_promote_data(self):
        cell=TableCell(paragraphs=(CellText(runs=(Span(text="first data"),)),))
        s=Snapshot2(blocks=(RichBlock(block_id="t",kind="table",rows=(TableRow(cells=(cell,)),)),))
        raw,losses=export_markdown(s,lambda _:None)
        self.assertEqual(losses.items[0]["code"],"TABLE_HEADER_REQUIRED")
        text=read_package(raw)["document.md"].decode()
        self.assertTrue(text.startswith("|  |\n| --- |\n| first data |"),text)

    def test_markdown_escaping_does_not_create_structure(self):
        text="*literal* [brackets] # heading | pipe"
        s=Snapshot2(properties=Properties(font_family="Arial"),blocks=(RichBlock(block_id="b1",text=text,runs=(Span(text=text),)),))
        raw,losses=export_markdown(s,lambda _:None)
        s2,_,_=import_markdown(read_package(raw)["document.md"],{})
        self.assertFalse(losses.items)
        self.assertEqual(s2.blocks[0].text,text)
        self.assertIsNone(s2.blocks[0].runs[0].style.bold)

    def test_markdown_delimiter_edge_loss_is_reported(self):
        s=Snapshot2(blocks=(RichBlock(block_id="a",text=" bold ",runs=(Span(text=" bold ",style=Style(bold=True)),)),))
        _,losses=export_markdown(s,lambda _:None)
        self.assertIn("MARKDOWN_ROUNDTRIP",{d["code"] for d in losses.items})


class DocxTests(unittest.TestCase):
    def test_supported_docx_roundtrip(self):
        s,assets,_=fixture()
        raw,losses=export_docx(s,assets.__getitem__)
        self.assertFalse(losses.items,losses.items)
        again,images,losses=import_docx(raw)
        self.assertFalse(losses.items,losses.items)
        self.assertEqual([b.kind for b in s.blocks],[b.kind for b in again.blocks])
        self.assertEqual([b.text for b in s.blocks],[b.text for b in again.blocks])
        self.assertEqual([b.list_depth for b in s.blocks],[b.list_depth for b in again.blocks])
        self.assertEqual([b.list_start for b in s.blocks],[b.list_start for b in again.blocks])
        self.assertEqual(images,assets)
        self.assertTrue(again.blocks[1].runs[1].style.bold)
        self.assertEqual(again.blocks[-1].image,s.blocks[-1].image)
        self.assertEqual(again.blocks[-3].rows,s.blocks[-3].rows)

    def test_heading_title_separate(self):
        s=Snapshot2(properties=Properties(title="Document purpose",font_family="Arial"),blocks=(RichBlock(block_id="a",kind="heading",heading_level=3,text="Actual level three"),))
        raw,_=export_docx(s,lambda _:None)
        again,_,losses=import_docx(raw)
        self.assertFalse(losses.items,losses.items)
        self.assertEqual(again.properties.title,"Document purpose")
        self.assertEqual(len(again.blocks),1)
        self.assertEqual(again.blocks[0].heading_level,3)

    def test_unsupported_run_color_reports_loss(self):
        raw=document_bytes(lambda doc:setattr(doc.paragraphs[0].runs[0].font.color,"rgb",RGBColor(255,0,0)))
        _,_,losses=import_docx(raw)
        self.assertIn("RUN_FORMAT",{d["code"] for d in losses.items})

    def test_inherited_style_color_is_not_silently_lost(self):
        def change(doc):
            doc.styles["Normal"].font.color.rgb=RGBColor(255,0,0)
        _,_,losses=import_docx(document_bytes(change))
        self.assertIn("STYLE_COLOR",{d["code"] for d in losses.items})

    def test_comments_tracked_changes_and_merged_cells_reported(self):
        def changes(doc):
            doc.add_comment(doc.paragraphs[0].runs[0],"A comment")
            ins=OxmlElement("w:ins")
            doc.paragraphs[0]._p.append(ins)
            table=doc.add_table(rows=1,cols=2)
            table.cell(0,0).merge(table.cell(0,1))
        _,_,losses=import_docx(document_bytes(changes))
        codes={d["code"] for d in losses.items}
        self.assertTrue({"PACKAGE_FEATURE","TRACKED_CHANGE","MERGED_CELL"}.issubset(codes),codes)

    def test_external_image_relationship_is_not_fetched(self):
        def external(doc):
            doc.part.relate_to("https://unreachable.invalid/pic.png","http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",is_external=True)
        _,_,losses=import_docx(document_bytes(external))
        self.assertIn("EXTERNAL_RELATIONSHIP",{d["code"] for d in losses.items})

    def test_font_half_point_rounding_is_reported(self):
        s=Snapshot(properties=Properties(font_family="Arial",font_size_mpt=11234),blocks=(Block(block_id="a",text="Precision"),))
        _,losses=export_docx(s,lambda _:None)
        self.assertIn("FONT_SIZE_PRECISION",{d["code"] for d in losses.items})

    def test_export_heading_and_code_inherit_document_font(self):
        s=Snapshot2(properties=Properties(font_family="Times New Roman"),blocks=(RichBlock(block_id="h",kind="heading",heading_level=1,text="Heading"),RichBlock(block_id="c",kind="code",text="Code\n")))
        raw,losses=export_docx(s,lambda _:None)
        doc=Document(BytesIO(raw))
        self.assertFalse(losses.items)
        self.assertEqual(doc.styles["Heading 1"].font.name,"Times New Roman")
        self.assertEqual(doc.styles["DocstreamCode"].base_style.style_id,"Normal")
        self.assertIsNone(doc.styles["DocstreamCode"].font.name)

    def test_zip_paths_duplicates_entities_and_expansion_rejected(self):
        for name in ("../outside.xml","/absolute.xml","C:/drive.xml"):
            raw=deterministic_zip({name:b"x"})
            with self.assertRaises(ModelError):
                read_package(raw)
        # ZipInfo normalizes backslashes on Windows construction; mutate the
        # stored name afterwards to exercise an actual malicious ZIP entry.
        output=BytesIO()
        with zipfile.ZipFile(output,"w") as archive:
            entry=zipfile.ZipInfo("placeholder")
            entry.filename="word\\bad.xml"
            archive.writestr(entry,b"x")
        with self.assertRaises(ModelError):
            read_package(output.getvalue())
        raw=deterministic_zip({"large":b"x"*(17*1024*1024)})
        with self.assertRaises(ModelError):
            read_package(raw)
        with self.assertRaises(ModelError):
            xml(b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///x">]><a>&x;</a>')
        with self.assertRaises(ModelError):
            xml('<?xml version="1.0" encoding="utf-16"?><!DOCTYPE a><a/>'.encode("utf-16"))
        output=BytesIO()
        with zipfile.ZipFile(output,"w") as archive:
            archive.writestr("word/document.xml",b"a")
            archive.writestr("Word/document.xml",b"b")
        with self.assertRaises(ModelError):
            read_package(output.getvalue())
        with self.assertRaises(ModelError):
            validate_image(b"not a png")


class FormatServiceTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT)
        self.root=Path(self.folder.name)
        self.store=Store(self.root)
        self.formats=FormatService(self.store)

    def tearDown(self):
        self.store.close()
        self.folder.cleanup()

    def ingest(self,key="source",data=MARKDOWN,**extra):
        return self.formats.import_document({"request_key":key,"format":"markdown","data_base64":b64(data),"assets":{"sample.png":b64(picture())},**extra})

    def test_import_retry_source_assets_and_restart(self):
        first=self.ingest()
        self.assertTrue(first["ok"],first)
        self.assertEqual(first,self.ingest())
        result=first["result"]
        self.assertEqual(self.store.model.source(result["document_id"]).original_bytes,MARKDOWN)
        self.store.close()
        self.store=Store(self.root)
        self.formats=FormatService(self.store)
        self.assertEqual(AssetStore(self.store).get(result["assets"][0]),picture())
        self.assertEqual(self.store.model.materialize(result["stream_id"]).digest,result["semantic_sha256"])

    def test_loss_reject_then_explicit_allow(self):
        rejected=self.ingest(data=b"<script>x</script>")
        self.assertFalse(rejected["ok"])
        self.assertEqual(rejected["error"]["code"],"CONVERSION_LOSS")
        self.assertTrue(rejected["error"]["diagnostics"])
        self.assertFalse(self.store.model._heads)
        accepted=self.ingest(key="allowed",data=b"<script>x</script>",loss_policy="allow")
        self.assertTrue(accepted["ok"],accepted)
        self.assertTrue(accepted["result"]["diagnostics"])

    def test_export_retry_bundle_reimport_and_head_unchanged(self):
        source=self.ingest()["result"]
        request={"request_key":"export","stream_id":source["stream_id"],"format":"markdown_bundle"}
        exported=self.formats.export_document(request)
        self.assertTrue(exported["ok"],exported)
        self.assertEqual(exported,self.formats.export_document(request))
        artifact=exported["result"]["artifact"]
        raw=self.formats.artifacts.path(artifact["relative_path"]).read_bytes()
        imported=self.formats.import_document({"request_key":"bundle","format":"markdown_bundle","data_base64":b64(raw)})
        self.assertTrue(imported["ok"],imported)
        self.assertEqual(imported["result"]["semantic_sha256"],source["semantic_sha256"])
        self.assertEqual(self.store.model.head(source["document_id"]).revision,0)

    def test_export_file_failure_is_atomic_and_receipt_durable(self):
        source=self.ingest()["result"]
        def fail(phase):
            if phase=="after_export_files":
                raise RuntimeError("publication interrupted")
        self.store.fault=fail
        request={"request_key":"failure","stream_id":source["stream_id"],"format":"docx"}
        failed=self.formats.export_document(request)
        self.assertFalse(failed["ok"])
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM artifacts").fetchone()[0],0)
        self.assertEqual(failed,self.formats.export_document(request))
        self.store.fault=lambda phase:None
        self.assertTrue(self.formats.export_document({**request,"request_key":"repair"})["ok"])

    def test_missing_export_is_reported_and_new_key_repairs(self):
        source=self.ingest()["result"]
        request={"request_key":"export","stream_id":source["stream_id"],"format":"docx"}
        exported=self.formats.export_document(request)
        self.assertTrue(exported["ok"],exported)
        self.formats.artifacts.path(exported["result"]["artifact"]["relative_path"]).unlink()
        self.assertEqual(self.formats.export_document(request)["error"]["code"],"ARTIFACT_UNAVAILABLE")
        self.assertTrue(self.formats.export_document({**request,"request_key":"repair"})["ok"])

    def test_structure_can_navigate_table_cell_runs(self):
        source=self.ingest()["result"]
        table=next(b for b in self.store.model.materialize(source["stream_id"]).blocks if b.kind=="table")
        reply=DocumentService(self.store).inspect({"target_id":source["stream_id"],"section":"structure","block_id":table.block_id,"path":["rows",1,"cells",0,"paragraphs",0,"runs",0,"text"],"limit":100})
        self.assertTrue(reply["ok"])
        self.assertEqual(reply["result"]["value"],"Tables")

    def test_request_key_conflict_and_size_limits(self):
        self.ingest()
        with self.assertRaises(ModelError):
            self.ingest(data=b"Different")
        reply=self.formats.import_document({"request_key":"size","format":"markdown","data_base64":b64(b"x"*1_048_577)})
        self.assertFalse(reply["ok"])
        with self.assertRaises(ModelError):
            self.formats.import_document({"request_key":"larger","format":"markdown","data_base64":b64(b"x"*1_048_579)})

    def test_version_one_persisted_plan_still_loads(self):
        service=DocumentService(self.store)
        original=service.ingest({"request_key":"old","text":"Old document"})["result"]
        transformed=service.transform({"request_key":"old-plan","base_stream_id":original["stream_id"],"mode":"commit","batch":{"base_sha256":original["semantic_sha256"],"operations":[{"kind":"set_font","operation_id":"f","font_family":"Arial"}]}})
        self.assertTrue(transformed["ok"],transformed)
        before=self.store.connection.execute("SELECT payload FROM snapshots ORDER BY digest").fetchall()
        self.ingest()
        self.store.close()
        self.store=Store(self.root)
        self.formats=FormatService(self.store)
        after={r[0] for r in self.store.connection.execute("SELECT payload FROM snapshots")}
        self.assertTrue({r[0] for r in before}.issubset(after))
        self.assertEqual(self.store.model.head(original["document_id"]).revision,1)

    def test_actual_m3_store_copy_loads_without_payload_or_identity_changes(self):
        import shutil
        source=ROOT.parent/"visual-example"/"state.sqlite3"
        target=self.root/"m3-copy"
        target.mkdir()
        shutil.copyfile(source,target/"state.sqlite3")
        import sqlite3
        con=sqlite3.connect(target/"state.sqlite3")
        before={table:con.execute("SELECT * FROM "+table).fetchall() for table in ("snapshots","streams","batches","documents")}
        con.close()
        with Store(target) as copied:
            for head in copied.model._heads.values():
                copied.model.materialize(head.stream_id)
            after={table:copied.connection.execute("SELECT * FROM "+table).fetchall() for table in before}
            self.assertEqual(before,{key:[tuple(row) for row in rows] for key,rows in after.items()})


class FormatNetworkTests(unittest.TestCase):
    def test_real_mcp_import_export_and_authenticated_download(self):
        import urllib.request
        import urllib.error
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            server=RunningServer(Path(folder))
            try:
                reply=asyncio.run(client_call(server.url,server.token,"docstream_import",{"request_key":"network","format":"markdown","data_base64":b64(b"## Actual heading\n\n**Bold** body.")}))
                self.assertTrue(reply["ok"],reply)
                exported=asyncio.run(client_call(server.url,server.token,"docstream_export",{"request_key":"network-export","stream_id":reply["result"]["stream_id"],"format":"docx"}))
                self.assertTrue(exported["ok"],exported)
                meta=exported["result"]["artifact"]
                url=f"http://127.0.0.1:{server.port}"+meta["download_path"]
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(url,timeout=5)
                self.assertEqual(caught.exception.code,401)
                caught.exception.close()
                request=urllib.request.Request(url,headers={"Authorization":"Bearer "+server.token})
                with urllib.request.urlopen(request,timeout=5) as response:
                    raw=response.read()
                self.assertEqual(sha256(raw).hexdigest(),meta["sha256"])
                self.assertIn("word/document.xml",read_package(raw))
            finally:
                server.close()


class RichRenderingTests(unittest.TestCase):
    def test_rich_code_font_obeys_semantic_inheritance(self):
        s=Snapshot2(properties=Properties(font_family="Arial"),blocks=(RichBlock(block_id="code",kind="code",text="Code\n"),RichBlock(block_id="inline",text="Inline",runs=(Span(text="Inline",code=True),))))
        batch=parse_batch({"base_sha256":s.digest,"operations":[{"kind":"set_font","operation_id":"font","font_family":"Times New Roman"}]})
        changed=execute(s,plan(s,batch)).snapshot
        renderer=Renderer()
        try:
            spec=renderer.prepare(changed,RenderProfile())
            self.assertEqual(set(spec.metadata["fonts"]),{"Times New Roman"})
            self.assertIn("font-family:DSFont0",spec.html)
        finally:
            renderer.close()

    def test_actual_browser_rich_content_and_cached_reuse(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder, Store(Path(folder)) as store:
            formats=FormatService(store)
            imported=formats.import_document({"request_key":"source","format":"markdown","data_base64":b64(MARKDOWN),"assets":{"sample.png":b64(picture())}})
            self.assertTrue(imported["ok"],imported)
            renderer=Renderer()
            visual=VisualService(store,renderer)
            try:
                request={"request_key":"render","stream_id":imported["result"]["stream_id"]}
                preview=visual.render(request)
                self.assertTrue(preview["ok"],preview)
                self.assertEqual(set(preview["result"]["artifacts"]),{"png","pdf"})
                cached=visual.render({**request,"request_key":"cached"})
                self.assertTrue(cached["result"]["cache_hit"])
                self.assertEqual(renderer.render_count,1)
                spec=renderer.prepare(store.model.materialize(imported["result"]["stream_id"]),RenderProfile(),AssetStore(store).get)
                self.assertIn("<table>",spec.html)
                self.assertIn("data:image/png;base64",spec.html)
                self.assertIn('<ol start="3">',spec.html)
            finally:
                visual.close()


if __name__=="__main__":
    unittest.main()
