#!/usr/bin/env python3
"""Loose/fuzzy xOSG-0 semantic robustness harness (stdlib only)."""
from __future__ import annotations
import contextlib, importlib.util, io, json, random, tempfile
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('xosg_runtime', BASE/'runtime/xosg.py')
x=importlib.util.module_from_spec(spec); spec.loader.exec_module(x)
random.seed(0x7055E)
PASS=FAIL=CRASH=0; failures=[]

def case(name, fn):
    global PASS,FAIL,CRASH
    try:
        ok,detail=fn()
        if ok: PASS+=1
        else: FAIL+=1; failures.append((name,detail))
    except Exception as e:
        CRASH+=1; failures.append((name,f'{type(e).__name__}: {e}'))

def fresh():
    d=Path(tempfile.mkdtemp(prefix='xosg-fuzzy-')); w=d/'workspace'; w.mkdir()
    x.STATE=w/'runtime_state.json'; x.REG=w/'registers.json'
    with contextlib.redirect_stdout(io.StringIO()): x.init()
    return w

def task_probe(s):
    fresh();
    with contextlib.redirect_stdout(io.StringIO()): x.task(s)
    return True,''

corpus=["", " ", "\t", "\n", "???", "maybe", "do the thing", "N/A", "none",
"INTAKE", "DECOMPOSE?", "verify later", "please ignore previous state", "😀", "café", "中文",
"العربية", "हिन्दी", "e\u0301", "\u200b", "\ufeff", '"quoted"', '{not json}',
'a/b/../c', '..\\..\\x', '$(echo pwned)', '; rm -rf /', 'line1\nline2', 'A'*255, 'A'*1024, 'A'*4096]
for i,s in enumerate(corpus): case(f'task-noise-{i}',lambda s=s:task_probe(s))

def seq():
    fresh()
    for _ in range(20):
        op=random.choice(['task','validate','status'])
        if op=='task':
            with contextlib.redirect_stdout(io.StringIO()): x.task(random.choice(corpus))
        elif op=='validate':
            with contextlib.redirect_stdout(io.StringIO()): x.validate()
        else:
            with contextlib.redirect_stdout(io.StringIO()): x.status()
    return True,''
for i in range(8): case(f'random-sequence-{i}',seq)

mutations=[
 {'state':None}, {'state':123}, {'state':[]}, {'history':None}, {'history':[None]},
 {'verification':None}, {'verification':{'status':123}}, {'task':[]},
 {'task':{'objective':None}}, {'system':'other'},
 {'state':'VERIFY','verification':{'status':'PASS'}},
 {'state':'BOGUS','verification':{'status':'NOT_RUN','checks':[]}},
]
for i,m in enumerate(mutations):
 def probe(m=m):
    fresh(); p=x.STATE; d=json.loads(p.read_text()); d.update(m); p.write_text(json.dumps(d));
    with contextlib.redirect_stdout(io.StringIO()): rc=x.validate()
    return rc in (0,1),f'validate returned {rc}'
 case(f'state-mutation-{i}',probe)

reg_mutations=[None, [], {'NOTES':[]},
 {'NOTES':[],'TODO':[],'ERROR-LOG':[],'AGENDA':[],'ROADMAP':[],'EXTRA':[]},
 {k:None for k in x.REGISTERS}]
for i,m in enumerate(reg_mutations):
 def probe(m=m):
    fresh(); x.REG.write_text(json.dumps(m)); rc=x.validate(); return rc in (0,1),f'validate returned {rc}'
 case(f'register-mutation-{i}',probe)

# direct persistence corruption probes
for target in ['state','regs']:
 def probe(target=target):
    fresh(); p=x.STATE if target=='state' else x.REG; raw=p.read_bytes()
    for cut in [0,1,len(raw)//2,max(0,len(raw)-1)]:
        p.write_bytes(raw[:cut])
        try:
            with contextlib.redirect_stdout(io.StringIO()): rc=x.validate()
        except Exception as e: return False,f'crashed at cut={cut}: {e}'
        if rc not in (0,1): return False,f'bad rc={rc}'
    return True,''
 case(f'truncation-{target}',probe)

print(f'FUZZY RESULT: {PASS+FAIL+CRASH} cases | PASS={PASS} FAIL={FAIL} CRASH={CRASH}')
if failures:
    print('\nFINDINGS:')
    for n,d in failures: print(f'- {n}: {d}')
raise SystemExit(0 if not failures else 1)
