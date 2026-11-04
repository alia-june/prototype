"""Bounded confirmation through public application services; no product fixes."""
import argparse
import asyncio
import json
from pathlib import Path

from docstream_cpu.format_service import FormatService
from docstream_cpu.harness.core import RUNS_ROOT, load_case, save
from docstream_cpu.mcp_server import invoke
from docstream_cpu.service import DocumentService
from docstream_cpu.storage import Store


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("run_id")
    args=parser.parse_args()
    root=(RUNS_ROOT/args.run_id).resolve()
    if not root.is_relative_to(RUNS_ROOT.resolve()) or not (root/"summary.json").exists():
        raise ValueError("completed managed run required")
    destination=root/"service-confirmation-verified"
    destination.mkdir(exist_ok=False)
    results=[]
    for label,filename in (("carriage_return","minimized-0013.json"),("nul","minimized-0021.json")):
        value=load_case(root/"fuzzy"/"failures"/filename)
        with Store(destination/("case-"+label)) as store:
            service=DocumentService(store)
            formats=FormatService(store)
            ingested=service.ingest({"request_key":"source","snapshot":value["input"]["snapshot"]})
            source=ingested["result"]
            exported=formats.export_document({"request_key":"export","stream_id":source["stream_id"],"format":"docx"})
            entry={"finding":label,"ingest":ingested,"export":exported,"head_revision":store.model.head(source["document_id"]).revision}
            if exported["ok"]:
                import base64
                raw=formats.artifacts.path(exported["result"]["artifact"]["relative_path"]).read_bytes()
                imported=formats.import_document({"request_key":"roundtrip","format":"docx","data_base64":base64.b64encode(raw).decode()})
                entry["import"]=imported
                entry["input_text"]=store.model.materialize(source["stream_id"]).blocks[0].text
                entry["output_text"]=store.model.materialize(imported["result"]["stream_id"]).blocks[0].text
            results.append(entry)
    value=load_case(root/"fuzzy"/"failures"/"minimized-0014.json")
    with Store(destination/"surrogate") as store:
        service=DocumentService(store)
        try:
            service.ingest(value["input"]["request"])
        except Exception as exc:
            entry={"finding":"surrogate","direct_exception":type(exc).__name__,"message":str(exc)}
        else:
            raise RuntimeError("expected finding no longer reproduces")
        entry["transport_invoke_wrapper"]=asyncio.run(invoke(service.ingest,value["input"]["request"]))
        entry["documents_created"]=len(store.model._heads)
        results.append(entry)
    save(destination/"observations.json",results)
    print(json.dumps({"confirmed_groups":len(results),"observations":str(destination/"observations.json")},ensure_ascii=True))


if __name__=="__main__":
    main()
