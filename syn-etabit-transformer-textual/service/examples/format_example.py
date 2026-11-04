"""Maintained service example and bounded visual-QA fixture; no caller rendering code."""
from __future__ import annotations

import base64
from io import BytesIO
import json
from pathlib import Path

from PIL import Image

from docstream_cpu.format_service import FormatService
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store
from docstream_cpu.visual_service import VisualService

ROOT=Path(__file__).resolve().parents[2]
MARKDOWN=b"# Document format service\n\nThis example imports a document once and produces reusable exports and previews through the maintained service.\n\n## Supported content\n\nA paragraph preserves **bold text**, *italic text*, `inline code` and [a reference link](https://example.com).\n\n1. Import a source document\n   - Retain its original bytes\n   - Catalog its supported content\n2. Apply an ordered transformation\n3. Obtain exports and a visual preview\n\n| Content | Service behavior |\n| --- | --- |\n| Headings and text | Preserve structure and supported formatting |\n| Tables and images | Retain ordered cells and original image bytes |\n| Unsupported features | Report conversion losses before acceptance |\n\n```\nimport -> inspect -> transform -> render -> export\n```\n\n![Blue image fixture](sample.png)\n"


def main():
    image=BytesIO()
    Image.new("RGB",(360,60),"#28659a").save(image,format="PNG")
    with Store(ROOT/".docstream"/"m4-validation"/"example-0.2.0.dev4") as store:
        formats=FormatService(store)
        imported=formats.import_document({"request_key":"m4-source","format":"markdown","data_base64":base64.b64encode(MARKDOWN).decode(),"assets":{"sample.png":base64.b64encode(image.getvalue()).decode()}})
        if not imported["ok"]:
            raise RuntimeError(imported)
        source=imported["result"]
        exports={name:formats.export_document({"request_key":"m4-export-"+name,"stream_id":source["stream_id"],"format":name}) for name in ("docx","markdown_bundle")}
        if any(not r["ok"] for r in exports.values()):
            raise RuntimeError(exports)
        service=DocumentService(store)
        transformed=service.transform({"request_key":"m4-font-cycle","base_stream_id":source["stream_id"],"mode":"plan","batch":{"base_sha256":source["semantic_sha256"],"operations":[{"kind":"set_font","operation_id":"temporary","font_family":"Consolas"},{"kind":"restore_font","operation_id":"original"}]}})
        if not transformed["ok"]:
            raise RuntimeError(transformed)
        visual=VisualService(store)
        try:
            preview=visual.render({"request_key":"m4-preview","stream_id":source["stream_id"]})
            committed=visual.render({"request_key":"m4-rendered-commit","candidate_id":transformed["result"]["candidate_id"],"commit":True})
            if not preview["ok"] or not committed["ok"]:
                raise RuntimeError((preview,committed))
            result={"import":imported,"exports":exports,"transform":transformed,"preview":preview,"rendered_commit":committed,
                "store_root":str(store.root),"worker_starts":visual.renderer.starts,"actual_renders":visual.renderer.render_count}
            (ROOT/"service"/"docs"/"M4_EXAMPLE.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print(json.dumps({"property_writes":transformed["result"]["property_writes"],"worker_starts":visual.renderer.starts,"actual_renders":visual.renderer.render_count,"exports":{name:str(formats.artifacts.path(r["result"]["artifact"]["relative_path"])) for name,r in exports.items()},"preview":{name:str(formats.artifacts.path(meta["relative_path"])) for name,meta in preview["result"]["artifacts"].items()}},indent=2))
        finally:
            visual.close()


if __name__=="__main__":
    main()
