#!/usr/bin/env python3
"""xOSG-0 hardened local runtime — standard library only."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
STATE = WORKSPACE / "runtime_state.json"
REG = WORKSPACE / "registers.json"
JOURNAL = WORKSPACE / ".transaction.json"
LOCK = WORKSPACE / ".runtime.lock"

REVISION = "0.5.0"
MAX_OBJECTIVE_CHARS = 16384
MAX_JSON_BYTES = 1024 * 1024
MAX_HISTORY = 512
LOCK_TIMEOUT_SECONDS = 0.75
LOCK_STALE_SECONDS = 30.0

PIPELINE = ["INTAKE","DECOMPOSE","ASSIGN","EXECUTE","RECONCILE","VERIFY","DELIVER","LOG"]
REGISTERS = ["NOTES","TODO","ERROR-LOG","AGENDA","ROADMAP"]

ALLOWED_TRANSITIONS = {
    "IDLE":{"INTAKE"},
    "INTAKE":{"DECOMPOSE","BLOCKED"},
    "DECOMPOSE":{"ASSIGN","BLOCKED","INTAKE"},
    "ASSIGN":{"EXECUTE","BLOCKED","INTAKE"},
    "EXECUTE":{"RECONCILE","BLOCKED","INTAKE"},
    "RECONCILE":{"VERIFY","BLOCKED","INTAKE"},
    "VERIFY":{"DELIVER","RECONCILE","BLOCKED","INTAKE"},
    "DELIVER":{"LOG","BLOCKED","INTAKE"},
    "LOG":{"IDLE","INTAKE"},
    "BLOCKED":{"INTAKE","IDLE"},
}

class XOSGError(Exception): pass
class DataCorruptionError(XOSGError): pass
class ValidationError(XOSGError): pass
class LockTimeoutError(XOSGError): pass

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def refuse_symlink(path: Path) -> None:
    if path.exists() and path.is_symlink():
        raise DataCorruptionError(f"refusing symlink path: {path}")

@dataclass
class LoadResult:
    value: Any
    missing: bool = False

def load_json(path: Path, *, default: Any = None, allow_missing: bool = False) -> LoadResult:
    if not path.exists():
        if allow_missing:
            return LoadResult(default, True)
        raise DataCorruptionError(f"missing file: {path}")
    refuse_symlink(path)
    if not path.is_file():
        raise DataCorruptionError(f"not a regular file: {path}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise DataCorruptionError(f"oversize json: {path}")
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise DataCorruptionError(f"utf8 bom not accepted: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise DataCorruptionError(f"invalid utf8: {path}: {e}") from e
    try:
        return LoadResult(json.loads(text))
    except json.JSONDecodeError as e:
        raise DataCorruptionError(f"malformed json: {path}: {e}") from e

def atomic_write_json(path: Path, obj: Any) -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    refuse_symlink(path)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    data = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if len(data.encode("utf-8")) > MAX_JSON_BYTES:
        raise ValidationError(f"serialized json exceeds bound: {path}")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(data); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)
    try:
        dfd = os.open(str(path.parent), os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    except OSError:
        pass

def default_state() -> dict:
    return {"system":"xOSG-0","artifact_revision":REVISION,"state":"IDLE","task":None,
            "verification":{"status":"NOT_RUN","checks":[]},"last_transition":None,"history":[]}

def default_registers() -> dict:
    return {k:[] for k in REGISTERS}

def validate_state(state: Any) -> list[str]:
    e=[]
    if not isinstance(state, dict): return ["runtime root must be object"]
    if state.get("system") != "xOSG-0": e.append("system mismatch")
    if not isinstance(state.get("artifact_revision"), str): e.append("artifact_revision must be string")
    if state.get("state") not in ALLOWED_TRANSITIONS: e.append("invalid state")
    v=state.get("verification")
    if not isinstance(v, dict):
        e.append("verification must be object")
    else:
        if v.get("status") not in ("NOT_RUN","PASS","FAIL"): e.append("invalid verification status")
        if not isinstance(v.get("checks"), list): e.append("verification checks must be list")
        if v.get("status")=="PASS" and state.get("state") not in ("VERIFY","DELIVER","LOG"):
            e.append("verification PASS in incompatible state")
    h=state.get("history")
    if not isinstance(h, list): e.append("history must be list")
    elif len(h) > MAX_HISTORY: e.append("history exceeds bound")
    task=state.get("task")
    if task is not None and not isinstance(task, dict): e.append("task must be object or null")
    return e

def validate_registers(regs: Any) -> list[str]:
    if not isinstance(regs, dict): return ["register root must be object"]
    if set(regs) != set(REGISTERS): return ["register set mismatch"]
    return [f"{k} must be list" for k,v in regs.items() if not isinstance(v,list)]

def transition(state: dict, new: str) -> None:
    old=state["state"]
    if new not in ALLOWED_TRANSITIONS.get(old,set()):
        raise ValidationError(f"illegal transition {old}->{new}")
    rec={"from":old,"to":new,"timestamp":now()}
    state["state"]=new
    state["last_transition"]=rec
    state["history"].append(rec)
    if len(state["history"]) > MAX_HISTORY:
        state["history"]=state["history"][-MAX_HISTORY:]

def journal_body(state: dict, regs: dict) -> dict:
    return {"revision":REVISION,"state":state,"registers":regs,"timestamp":now()}

def commit_pair(state: dict, regs: dict) -> None:
    es=validate_state(state); er=validate_registers(regs)
    if es or er: raise ValidationError("; ".join(es+er))
    body=journal_body(state,regs)
    wrapper={"body":body,"sha256":digest(body)}
    atomic_write_json(JOURNAL, wrapper)
    atomic_write_json(STATE, state)
    atomic_write_json(REG, regs)
    try: JOURNAL.unlink()
    except FileNotFoundError: pass

def recover_if_needed() -> str | None:
    if not JOURNAL.exists(): return None
    refuse_symlink(JOURNAL)
    j=load_json(JOURNAL).value
    if not isinstance(j,dict) or not isinstance(j.get("body"),dict) or not isinstance(j.get("sha256"),str):
        raise DataCorruptionError("invalid transaction journal structure")
    if digest(j["body"]) != j["sha256"]:
        raise DataCorruptionError("transaction journal checksum mismatch")
    body=j["body"]; state=body.get("state"); regs=body.get("registers")
    es=validate_state(state); er=validate_registers(regs)
    if es or er: raise DataCorruptionError("journal payload invalid: " + "; ".join(es+er))
    atomic_write_json(STATE,state); atomic_write_json(REG,regs)
    JOURNAL.unlink()
    return "recovered"

class MutationLock:
    def __enter__(self):
        WORKSPACE.mkdir(parents=True,exist_ok=True)
        deadline=time.monotonic()+LOCK_TIMEOUT_SECONDS
        while True:
            refuse_symlink(LOCK)
            try:
                fd=os.open(LOCK, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
                with os.fdopen(fd,"w",encoding="utf-8") as fh:
                    fh.write(json.dumps({"pid":os.getpid(),"created":time.time()}))
                return self
            except FileExistsError:
                try:
                    age=time.time()-LOCK.stat().st_mtime
                    if age > LOCK_STALE_SECONDS:
                        LOCK.unlink(); continue
                except FileNotFoundError:
                    continue
                if time.monotonic()>=deadline:
                    raise LockTimeoutError("mutation lock timeout")
                time.sleep(0.025)
    def __exit__(self,*_):
        try: LOCK.unlink()
        except FileNotFoundError: pass

def init() -> None:
    with MutationLock():
        commit_pair(default_state(),default_registers())
    print("initialized xOSG-0 runtime workspace")

def current_pair() -> tuple[dict,dict]:
    recover_if_needed()
    s=load_json(STATE,allow_missing=True,default=None)
    r=load_json(REG,allow_missing=True,default=None)
    if s.missing and r.missing: return default_state(), default_registers()
    if s.missing != r.missing: raise DataCorruptionError("partial workspace persistence")
    state,regs=s.value,r.value
    es=validate_state(state); er=validate_registers(regs)
    if es or er: raise DataCorruptionError("; ".join(es+er))
    return state,regs

def task(text: str) -> None:
    if not isinstance(text,str): raise ValidationError("task objective must be string")
    if len(text)>MAX_OBJECTIVE_CHARS: raise ValidationError("task objective exceeds bound")
    with MutationLock():
        state,regs=current_pair()
        if state["state"]!="IDLE":
            if "INTAKE" not in ALLOWED_TRANSITIONS.get(state["state"],set()):
                raise ValidationError(f"cannot accept new task from {state['state']}")
        transition(state,"INTAKE")
        state["task"]={"objective":text,"requested_at":now(),"status":"REQUESTED"}
        state["verification"]={"status":"NOT_RUN","checks":[]}
        regs["AGENDA"].append({"objective":text,"next_action":"decompose","open_questions":[],"timestamp":now()})
        regs["NOTES"].append({"type":"context","content":"Task received; no execution is implied by intake.",
                             "timestamp":now(),"provenance":{"source":"user_request","actor":"user","claim_type":"fact"}})
        transition(state,"DECOMPOSE")
        commit_pair(state,regs)
    print("task accepted: INTAKE -> DECOMPOSE")
    print("No external action was executed.")

def validate_cmd() -> int:
    try:
        rec=recover_if_needed()
        state=load_json(STATE).value; regs=load_json(REG).value
        errors=validate_state(state)+validate_registers(regs)
        print("VALID" if not errors else "INVALID")
        if rec: print(" - transaction recovered")
        for e in errors: print(" -",e)
        return 0 if not errors else 1
    except XOSGError as e:
        print("INVALID"); print(" -",e); return 1

def status() -> int:
    try:
        rec=recover_if_needed()
        state=load_json(STATE,allow_missing=True,default={"state":"UNINITIALIZED"}).value
        regs=load_json(REG,allow_missing=True,default=default_registers()).value
        errs=validate_state(state) if state.get("state")!="UNINITIALIZED" else []
        errs += validate_registers(regs)
        print(json.dumps({"status":"VALID" if not errs else "INVALID","recovery":rec,
                          "runtime":state,"register_counts":{k:len(v) if isinstance(v,list) else None for k,v in regs.items()},
                          "errors":errs},indent=2))
        return 0 if not errs else 1
    except XOSGError as e:
        print(json.dumps({"status":"INVALID","errors":[str(e)]},indent=2)); return 1

def recover_cmd() -> int:
    try:
        print(recover_if_needed() or "no recovery needed"); return 0
    except XOSGError as e:
        print("recovery failed:",e); return 1

def main():
    p=argparse.ArgumentParser(prog="xosg")
    s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("init"); s.add_parser("status"); s.add_parser("validate"); s.add_parser("recover")
    t=s.add_parser("task"); t.add_argument("text")
    a=p.parse_args()
    try:
        if a.cmd=="init": init(); rc=0
        elif a.cmd=="status": rc=status()
        elif a.cmd=="task": task(a.text); rc=0
        elif a.cmd=="validate": rc=validate_cmd()
        elif a.cmd=="recover": rc=recover_cmd()
        else: rc=2
    except XOSGError as e:
        print(f"ERROR: {e}",file=sys.stderr); rc=1
    raise SystemExit(rc)

if __name__=="__main__":
    main()
