"""One-time freeze of the already reviewed M4 output; refuses to overwrite it.

This utility is never called by a validation run. The approved PNG hash is fixed
here, so rerunning cannot silently approve a changed renderer baseline.
"""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3


def main():
    service=Path(__file__).resolve().parents[1]
    folder=service/"tests"/"fixtures"/"harness"
    target=folder/"reviewed-m4.json"
    png_target=folder/"reviewed-m4.png"
    if target.exists() or png_target.exists():
        raise RuntimeError("reviewed baseline already exists; explicit new review is required")
    example=json.loads((service/"docs"/"M4_EXAMPLE.json").read_text())
    root=Path(example["store_root"])
    source=example["import"]["result"]
    preview=example["preview"]["result"]
    expected_png="e200597428a67f4c1e406b55f52b66e82d2e54f6bdaccc64c59a3a9e77888e22"
    png=(root/"artifacts"/preview["artifacts"]["png"]["relative_path"]).read_bytes()
    if sha256(png).hexdigest()!=expected_png or preview["artifacts"]["png"]["sha256"]!=expected_png:
        raise RuntimeError("reviewed M4 PNG does not match its accepted hash")
    con=sqlite3.connect((root/"state.sqlite3").as_uri()+"?mode=ro",uri=True)
    try:
        request=json.loads(con.execute("SELECT payload FROM requests WHERE family='import' AND request_key='m4-source'").fetchone()[0])
        snapshot=json.loads(con.execute("SELECT payload FROM snapshots WHERE digest=?",(source["semantic_sha256"],)).fetchone()[0])
    finally:
        con.close()
    metadata=preview["renderer_metadata"]
    keys=("renderer","playwright","browser_revision","browser_version","executable_sha256","engine_sha256","fonts","profile","semantic_sha256","html_sha256")
    fixture={"schema":"docstream.harness.golden/1","provenance":"M4_EXAMPLE.json; final one-page PNG/PDF visually reviewed in M4a",
        "source_store":str(root),"import_request":request,"snapshot":snapshot,"source_sha256":source["original_sha256"],
        "semantic_sha256":source["semantic_sha256"],"renderer_identity":{key:metadata[key] for key in keys},"png_sha256":expected_png,
        "pdf":{"pages":1,"required_text":["Document format service","Supported content","Import a source document","Retain its original bytes","Tables and images","Unsupported features","import -> inspect -> transform -> render -> export"]}}
    folder.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(fixture,ensure_ascii=True,indent=2)+"\n",encoding="utf-8")
    png_target.write_bytes(png)
    print(json.dumps({"fixture":str(target),"png_sha256":expected_png,"source_opened_read_only":True}))


if __name__=="__main__":
    main()
