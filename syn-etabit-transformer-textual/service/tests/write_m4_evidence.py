"""Retain schemas, dependency pins and bounded implementation/source evidence."""
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path

from docstream_cpu.format_service import ImportRequest, ExportRequest
from docstream_cpu.models import Snapshot
from docstream_cpu.operations import Batch
from docstream_cpu.rich import Snapshot2
from docstream_cpu.service import IngestRequest, TransformRequest, CommitRequest, InspectRequest
from docstream_cpu.visual_service import RenderRequest, ArtifactRequest


def main():
    service=Path(__file__).resolve().parents[1]
    workspace=service.parent
    docs=service/"docs"
    def write(name,value):
        (docs/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    requests=(IngestRequest,TransformRequest,CommitRequest,InspectRequest,RenderRequest,ArtifactRequest,ImportRequest,ExportRequest)
    write("MCP_SCHEMAS.json",{kind.__name__:kind.model_json_schema() for kind in requests})
    write("M4_SNAPSHOT_SCHEMAS.json",{kind.__name__:kind.model_json_schema() for kind in (Snapshot,Snapshot2)})
    write("M4_BATCH_SCHEMA.json",Batch.model_json_schema())
    lock=service/"requirements-service.lock"
    old=lock.read_text(encoding="utf-8")
    previous=service/"requirements-m3.lock"
    if not previous.exists():
        previous.write_text(old,encoding="utf-8")
    names={line.split("==")[0] for line in old.splitlines() if "==" in line}
    names.update(("markdown-it-py","mdurl","python-docx","Pillow","lxml"))
    versions={name:importlib.metadata.version(name) for name in sorted(names,key=str.casefold)}
    content="# M4a Windows Python 3.12 resolved service/build closure; no wheel hashes.\n"+"\n".join(name+"=="+version for name,version in versions.items())+"\n"
    lock.write_text(content,encoding="utf-8")
    (service/"requirements-m4.lock").write_text(content,encoding="utf-8")
    write("M4_DEPENDENCIES.json",versions)
    baseline=json.loads((docs/"BASELINE_MANIFEST.json").read_text())
    archive=Path(baseline["source"])
    actual=sha256(archive.read_bytes()).hexdigest()
    if actual!=baseline["archive_sha256"]:
        raise RuntimeError("original archive differs from intake")
    original_files=[]
    for entry in baseline["entries"]:
        if entry["kind"]=="file":
            path=service/"baseline"/entry["path"]
            value=sha256(path.read_bytes()).hexdigest()
            if value!=entry["sha256"]:
                raise RuntimeError("baseline differs: "+entry["path"])
            original_files.append({"path":entry["path"],"sha256":value,"match":True})
    write("M4_SOURCE_VERIFICATION.json",{"archive":str(archive),"sha256":actual,"match":True,"baseline_files":original_files})
    paths=[]
    for folder in ("src","tests","examples","docs"):
        paths.extend(p for p in (service/folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and not any(part.endswith(".egg-info") for part in p.parts))
    paths.extend(service/name for name in ("README.md","pyproject.toml","requirements-service.lock","requirements-m3.lock","requirements-m4.lock"))
    paths.extend(workspace/name for name in ("DEVELOPMENT_PLAN.md","PROJECT_DECISIONS.md","RESEARCH_NOTES.md"))
    example=json.loads((docs/"M4_EXAMPLE.json").read_text())
    for item in example["exports"].values():
        paths.append(Path(example["store_root"])/"artifacts"/item["result"]["artifact"]["relative_path"])
    for item in example["preview"]["result"]["artifacts"].values():
        paths.append(Path(example["store_root"])/"artifacts"/item["relative_path"])
    manifest_path=docs/"M4_IMPLEMENTATION_MANIFEST.json"
    entries=[]
    for path in sorted(set(paths)):
        if path==manifest_path:
            continue
        raw=path.read_bytes()
        entries.append({"path":str(path.relative_to(workspace)).replace("\\","/"),"bytes":len(raw),"sha256":sha256(raw).hexdigest()})
    write(manifest_path.name,{"recorded_utc":datetime.now(timezone.utc).isoformat(),"scope":"M4a implementation, contracts, retained validation and representative outputs",
        "excludes":["venv","browser binaries","mutable SQLite stores","Python caches","manifest itself"],"files":entries,"file_count":len(entries)})
    print(json.dumps({"schemas":len(requests),"dependency_pins":len(versions),"original_files_verified":len(original_files),"manifest_files":len(entries),"archive_unchanged":True}))


if __name__=="__main__":
    main()
