#!/usr/bin/env python3
"""xOSG-0 local runtime — standard library only.

This is a stateful workspace simulator, not a hidden multi-agent runtime.
It enforces the artifact's explicit state, register, provenance, and
verification conventions without modifying the host model or privileges.
"""
from __future__ import annotations
import argparse, json, hashlib, os, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "workspace" / "runtime_state.json"
REG = ROOT / "workspace" / "registers.json"

PIPELINE = ["INTAKE","DECOMPOSE","ASSIGN","EXECUTE","RECONCILE","VERIFY","DELIVER","LOG"]
REGISTERS = ["NOTES","TODO","ERROR-LOG","AGENDA","ROADMAP"]

def now():
    return datetime.now(timezone.utc).isoformat()

def load(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    tmp.replace(path)

def init():
    state = {
        "system":"xOSG-0",
        "artifact_revision":"0.2.0",
        "state":"IDLE",
        "task":None,
        "verification":{"status":"NOT_RUN","checks":[]},
        "last_transition":None,
        "history":[]
    }
    regs = {k:[] for k in REGISTERS}
    save(STATE,state); save(REG,regs)
    print("initialized xOSG-0 runtime workspace")

def transition(state, new):
    old=state["state"]
    state["state"]=new
    state["last_transition"]={"from":old,"to":new,"timestamp":now()}
    state["history"].append(state["last_transition"])

def add_reg(name, entry):
    regs=load(REG,{k:[] for k in REGISTERS})
    regs[name].append(entry)
    save(REG,regs)

def task(text):
    state=load(STATE,None)
    if not state:
        init(); state=load(STATE,None)
    transition(state,"INTAKE")
    state["task"]={"objective":text,"requested_at":now(),"status":"REQUESTED"}
    save(STATE,state)
    add_reg("AGENDA",{"objective":text,"next_action":"decompose","open_questions":[],"timestamp":now()})
    add_reg("NOTES",{"type":"context","content":"Task received; no execution is implied by intake.","timestamp":now(),"provenance":{"source":"user_request","actor":"user","claim_type":"fact"}})
    transition(state,"DECOMPOSE")
    save(STATE,state)
    print("task accepted: INTAKE -> DECOMPOSE")
    print("No external action was executed.")

def validate():
    state=load(STATE,None); regs=load(REG,None)
    errors=[]
    if not state: errors.append("runtime_state.json missing")
    if not regs: errors.append("registers.json missing")
    if regs and set(regs)!=set(REGISTERS): errors.append("register set mismatch")
    if state and state.get("verification",{}).get("status")=="PASS" and state.get("state") not in ("VERIFY","DELIVER","LOG"):
        errors.append("verification PASS in incompatible state")
    # machine JSON parse check
    try: json.load(open(ROOT/"machine/xOSG-0_machine_v1.1.0.json",encoding="utf-8"))
    except Exception as e: errors.append(f"machine configuration invalid: {e}")
    print("VALID" if not errors else "INVALID")
    for e in errors: print(" -",e)
    return 0 if not errors else 1

def status():
    state=load(STATE,{"state":"UNINITIALIZED"})
    regs=load(REG,{k:[] for k in REGISTERS})
    print(json.dumps({"runtime":state,"register_counts":{k:len(v) for k,v in regs.items()}},indent=2))

def main():
    p=argparse.ArgumentParser(prog="xosg")
    s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("init")
    s.add_parser("status")
    t=s.add_parser("task"); t.add_argument("text")
    s.add_parser("validate")
    a=p.parse_args()
    if a.cmd=="init": init()
    elif a.cmd=="status": status()
    elif a.cmd=="task": task(a.text)
    elif a.cmd=="validate": raise SystemExit(validate())

if __name__=="__main__":
    main()
