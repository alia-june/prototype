#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'/'minimal_interpreter.py'; RUNNER=ROOT/'runner'/'run_validation.py'
rows=[]
for fixture in sorted((ROOT/'fixtures').glob('*.json')):
    with tempfile.TemporaryDirectory() as td:
        cand=Path(td)/'candidate.json'
        try:
            e=subprocess.run([sys.executable,str(ENGINE),str(fixture),'-o',str(cand)],capture_output=True,encoding='utf-8',timeout=10)
        except subprocess.TimeoutExpired:
            rows.append({'fixture_id':fixture.stem.upper(),'pass':False,'engine_error':'timeout after 10 seconds'}); continue
        if e.returncode!=0:
            rows.append({'fixture_id':fixture.stem.upper(),'pass':False,'engine_error':e.stderr.strip()}); continue
        try:
            v=subprocess.run([sys.executable,str(RUNNER),str(cand)],capture_output=True,encoding='utf-8',timeout=10)
        except subprocess.TimeoutExpired:
            rows.append({'fixture_id':fixture.stem.upper(),'pass':False,'engine_error':'validator timeout after 10 seconds'}); continue
        try: rep=json.loads(v.stdout or v.stderr)
        except Exception: rep={'pass':False,'raw':(v.stdout+v.stderr).strip()}
        rep['fixture_file']=fixture.name; rows.append(rep)
passed=sum(1 for r in rows if r.get('pass'))
report={'engine':'ssmi-minimal-interpreter/0.2.1','fixture_count':len(rows),'passed':passed,'failed':len(rows)-passed,'pass_pct':round(100*passed/len(rows),1) if rows else 0,'results':rows}
(ROOT/'engine'/'benchmark-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=['# Minimal interpreter benchmark','',f"Fixtures: **{len(rows)}**",f"Passed: **{passed}**",f"Failed: **{len(rows)-passed}**",f"Pass rate: **{report['pass_pct']}%**",'', 'This is a narrow rule-based baseline over structured synthetic bearer input; failures are preserved as development evidence.','']
for r in rows:
    if not r.get('pass'):
        lines.append(f"- {r.get('fixture_id',r.get('fixture_file'))}: FAIL — missing {len(r.get('missing_required',[]))}, forbidden {len(r.get('forbidden_present',[]))}, unknowns {len(r.get('missing_required_unknowns',[]))}, error {r.get('engine_error',r.get('error','none'))}")
(ROOT/'engine'/'benchmark-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['engine','fixture_count','passed','failed','pass_pct']},indent=2))
