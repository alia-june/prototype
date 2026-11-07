#!/usr/bin/env python3
from pathlib import Path
import argparse,csv,json,sys

ROOT=Path(__file__).resolve().parents[1]

def load():
    tax=json.loads((ROOT/'coverage'/'taxonomy.json').read_text(encoding='utf-8'))
    fc=json.loads((ROOT/'coverage'/'fixture-coverage.json').read_text(encoding='utf-8'))['fixtures']
    return tax,fc

def analyze(tax,fc):
    out={'fixture_count':len(fc),'dimensions':{},'overall':{}}
    all_rows=[]
    total_items=touched_items=covered_items=0
    for dname,ddef in tax['dimensions'].items():
        counts={name:[] for name in ddef['items']}
        for fid,tags in fc.items():
            for item in tags.get(dname,[]):
                if item not in counts:
                    raise ValueError(f'{fid}: unknown {dname} coverage item {item}')
                if fid not in counts[item]: counts[item].append(fid)
        rows=[]
        covered=touched=0
        for item,meta in ddef['items'].items():
            n=len(counts[item]); minimum=meta.get('minimum_examples',1)
            status='GAP' if n==0 else ('COVERED' if n>=minimum else 'THIN')
            if n>0: touched+=1
            if status=='COVERED': covered+=1
            rows.append({'item':item,'count':n,'minimum_examples':minimum,'status':status,'fixtures':counts[item]})
            all_rows.append({'dimension':dname,**rows[-1]})
        total=len(rows)
        out['dimensions'][dname]={
            'description':ddef.get('description',''),
            'total_items':total,'touched_items':touched,'covered_items':covered,
            'touched_pct':round(100*touched/total,1) if total else 100.0,
            'covered_pct':round(100*covered/total,1) if total else 100.0,
            'gaps':[r['item'] for r in rows if r['status']=='GAP'],
            'thin':[r['item'] for r in rows if r['status']=='THIN'],
            'items':rows
        }
        total_items+=total; touched_items+=touched; covered_items+=covered
    out['overall']={
        'total_items':total_items,'touched_items':touched_items,'covered_items':covered_items,
        'touched_pct':round(100*touched_items/total_items,1),
        'covered_pct':round(100*covered_items/total_items,1),
        'interpretation':'Touched means at least one fixture exercises the item; Covered means the configured minimum example count is met.'
    }
    return out,all_rows

def write_outputs(report,rows):
    cov=ROOT/'coverage'; cov.mkdir(exist_ok=True)
    (cov/'coverage-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    with (cov/'coverage-matrix.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['dimension','item','count','minimum_examples','status','fixtures'])
        w.writeheader()
        for r in rows:
            x=dict(r); x['fixtures']=';'.join(x['fixtures']); w.writerow(x)
    lines=['# SSMI coverage report','',f"Fixtures: **{report['fixture_count']}**",'',
           f"Overall touched: **{report['overall']['touched_pct']}%**",f"Overall threshold-covered: **{report['overall']['covered_pct']}%**",'',
           '> Touched means at least one fixture exercises the item. Covered means the configured minimum number of independent fixtures is met.','']
    for dname,d in report['dimensions'].items():
        lines += [f'## {dname}', '', f"Touched: {d['touched_items']}/{d['total_items']} ({d['touched_pct']}%)  ", f"Covered: {d['covered_items']}/{d['total_items']} ({d['covered_pct']}%)", '']
        if d['gaps']:
            lines += ['**Gaps:** '+', '.join(d['gaps']),'']
        if d['thin']:
            lines += ['**Thin coverage:** '+', '.join(d['thin']),'']
        if not d['gaps'] and not d['thin']:
            lines += ['No detected gaps at the configured thresholds.','']
    (cov/'coverage-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description='Analyze SSMI fixture coverage and report gaps/thin areas.')
    ap.add_argument('--check',action='store_true',help='Return nonzero if taxonomy/annotations are invalid. Coverage gaps themselves are not errors.')
    ap.add_argument('--json',action='store_true',help='Print full JSON report.')
    ap.add_argument('--require-targets',action='store_true',help='Fail if implication macro-dynamics, CONFLICTED or NOT_APPLICABLE are below threshold.')
    args=ap.parse_args()
    try:
        tax,fc=load()
        identities=[json.loads(p.read_text(encoding='utf-8'))['fixture_id'] for p in (ROOT/'fixtures').glob('*.json')]
        actual=set(identities)
        if len(actual)!=len(identities): raise ValueError('duplicate fixture IDs')
        if actual != set(fc): raise ValueError('coverage annotations and fixture IDs do not match')
        report,rows=analyze(tax,fc); write_outputs(report,rows)
    except Exception as e:
        print(json.dumps({'pass':False,'error':str(e)},indent=2))
        return 2
    if args.json:
        print(json.dumps(report,indent=2))
    else:
        print(f"fixtures: {report['fixture_count']}")
        print(f"overall touched: {report['overall']['touched_pct']}%")
        print(f"overall covered: {report['overall']['covered_pct']}%")
        for name,d in report['dimensions'].items():
            print(f"{name}: touched {d['touched_pct']}%, covered {d['covered_pct']}%, gaps {len(d['gaps'])}, thin {len(d['thin'])}")
        print('reports: coverage/coverage-report.json, coverage/coverage-report.md, coverage/coverage-matrix.csv')
    if args.require_targets:
        targets={'semantic_cells':['IMPLICATION.MACRO_DYNAMICS'],'uncertainty_states':['CONFLICTED','NOT_APPLICABLE']}
        if any(row['status']!='COVERED' for dim,items in targets.items() for row in report['dimensions'][dim]['items'] if row['item'] in items): return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
