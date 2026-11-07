from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=subprocess.run([sys.executable,str(ROOT/'runner'/'analyze_coverage.py')],capture_output=True,text=True)
assert p.returncode==0,p.stdout+p.stderr
r=json.loads((ROOT/'coverage'/'coverage-report.json').read_text(encoding='utf-8'))
assert r['fixture_count']>=68, r['fixture_count']
sem={x['item']:x for x in r['dimensions']['semantic_cells']['items']}
for k in ('SYMBOL.ATOMICS','SYMBOL.DILATION','SYMBOL.MACRO_DYNAMICS','SYMBOL.META_CONTEXT'):
    assert sem[k]['status']=='COVERED',(k,sem[k])
    assert sem[k]['count']>=8,(k,sem[k]['count'])
assert not r['dimensions']['symbol_depth']['gaps'],r['dimensions']['symbol_depth']['gaps']
assert not r['dimensions']['symbol_depth']['thin'],r['dimensions']['symbol_depth']['thin']
assert not r['dimensions']['symbol_dilation_radii']['gaps'],r['dimensions']['symbol_dilation_radii']['gaps']
print('symbol-depth-test: PASS')
