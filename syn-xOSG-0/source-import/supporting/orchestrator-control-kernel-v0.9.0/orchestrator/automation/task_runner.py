#!/usr/bin/env python3
"""Whitelisted synchronous task runner for TG-DET-001.

No arbitrary command execution is supported. Tasks map to fixed Python functions.
The runner prints minimized results only.
"""
from __future__ import annotations
import hashlib, importlib.util, json, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DET_PATH=ROOT/'orchestrator/automation/deterministic_offload.py'
spec=importlib.util.spec_from_file_location('deterministic_offload',DET_PATH)
det=importlib.util.module_from_spec(spec); spec.loader.exec_module(det)
GRAPH=json.loads((ROOT/'orchestrator/state/TASK_GRAPH.json').read_text())

class Runner:
    def __init__(self, output_zip: Path):
        self.output_zip=output_zip
        self.done=set(); self.cache={}; self.results=[]
    def record(self,tid,status,summary):
        self.results.append({'task':tid,'status':status,'summary':summary})
        if status!='PASS': raise RuntimeError(f'{tid} failed: {summary}')
        self.done.add(tid)
    def run_task(self,t):
        tid,typ=t['id'],t['type']
        if not set(t.get('depends_on',[])) <= self.done:
            raise RuntimeError(f'{tid}: unmet dependencies')
        if typ=='inventory':
            self.cache['inventory']=det.inventory(); self.record(tid,'PASS',{'files':len(self.cache['inventory'])})
        elif typ=='hash':
            self.cache['hashes']=det.hashes(); self.record(tid,'PASS',{'files':len(self.cache['hashes'])})
        elif typ=='merkle':
            self.cache['merkle']=det.merkle(self.cache['hashes']); self.record(tid,'PASS',{'merkle_sha256':self.cache['merkle']})
        elif typ=='structure':
            r=det.required_structure(); self.record(tid,'PASS' if r['pass'] else 'FAIL',{'required':r['required'],'missing_count':len(r['missing'])})
        elif typ=='regression':
            r=det.run_regressions(); ok=all(x['pass'] for x in r); self.cache['regressions']=r
            self.record(tid,'PASS' if ok else 'FAIL',{'suites':len(r),'passed':sum(x['pass'] for x in r)})
        elif typ=='tool_policy':
            r=[det.validate_json('orchestrator/hypervisor/TOOL_POLICY.json'),det.validate_json('orchestrator/state/TASK_GRAPH.json')]
            self.record(tid,'PASS' if all(x['pass'] for x in r) else 'FAIL',{'json_documents':len(r)})
        elif typ=='gate_probe':
            r=det.gate_probe(); self.record(tid,'PASS' if r['pass'] else 'FAIL',{'checks':r['checks']})
        elif typ=='attest':
            hashes=self.cache['hashes']
            regs=self.cache['regressions']
            structure=det.required_structure()
            json_validation=[det.validate_json('orchestrator/hypervisor/TOOL_POLICY.json'),det.validate_json('orchestrator/state/TASK_GRAPH.json')]
            gate=det.gate_probe()
            evidence={
              'schema':'xosg.minimized-evidence.v1',
              'data_touch':{'model_default':'DT0-DT3','semantic_full_content':False},
              'inventory':{'files':len(hashes),'bytes':sum(r['bytes'] for r in hashes)},
              'tree_merkle_sha256':self.cache['merkle'],
              'structure':structure,
              'json_validation':json_validation,
              'regressions':regs,
              'gate':gate
            }
            evidence['regression_totals']={
              'suites':len(regs),
              'checks':sum((x.get('checks') or 0) for x in regs),
              'passed':sum((x.get('passed') or 0) for x in regs),
              'failed':sum((x.get('failed') or 0) for x in regs)
            }
            evidence['pass']=structure['pass'] and all(x['pass'] for x in json_validation) and all(x['pass'] for x in regs) and gate['pass']
            if not evidence['pass']: self.record(tid,'FAIL',{'evidence_pass':False})
            (ROOT/'orchestrator/validation/MINIMIZED_EVIDENCE.json').write_text(json.dumps(evidence,indent=2)+'\n')
            (ROOT/'orchestrator/validation/FILE_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n')
            with (ROOT/'orchestrator/validation/ATTESTATION.md').open('a') as f:
                f.write(f'\n## Sealed deterministic evidence\n\n- files in Merkle scope: {evidence["inventory"]["files"]}\n- bytes in Merkle scope: {evidence["inventory"]["bytes"]}\n- Merkle SHA-256: `{evidence["tree_merkle_sha256"]}`\n- regression suites: {evidence["regression_totals"]["suites"]}\n- regression checks: {evidence["regression_totals"]["checks"]} / {evidence["regression_totals"]["passed"]} passed\n- gate probe: PASS\n')
            self.record(tid,'PASS',{'merkle_sha256':evidence['tree_merkle_sha256'],'files':evidence['inventory']['files'],'regression_checks':evidence['regression_totals']['checks']})
        elif typ=='relock_gate':
            r=det.gate_probe(); self.record(tid,'PASS' if r['pass'] else 'FAIL',{'gate':'LOCKED_POST_RELEASE'})
        elif typ=='package':
            inv=det.inventory()
            lines=['# Inventory','','Generated deterministically from package paths/sizes.','',f'Files in deterministic scope: {len(inv)}','']
            lines += [f'- `{x["path"]}` — {x["bytes"]} bytes' for x in inv]
            (ROOT/'docs/INVENTORY.md').write_text('\n'.join(lines)+'\n')
            checksum_lines=[]
            for p in sorted(ROOT.rglob('*')):
                if not p.is_file(): continue
                rel=p.relative_to(ROOT).as_posix()
                if rel=='operator/SHA256SUMS.txt' or '__pycache__' in p.parts: continue
                checksum_lines.append(f'{det.sha256_file(p)}  {rel}')
            (ROOT/'operator/SHA256SUMS.txt').write_text('\n'.join(checksum_lines)+'\n')
            if self.output_zip.exists(): self.output_zip.unlink()
            with zipfile.ZipFile(self.output_zip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
                for p in sorted(ROOT.rglob('*')):
                    if p.is_file() and '__pycache__' not in p.parts:
                        z.write(p,p.relative_to(ROOT).as_posix())
            self.record(tid,'PASS',{'archive':self.output_zip.name,'bytes':self.output_zip.stat().st_size})
        elif typ=='archive_verify':
            with zipfile.ZipFile(self.output_zip) as z:
                bad=z.testzip(); count=len(z.infolist())
            h=det.sha256_file(self.output_zip)
            sha_path=Path(str(self.output_zip)+'.sha256')
            sha_path.write_text(f'{h}  {self.output_zip.name}\n')
            self.cache['archive_sha256']=h
            self.record(tid,'PASS' if bad is None else 'FAIL',{'zip_entries':count,'sha256':h})
        else:
            raise RuntimeError(f'unsupported task type: {typ}')
    def run(self):
        pending={t['id']:t for t in GRAPH['tasks']}
        while pending:
            progressed=False
            for tid,t in list(pending.items()):
                if set(t.get('depends_on',[])) <= self.done:
                    self.run_task(t); pending.pop(tid); progressed=True
            if not progressed: raise RuntimeError('task graph cycle/unmet dependency')
        return {'graph':GRAPH['graph_id'],'tasks':len(self.results),'pass':True,'results':self.results,'archive_sha256':self.cache.get('archive_sha256')}

def main():
    if len(sys.argv)!=2: raise SystemExit('usage: task_runner.py OUTPUT_ZIP')
    r=Runner(Path(sys.argv[1]).resolve()).run()
    print(json.dumps(r,indent=2))
if __name__=='__main__': main()
