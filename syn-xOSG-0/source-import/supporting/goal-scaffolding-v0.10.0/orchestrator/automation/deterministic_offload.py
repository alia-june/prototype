#!/usr/bin/env python3
"""Deterministic, minimal-report validation/attestation helpers for xOSG.

The program may stream file bytes for hashing/validation but reports only minimized
metadata, digests, invariant outcomes, and bounded errors by default.
"""
from __future__ import annotations
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_FILES = {"operator/SHA256SUMS.txt", "docs/INVENTORY.md", "orchestrator/validation/MINIMIZED_EVIDENCE.json", "orchestrator/validation/FILE_HASHES.json", "orchestrator/validation/ATTESTATION.md"}

def relfiles():
    out=[]
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel=p.relative_to(ROOT).as_posix()
        if any(part in EXCLUDE_DIRS for part in p.parts) or rel in EXCLUDE_FILES:
            continue
        out.append((rel,p))
    return sorted(out)

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def inventory():
    return [{"path":rel,"bytes":p.stat().st_size} for rel,p in relfiles()]

def hashes():
    return [{"path":rel,"bytes":p.stat().st_size,"sha256":sha256_file(p)} for rel,p in relfiles()]

def merkle(records):
    leaves=[]
    for r in records:
        payload=f'{r["path"]}\0{r["bytes"]}\0{r["sha256"]}'.encode()
        leaves.append(hashlib.sha256(payload).digest())
    if not leaves:
        return hashlib.sha256(b"").hexdigest()
    while len(leaves)>1:
        if len(leaves)%2: leaves.append(leaves[-1])
        leaves=[hashlib.sha256(leaves[i]+leaves[i+1]).digest() for i in range(0,len(leaves),2)]
    return leaves[0].hex()

def required_structure():
    required=[
      "orchestrator/hypervisor/GESTALT_HYPERVISOR.md",
      "orchestrator/hypervisor/DATA_TOUCH_POLICY.md",
      "orchestrator/hypervisor/META_ORCHESTRATION_SYSTEM.md",
      "orchestrator/hypervisor/TOOL_POLICY.json",
      "orchestrator/hypervisor/SELF_TASK_CATALOG.md",
      "orchestrator/hypervisor/ATTESTATION_PIPELINE.md",
      "orchestrator/state/TASK_GRAPH.json",
      "operator/security/SUB_ZERO_STACK.md",
      "operator/security/ZERO_SENTINEL_STACK.md",
      "operator/gates/PRODUCTION_GATE.md"
    ]
    missing=[x for x in required if not (ROOT/x).is_file()]
    return {"pass":not missing,"required":len(required),"missing":missing}

def validate_json(rel):
    try:
        with (ROOT/rel).open("r",encoding="utf-8") as f: json.load(f)
        return {"path":rel,"pass":True}
    except Exception as e:
        return {"path":rel,"pass":False,"error_type":type(e).__name__}

def run_regressions():
    results=[]
    paths=list((ROOT/"operator/validation").glob("test_*.py"))+list((ROOT/"orchestrator/validation").glob("test_*.py"))
    for p in sorted(paths):
        cp=subprocess.run([sys.executable,str(p)],cwd=ROOT,text=True,capture_output=True,timeout=30)
        lines=cp.stdout.strip().splitlines()
        joined="\n".join(lines)
        def metric(name):
            m=re.search(rf"^{name}\s*=\s*(\d+)$",joined,re.M) or re.search(rf"^{name}=(\d+)\b",joined,re.M)
            return int(m.group(1)) if m else None
        summary=" | ".join(lines[-3:])[:500]
        results.append({"test":p.relative_to(ROOT).as_posix(),"pass":cp.returncode==0,"returncode":cp.returncode,"checks":metric("checks"),"passed":metric("pass"),"failed":metric("fail"),"summary":summary})
    return results

def gate_probe():
    p=ROOT/"operator/gates/PRODUCTION_GATE.md"
    needles=[b"GATE_STATE             = LOCKED_POST_RELEASE", b"CURRENT_RELEASE_ACTIVE = TRUE"]
    data=p.read_bytes()
    return {"pass":all(n in data for n in needles),"checks":len(needles)}

def build_evidence():
    hs=hashes()
    regs=run_regressions()
    obj={
      "schema":"xosg.minimized-evidence.v1",
      "data_touch":{"model_default":"DT0-DT3","semantic_full_content":False},
      "inventory":{"files":len(hs),"bytes":sum(r["bytes"] for r in hs)},
      "tree_merkle_sha256":merkle(hs),
      "structure":required_structure(),
      "json_validation":[validate_json("orchestrator/hypervisor/TOOL_POLICY.json"),validate_json("orchestrator/state/TASK_GRAPH.json")],
      "regressions":regs,
      "gate":gate_probe(),
    }
    obj["pass"]=(obj["structure"]["pass"] and all(x["pass"] for x in obj["json_validation"]) and all(x["pass"] for x in regs) and obj["gate"]["pass"])
    return obj,hs

def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else "evidence"
    if cmd=="inventory": out=inventory()
    elif cmd=="hashes": out=hashes()
    elif cmd=="evidence": out,_=build_evidence()
    elif cmd=="seal":
        out,hs=build_evidence()
        (ROOT/"orchestrator/validation/MINIMIZED_EVIDENCE.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
        (ROOT/"orchestrator/validation/FILE_HASHES.json").write_text(json.dumps(hs,indent=2)+"\n",encoding="utf-8")
    else: raise SystemExit("unknown command")
    if cmd!="seal": print(json.dumps(out,indent=2))
    if isinstance(out,dict) and out.get("pass") is False: raise SystemExit(1)

if __name__=="__main__": main()
