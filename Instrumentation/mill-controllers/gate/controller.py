#!/usr/bin/env python3
"""Deterministic receipt controller for unchanged Mill Set-MillGate.ps1."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, sqlite3, subprocess, uuid
from pathlib import Path

MAX_JSON=65536; TIMEOUT=120
GATES={'source_freeze','candidate','static','compiler','package','live'}; RESULTS={'PENDING','PASS','FAIL','BLOCKED'}
SOURCE=('Set-MillGate.ps1','Update-MillManifest.ps1','Test-MillBatch.ps1')
def now(): return dt.datetime.now(dt.UTC).isoformat().replace('+00:00','Z')
def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def rh(v): return sha(canon(v))
def path(v):
    if not isinstance(v,str) or not v: raise ValueError('nonempty path required')
    return Path(os.path.abspath(v))
def inside(c,p):
    try:
        c,p=os.path.normcase(os.path.normpath(str(c))),os.path.normcase(os.path.normpath(str(p)))
        return c==p or os.path.commonpath((c,p))==p
    except ValueError: return False
def fh(p): return sha(p.read_bytes()) if p.is_file() else None
def ident(root):
    files=[]
    for name in SOURCE:
        p=root/name
        if not p.is_file(): raise RuntimeError(f'missing source: {p}')
        files.append({'path':name,'sha256':fh(p)})
    return {'tool':'Set-MillGate.ps1','root':str(root),'files':files,'sha256':sha(canon(files))}
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name('.'+p.name+'.'+uuid.uuid4().hex+'.tmp')
    t.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(t,p)
def load(p):
    raw=p.read_bytes()
    if len(raw)>MAX_JSON: raise RuntimeError('JSON too large')
    return json.loads(raw.decode())
def snap(b): return {n:fh(b/n) for n in ('MILL_BATCH.json','GATE_LEDGER.csv','MANIFEST.sha256')}
def db(state):
    state.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(state/'controller.sqlite3',timeout=5,isolation_level=None)
    c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA busy_timeout=5000')
    c.execute('CREATE TABLE IF NOT EXISTS ops (id TEXT PRIMARY KEY,digest TEXT,target TEXT,status TEXT,receipt TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS leases (target TEXT PRIMARY KEY,holder TEXT)'); return c
def invoke(cmd,cwd):
    try: p=subprocess.run(cmd,cwd=str(cwd),text=True,capture_output=True,timeout=TIMEOUT)
    except FileNotFoundError as e: return {'launched':False,'exit_code':None,'timed_out':False,'stdout':'','stderr':'','error':str(e)}
    except subprocess.TimeoutExpired as e: return {'launched':True,'exit_code':None,'timed_out':True,'stdout':e.stdout or '','stderr':e.stderr or ''}
    return {'launched':True,'exit_code':p.returncode,'timed_out':False,'stdout':p.stdout,'stderr':p.stderr}
def parsed(v):
    try: return json.loads(v.strip())
    except Exception: return None
def receipt(rid,rd,source,batch):
    return {'receipt_schema':'mill-gate-controller/v1','receipt_id':uuid.uuid4().hex,'recorded_utc':now(),'request_id':rid,'request_digest':rd,'derived':{'batch_path':str(batch)},'tool_identity':source,'admission':'not_permitted','gate_write_reported':'not_run','process_outcome':None,'pre_write_batch_identity':None,'post_write_batch_identity':None,'evidence_identity':None,'ledger_append_observed':'not_observed','manifest_reseal_observed':'not_observed','structural_validation':'not_run','retained_state':'none_observed','authority':'assertion_not_accepted','next_permitted_action':'correct_request_or_authority','problems':[]}
def save(c,state,r,status,new):
    s=json.dumps(r,sort_keys=True,separators=(',',':'))
    if new: c.execute('INSERT INTO ops VALUES (?,?,?,?,?)',(r['request_id'],r['request_digest'],r['derived']['batch_path'],status,s))
    else: c.execute('UPDATE ops SET status=?,receipt=? WHERE id=?',(status,s,r['request_id']))
    dump(state/'receipts'/(r['request_id']+'.json'),r)
def execute(req,auth,root,state,powershell='pwsh'):
    source=ident(root); rd=rh(req); rid=req.get('request_id','UNUSABLE') if isinstance(req,dict) else 'UNUSABLE'; issues=[]
    try: batch=path(req.get('batch_path'))
    except Exception: batch=Path('.'); issues.append('invalid batch_path')
    r=receipt(rid,rd,source,batch)
    if not isinstance(rid,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}',rid): issues.append('invalid request_id'); r['request_id']=rid='UNUSABLE'
    gate=req.get('gate'); result=req.get('result')
    if gate not in GATES: issues.append('invalid gate')
    if result not in RESULTS: issues.append('invalid result')
    evidence=req.get('evidence_path',''); ev=None
    if result!='PENDING':
        if not isinstance(evidence,str) or not evidence or os.path.isabs(evidence) or re.search(r'(^|[\\/])\.\.([\\/]|$)',evidence): issues.append('unsafe evidence_path')
        else:
            ev=path(str(batch/evidence))
            if not inside(ev,batch) or not ev.is_file(): issues.append('missing evidence')
            else: r['evidence_identity']={'path':evidence.replace('\\','/'),'sha256':fh(ev)}
    if not isinstance(auth,dict) or auth.get('request_digest')!=rd or auth.get('tool_identity_sha256')!=source['sha256']: issues.append('authority binding mismatch')
    roots=auth.get('allowed_batch_roots') if isinstance(auth,dict) else None
    try: allowed=[path(x) for x in roots] if isinstance(roots,list) else []
    except Exception: allowed=[]; issues.append('invalid allowed roots')
    if not allowed or not any(inside(batch,x) for x in allowed): issues.append('batch outside authorized roots')
    if result!='PENDING' and (not r['evidence_identity'] or auth.get('evidence_sha256')!=r['evidence_identity']['sha256']): issues.append('evidence digest mismatch')
    c=db(state)
    try:
        c.execute('BEGIN IMMEDIATE'); old=c.execute('SELECT digest FROM ops WHERE id=?',(rid,)).fetchone()
        if old:
            c.execute('COMMIT'); r['problems'].append('request_id already bound'); r['retained_state']='prior_request_preserved'; return r
        if issues:
            r['problems']=issues; save(c,state,r,'not_permitted',True); c.execute('COMMIT'); return r
        held=c.execute('SELECT holder FROM leases WHERE target=?',(str(batch),)).fetchone()
        if held:
            r['problems'].append('gate lease held'); r['retained_state']='lease_preserved'; r['next_permitted_action']='await_recovery_authority'; save(c,state,r,'blocked',True); c.execute('COMMIT'); return r
        c.execute('INSERT INTO leases VALUES (?,?)',(str(batch),rid)); r['admission']='permitted'; r['authority']='assertion_accepted_for_gate_write_only'; r['next_permitted_action']='invoke_gate_writer'; r['pre_write_batch_identity']=snap(batch); save(c,state,r,'running',True); c.execute('COMMIT')
    finally: c.close()
    cmd=[powershell,'-NoProfile','-NonInteractive','-File',str(root/'Set-MillGate.ps1'),'-BatchPath',str(batch),'-Gate',gate,'-Result',result,'-Reviewer',req.get('reviewer','UNASSIGNED'),'-Notes',req.get('notes','')]
    if result!='PENDING': cmd+=['-EvidencePath',evidence]
    out=invoke(cmd,root); report=parsed(out['stdout']); r['process_outcome']=out; r['gate_write_reported']='true' if report and report.get('result')=='GATE_RECORDED' else 'unknown'; r['post_write_batch_identity']=snap(batch)
    pre,post=r['pre_write_batch_identity'],r['post_write_batch_identity']; r['ledger_append_observed']='changed' if pre['GATE_LEDGER.csv']!=post['GATE_LEDGER.csv'] else 'not_observed'; r['manifest_reseal_observed']='changed' if pre['MANIFEST.sha256']!=post['MANIFEST.sha256'] else 'not_observed'
    check=invoke([powershell,'-NoProfile','-NonInteractive','-File',str(root/'Test-MillBatch.ps1'),'-BatchPath',str(batch)],root); r['structural_validation']=(parsed(check['stdout']) or {}).get('result','unknown')
    r['retained_state']='receipt_retained' if r['gate_write_reported']=='true' and r['structural_validation']=='PASS' else 'partial_or_unknown'; r['next_permitted_action']='await_user_review' if r['retained_state']=='receipt_retained' else 'await_recovery_authority'
    c=db(state); c.execute('BEGIN IMMEDIATE'); save(c,state,r,'pass' if r['retained_state']=='receipt_retained' else 'unknown',False); c.execute('DELETE FROM leases WHERE target=?',(str(batch),)); c.execute('COMMIT'); c.close(); return r
def main():
    p=argparse.ArgumentParser(); p.add_argument('--tool-root',required=True,type=Path); p.add_argument('--state-root',required=True,type=Path); p.add_argument('--powershell',default='pwsh'); p.add_argument('request',type=Path); p.add_argument('authority',type=Path); a=p.parse_args(); r=execute(load(a.request),load(a.authority),a.tool_root.resolve(),a.state_root.resolve(),a.powershell); print(json.dumps(r,indent=2)); return 0 if r['retained_state']=='receipt_retained' else 2
if __name__=='__main__': raise SystemExit(main())
