from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'/'minimal_interpreter.py'; RUNNER=ROOT/'runner'/'run_validation.py'

def case(fid, expect_pass=True):
    fixture=ROOT/'fixtures'/f'{fid.lower()}.json'
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'out.json'
        e=subprocess.run([sys.executable,str(ENGINE),str(fixture),'-o',str(out)],capture_output=True,encoding='utf-8',timeout=10)
        assert e.returncode==0,e.stderr
        c=json.loads(out.read_text(encoding='utf-8'))
        assert 'claims' in c and 'unknowns' in c and 'provenance' in c
        v=subprocess.run([sys.executable,str(RUNNER),str(out)],capture_output=True,encoding='utf-8',timeout=10)
        if expect_pass: assert v.returncode==0,v.stdout+v.stderr

for fid in ['WB-001','WB-009','WB-021','WB-022','WB-023','WB-024','WB-025','WB-026','WB-027','WB-028','WB-029','WB-030','SYM-001','SYM-003','SYM-010','SYM-011','SYM-020','SYM-025','SYM-026','SYM-027','SYM-032','SYM-033']:
    case(fid,True)
print('minimal engine regression: PASS')
