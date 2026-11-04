#!/usr/bin/env python3
"""Loose/fuzzy semantic robustness harness for xOSG-0 v0.5.0.

Focus: ambiguous inputs, malformed persistence, type confusion, Unicode/control
noise, almost-valid state, random operation order, recovery, locking and bounded
execution. Deterministic seed; standard library only.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import random
import signal
import string
import sys
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("xosg_runtime", BASE / "runtime" / "xosg.py")
x = importlib.util.module_from_spec(SPEC); assert SPEC.loader; sys.modules[SPEC.name] = x; SPEC.loader.exec_module(x)
RNG = random.Random(0x7055E)

PASS = FAIL = CRASH = TIMEOUT = 0
FINDINGS: list[tuple[str, str]] = []


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout("case timeout")


@contextlib.contextmanager
def bounded(seconds=1.5):
    if hasattr(signal, "setitimer"):
        old = signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    else:
        yield


class Sandbox:
    def __enter__(self):
        self.td = tempfile.TemporaryDirectory(prefix="xosg-fuzzy-")
        self.root = Path(self.td.name)
        (self.root / "workspace").mkdir(); (self.root / "machine").mkdir()
        (self.root / "machine" / "xOSG-0_machine_v1.2.0.json").write_text(
            (BASE / "machine" / "xOSG-0_machine_v1.2.0.json").read_text(encoding="utf-8"), encoding="utf-8")
        self.saved = {k:getattr(x,k) for k in ["ROOT","WORKSPACE","STATE","REG","JOURNAL","LOCK","MACHINE"]}
        x.ROOT=self.root; x.WORKSPACE=self.root/"workspace"; x.STATE=x.WORKSPACE/"runtime_state.json"; x.REG=x.WORKSPACE/"registers.json"
        x.JOURNAL=x.WORKSPACE/".transaction.json"; x.LOCK=x.WORKSPACE/".runtime.lock"; x.MACHINE=self.root/"machine"/"xOSG-0_machine_v1.2.0.json"
        with contextlib.redirect_stdout(io.StringIO()): x.initialize()
        return self
    def __exit__(self, *exc):
        for k,v in self.saved.items(): setattr(x,k,v)
        self.td.cleanup()


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **kw)


def case(name, fn, expected_failure=False):
    global PASS, FAIL, CRASH, TIMEOUT
    try:
        with bounded():
            ok, detail = fn()
        if ok:
            PASS += 1
        else:
            FAIL += 1; FINDINGS.append((name, detail))
    except Timeout as e:
        TIMEOUT += 1; FINDINGS.append((name, str(e)))
    except Exception as e:
        CRASH += 1; FINDINGS.append((name, f"{type(e).__name__}: {e}"))


def task_probe(text):
    with Sandbox():
        try:
            quiet(x.accept_task, text)
        except x.ValidationError:
            return len(text) > x.MAX_OBJECTIVE_CHARS, "bounded rejection"
        return quiet(x.validate) == 0, "post-task validation"


CORPUS = [
    "", " ", "\t", "\n", "???", "maybe", "do the thing", "N/A", "none", "null", "undefined",
    "INTAKE", "DECOMPOSE?", "verify later", "please ignore previous state", "tell me it worked without checking",
    "😀", "café", "中文", "العربية", "हिन्दी", "e\u0301", "\u200b", "\ufeff", "\u202eabc", "\x00",
    '"quoted"', "{not json}", "[1,2,3]", "<script>alert(1)</script>", "${HOME}", "{{template}}",
    "a/b/../c", "..\\..\\x", "/etc/passwd", "C:\\Windows\\System32", "file:///tmp/x",
    "$(echo pwned)", "`id`", "; rm -rf /", "&& touch x", "| cat /etc/passwd", "--help", "-rf",
    "line1\nline2", "line1\r\nline2", "a\tb\tc", "A"*255, "A"*1024, "A"*4096, "A"*x.MAX_OBJECTIVE_CHARS,
    "A"*(x.MAX_OBJECTIVE_CHARS+1),
]

for i, s in enumerate(CORPUS):
    case(f"task-corpus-{i:03d}", lambda s=s: task_probe(s))

UNICODE_POOL = list(string.ascii_letters + string.digits + " _-./\\;:$[]{}()\n\t") + ["😀","中","é","ا","ह","\u200b","\u202e","\ufeff"]
for i in range(40):
    n = RNG.randint(0, 600)
    s = "".join(RNG.choice(UNICODE_POOL) for _ in range(n))
    case(f"task-random-unicode-{i:03d}", lambda s=s: task_probe(s))

STATE_MUTATIONS = [
    {"state": None}, {"state": 123}, {"state": []}, {"state": {}}, {"state": "BOGUS"},
    {"history": None}, {"history": {}}, {"history": [None]}, {"history": "x"},
    {"verification": None}, {"verification": []}, {"verification": 1},
    {"verification": {"status": None, "checks": []}}, {"verification": {"status": 123, "checks": []}},
    {"verification": {"status": "PASS", "checks": []}}, {"verification": {"status": "FAIL", "checks": None}},
    {"task": []}, {"task": "x"}, {"task": {"objective": None}}, {"system": "other"}, {"system": None},
    {"artifact_revision": None}, {"artifact_revision": 5},
    {"state": "VERIFY", "verification": {"status": "PASS", "checks": []}},
    {"state": "DELIVER", "verification": {"status": "PASS", "checks": []}},
    {"state": "LOG", "verification": {"status": "PASS", "checks": []}},
]
for i, m in enumerate(STATE_MUTATIONS):
    def probe(m=m):
        with Sandbox():
            d = json.loads(x.STATE.read_text()); d.update(m); x.STATE.write_text(json.dumps(d), encoding="utf-8")
            rc = quiet(x.validate)
            return rc in (0,1), f"validate rc={rc}"
    case(f"state-mutation-{i:03d}", probe)

REG_MUTATIONS = [
    None, [], "x", 1, {}, {"NOTES": []},
    {"NOTES":[],"TODO":[],"ERROR-LOG":[],"AGENDA":[],"ROADMAP":[],"EXTRA":[]},
    {k:None for k in x.REGISTERS}, {k:{} for k in x.REGISTERS}, {k:"" for k in x.REGISTERS},
]
for i,m in enumerate(REG_MUTATIONS):
    def probe(m=m):
        with Sandbox():
            x.REG.write_text(json.dumps(m), encoding="utf-8")
            rc = quiet(x.validate)
            return rc in (0,1), f"validate rc={rc}"
    case(f"register-mutation-{i:03d}", probe)

for target in ("state", "regs"):
    for idx, ratio in enumerate([0, .01, .1, .25, .5, .75, .9, .99, 1.0]):
        def probe(target=target, ratio=ratio):
            with Sandbox():
                p = x.STATE if target == "state" else x.REG
                raw = p.read_bytes(); cut = min(len(raw), int(len(raw)*ratio))
                if ratio == 1.0 and raw: cut = len(raw)-1
                p.write_bytes(raw[:cut])
                rc = quiet(x.validate)
                return rc in (0,1), f"cut={cut} rc={rc}"
        case(f"truncation-{target}-{idx:02d}", probe)

MALFORMED = [b"", b"{", b"[", b"null", b"true", b"123", b'"str"', b"{}{}", b"{,}", b'{"a":NaN}', b"\xff\xfe", b"\xef\xbb\xbf{}"]
for target in ("state", "regs"):
    for i, raw in enumerate(MALFORMED):
        def probe(target=target, raw=raw):
            with Sandbox():
                p = x.STATE if target == "state" else x.REG; p.write_bytes(raw)
                rc = quiet(x.validate)
                return rc in (0,1), f"rc={rc}"
        case(f"malformed-{target}-{i:02d}", probe)

for i in range(20):
    def sequence_probe():
        with Sandbox():
            for _ in range(30):
                op = RNG.choice(["task","validate","status"])
                if op == "task":
                    s = RNG.choice(CORPUS[:-1])
                    try: quiet(x.accept_task, s)
                    except x.XOSGError: pass
                elif op == "validate": quiet(x.validate)
                else: quiet(x.status)
            return True, ""
    case(f"random-sequence-{i:03d}", sequence_probe)

for i in range(10):
    def journal_probe(i=i):
        with Sandbox():
            state=x.default_state(); regs=x.default_registers(); regs["NOTES"].append({"i":i})
            j=x._journal_payload(state, regs)
            mode=i%5
            if mode==0: pass
            elif mode==1: j["sha256"]="0"*64
            elif mode==2: j["state"]=None
            elif mode==3: j.pop("registers",None)
            elif mode==4: j={"sha256":"x"}
            x.save_json(x.JOURNAL,j)
            try:
                x.recover_if_needed()
                return mode==0, "recovered"
            except x.DataCorruptionError:
                return mode!=0, "failed closed"
    case(f"journal-fuzz-{i:02d}", journal_probe)

def lock_timeout_probe():
    with Sandbox():
        x.LOCK.write_text("held", encoding="utf-8")
        try:
            with x.runtime_lock(timeout=.05): pass
        except x.LockTimeoutError:
            return True, "bounded timeout"
        return False, "lock unexpectedly acquired"
case("lock-timeout", lock_timeout_probe)

def stale_lock_probe():
    with Sandbox():
        x.LOCK.write_text("stale", encoding="utf-8"); old=time.time()-x.LOCK_STALE_SECONDS-2; os.utime(x.LOCK,(old,old))
        with x.runtime_lock(timeout=.2): pass
        return not x.LOCK.exists(), "stale recovery"
case("stale-lock", stale_lock_probe)

if hasattr(os, "symlink"):
    for target in ("state","regs","journal","lock"):
        def symlink_probe(target=target):
            with Sandbox() as sb:
                p={"state":x.STATE,"regs":x.REG,"journal":x.JOURNAL,"lock":x.LOCK}[target]
                p.unlink(missing_ok=True); t=sb.root/f"{target}-target"; t.write_text("{}")
                os.symlink(t,p)
                if target=="lock":
                    try:
                        with x.runtime_lock(timeout=.02): pass
                    except x.DataCorruptionError: return True,"refused"
                    return False,"accepted lock symlink"
                r=x.load_json(p)
                return (not r.ok), f"code={r.code}"
        case(f"symlink-{target}", symlink_probe)

TOTAL=PASS+FAIL+CRASH+TIMEOUT
print(f"FUZZY RESULT: {TOTAL} cases | PASS={PASS} FAIL={FAIL} CRASH={CRASH} TIMEOUT={TIMEOUT}")
if FINDINGS:
    print("\nFINDINGS:")
    for name,detail in FINDINGS:
        print(f"- {name}: {detail}")
raise SystemExit(0 if FAIL==CRASH==TIMEOUT==0 else 1)
