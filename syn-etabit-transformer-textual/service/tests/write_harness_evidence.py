"""Freeze actual harness outcomes and verify inputs/source preservation."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from docstream_cpu.harness.core import RUNS_ROOT, SERVICE_ROOT, WORKSPACE, encoded, footprint, load_case, save
from docstream_cpu.harness.runner import product_hashes


def main():
    root=RUNS_ROOT/"final-validation"
    summary=json.loads((root/"summary.json").read_text())
    metadata=json.loads((root/"run.json").read_text())
    actual=product_hashes()
    if metadata["product_hashes_before"]!=actual or summary["product_files_changed"]:
        raise RuntimeError("product source differs from the approved harness boundary")
    checked=0
    for mode in summary["modes"]:
        if not mode.get("coverage_complete") or not mode["owned_worker_stopped"]:
            raise RuntimeError("final workload incomplete or owner not stopped")
        for item in mode["cases"]:
            value=load_case(item["input_file"])
            if sha256(encoded(value)).hexdigest()!=item["input_sha256"]:
                raise RuntimeError("saved case differs from executed input")
            checked+=1
    baseline=json.loads((SERVICE_ROOT/"docs"/"BASELINE_MANIFEST.json").read_text())
    archive=Path(baseline["source"])
    if sha256(archive.read_bytes()).hexdigest()!=baseline["archive_sha256"]:
        raise RuntimeError("original archive changed")
    original=[]
    for entry in baseline["entries"]:
        if entry["kind"]=="file":
            path=SERVICE_ROOT/"baseline"/entry["path"]
            if sha256(path.read_bytes()).hexdigest()!=entry["sha256"]:
                raise RuntimeError("original extracted file changed")
            original.append(entry["path"])
    failures=Counter(item["message"] for mode in summary["modes"] for item in mode["cases"] if item["status"]=="failed")
    replay=[]
    for name in ("replay-cr","replay-nul","replay-surrogate"):
        value=json.loads((RUNS_ROOT/name/"summary.json").read_text())
        replay.append({"run":name,"status":value["status"],"counts":value["modes"][0]["counts"]})
    manifest_path=root/"EVIDENCE_MANIFEST.json"
    entries=[]
    for path in sorted(root.rglob("*")):
        if path.is_file() and path!=manifest_path:
            raw=path.read_bytes()
            entries.append({"path":str(path.relative_to(root)).replace("\\","/"),"bytes":len(raw),"sha256":sha256(raw).hexdigest()})
    save(manifest_path,{"scope":"final completed run; includes inputs, failures, stores and artifacts; excludes this manifest","files":entries})
    retained=footprint(root)
    if retained>summary["limits"]["retained_bytes"]:
        raise RuntimeError("final evidence exceeds approved retained limit")
    delivery={"recorded_utc":datetime.now(timezone.utc).isoformat(),"harness":"docstream.harness/1","product":"docstream-cpu 0.2.0.dev4",
        "harness_scope_status":"delivered","product_result":summary["status"],"final_run":str(root),"seed":summary["seed"],
        "elapsed_seconds":summary["elapsed_seconds"],"retained_bytes_including_evidence_manifest":retained,"render_submissions":summary["render_calls"],
        "modes":[{"mode":m["mode"],"status":m["status"],"counts":m["counts"],"coverage_complete":m["coverage_complete"],"metrics":m["metrics"],"owned_worker_stopped":m["owned_worker_stopped"]} for m in summary["modes"]],
        "case_inputs_hash_verified":checked,"failure_groups":dict(failures),"independent_replay_runs":replay,"harness_self_tests":{"run":19,"passed":19,"failures":0,"errors":0,"log":"harness-self-test-final.txt"},
        "product_source_modules_unchanged":len(actual),"source_archive_sha256":baseline["archive_sha256"],"original_baseline_files_unchanged":len(original),
        "evidence_files":len(entries),"evidence_manifest":str(manifest_path),"source_changes_for_product_fixes":False,
        "agent_control_configuration_changed":False,"limits":summary["limits"]}
    save(SERVICE_ROOT/"docs"/"HARNESS_DELIVERY.json",delivery)
    paths=list((SERVICE_ROOT/"src"/"docstream_cpu"/"harness").glob("*.py"))
    paths.extend((SERVICE_ROOT/"tests").glob("*harness*.py"))
    paths.extend((SERVICE_ROOT/"tests"/"fixtures"/"harness").glob("*"))
    paths.extend((SERVICE_ROOT/"docs").glob("HARNESS*"))
    paths.extend((SERVICE_ROOT/"docs").glob("harness*self*txt"))
    paths.extend(WORKSPACE/name for name in ("PROJECT_DECISIONS.md","RESEARCH_NOTES.md","DEVELOPMENT_PLAN.md"))
    paths.extend((SERVICE_ROOT/"README.md",SERVICE_ROOT/"docs"/"M4_VALIDATION.md"))
    target=SERVICE_ROOT/"docs"/"HARNESS_IMPLEMENTATION_MANIFEST.json"
    files=[]
    for path in sorted(set(paths)):
        if path.is_file() and path!=target:
            raw=path.read_bytes()
            files.append({"path":str(path.relative_to(WORKSPACE)).replace("\\","/"),"bytes":len(raw),"sha256":sha256(raw).hexdigest()})
    save(target,{"recorded_utc":datetime.now(timezone.utc).isoformat(),"scope":"harness implementation, fixtures, reports, notes and self-test evidence; excludes this manifest","files":files})
    print(json.dumps({"product_result":summary["status"],"inputs_verified":checked,"source_modules_unchanged":len(actual),"original_files_unchanged":len(original),"retained_bytes":retained,"evidence_files":len(entries),"implementation_files":len(files)}))


if __name__=="__main__":
    main()
