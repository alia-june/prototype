"""Portable records and bounded structural checks, not semantic attestation."""
import copy
import hashlib
import json

INVARIANTS = ('raw_observation_preserved','whole_bearer_preserved',
              'alternatives_preserved','no_unobserved_as_observed',
              'scope_respected','provenance_complete')

def digest(bearer):
    return hashlib.sha256(json.dumps(bearer,ensure_ascii=False,sort_keys=True,
                                    separators=(',',':')).encode('utf-8')).hexdigest()

def begin(out, bearer, version):
    source = bearer['source']
    segments = source if isinstance(source,list) else [source]
    observations = []
    for segment_index, text in enumerate(segments):
        observations.append({'id':f'o{segment_index}-whole','segment':segment_index,
                             'start':0,'end':len(text),'text':text,'kind':'whole_segment'})
        offset = 0
        for line_index, line in enumerate(text.splitlines(keepends=True)):
            observations.append({'id':f'o{segment_index}-line{line_index}',
                                 'segment':segment_index,'start':offset,
                                 'end':offset+len(line),'text':line,'kind':'line'})
            offset += len(line)
    out['interpretation'] = {
        'schema_version':'1.0','engine_version':version,
        'bearer':copy.deepcopy(bearer),'bearer_sha256':digest(bearer),
        'offset_unit':'Unicode code point; end exclusive; per source segment',
        'observations':observations,'rules':[],'candidates':[],
        'assessments':[],'alternatives':[],'provenance_records':[],
        'capability':'synthetic text / supplied textual descriptions only',
        'completeness':bearer.get('completeness','UNKNOWN'),
        'limits':['No OCR or perception performed.',
                  'Rule source spans are conservative whole-segment dependencies.',
                  'Candidate support is not independently established world truth.']}
    out['_active_rule'] = None

def record(out, collection, value, status=None):
    graph = out['interpretation']
    rule_id = out['_active_rule'] or 'engine-metadata'
    rule = next((r for r in graph['rules'] if r['id']==rule_id),None)
    if rule is None:
        rule = {'id':rule_id,'source':'engine/minimal_interpreter.py',
                'scope':'whole_bearer','evidence_ids':[o['id'] for o in graph['observations'] if o['kind']=='whole_segment'],
                'authority':'prototype rule specification; no action authority',
                'convention_status':'declared synthetic rule; external conventions are assumptions, not observed facts'}
        graph['rules'].append(rule)
    key={'claim':'candidates','assessment':'assessments','alternative':'alternatives',
         'provenance':'provenance_records'}[collection]
    prefix=value.split(':',1)[0]
    level = ('IMPLICATION' if prefix=='implication' else
             'MESSAGE' if prefix.startswith('message') else
             'SIGN' if prefix=='sign' else
             'SYMBOL' if prefix.startswith(('symbol','raw_symbol','raw_run','tokenization','operator','fixity')) else 'ANALYSIS')
    deps=list(rule['evidence_ids'])
    if level=='IMPLICATION':
        deps += [n['id'] for n in graph['candidates'] if n['rule_id']==rule_id and n['level'] in ('MESSAGE','SIGN')]
    elif level=='MESSAGE':
        deps += [n['id'] for n in graph['candidates'] if n['rule_id']==rule_id and n['level'] in ('SYMBOL','SIGN')]
    elif level=='SIGN':
        deps += [n['id'] for n in graph['candidates'] if n['rule_id']==rule_id and n['level']=='SYMBOL']
    node={'id':f'{key}-{len(graph[key])+1}','value':value,'level':level,
          'rule_id':rule_id,'scope':'whole_bearer','dependency_ids':deps,
          'completeness':graph['completeness'],'status':status or 'CANDIDATE',
          'truth_assessment':'UNKNOWN'}
    if collection=='assessment':
        state=value.rsplit(':',1)[-1]
        node['status']=state
        node['dimension']=value.rsplit(':',1)[0]
        if state=='NOT_APPLICABLE': node['truth_assessment']='NOT_APPLICABLE'
    graph[key].append(node)
    if collection=='claim' and prefix in ('tokenization_candidate','reading_order_candidate'):
        record(out,'alternative',value,status='AMBIGUOUS')

def inspect_result(out, expected_bearer=None):
    """Validate source/span/graph contract. Does not prove rule conclusions true."""
    errors=[]
    graph=out.get('interpretation')
    if not isinstance(graph,dict): return ['missing interpretation graph']
    bearer=graph.get('bearer',{})
    if expected_bearer is not None and bearer != expected_bearer:
        errors.append('bearer differs from supplied input')
    try:
        if graph.get('bearer_sha256') != digest(bearer): errors.append('bearer hash mismatch')
        src=bearer['source']; segments=src if isinstance(src,list) else [src]
        if any(not isinstance(x,str) for x in segments): raise ValueError('non-text source')
    except (KeyError,TypeError,ValueError): return errors+['invalid preserved bearer']
    observations=graph.get('observations',[])
    nodes=observations+sum((graph.get(k,[]) for k in ('candidates','assessments','alternatives','provenance_records')),[])
    ids=[n.get('id') for n in nodes]
    if len(ids)!=len(set(ids)) or None in ids: errors.append('duplicate or missing node IDs')
    known=set(ids)
    whole=set()
    for obs in observations:
        try:
            index,start,end=obs['segment'],obs['start'],obs['end']
            if not all(type(x) is int for x in (index,start,end)): raise ValueError()
            if not (0<=index<len(segments) and 0<=start<=end<=len(segments[index])): raise ValueError()
            if obs['text']!=segments[index][start:end]: raise ValueError()
            if obs['kind']=='whole_segment' and start==0 and end==len(segments[index]): whole.add(index)
        except (KeyError,TypeError,ValueError): errors.append('invalid observation span')
    if whole!=set(range(len(segments))): errors.append('whole source segments not preserved')
    rules={r.get('id'):r for r in graph.get('rules',[])}
    if len(rules)!=len(graph.get('rules',[])): errors.append('duplicate rule IDs')
    obsids={n['id'] for n in observations}
    for rule in rules.values():
        if not rule.get('evidence_ids') or not set(rule['evidence_ids'])<=obsids: errors.append('invalid rule evidence')
        if rule.get('scope')!='whole_bearer': errors.append('invalid rule scope')
    adjacency={}
    for n in nodes[len(observations):]:
        rule=rules.get(n.get('rule_id'))
        deps=n.get('dependency_ids',[])
        if rule is None or not deps or not set(deps)<=known: errors.append('missing provenance dependency')
        if rule and not set(rule['evidence_ids'])<=set(deps): errors.append('rule evidence omitted from node')
        if n.get('scope')!='whole_bearer': errors.append('invalid candidate scope')
        if n.get('completeness')!=bearer.get('completeness','UNKNOWN'): errors.append('completeness not propagated')
        adjacency[n['id']]=deps
        if n.get('level')=='IMPLICATION' and n in graph.get('candidates',[]):
            evidence=[x for x in graph.get('candidates',[]) if x['id'] in deps and x['level'] in ('MESSAGE','SIGN')]
            if not evidence: errors.append('implication lacks message/sign dependency')
    visiting=set(); visited=set()
    def visit(nid):
        if nid in visiting: errors.append('cyclic evidence dependency'); return
        if nid in visited: return
        visiting.add(nid)
        for dep in adjacency.get(nid,[]): visit(dep)
        visiting.remove(nid); visited.add(nid)
    for nid in adjacency: visit(nid)
    for field,key in (('claims','candidates'),('unknowns','assessments'),('provenance','provenance_records')):
        if out.get(field)!=[n['value'] for n in graph.get(key,[])]: errors.append(f'{field} differ from structured records')
    for assessment in graph.get('assessments',[]):
        if assessment['status']=='CONFLICTED':
            alternatives=[n for n in graph.get('alternatives',[]) if n['rule_id']==assessment['rule_id'] and n['status']=='CONFLICTED']
            if len({n['value'] for n in alternatives})<2: errors.append('conflict alternatives lost')
        if assessment['status']=='NOT_APPLICABLE' and assessment.get('truth_assessment')!='NOT_APPLICABLE':
            errors.append('applicability flattened into truth')
    return sorted(set(errors))

def finish(out):
    graph=out['interpretation']
    errors=inspect_result(out)
    out['invariants']={name:not errors for name in INVARIANTS}
    graph['validation']={'structural_errors':errors,
                         'scope':'source retention and graph structure; no semantic attestation'}
    out.pop('_active_rule',None)
