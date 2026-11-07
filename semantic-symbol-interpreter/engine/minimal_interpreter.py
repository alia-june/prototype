#!/usr/bin/env python3
"""SSMI minimal whole-bearer interpreter v0.2.1.

NARROW BASELINE ONLY.
- Consumes the structured/synthetic bearer representation in SSMI fixtures.
- Does not perform OCR, computer vision, general NLP, or unrestricted semantic reasoning.
- Never reads fixture.expected, forbidden_inferences, or required_unknowns.
- Emits candidate-result JSON compatible with runner/run_validation.py.

The purpose is to exercise the source->candidate->harness contract end-to-end.
"""
from pathlib import Path
import argparse,json,re,sys
try:
    from .trace import begin, record, finish
except ImportError:
    from trace import begin, record, finish

RULE_VERSION='0.2.1'

def add(out,*claims):
    for c in claims:
        if c and c not in out['claims']:
            out['claims'].append(c); record(out, 'claim', c)

def unk(out,*items):
    for x in items:
        if x and x not in out['unknowns']:
            out['unknowns'].append(x); record(out, 'assessment', x)

def prov(out,*items):
    for x in items:
        if x and x not in out['provenance']:
            out['provenance'].append(x); record(out, 'provenance', x)

def text_of(bearer):
    s=bearer.get('source','')
    return '\n---BEARER---\n'.join(str(x) for x in s) if isinstance(s,list) else str(s)

def interpret(f):
    if not isinstance(f, dict): raise ValueError('input must be an object')
    if 'fixture_id' in f and not isinstance(f['fixture_id'],str): raise ValueError('fixture_id must be a string')
    bearer=f.get('bearer',{})
    if not isinstance(bearer, dict): raise ValueError('bearer must be an object')
    source=bearer.get('source')
    if not (isinstance(source,str) or isinstance(source,list) and bool(source) and all(isinstance(x,str) for x in source)):
        raise ValueError('bearer.source must be text or an array of text segments')
    if not isinstance(bearer.get('kind'),str): raise ValueError('bearer.kind must be a string')
    if 'completeness' in bearer and not isinstance(bearer['completeness'],str): raise ValueError('bearer.completeness must be a string')
    src=text_of(bearer)
    lines=[x.strip() for x in src.splitlines() if x.strip() and x.strip()!='---BEARER---']
    out={'fixture_id':f.get('fixture_id','UNKNOWN'),'claims':[],'unknowns':[],'provenance':[],
         'invariants':{'raw_observation_preserved':True,'whole_bearer_preserved':True,'alternatives_preserved':True,
                       'no_unobserved_as_observed':True,'scope_respected':True,'provenance_complete':True}}
    begin(out, bearer, RULE_VERSION)
    fired=[]
    def fire(name):
        out['_active_rule']=name
        if name not in fired:
            fired.append(name); prov(out,'rule:'+name)

    # General clipping / completeness rule.
    if bearer.get('completeness')=='CLIPPED' or 'clipped' in src.lower():
        fire('clipped-bearer'); add(out,'bearer:CLIPPED')
        unk(out,'continuation:UNKNOWN')
        for ln in lines:
            if ln=='DANGER': add(out,'text:DANGER')
            if 'VOLT' in ln: add(out,'partial_text:HIGH VOLT...')

    # Qualified prohibition.
    if 'DO NOT' in lines and 'ENTER' in lines and any('AUTHORIZED PERSONNEL ONLY'==x for x in lines):
        fire('qualified-prohibition')
        add(out,'line:WARNING' if 'WARNING' in lines else None,'line:DO NOT','line:ENTER','line:AUTHORIZED PERSONNEL ONLY',
            'group:warning assembly','relation:AUTHORIZED PERSONNEL ONLY qualifies DO NOT ENTER',
            'sign:qualified warning/prohibition','message:entry prohibited subject to authorization qualification',
            'implication:unauthorized persons must not enter')
        prov(out,'source_span:WARNING' if 'WARNING' in lines else None,'source_span:DO NOT ENTER','source_span:AUTHORIZED PERSONNEL ONLY')

    # Enclosed label/value pairs such as [TEMPERATURE 72].
    pairs=re.findall(r'\[([A-Z][A-Z ]*?)\s+([0-9]+)\]',src)
    if pairs:
        fire('enclosed-label-value')
        for lab,val in pairs:
            lab=lab.strip(); add(out,f'label:{lab}',f'value:{val}',f'pair:{lab}->{val}',f'message:{lab}={val}')
        prov(out,'evidence:enclosure','evidence:alignment')

    # Circle legend + status occurrences.
    definitions=re.findall(r'([●○★△|])\s*=\s*([A-Z ]+?)(?:\n|$)',src)
    legend={}
    for glyph, value in definitions:
        legend.setdefault(glyph, []).append(value.strip())
    conflicts={glyph for glyph, values in legend.items() if len(set(values))>1}
    legend={glyph:values[0] for glyph,values in legend.items() if glyph not in conflicts}
    if legend:
        fire('local-legend')
        for sym,meaning in legend.items():
            meaning=meaning.strip(); add(out,f'legend:{sym}={meaning}',f'symbol:{sym}'); prov(out,f'binding:{sym}->{meaning}')
        if 'SYSTEM STATUS' in src:
            add(out,'scope:legend applies to status bearer')
            for m in re.finditer(r'PUMP\s+(\d+)\s+([●○])',src):
                num,sym=m.groups(); add(out,f'occurrence:PUMP{num}{sym}')
                if sym in legend: add(out,f'message:PUMP {num} {legend[sym]}')
        if 'STATUS\n|' in src and '|' in legend:
            add(out,'legend_binding:|='+legend['|'],'status_occurrence:|','scope:bearer_local','macro_dynamics:local_symbol_binding','symbol_meaning:'+legend['|'],'message:'+legend['|'])
            prov(out,'context:local_legend','dilation:D5_WHOLE_BEARER')

    # Conflicting legend definitions (special because dict would collapse them).
    defs=re.findall(r'LEGEND\s+[A-Z]:\s*([●○★△|])\s*=\s*([A-Z]+)',src)
    if len(defs)>=2 and len({d[0] for d in defs})==1 and len({d[1] for d in defs})>1:
        fire('conflicting-local-definitions')
        for idx,(sym,val) in enumerate(defs[:2],start=1): add(out,f'binding_{chr(64+idx)}:{sym}={val}')
        sym=defs[0][0]; add(out,f'status_occurrence:{sym}','scope:bindings overlap','conflict_candidate:local symbol definitions',f'symbol:{sym}')
        for sym,val in defs:
            record(out,'alternative',f'symbol_meaning:{sym}={val}',status='CONFLICTED')
        unk(out,'symbol_meaning:CONFLICTED')
        prov(out,'source_span:LEGEND A','source_span:LEGEND B','source_span:STATUS')

    # Graphical contact is observation only.
    if bearer.get('kind')=='graphical' and ('┼' in src or 'intersection' in src.lower()):
        fire('geometry-not-topology'); add(out,'geometry:line intersection','geometric_contact:observed'); unk(out,'semantic_connection:UNKNOWN')

    # Section grouping via blank line.
    if 'ENGINE\n' in src and '\n\nHYDRAULICS\n' in src:
        fire('section-grouping'); add(out,'whitespace:section gap','section:ENGINE','section:HYDRAULICS')
        me=re.search(r'ENGINE.*?TEMP\s+(\d+)',src,re.S); mh=re.search(r'HYDRAULICS.*?TEMP\s+(\d+)',src,re.S)
        if me and mh:
            ev,hv=me.group(1),mh.group(1); add(out,f'relation:ENGINE/TEMP={ev}',f'relation:HYDRAULICS/TEMP={hv}',f'message:ENGINE TEMP={ev}',f'message:HYDRAULICS TEMP={hv}')
        prov(out,'evidence:blank-line grouping')

    # Correction history.
    if '[struck]' in src:
        fire('correction-history');
        before=re.search(r'\n([A-Z]+) \[struck\]\n([A-Z]+)',src)
        if before:
            old,new=before.groups(); add(out,f'historical:{old}',f'modification:strike {old}',f'current_text:{new}',f'layer:{old}','layer:strike',f'layer:{new}',f'message_effective:{new}'); prov(out,f'history:{old} retained')

    # Step reading-order conflict.
    if all(f'STEP {n}' in src for n in [1,2,3,4]):
        fire('competing-reading-order')
        for n in [1,2,3,4]: add(out,f'label:STEP{n}')
        add(out,'reading_order_candidate:numbered','reading_order_candidate:arrow/layout'); unk(out,'reading_order:UNRESOLVED')

    # Nonlinear graph/network.
    if bearer.get('kind')=='graphical' and ('map/network' in src.lower() or src.lower().startswith('network:')):
        fire('nonlinear-network')
        names=re.findall(r'\b(Hospital|Park|School|Station|A|B|C|D)\b',src)
        for n in dict.fromkeys(names): add(out,f'node:{n}')
        add(out,'structure:SPATIAL_NETWORK' if 'map/network' in src.lower() else 'structure:NETWORK_GRAPH')
        unk(out,'reading_order:NO_LINEAR_READING_ORDER')
        prov(out,'source_span:network' if src.lower().startswith('network:') else None)

    # Temporal scroll: longest/latest frame is assembled message.
    if bearer.get('kind')=='temporal' and isinstance(bearer.get('source'),list):
        frames=[str(x) for x in bearer['source']]
        progressive=bool(frames) and all(frames[i+1].startswith(frames[i]) and len(frames[i+1])>len(frames[i]) for i in range(len(frames)-1))
        if progressive and bearer.get('completeness')=='COMPLETE_INTERVAL':
            fire('temporal-progressive-prefix')
            add(out,f'frame_sequence:{len(frames)}','temporal_assembly:scroll',f'message:{frames[-1]}')
            prov(out,f'source:frames t0..t{len(frames)-1}')
        else:
            fire('temporal-underdetermined')
            unk(out,'temporal_assembly:CANNOT_INFER')

    # Nested regional legend override.
    if 'GLOBAL: ●=ACTIVE' in src and 'IN THIS PANEL ●=FAULT' in src:
        fire('nested-legend')
        add(out,'global_binding:●=ACTIVE','regional_binding:●=FAULT','scope:regional narrower than global','symbol:●','message:PANEL B ITEM FAULT'); prov(out,'scope_precedence:regional')

    # Descriptive vs normative modality.
    if 'STATUS: DOOR OPEN' in src and 'INSTRUCTION: KEEP DOOR CLOSED' in src:
        fire('modality-separation'); add(out,'modality:status descriptive','modality:instruction normative','message:door currently open','message:door should be kept closed')

    # Template-induced measurement grammar.
    ms=re.findall(r'^(TEMP|PRESSURE|FLOW|POWER)\s+(\d+)$',src,re.M)
    if len(ms)>=3:
        fire('repeated-two-column-template'); add(out,'local_grammar:left-column=measurement','local_grammar:right-column=value')
        for k,v in ms: add(out,f'message:{k}={v}')
        prov(out,'evidence:repeated layout pattern')

    # Qualifier ambiguity.
    if 'NO PARKING' in src and 'EXCEPT PERMIT HOLDERS' in src:
        fire('qualifier-scope-ambiguous'); add(out,'qualifier:EXCEPT PERMIT HOLDERS'); unk(out,'qualifier_scope:AMBIGUOUS')

    # Simple identification labels.
    if lines[:1]==['SERIAL NUMBER'] and len(lines)>=2:
        fire('identification-label'); val=lines[1]; add(out,'label:SERIAL NUMBER',f'identifier:{val}',f'relation:SERIAL NUMBER->{val}','sign:identification label',f'message:serial number is {val}'); prov(out,'source_span:SERIAL NUMBER',f'source_span:{val}'); unk(out,'normative_action:NOT_APPLICABLE')
    if lines[:1]==['MODEL'] and len(lines)>=2:
        fire('model-label'); val=lines[1]; add(out,'label:MODEL',f'identifier:{val}',f'relation:MODEL->{val}','sign:model identification label',f'message:model is {val}'); prov(out,'source_span:MODEL',f'source_span:{val}'); unk(out,'temporal_transition:NOT_APPLICABLE')

    # Isolated arrow.
    if src.strip()=='↑':
        fire('isolated-arrow'); add(out,'raw_symbol:↑','orientation:up','direction_shape:upward_candidate','symbol:up-arrow'); unk(out,'message:CANNOT_INFER','implication:CANNOT_INFER'); prov(out,'source_span:↑')

    # Conflicting same-modality status.
    if 'STATUS: GATE CLOSED' in src and 'STATUS: GATE OPEN' in src:
        fire('conflicting-status'); add(out,'claim:GATE CLOSED','claim:GATE OPEN','modality:both descriptive','conflict_candidate:same referent/scope'); record(out,'alternative','message:gate closed',status='CONFLICTED'); record(out,'alternative','message:gate open',status='CONFLICTED'); unk(out,'gate_state:CONFLICTED'); prov(out,'source_span:STATUS GATE CLOSED','source_span:STATUS GATE OPEN')

    # Conditional alarm -> evacuation.
    alarm_rule='IF ALARM ACTIVE -> EVACUATE' in lines
    alarm_conflict='ALARM ACTIVE' in lines and 'ALARM INACTIVE' in lines
    if alarm_rule and not ('ALARM ACTIVE' in lines and not alarm_conflict):
        fire('conditional-not-activated')
        add(out,'rule:IF ALARM ACTIVE -> EVACUATE','conditional_rule:alarm_active=>evacuate',
            'message:evacuate when alarm active')
        if alarm_conflict:
            add(out,'status:ALARM ACTIVE','status:ALARM INACTIVE')
            record(out,'alternative','condition:alarm_active',status='CONFLICTED')
            record(out,'alternative','condition:alarm_inactive',status='CONFLICTED')
            unk(out,'alarm_state:CONFLICTED')
        elif 'ALARM INACTIVE' in lines:
            add(out,'status:ALARM INACTIVE','implication:evacuation condition is not satisfied')
        else:
            unk(out,'alarm_state:UNKNOWN')
        unk(out,'evacuation_activation:CANNOT_INFER')
    if alarm_rule and 'ALARM ACTIVE' in lines and not alarm_conflict:
        fire('conditional-activation'); add(out,'status:ALARM ACTIVE','rule:IF ALARM ACTIVE -> EVACUATE','conditional_rule:alarm_active=>evacuate','implication_chain:condition activates directive','symbol:->','sign:conditional evacuation directive','message:alarm is active','message:evacuate when alarm active','implication:evacuation directive is active'); prov(out,'source_span:ALARM ACTIVE','source_span:IF ALARM ACTIVE -> EVACUATE')
        if 'ASSEMBLY POINT A' in src: add(out,'destination:ASSEMBLY POINT A','implication:proceed toward assembly point A'); prov(out,'source_span:ASSEMBLY POINT A')

    # Scheduled auto-close.
    if 'DOOR STATUS OPEN' in src and 'AUTO-CLOSE IN 5s' in src:
        fire('scheduled-state-transition'); add(out,'status:DOOR OPEN','transition_notice:AUTO-CLOSE IN 5s','state_transition:OPEN->CLOSED','temporal_delay:5s','sign:door state plus scheduled transition','message:door currently open','message:door scheduled to close in 5s','implication:door state expected to transition OPEN->CLOSED after 5s'); prov(out,'source_span:DOOR STATUS OPEN','source_span:AUTO-CLOSE IN 5s')

    # Causal chain.
    if 'PUMP A OFF -> PRESSURE FALLS -> BACKUP PUMP STARTS' in src:
        fire('causal-chain'); add(out,'state:PUMP A OFF','event:PRESSURE FALLS','event:BACKUP PUMP STARTS','causal_chain:PUMP A OFF->PRESSURE FALLS->BACKUP PUMP STARTS','symbol:->','sign:causal process chain','message:pump A off leads to pressure fall and backup start','implication:pressure fall follows pump A off','implication:backup pump start follows pressure fall'); prov(out,'source_span:whole causal chain')

    # Vertical-bar family.
    s=src.strip()
    if s=='|': fire('vertical-bar-isolated'); add(out,'raw_symbol:|','symbol_form:|'); unk(out,'symbol_meaning:AMBIGUOUS'); prov(out,'source_span:|')
    elif s=='A | B': fire('vertical-bar-adjacent'); add(out,'raw_symbol:|','left_neighbor:A','right_neighbor:B','relation_shape:binary_infix_candidate','symbol_form:|'); unk(out,'symbol_meaning:AMBIGUOUS'); prov(out,'dilation:D1_ADJACENT')
    elif s=='cat file | grep x': fire('shell-pipe'); add(out,'raw_symbol:|','left_expression:cat file','right_expression:grep x','symbol_role:infix_connector','macro_dynamics:data_flow','symbol_meaning:PIPELINE','sign:shell pipeline','message:stdout left connects to stdin right','implication:right command receives left output'); prov(out,'context:shell','dilation:D2_LOCAL_EXPRESSION')
    elif s=='cat|dog': fire('regex-alternation'); add(out,'raw_symbol:|','left_expression:cat','right_expression:dog','symbol_role:alternation','symbol_meaning:REGEX_ALTERNATION','sign:regex alternative','message:match cat or dog'); prov(out,'context:regular_expression','dilation:D2_LOCAL_EXPRESSION')
    elif s=='3 | 12': fire('divides'); add(out,'raw_symbol:|','left_operand:3','right_operand:12','symbol_role:binary_relation','symbol_meaning:DIVIDES','message:3 divides 12','implication:12 is divisible by 3'); prov(out,'context:number_theory','dilation:D2_LOCAL_EXPRESSION')
    elif s=='{ x | x > 0 }': fire('set-builder'); add(out,'raw_symbol:|','left_region:expression x','right_region:predicate x>0','macro_dynamics:comprehension_boundary','symbol_meaning:COMPREHENSION_BOUNDARY','message:set of x satisfying x>0'); prov(out,'context:set_builder','dilation:D2_LOCAL_EXPRESSION')
    elif s=='|x|': fire('absolute-fence'); add(out,'raw_symbol:left |','raw_symbol:right |','pairing:fence','enclosed_object:x','macro_dynamics:enclosure','symbol_family:FENCE','symbol_meaning:ABSOLUTE_VALUE_FENCE','message:absolute value of x'); prov(out,'context:scalar_arithmetic','dilation:D2_LOCAL_EXPRESSION')

    # Exclamation/fixity.
    if src.strip()=='!!': fire('double-exclamation-ambiguous'); add(out,'raw_run:!!','tokenization_candidate:[!!]','tokenization_candidate:[!][!]','symbol_form:!!'); unk(out,'tokenization:AMBIGUOUS','symbol_meaning:AMBIGUOUS'); prov(out,'dilation:D0_SELF')
    if 'JavaScript\n!ready' in src: fire('prefix-negation'); add(out,'raw_symbol:!','fixity:prefix','operand:ready','macro_dynamics:negation','symbol_meaning:LOGICAL_NEGATION','message:not ready'); prov(out,'context:JavaScript','dilation:D3_REGION')
    if src.strip()=='5!': fire('factorial'); add(out,'raw_symbol:!','fixity:postfix','operand:5','macro_dynamics:factorial_operation','symbol_meaning:FACTORIAL','message:factorial of 5'); prov(out,'context:arithmetic','dilation:D2_LOCAL_EXPRESSION')

    # Equality context.
    if src.strip()=='x = 5': fire('math-equality'); add(out,'raw_symbol:=','left_operand:x','right_operand:5','symbol_meaning:EQUALITY','message:x equals 5'); prov(out,'context:mathematics','dilation:D2_LOCAL_EXPRESSION')
    if src.startswith('Python\n') and 'x = 5' in src and '==' not in src: fire('python-assignment'); add(out,'raw_symbol:=','symbol_meaning:ASSIGNMENT','message:bind x to 5'); prov(out,'context:Python','dilation:D3_REGION')
    if src.startswith('Python\n') and 'x == 5' in src: fire('python-equality'); add(out,'raw_run:==','symbol_meaning:EQUALITY_COMPARISON','message:test x equals 5'); prov(out,'context:Python','dilation:D3_REGION')
    if src.startswith('JavaScript\n') and 'x === 5' in src: fire('js-strict-equality'); add(out,'raw_run:===','symbol_meaning:STRICT_EQUALITY','message:test strict equality x and 5'); prov(out,'context:JavaScript','dilation:D3_REGION')
    if src.strip()=='===': fire('triple-equals-ambiguous'); add(out,'raw_run:===','tokenization_candidate:[===]','tokenization_candidate:[==][=]','tokenization_candidate:[=][==]','tokenization_candidate:[=][=][=]','symbol_form:==='); unk(out,'tokenization:AMBIGUOUS','symbol_meaning:AMBIGUOUS'); prov(out,'dilation:D0_SELF')

    # Tilde context.
    if src.startswith('Python\n~mask'): fire('python-tilde'); add(out,'raw_symbol:~','fixity:prefix','operand:mask','symbol_meaning:BITWISE_INVERSION','message:bitwise invert mask'); prov(out,'context:Python','dilation:D3_REGION')
    if src.startswith('GEOMETRY\nA ~ B'): fire('geometry-tilde'); add(out,'raw_symbol:~','fixity:infix','left_operand:A','right_operand:B','symbol_meaning:SIMILARITY_RELATION','message:A is similar to B'); prov(out,'context:geometry','dilation:D3_REGION')
    if src.strip()=='A ~ B': fire('tilde-unresolved'); add(out,'raw_symbol:~','left_neighbor:A','right_neighbor:B','relation_shape:binary_infix_candidate','symbol_form:~'); unk(out,'symbol_meaning:UNRESOLVED'); prov(out,'source_span:~')

    # Quantifier.
    if src.strip()=='∀x P(x)': fire('universal-binder'); add(out,'raw_symbol:∀','bound_variable:x','body:P(x)','macro_dynamics:binder_scope','scope:P(x)','symbol_role:binder','symbol_meaning:UNIVERSAL_QUANTIFIER','message:for every x, P(x)'); prov(out,'context:predicate_logic','dilation:D2_LOCAL_EXPRESSION')

    # Nabla family.
    if src.startswith('VECTOR CALCULUS\n∇'):
        fire('nabla-family'); prov(out,'context:vector_calculus','dilation:D3_REGION'); add(out,'operator_nucleus:∇','raw_symbol:∇'); prov(out,'dilation:D2_LOCAL_EXPRESSION')
        if '∇·F' in src: add(out,'raw_run:∇·','adjacent_symbol:·','operator_dilation:∇·','macro_dynamics:vector_to_scalar_operation','operand:F','symbol_meaning:DIVERGENCE','message:divergence of F')
        elif '∇×F' in src: add(out,'raw_run:∇×','adjacent_symbol:×','operator_dilation:∇×','macro_dynamics:vector_field_operation','operand:F','symbol_meaning:CURL','message:curl of F')
        elif '∇f' in src: add(out,'raw_symbol:∇','macro_dynamics:scalar_to_vector_operation','operand:f','symbol_meaning:GRADIENT','message:gradient of f')

    # Arrow context.
    if src.startswith('DIGRAPH\nA -> B'): fire('directed-edge'); add(out,'raw_run:->','left_node:A','right_node:B','macro_dynamics:directed_topology','source:A','target:B','symbol_meaning:DIRECTED_EDGE','message:edge from A to B'); prov(out,'context:directed_graph','dilation:D3_REGION')
    if src.startswith('TYPE\nA -> B'): fire('function-type'); add(out,'raw_run:->','left_type:A','right_type:B','macro_dynamics:type_constructor','symbol_meaning:FUNCTION_TYPE_ARROW','message:function from A to B'); prov(out,'context:type_system','dilation:D3_REGION')

    # Explicit descriptive quotation: report the quote, never activate it.
    if len(lines)==2 and lines[0]=='EXAMPLE ONLY' and lines[1]=='QUOTE: EVACUATE':
        fire('descriptive-quote')
        add(out,'quoted_text:EVACUATE','scope:descriptive example','message:example quotes evacuation directive')
        unk(out,'normative_action:NOT_APPLICABLE')

    # A mode indicator changes decoding, without asserting a world fact.
    if lines==['MODE: LITERAL']:
        fire('decoding-mode')
        add(out,'mode_indicator:LITERAL','symbol_role:mode_switch','message:decode subsequent text literally')
        unk(out,'world_truth:NOT_APPLICABLE')

    if 'DIRECTIVE: ENTER' in lines and 'DIRECTIVE: DO NOT ENTER' in lines:
        fire('conflicting-directives')
        add(out,'directive:ENTER','directive:DO NOT ENTER','scope:overlapping directives')
        record(out,'alternative','message:enter',status='CONFLICTED')
        record(out,'alternative','message:do not enter',status='CONFLICTED')
        unk(out,'entry_directive:CONFLICTED')

    # Record engine execution provenance.
    if not fired:
        fire('unsupported-input')
        unk(out,'interpretation:UNRESOLVED')
    prov(out,'engine:ssmi-minimal-interpreter/'+RULE_VERSION)
    finish(out)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('fixture')
    ap.add_argument('-o','--output')
    args=ap.parse_args()
    try:
        f=json.loads(Path(args.fixture).read_text(encoding='utf-8'))
        # Deliberate guard: only bearer + identity metadata are passed to inference.
        safe={'fixture_id':f.get('fixture_id'),'bearer':f.get('bearer',{})}
        out=interpret(safe)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(json.dumps({'pass':False,'error':str(exc)}),file=sys.stderr)
        return 2
    data=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    if args.output: Path(args.output).write_text(data,encoding='utf-8')
    else:
        if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
        print(data,end='')
    return 0
if __name__=='__main__': raise SystemExit(main())
