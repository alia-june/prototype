"""Maintained rendering demonstration; no caller-generated rendering code."""
from __future__ import annotations

import json
from pathlib import Path

from docstream_cpu.models import Block, Properties, Snapshot, Style
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store
from docstream_cpu.visual_service import VisualService


def specimen():
    return Snapshot(properties=Properties(title="Docstream Agent Service", font_family="Arial"), blocks=(
        Block(block_id="intro", text="CPU model, durable transformations, and reusable visual output. This document is constructed by the installed service implementation."),
        Block(block_id="heading", kind="heading", heading_level=2, text="Preserved streams"),
        Block(block_id="paragraph", text="Each requested transformation has an addressable logical result. The execution plan removes unnecessary assignments while preserving the original requests, input relationships, and inspection history. A new stream can share its semantic payload and rendering with an earlier stream."),
        Block(block_id="bold", text="The final result can be inspected before commitment.", style=Style(bold=True)),
        Block(block_id="italic", text="An unavailable font produces an explicit error, rather than a silent substitution.", style=Style(italic=True)),
        Block(block_id="item1", kind="list_item", list_kind="bullet", text="Catalog the requested transformations."),
        Block(block_id="item2", kind="list_item", list_kind="bullet", text="Reduce work, construct the result, then publish verified artifacts."),
        Block(block_id="code", kind="code", text="requested fonts: Times New Roman -> Arial -> Consolas -> Arial\nretained font writes: 0\nnew logical outputs: 4"),
        Block(block_id="closing", text="The service retains this example as local validation evidence. It represents the service's document layout; it is not a claim about Word pagination."),
    ))


def main():
    root = Path(__file__).resolve().parents[2] / ".docstream" / "visual-example"
    with Store(root) as store:
        service, visual = DocumentService(store), VisualService(store)
        try:
            source = service.ingest({"request_key": "visual-source-v1", "snapshot": specimen().model_dump(mode="json")})
            if not source["ok"]:
                raise RuntimeError(source)
            source = source["result"]
            preview = visual.render({"request_key": "visual-reference-v2", "stream_id": source["stream_id"]})
            if not preview["ok"]:
                raise RuntimeError(preview)
            staged = service.transform({"request_key": "visual-font-sequence-v1", "base_stream_id": source["stream_id"], "mode": "plan",
                "batch": {"base_sha256": source["semantic_sha256"], "operations": [
                    {"operation_id": f"font{i}", "kind": "set_font", "font_family": name}
                    for i, name in enumerate(("Times New Roman", "Arial", "Consolas", "Arial"))]}})
            if not staged["ok"]:
                raise RuntimeError(staged)
            committed = visual.render({"request_key": "visual-commit-v1", "candidate_id": staged["result"]["candidate_id"], "commit": True})
            if not committed["ok"]:
                raise RuntimeError(committed)
            report = {"preview": preview, "transformation": staged, "rendered_commit": committed,
                "artifact_files": {name: str(visual.artifacts.path(meta["relative_path"])) for name, meta in committed["result"]["artifacts"].items()}}
            destination = Path(__file__).resolve().parents[1] / "docs" / "M3_EXAMPLE.json"
            destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"property_writes": staged["result"]["property_writes"], "logical_outputs": len(staged["result"]["output_stream_ids"]),
                "cache_hit": committed["result"]["cache_hit"], "actual_renders": visual.renderer.render_count,
                "worker_starts": visual.renderer.starts, "artifact_files": report["artifact_files"]}, indent=2))
        finally:
            visual.close()


if __name__ == "__main__":
    main()
