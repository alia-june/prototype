"""Case journals, bounded evidence and explicit semantic comparison rules."""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import threading
import time
import traceback

from . import HARNESS_VERSION

SERVICE_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = SERVICE_ROOT.parent
RUNS_ROOT = WORKSPACE / ".docstream" / "harness-runs"
CASE_SCHEMA = "docstream.harness.case/1"


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def save(path, value):
    path = Path(path)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


class CheckFailed(AssertionError):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}


class BudgetExceeded(RuntimeError):
    pass


def require(condition, message, **details):
    if not condition:
        raise CheckFailed(message, details)


def footprint(path):
    total=0
    for p in Path(path).rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total+=p.stat().st_size
        except FileNotFoundError:
            # SQLite removes rollback journals between directory enumeration
            # and stat. A vanished file consumes no retained bytes.
            continue
    return total


class Journal:
    def __init__(self, root, mode, seed, *, seconds=1200, max_bytes=512*1024*1024):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "failures").mkdir(exist_ok=True)
        (self.root / "inputs").mkdir(exist_ok=True)
        self.mode, self.seed = mode, seed
        self.started = time.monotonic()
        self.deadline = self.started + seconds
        self.max_bytes = max_bytes
        self.records = []
        self.features = Counter()
        self.incomplete = []
        self.metrics = {}
        self.lock = threading.RLock()
        self._journal = (self.root / "events.jsonl").open("a", encoding="utf-8", buffering=1)
        self.event("mode_started", {"mode": mode, "seed": seed})

    def event(self, kind, detail):
        with self.lock:
            self._journal.write(encoded({"event":kind, "at_seconds":round(time.monotonic()-self.started,6), **detail}).decode()+"\n")
            self._journal.flush()

    def check_budget(self):
        if time.monotonic() >= self.deadline:
            raise BudgetExceeded("mode wall-clock budget reached")
        if footprint(self.root) >= self.max_bytes:
            raise BudgetExceeded("retained-run byte budget reached")

    def record(self, name, case, function):
        self.check_budget()
        started = time.perf_counter()
        incomplete_before=len(self.incomplete)
        self.event("case_started", {"name":name, "kind":case["kind"]})
        item = {"name":name, "kind":case["kind"], "input_sha256":sha256(encoded(case)).hexdigest()}
        input_path=self.root/"inputs"/f"{len(self.records):04d}-{item['input_sha256'][:12]}.json"
        if input_path.exists():
            raise FileExistsError("case input already exists; create a new run")
        save(input_path,case)
        item["input_file"]=str(input_path)
        try:
            result = function() or {}
            item.update(status="passed", result=result)
        except BudgetExceeded as exc:
            self.incomplete.append(str(exc))
            item.update(status="incomplete", message=str(exc))
        except Exception as exc:
            item.update(status="incomplete" if len(self.incomplete)>incomplete_before else "failed", message=str(exc)[:2000], exception=type(exc).__name__,
                        details=getattr(exc,"details",{}), traceback=traceback.format_exc()[-16000:])
            if sum(r["status"]=="failed" for r in self.records) < 20:
                filename=f"{len(self.records):04d}-{item['input_sha256'][:12]}.json"
                path=self.root/"failures"/filename
                save(path,{"case":case,"failure":item})
                item["replay_file"]=str(path)
        item["elapsed_seconds"]=round(time.perf_counter()-started,6)
        self.records.append(item)
        self.features[case["kind"]]+=1
        self.event("case_finished",item)
        return item

    def finish(self):
        counts=Counter(r["status"] for r in self.records)
        status="failed" if counts["failed"] else "incomplete" if self.incomplete or counts["incomplete"] else "passed"
        result={"schema":HARNESS_VERSION,"mode":self.mode,"seed":self.seed,"status":status,
                "coverage_complete":not self.incomplete and not counts["incomplete"],
                "recorded_utc":datetime.now(timezone.utc).isoformat(),"elapsed_seconds":round(time.monotonic()-self.started,6),
                "counts":dict(counts),"features":dict(self.features),"incomplete_reasons":self.incomplete,
                "metrics":self.metrics,"cases":self.records}
        self.event("mode_finished",{"status":status,"counts":dict(counts)})
        self._journal.close()
        save(self.root/"results.json",result)
        return result


def semantic_meaning(snapshot):
    """Only explicit span fragmentation/inheritance normalization is permitted.

    IDs, source spelling and ZIP metadata are not portable export identity.
    Text codepoints, order, styles, levels, links, cells and images stay exact.
    """
    from ..models import Style
    from ..rich import Span
    default=snapshot.properties
    def spans(values,text="",parent=Style()):
        values=values or (Span(text=text),)
        result=[]
        for value in values:
            style={key:val if val is not None else getattr(parent,key) for key,val in value.style.model_dump().items()}
            for key,base in (("font_family",default.font_family),("font_size_mpt",default.font_size_mpt),("bold",False),("italic",False)):
                if style[key] is None:
                    style[key]=base
            item={"text":value.text,"style":style,"code":value.code,"href":value.href}
            if result and {k:v for k,v in result[-1].items() if k!="text"}=={k:v for k,v in item.items() if k!="text"}:
                result[-1]["text"]+=item["text"]
            elif item["text"]:
                result.append(item)
        return result
    blocks=[]
    for block in snapshot.blocks:
        value={"kind":block.kind,"text":block.text,"heading_level":block.heading_level,"list_kind":block.list_kind,
               "list_depth":getattr(block,"list_depth",0),"list_start":getattr(block,"list_start",1),
               "spans":spans(getattr(block,"runs",()),block.text,block.style)}
        if block.kind=="table":
            value["rows"]=[{"header":row.header,"cells":[[spans(p.runs,parent=block.style) for p in cell.paragraphs] for cell in row.cells]} for row in block.rows]
        if block.kind=="image":
            value["image"]=block.image.model_dump()
        blocks.append(value)
    return {"properties":default.model_dump(),"blocks":blocks}


def load_case(path):
    path=Path(path)
    if path.stat().st_size>2*1024*1024:
        raise ValueError("replay file exceeds 2 MiB")
    value=json.loads(path.read_text(encoding="utf-8"))
    case=value.get("case",value)
    if type(case) is not dict or case.get("schema")!=CASE_SCHEMA or set(case)-{"schema","kind","seed","input"}:
        raise ValueError("invalid replay case schema")
    from .cases import KINDS
    if case.get("kind") not in KINDS or type(case.get("seed")) is not int or type(case.get("input")) is not dict:
        raise ValueError("unknown case kind or invalid replay data")
    return case
