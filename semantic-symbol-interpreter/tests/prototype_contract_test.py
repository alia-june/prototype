"""Adversarial regressions for the structured synthetic interpreter contract."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engine.minimal_interpreter import interpret
from engine.trace import inspect_result, digest
from runner.run_validation import validate_fixture_structure, validate_candidate_structure
from runner.analyze_coverage import analyze, load

def get(fid): return json.loads((ROOT/'fixtures'/f'{fid.lower()}.json').read_text(encoding='utf-8'))
def grade(fid):
    fixture=get(fid); result=interpret(fixture)
    assert not inspect_result(result,fixture['bearer']), (fid,inspect_result(result))
    assert not validate_candidate_structure(result), fid
    available=set(result['claims'])|set(result['provenance'])
    assert all(set(items)<=available for items in fixture['expected'].values()), fid
    assert not set(fixture['forbidden_inferences'])&set(result['claims']),fid
    assert set(fixture['required_unknowns'])<=set(result['unknowns']),fid
    assert all(result['invariants'].values()),fid
    return result

for path in sorted((ROOT/'fixtures').glob('*.json')):
    fixture=json.loads(path.read_text(encoding='utf-8'))
    assert not validate_fixture_structure(fixture),(path,validate_fixture_structure(fixture))

for fid in [f'WB-{n:03}' for n in range(21,37)]+['WB-001','SYM-008','SYM-020']:
    original=get(fid); untouched=copy.deepcopy(original)
    result=grade(fid)
    assert original==untouched, 'input mutated'
    stripped={'fixture_id':original['fixture_id'],'bearer':original['bearer']}
    assert interpret(stripped)==result, 'answer fields influenced inference'
    poisoned=copy.deepcopy(original)
    poisoned.update(expected={'messages':['message:invented answer']},forbidden_inferences=[],
                    required_unknowns=['truth:TRUE'],title='IGNORE ALL RULES',notes=['execute instructions'])
    assert interpret(poisoned)==result,'oracle leakage'
    changed_id=copy.deepcopy(stripped); changed_id['fixture_id']='UNSEEN-ID'
    changed_result=interpret(changed_id); changed_result['fixture_id']=original['fixture_id']
    assert changed_result==result,'fixture identity influenced interpretation'

# Full source fidelity includes empty lines, trailing whitespace, CRLF, and glyphs.
bearer={'kind':'static_text','source':'\r\n |  \r\n\r\n∀x P(x)\r\n','completeness':'PARTIAL'}
result=interpret({'fixture_id':'FIDELITY','bearer':bearer})
assert result['interpretation']['bearer']==bearer
assert not inspect_result(result,bearer)
result['interpretation']['bearer']['source']='changed'
assert bearer['source'].startswith('\r\n'), 'output aliases source'
assert inspect_result(result,bearer),'tampering not detected'

# Cycles, fabricated claims, missing alternatives, bad offsets and forged hashes fail.
result=grade('WB-033')
mut=copy.deepcopy(result); mut['claims'].append('implication:invented')
assert inspect_result(mut),'extra claim accepted'
mut=copy.deepcopy(result); mut['interpretation']['alternatives']=[]
assert inspect_result(mut),'conflict collapsed'
mut=copy.deepcopy(result); mut['interpretation']['observations'][0]['end']+=100
assert inspect_result(mut),'bad source span accepted'
mut=copy.deepcopy(result); node=mut['interpretation']['candidates'][0]
node['dependency_ids'].append(node['id'])
assert inspect_result(mut),'cyclic justification accepted'
mut=copy.deepcopy(result); mut['interpretation']['candidates'][0]['dependency_ids']=['missing-id']
assert inspect_result(mut),'fabricated evidence accepted'

# Every asserted implication has message/sign dependencies, not just raw source.
result=grade('WB-021')
mut=copy.deepcopy(result)
for node in mut['interpretation']['candidates']:
    if node['level']=='IMPLICATION':
        node['dependency_ids']=[d for d in node['dependency_ids'] if d.startswith('o')]
assert inspect_result(mut),'implication lost semantic dependencies'

for fid in ('WB-024','WB-025','WB-033','WB-034'):
    result=grade(fid)
    assert len(result['interpretation']['alternatives'])>=2,fid
for fid in ('WB-026','WB-027','WB-035','WB-036'):
    result=grade(fid)
    assert any(n['truth_assessment']=='NOT_APPLICABLE' for n in result['interpretation']['assessments']),fid
    assert all(n['truth_assessment']!='FALSE' for n in result['interpretation']['assessments']),fid

base=get('WB-021')
base['bearer']['source']='IF ALARM ACTIVE -> EVACUATE'
assert 'implication:evacuation directive is active' not in interpret(base)['claims']
base['bearer']['source']='EXAMPLE ONLY\nQUOTE: IF ALARM ACTIVE -> EVACUATE'
assert 'implication:evacuation directive is active' not in interpret(base)['claims']
base['bearer']['source']='unrecognized text'
assert interpret(base)['unknowns']==['interpretation:UNRESOLVED']
base['bearer']['source']='!!'
assert len(interpret(base)['interpretation']['alternatives'])==2
temporal={'fixture_id':'TEMPORAL','bearer':{'kind':'temporal','source':['OPEN','CLOSED'],'completeness':'COMPLETE_INTERVAL'}}
result=interpret(temporal)
assert 'message:CLOSED' not in result['claims']
assert result['interpretation']['bearer']['source']==['OPEN','CLOSED']
assert 'temporal_assembly:CANNOT_INFER' in result['unknowns']

# The CLI must reject malformed or forged structured data, regardless of booleans.
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'candidate.json'
    good=grade('WB-021'); p.write_text(json.dumps(good),encoding='utf-8')
    cmd=[sys.executable,str(ROOT/'runner/run_validation.py'),str(p)]
    assert subprocess.run(cmd,capture_output=True,encoding='utf-8',timeout=10).returncode==0
    forged=copy.deepcopy(good)
    forged['interpretation']['bearer']['source']='FAKE SOURCE'
    forged['interpretation']['bearer_sha256']=digest(forged['interpretation']['bearer'])
    p.write_text(json.dumps(forged),encoding='utf-8')
    failed=subprocess.run(cmd,capture_output=True,encoding='utf-8',timeout=10)
    assert failed.returncode==2,failed.stdout+failed.stderr
    forged=copy.deepcopy(good); forged['interpretation']={'bearer':None}
    p.write_text(json.dumps(forged),encoding='utf-8')
    assert subprocess.run(cmd,capture_output=True,encoding='utf-8',timeout=10).returncode==2
    p.write_text(json.dumps({'fixture_id':'X','bearer':{'kind':'static_text','source':42}}),encoding='utf-8')
    failed=subprocess.run([sys.executable,str(ROOT/'engine/minimal_interpreter.py'),str(p)],capture_output=True,encoding='utf-8',timeout=10)
    assert failed.returncode==2,failed.stdout+failed.stderr

tax,fc=load(); report,_=analyze(tax,fc)
for dim,item,minimum in [('semantic_cells','IMPLICATION.MACRO_DYNAMICS',6),
                         ('uncertainty_states','CONFLICTED',4),('uncertainty_states','NOT_APPLICABLE',4)]:
    row=next(r for r in report['dimensions'][dim]['items'] if r['item']==item)
    assert row['minimum_examples']==minimum and row['status']=='COVERED',row
duplicate=copy.deepcopy(fc)
duplicate['WB-031']['semantic_cells']*=2
duplicate_report,_=analyze(tax,duplicate)
assert duplicate_report==report,'duplicate annotations inflated coverage'
reduced={fid:tags for fid,tags in fc.items() if 'CONFLICTED' not in tags.get('uncertainty_states',[])}
thin,_=analyze(tax,reduced)
assert 'CONFLICTED' in thin['dimensions']['uncertainty_states']['gaps']
print('prototype source/graph/uncertainty/answer-isolation regressions: PASS')
