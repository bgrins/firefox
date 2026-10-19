import argparse
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args=parser.parse_args()
manifest=json.loads((ROOT/'INPUTS.json').read_text())
import collections
import concurrent.futures
import math
import re
import statistics
import subprocess
import time

from generate import generate
from corpus import corpus,encode,reset,setter,frame,prop
from oracle import Oracle
from mutations import MUTATIONS
from tamper import run_tamper_controls
from readiness import check_readiness
out=pathlib.Path(args.output).resolve()
assert not out.exists(), 'Replay output must be fresh'
out.mkdir(parents=True)

def save(name,value):
    path=out/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def same(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(a,b,rel_tol=2e-14,abs_tol=2e-14)
    if type(a)!=type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b

started=time.monotonic()
tamper_results=run_tamper_controls(ROOT,out/'tamper')
print('Exact-closure tamper controls passed',len(tamper_results),flush=True)
tools=json.loads((ROOT/'TOOLCHAIN.json').read_text())
for path,key in [(tools['lean'],'lean_sha256'),(tools['compiler'],'compiler_sha256'),(tools['sdk']+'/SDKSettings.json','sdk_settings_sha256')]:assert sha(pathlib.Path(path))==tools[key],path
source=(ROOT/'Composite.lean').read_text()+'\n'+(ROOT/'Witnesses.lean').read_text()
assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',source)
theorems=re.findall(r'^theorem\s+(\w+)',source,re.M)
assert len(theorems)==len(set(theorems))
source+='\n'+'\n'.join('#print axioms Composite.'+name for name in theorems)+'\n'
(out/'All.lean').write_text(source)
lean=subprocess.run([tools['lean'],str(out/'All.lean')],capture_output=True,text=True)
(out/'lean.log').write_text(lean.stdout+lean.stderr)
assert lean.returncode==0,(lean.returncode,lean.stdout,lean.stderr)
assert not re.search(r'sorryAx|ofReduceBool|native_decide|error:',lean.stdout+lean.stderr)
assert all("'Composite."+name+"'" in lean.stdout for name in theorems)
allowed={'propext','Classical.choice','Quot.sound'}
for group in re.findall(r'depends on axioms: \[([^]]*)\]',lean.stdout):assert set(filter(None,(x.strip() for x in group.split(','))))<=allowed,group
save('LEAN.json',dict(exit=0,theorems=theorems,axioms_allowed=sorted(allowed),semantic_mutation_witnesses=[n for n in theorems if n.startswith('mutant_')]))
print('Lean kernel checks passed',len(theorems),flush=True)

cases=corpus()
retained=json.loads((ROOT/'evidence/v2-independent/PRODUCER-CORPUS.json').read_text())
assert len(retained)==691 and cases[:len(retained)]==retained
actions=[a for c in cases for a in c['actions']]
data='\n'.join(map(encode,actions))+'\n'
(out/'input.txt').write_text(data);save('CORPUS.json',cases)
oracle=Oracle();expected=[oracle.apply(a) for a in actions]
(out/'expected.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in expected)+'\n')

def compile_variant(name,variant='candidate',mutation=None,old_null_provider=False):
    src,records=generate(variant,mutation)
    if old_null_provider:
        old='if(p.mServoDeclarationBlock)item.mValue.value.emplace(p.mServoDeclarationBlock->value*style->scale);'
        assert src.count(old)==1
        src=src.replace(old,'item.mValue.value.emplace(p.mServoDeclarationBlock ? p.mServoDeclarationBlock->value*style->scale : style->base);')
    path=out/'native'/(name+'.cpp');path.parent.mkdir(exist_ok=True);path.write_text(src)
    save('native/'+name+'-extraction.json',records)
    executable=out/'native'/name
    command=[tools['compiler'],'-std=c++20','-O1','-isysroot',tools['sdk'],str(path),'-o',str(executable)]
    run=subprocess.run(command,capture_output=True,text=True)
    (out/'native'/(name+'-compile.log')).write_text(run.stdout+run.stderr)
    assert run.returncode==0,(name,run.stderr)
    return executable,records

variants={}
for name in ['original','candidate']:
    executable,records=compile_variant(name,name)
    run=subprocess.run([str(executable)],input=data,capture_output=True,text=True)
    (out/'native'/(name+'-output.jsonl')).write_text(run.stdout)
    assert run.returncode==0,(name,run.returncode,run.stderr)
    rows=[json.loads(s) for s in run.stdout.splitlines()]
    assert len(rows)==len(expected)
    differences=[i for i,(a,b) in enumerate(zip(rows,expected)) if not same(a,b)]
    variants[name]=dict(rows=rows,records=records,differences=differences)
assert not variants['candidate']['differences'],variants['candidate']['differences'][:10]
assert variants['original']['differences']
changed=[a['marker'] for a,b in zip(variants['original']['records'],variants['candidate']['records']) if a['sha256']!=b['sha256']]
assert changed==['static bool KeyframesEqualIgnoringComputedOffsets('],changed
save('NATIVE.json',dict(cases=len(cases),action_rows=len(actions),operation_counts=dict(collections.Counter(a['op'] for a in actions)),extracted_definitions=len(variants['candidate']['records']),changed_extractions=changed,candidate_disagreements=0,original_disagreements=variants['original']['differences'],float_comparison=dict(relative=2e-14,absolute=2e-14),signed_zero_flags_compared_exactly=True))
print('Complete native core passed',len(cases),len(actions),flush=True)

readiness=check_readiness(cases,variants['candidate']['rows'],same)
save('DELIVERED-READINESS.json',readiness)
print('Raw-provider/native-dispatch readiness checks passed',json.dumps(readiness['counts'],sort_keys=True),flush=True)
v2_manifest=json.loads((ROOT/'V2-INPUTS.json').read_text())
retained_names=['generate.py','extract.py','mutations.py','adapter-prefix.cpp','adapter-middle.cpp','adapter-main.cpp','oracle.py','SCOPE.md','SCOPE-ADDENDUM-v1.md']
v2_unchanged=[row for row in v2_manifest['inputs'] if row['path'] in retained_names or row['path'].split('/')[0] in ['sources','original','candidate']]
assert all(sha(ROOT/row['path'])==row['sha256'] for row in v2_unchanged)
save('V2-PRESERVATION.json',dict(unchanged_inputs=v2_unchanged,retained_cases=len(retained),added_cases=len(cases)-len(retained),retained_action_rows=sum(len(c['actions']) for c in retained),all_original_mutations_retained=True))

source_rows=[row for row in json.loads((ROOT/'V1-INPUTS.json').read_text())['inputs'] if row['path'].split('/')[0] in ['sources','original','candidate']]
assert all(sha(ROOT/row['path'])==row['sha256'] for row in source_rows)
save('V1-SOURCE-DELTA.json',dict(unchanged_full_source_files=len(source_rows),rows=source_rows,extracted_definitions=len(variants['candidate']['records']),statement='All original full native/provider snapshots are byte-identical to v1; adapters, oracle, model, corpus and authentication are corrected.'))
controls=[];start=0
for case in cases:
    stop=start+len(case['actions']);rows=variants['candidate']['rows'][start:stop]
    if case['name'].startswith('pending-cache-'):
        before=rows[2]
        for at in [3,4,5]:
            assert rows[at]['properties']==before['properties'] and rows[at]['base']==before['base']
            assert 'update' not in rows[at]['trace']
        assert rows[3]['trace']==[] and rows[8]['trace']==[]
        assert rows[9]['trace'].count('update')==1
        controls.append(dict(name=case['name'],start=start,rows=rows,claim='Explicit invalidation and equal setter/getter retain caches before actual default/style delivery.'))
    if case['name']=='pending-offset-missing-timeline':
        assert 'refresh' not in rows[2]['trace'] and 'update' not in rows[2]['trace']
        assert rows[3]['frames']==rows[1]['frames'] and 'compute' not in rows[3]['trace']
        assert rows[5]['frames']!=rows[1]['frames'] and rows[5]['trace'].count('update')==1
        controls.append(dict(name=case['name'],start=start,rows=rows,claim='Missing timeline retains pending derived state; equal setter here is outside valid-offset refinement admission; delivered context restores.'))
    if case['name'].startswith('null-existing-and-missing-'):
        assert all(segment[2] is None and segment[3] is None for property in rows[1]['properties'] for segment in property[3])
        assert rows[1]['properties']==rows[3]['properties'] and rows[1]['base']!=rows[3]['base']
        assert 'effect-set' not in rows[3]['trace'] and rows[3]['trace'].count('restyle')==1
        assert rows[5]['properties']==[]
        controls.append(dict(name=case['name'],start=start,rows=rows,claim='Existing raw null is retained; real base-only update and getter fallback differ from absent property/missing endpoint.'))
    start=stop
save('CACHE-NULL-CONTROLS.json',dict(controls=controls,count=len(controls),exact_numeric_disagreement_rows=sum(a!=b for a,b in zip(variants['candidate']['rows'],expected)),tolerant_disagreement_rows=0))
executable,_=compile_variant('old-null-provider',old_null_provider=True)
run=subprocess.run([str(executable)],input=data,capture_output=True,text=True)
(out/'native/old-null-provider-output.jsonl').write_text(run.stdout)
assert run.returncode==0,run.stderr
rows=[json.loads(row) for row in run.stdout.splitlines()]
assert len(rows)==len(expected)
differences=[i for i,(a,b) in enumerate(zip(rows,expected)) if not same(a,b)]
assert differences
first=differences[0]
save('NULL-PROVIDER-REGRESSION.json',dict(compile_exit=0,run_exit=0,disagreements=len(differences),first=first,action=actions[first],actual=rows[first],expected=expected[first],kernel_witness='null_is_not_base_value',scope='Adapter regression witness, additional to the 20 native-body semantic mutations.'))

def check_mutation(pair):
    name,mutation=pair
    executable,_=compile_variant(name,mutation=mutation)
    subset=actions[:2] if name=='skip-recompute' else actions
    run=subprocess.run([str(executable)],input='\n'.join(map(encode,subset))+'\n',capture_output=True,text=True)
    (out/'native'/(name+'-output.jsonl')).write_text(run.stdout)
    assert run.returncode==0,(name,run.returncode,run.stderr)
    rows=[json.loads(s) for s in run.stdout.splitlines()]
    assert len(rows)==len(subset)
    differences=[i for i,(a,b) in enumerate(zip(rows,expected)) if not same(a,b)]
    assert differences,name
    i=differences[0]
    if name=='suppress-base-restyle':
        assert actions[i]['op']=='STYLE'
        assert rows[i]['properties']==expected[i]['properties'] and rows[i]['base']==expected[i]['base']
        assert 'effect-set' not in expected[i]['trace'] and expected[i]['trace'].count('restyle')==1
        assert rows[i]['trace']==[event for event in expected[i]['trace'] if event!='restyle']
    if name=='omit-composite':assert rows==variants['original']['rows']
    result=dict(name=name,compile_exit=0,run_exit=0,rows=len(rows),disagreements=len(differences),first=i,action=actions[i],actual=rows[i],expected=expected[i])
    save('mutations/'+name+'.json',result)
    print('Semantic mutation:',name,len(differences),flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:mutations=list(pool.map(check_mutation,MUTATIONS.items()))
assert len(mutations)==len([t for t in theorems if t.startswith('mutant_')])==20
save('MUTATIONS.json',[{k:v for k,v in r.items() if k not in ('actual','expected','action')} for r in mutations])

cost=[]
for count in [1,2,16,128,1024]:
    frames=[frame([0,i/max(count-1,1)],properties=[prop(0,i,i+1)]) for i in range(count)]
    prefix=encode(reset())+'\n'+encode(setter(frames))+'\n'
    for changed in [0,1]:
        runs=[]
        repetitions=100 if changed else 1000
        for sample in range(5):
            run=subprocess.run([str(out/'native/candidate')],input=prefix+f'COST {repetitions} {changed}\n',capture_output=True,text=True)
            assert run.returncode==0,run.stderr
            row=json.loads(run.stdout.splitlines()[-1]);assert row['frames']==count and row['checksum']>0
            runs.append(row)
        assert len({r['checksum'] for r in runs})==1
        cost.append(dict(frames=count,changed=bool(changed),runs=runs,median_ns_per_setter=statistics.median(r['costNs']/repetitions for r in runs)))
save('COST.json',dict(scope='Candidate typed native core, parser boundary copies supplied records; includes declaration/segment/base provider adapters, tracing and input copies. Not browser rendering performance.',comparisons=len(cost),samples=sum(len(r['runs']) for r in cost),rows=cost))
result=dict(status='PASS',authenticated_inputs=len(manifest['inputs']),cases=len(cases),action_rows=len(actions),extracted_definitions=len(variants['candidate']['records']),lean_theorems=len(theorems),semantic_mutants=len(mutations),cost_samples=50,tamper_controls=len(tamper_results),readiness=readiness['counts'],elapsed_seconds=time.monotonic()-started)
save('RESULT.json',result)
receipts=[]
for path in sorted(out.rglob('*')):
    if path.is_file() and path.name!='RECEIPTS.json' and path.suffix not in ['.cpp'] and not (path.parent.name=='native' and not path.suffix):
        receipts.append(dict(path=str(path.relative_to(out)),sha256=sha(path),bytes=path.stat().st_size))
save('RECEIPTS.json',dict(files=receipts))
print(json.dumps(result,sort_keys=True),flush=True)
