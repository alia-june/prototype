"""Packaged CPU example; writes only its declared local evidence file."""
from pathlib import Path
import json

from docstream_cpu import Block, CpuModel, Properties, Snapshot, execute, parse_batch, reference_execute


def main():
    original = Snapshot(properties=Properties(font_family="A"), blocks=(Block(block_id="body", text="Preserved text"),))
    model = CpuModel()
    head = model.ingest(original)
    request = parse_batch({"base_sha256": original.digest, "operations": [
        {"operation_id": f"font{i}", "kind": "set_font", "font_family": value}
        for i, value in enumerate(("B", "A", "C", "A"))
    ]})
    candidate = model.stage(head.stream_id, request)
    reduced = execute(original, candidate.compiled)
    reference = reference_execute(original, request)
    committed = model.commit_semantic(candidate.candidate_id)
    result = {
        "requested_fonts": ["B", "A", "C", "A"],
        "original_font": "A", "result_font": reduced.snapshot.properties.font_family,
        "requested_operations": 4, "logical_outputs": len(candidate.output_stream_ids),
        "reference_property_writes": reference.property_writes,
        "reduced_property_writes": reduced.property_writes,
        "same_semantic_digest": original.digest == reduced.snapshot.digest,
        "distinct_result_stream": committed.stream_id != head.stream_id,
        "stored_payload_count": model.payload_count,
        "visual_state": "not_rendered", "durability": "memory_only",
        "plan": candidate.compiled.to_dict(),
    }
    destination = Path(__file__).resolve().parents[1] / "docs" / "font-example.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "plan"}, indent=2))


if __name__ == "__main__":
    main()
