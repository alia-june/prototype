"""Owned per-mode process. Product instrumentation exists only in this process."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import functools
import json
import logging
import os
from pathlib import Path
import sys
import threading
import time
import unittest

from .cases import REGRESSION_MODULES, execute_case
from .core import BudgetExceeded, CASE_SCHEMA, Journal, RUNS_ROOT, SERVICE_ROOT, encoded, load_case, save
from .generate import case, generate


class Context:
    def __init__(self,journal,render_budget=25,api_budget=2000):
        self.journal=journal
        self.render_budget=render_budget
        self.api_budget=api_budget
        self.render_calls=0
        self.api_calls=0
        self.lock=threading.Lock()

    def spend(self,kind):
        with self.lock:
            key="render_calls" if kind=="render" else "api_calls"
            limit=self.render_budget if kind=="render" else self.api_budget
            if getattr(self,key)>=limit:
                reason=kind+" budget reached"
                self.journal.incomplete.append(reason)
                raise BudgetExceeded(reason)
            setattr(self,key,getattr(self,key)+1)
            if kind=="render":
                self.journal.event("render_submitted",{"render_call":self.render_calls})


@contextmanager
def instrumentation(context,count_api=False):
    from ..rendering import Renderer
    from ..service import DocumentService
    from ..format_service import FormatService
    from ..visual_service import VisualService
    patches=[]
    def patch(cls,name,kind):
        original=getattr(cls,name)
        @functools.wraps(original)
        def counted(*args,**kwargs):
            context.spend(kind)
            return original(*args,**kwargs)
        setattr(cls,name,counted)
        patches.append((cls,name,original))
    patch(Renderer,"render","render")
    if count_api:
        for cls,names in ((DocumentService,("status","ingest","transform","commit","inspect","job")),
                          (FormatService,("import_document","export_document")),
                          (VisualService,("render","artifact","artifact_file"))):
            for name in names:
                patch(cls,name,"api")
    try:
        yield
    finally:
        for cls,name,original in reversed(patches):
            setattr(cls,name,original)


def regression_ids():
    if str(SERVICE_ROOT/"tests") not in sys.path:
        sys.path.insert(0,str(SERVICE_ROOT/"tests"))
    def flatten(suite):
        for item in suite:
            if isinstance(item,unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item.id()
    for name in REGRESSION_MODULES:
        yield from flatten(unittest.defaultTestLoader.loadTestsFromName(name))


def failure_signature(function):
    try:
        function()
    except BudgetExceeded:
        raise
    except Exception as exc:
        return (type(exc).__name__,str(exc).split("\n")[0])
    return None


def minimize(original,oracle,max_attempts=40):
    """Retain the same failure signature. Never changes pass criteria or sources."""
    target=failure_signature(lambda:oracle(original))
    if target is None:
        return original,{"attempts":0,"reproduced":False}
    current=copy.deepcopy(original)
    attempts=0
    def accepts(candidate):
        nonlocal attempts
        if attempts>=max_attempts:
            return False
        attempts+=1
        return failure_signature(lambda:oracle(candidate))==target
    if current["kind"]=="batch":
        size=max(1,len(current["input"]["batch"]["operations"])//2)
        while size and attempts<max_attempts:
            changed=False
            values=current["input"]["batch"]["operations"]
            for start in range(0,len(values),size):
                candidate=copy.deepcopy(current)
                candidate["input"]["batch"]["operations"]=values[:start]+values[start+size:]
                if accepts(candidate):
                    current=candidate
                    changed=True
                    break
            if not changed:
                size//=2
    elif current["kind"] in ("docx_roundtrip","markdown_roundtrip"):
        blocks=current["input"]["snapshot"]["blocks"]
        if len(blocks)==1 and len(blocks[0].get("runs",[]))==1:
            size=max(1,len(blocks[0]["text"])//2)
            while size and attempts<max_attempts:
                changed=False
                text=current["input"]["snapshot"]["blocks"][0]["text"]
                for start in range(0,len(text),size):
                    candidate=copy.deepcopy(current)
                    target_block=candidate["input"]["snapshot"]["blocks"][0]
                    target_block["text"]=text[:start]+text[start+size:]
                    target_block["runs"][0]["text"]=target_block["text"]
                    if accepts(candidate):
                        current=candidate
                        changed=True
                        break
                if not changed:
                    size//=2
    return current,{"attempts":attempts,"reproduced":True,"signature":list(target),"original_bytes":len(encoded(original)),"reduced_bytes":len(encoded(current))}


def run_mode(config):
    logging.disable(logging.CRITICAL)
    root=Path(config["root"]).resolve()
    if not root.is_relative_to(RUNS_ROOT.resolve()):
        raise ValueError("mode root must remain inside managed harness runs")
    journal=Journal(root,config["mode"],config["seed"],seconds=config["seconds"],max_bytes=config["max_bytes"])
    context=Context(journal,config["render_budget"])
    seen=set()
    try:
        with instrumentation(context,count_api=config["mode"]=="torture"):
            if config.get("replay"):
                cases=[("replay",load_case(config["replay"]))]
            elif config["mode"]=="rigid":
                cases=[("regression-"+test_id,case("regression",{"test_id":test_id},config["seed"])) for test_id in regression_ids()]
                cases.extend((name,case(kind,{},config["seed"])) for name,kind in (("fixed-reviewed-golden","golden"),("complete-workflow","workflow")))
            elif config["mode"]=="fuzzy":
                cases=((f"fuzzy-{index:04d}",value) for index,value in enumerate(generate(config["seed"],config["cases"])))
            else:
                cases=[(name,case(name,values,config["seed"])) for name,values in (
                    ("limits",{}),("storage_faults",{}),("crash_recovery",{"cycles":config["crashes"]}),
                    ("network_load",{"requests":config["requests"]}),("render_recovery",{}))]
            for index,(name,value) in enumerate(cases):
                item=journal.record(name,value,lambda value=value,index=index:execute_case(value,root/"stores"/f"case-{index:04d}",context))
                if item["status"]=="incomplete":
                    break
                signature=(item.get("exception"),item.get("message"))
                if config["mode"]=="fuzzy" and item["status"]=="failed" and signature not in seen and len(seen)<5:
                    seen.add(signature)
                    attempt=0
                    def oracle(candidate):
                        nonlocal attempt
                        journal.check_budget()
                        attempt+=1
                        return execute_case(candidate,root/"shrinking"/f"case-{index:04d}-{attempt:02d}",context)
                    reduced,report=minimize(value,oracle)
                    path=root/"failures"/f"minimized-{index:04d}.json"
                    save(path,{"case":reduced,"minimization":report,"original_failure":item.get("replay_file")})
                    item["minimized_replay_file"]=str(path)
                    item["minimization"]=report
                    journal.event("case_minimized",{"name":name,"replay_file":str(path),**report})
    except BudgetExceeded as exc:
        journal.incomplete.append(str(exc))
    except Exception as exc:
        import traceback
        journal.incomplete.append("harness runtime error prevented remaining cases")
        journal.records.append({"name":"harness-runtime","kind":"infrastructure","status":"failed","exception":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()})
    finally:
        journal.metrics.update(render_calls=context.render_calls,service_calls=context.api_calls,
                               render_budget=config["render_budget"],fuzzy_cases_requested=config["cases"] if config["mode"]=="fuzzy" else 0)
        return journal.finish()


def crash_actor(path,phase):
    from ..service import DocumentService
    from ..storage import Store
    path=Path(path).resolve()
    if not path.is_relative_to(RUNS_ROOT.resolve()) or phase not in ("after_reserved","after_flush","before_commit","after_commit"):
        raise ValueError("invalid owned crash actor target")
    def fault(current):
        if current==phase:
            signal=path/"crash-ready.json"
            with signal.open("x",encoding="utf-8") as handle:
                json.dump({"pid":os.getpid(),"phase":phase},handle)
                handle.flush()
                os.fsync(handle.fileno())
            time.sleep(30)
            raise RuntimeError("supervisor did not terminate crash actor")
    with Store(path,fault=fault) as store:
        DocumentService(store).ingest({"request_key":"crash","text":"Crash recovery"})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",type=Path)
    parser.add_argument("--crash-actor",nargs=2)
    args=parser.parse_args()
    if args.crash_actor:
        crash_actor(*args.crash_actor)
        return 0
    result=run_mode(json.loads(args.config.read_text(encoding="utf-8")))
    return {"passed":0,"failed":1,"incomplete":2}[result["status"]]


if __name__=="__main__":
    raise SystemExit(main())
