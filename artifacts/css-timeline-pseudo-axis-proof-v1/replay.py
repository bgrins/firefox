import collections
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
import re
import os
from pathlib import Path
import subprocess
import sys

import cases
import extract
import native_model
import oracle
import mutants

BASE=Path(__file__).resolve().parent

def digest(data):return hashlib.sha256(data).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def command(args,out,env=None,input=None):
    with out.open('wb') as log:
        p=subprocess.run([str(x) for x in args],cwd=BASE,env=env,input=input,stdout=log,stderr=subprocess.STDOUT)
    assert p.returncode==0,(args,p.returncode,str(out))
    return dict(argv=[str(x) for x in args],status=p.returncode,output_sha256=digest(out.read_bytes()))

def validate(w,diagnostic=False):
    es={e[0]:e for e in w['elements']};fs={f[0]:f for f in w['frames']}
    assert 0 not in es and 0 not in fs and len(es)==len(w['elements']) and len(fs)==len(w['frames'])
    assert 0<=w['type']<=4 and 0<=w['axis']<=3 and 0<=w['pseudo']<=7
    assert w['host'] in es or w['type'] in [0,3] and w['host']==0
    assert w['root'] in es and w['scrolling'] in es and (not w['root_frame'] or w['root_frame'] in fs)
    for e in es.values():
        assert len(e)==14 and (not e[1] or e[1] in fs) and (not e[3] or e[3] in es)
        for k,p in enumerate(e[7:],1):
            assert not p or p in es and es[p][2]==k and es[p][3]==e[0]
    for f in fs.values():
        assert len(f)==15 and (not f[1] or f[1] in fs) and (not f[2] or f[2] in es)
        assert not f[4] or f[4] in fs and fs[f[4]][3]
        assert f[5] in [0,1] and f[14] in [0,1] and 0<=f[6]<=3
        assert all(-2147483647<=n<=2147483647 for n in f[7:9])
        assert all(0<=n<=2147483647 for n in f[9:11])
        seen=set();cur=f[0]
        while cur:
            assert cur not in seen,'cyclic frame ancestry'
            seen.add(cur);cur=fs[cur][1]
        assert len(seen)<=len(fs)
        if not diagnostic and f[3] and f[4]==f[0]:
            assert bool(f[6]&1)==bool(f[9]) and bool(f[6]&2)==bool(f[10])
            assert abs(f[7])<=f[9] and abs(f[8])<=f[10]
    for variant in ['original','candidate']:
        _,cache=oracle.observe(w,variant)
        if cache is not None:assert cache[1]>0

def lean_world(w,subscribers):
    out={a:w[b] for a,b in [('sourceType','type'),('host','host'),('pseudo','pseudo'),('axis','axis'),('root','root'),('scrolling','scrolling'),('rootFrame','root_frame')]}
    out.update(shell=bool(w['shell']),apz=bool(w['apz']),subscribers=subscribers)
    out['elements']=[dict(id=e[0],primary=e[1],kind=e[2],parent=e[3],isElement=bool(e[4]),apzDisabled=bool(e[5]),displayport=bool(e[6]),pseudos=e[7:]) for e in w['elements']]
    out['frames']=[dict(id=f[0],parent=f[1],content=f[2],scroll=bool(f[3]),target=f[4],vertical=bool(f[5]),availableX=bool(f[6]&1),availableY=bool(f[6]&2),x=f[7],y=f[8],width=f[9],height=f[10],overflowX=f[11],overflowY=f[12],shell=bool(f[13]),reversed=bool(f[14])) for f in w['frames']]
    out['document']={'raw':2000}
    for key in ['host','root','scrolling']:out[key]={'element':{'raw':out[key]}}
    out['rootFrame']={'frame':{'raw':out['rootFrame']}}
    for e in out['elements']:
        e['owner']={'raw':2000}
        for key in ['id','parent']:e[key]={'raw':e[key]}
        e['primary']={'frame':{'raw':e['primary']}}
        e['pseudos']=[{'element':{'raw':p}} for p in e['pseudos']]
    for f in out['frames']:
        for key in ['id','parent','content']:f[key]={'raw':f[key]}
        f['target']={'frame':{'raw':f['target']}}
    return out

def structural(row):return {k:v for k,v in row.items() if k not in ['duration','percent','fallback']}
def numeric(row,expected):
    for key in ['duration','percent','fallback']:
        a,b=row[key],expected[key]
        assert a==b,(key,a,b)
        if a is not None:
            assert math.isfinite(a)
            position,extent=row['cache'];scale=100 if key=='percent' else 100000
            rational=Fraction(abs(position)*scale,extent)
            error=abs(Fraction.from_float(a)-rational)
            assert error<=2*Fraction.from_float(math.ulp(a)),(key,a,rational,error)
            denominator=Fraction(abs(position),extent).denominator
            if denominator&(denominator-1)==0:assert error==0

def run(out,lean,cxx):
    out.mkdir(parents=True,exist_ok=True);out=out.resolve();lean=Path(lean).resolve();cxx=Path(cxx).absolute()
    sdk=Path(json.loads((BASE/'TOOLCHAINS-v1.json').read_text())['cxx']['sdk_settings']['path']).parent
    commands=[];corpus=cases.cases()
    for c in corpus:
        for w in c['worlds']:validate(w,c['label'].startswith('diagnostic-'))
    rejected=[]
    for name in ['cycle','null-required-target','inconsistent-pseudo','int-min','zero-selected-extent']:
        w=cases.base()
        if name=='cycle':cases.frame(w,1003)[1]=1004
        elif name=='null-required-target':w.update(type=1,host=0)
        elif name=='inconsistent-pseudo':cases.element(w,3)[3]=1
        elif name=='int-min':cases.frame(w,1007)[8]=-2147483648
        else:cases.frame(w,1007)[10]=0
        try:validate(w)
        except AssertionError as e:rejected.append(dict(label=name,world=w,rejected=True,reason=str(e)))
        else:raise AssertionError(('invalid record accepted',name))
    write_json(out/'rejected-inputs.json',rejected)
    write_json(out/'cases.json',corpus)
    raw=cases.encode(corpus).encode();(out/'input.txt').write_bytes(raw)
    (out/'lean-input.jsonl').write_text(''.join(json.dumps(dict(id=c['id'],worlds=[lean_world(w,c['subscribers']) for w in c['worlds']]))+'\n' for c in corpus))
    boundary=[]
    for path,signatures in [
        ('candidate/ScrollTimeline.cpp',['void ScrollTimeline::WillRefresh()','bool ScrollTimeline::UpdateIfStale()']),
        ('providers/dom/animation/AnimationTimelinesController.cpp',['void AnimationTimelinesController::AddScrollTimeline(','void AnimationTimelinesController::WillRefresh()','bool AnimationTimelinesController::UpdateStaleTimelines()']),
        ('providers/layout/style/TimelineManager.cpp',['struct TimelineBuilder<ScrollTimeline> {']),
        ('providers/dom/animation/ViewTimeline.cpp',['already_AddRefed<ViewTimeline> ViewTimeline::MakeNamed(','already_AddRefed<ViewTimeline> ViewTimeline::MakeAnonymous(','bool ViewTimeline::UpdateCachedCurrentTime()'])]:
        text=(BASE/'source'/path).read_text()
        for sig in signatures:
            body,pin=extract.definition(text,sig,semicolon=sig.startswith('struct '))
            pin.update(source=path,classification='retained external caller/impact boundary; not executed in capsule')
            boundary.append(pin)
    write_json(out/'external-boundary.json',boundary)
    expected_by_variant={}
    for variant in ['original','candidate']:
        code,binding=extract.build(variant);(out/f'{variant}.cpp').write_text(code);write_json(out/f'{variant}-bindings.json',binding)
        for pin in binding:
            data=(BASE/'source'/pin['source']).read_bytes()
            body=data[pin['byte_start']:pin['byte_end']]
            assert digest(body)==pin['sha256'] and code.count(body.decode())==1
        write_json(out/f'{variant}-adaptations.json',dict(semantic_edits=0,signature_edits=0,namespace_edits=0,access_edits=0,wrapper='extracted declarations nested in public adapter outer class; all inner access labels unchanged',source_restored=True))
        commands.append(command([cxx,'-isysroot',sdk,'-std=c++20','-O1','-g','-fsanitize=undefined','-fno-sanitize-recover=all','-Wall','-Wextra','-Werror',out/f'{variant}.cpp','-o',out/variant],out/f'{variant}-compile.log'))
        commands.append(command([out/variant],out/f'{variant}.jsonl',input=raw))
        actual=[json.loads(x) for x in (out/f'{variant}.jsonl').read_text().splitlines()]
        independent=[r for c in corpus for r in oracle.run(c,variant)]
        model=[r for c in corpus for r in native_model.run(c,variant)]
        assert len(actual)==len(independent)==len(model)
        for a,b,m in zip(actual,independent,model):
            assert a==m,('native/model',a,b,m)
            notifications=[e for e in a['trace'] if e[1] in [23,24]]
            assert notifications==b['notifications']
            assert {k:v for k,v in a.items() if k!='trace'}=={k:v for k,v in b.items() if k!='notifications'},('native/oracle',a,b)
            numeric(a,b)
        expected_by_variant[variant]=actual
    def preservation(w):
        snap,_=oracle.observe(w,'candidate')
        if not snap[3] or w['axis'] in [2,3]:return True
        source=oracle.selected(w);es={e[0]:e for e in w['elements']};fs={f[0]:f for f in w['frames']}
        return fs[oracle.resolve(w,source)][5]==fs[es[source[0]][1]][5]
    preservation_cases=[]
    for c in corpus:
        if all(preservation(w) for w in c['worlds']):
            original=[{k:v for k,v in row.items() if k!='trace'} for row in expected_by_variant['original'] if row['case']==c['id']]
            candidate_rows=[{k:v for k,v in row.items() if k!='trace'} for row in expected_by_variant['candidate'] if row['case']==c['id']]
            assert original==candidate_rows
            preservation_cases.append(c['id'])
    write_json(out/'preservation-cases.json',preservation_cases)
    env=dict(os.environ,LEAN_PATH=str(out))
    for module in ['Timeline','Typed','Trace','Runner','CorpusRunner','InvalidRunner']:
        commands.append(command([lean,'-o',out/f'{module}.olean',BASE/f'{module}.lean'],out/f'{module}-compile.log',env))
    invalid_typed=[]
    for i,label in enumerate(['wrong-owner','scroll-role-on-nonscroll-frame','root-role-on-nonscroll-frame','host-pseudo-alias','missing-primary-role']):
        w=lean_world(cases.base(),1)
        if i==0:w['elements'][1]['owner']['raw']=2999
        elif i==1:w['frames'][3]['target']['frame']['raw']=1008
        elif i==2:w['rootFrame']['frame']['raw']=1002
        elif i==3:w['elements'][1]['pseudos'][0]['element']['raw']=2
        else:w['elements'][1]['primary']['frame']['raw']=1999
        invalid_typed.append(dict(id=i,label=label,worlds=[w]))
    (out/'invalid-typed.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in invalid_typed))
    commands.append(command([lean,'--run',BASE/'InvalidRunner.lean',out/'invalid-typed.jsonl'],out/'invalid-typed.log',env))
    for variant in ['original','candidate']:
        commands.append(command([lean,'--run',BASE/'CorpusRunner.lean',out/'lean-input.jsonl',variant],out/f'{variant}-lean.jsonl',env))
        actual=[json.loads(x) for x in (out/f'{variant}-lean.jsonl').read_text().splitlines()]
        expected=[structural(x) for x in expected_by_variant[variant]]
        assert actual==expected,('Lean/native',variant,next(((a,b) for a,b in zip(actual,expected) if a!=b),None))
    mutant_receipts=[];lean_mutants=[];mutant_expected=[]
    candidate=(out/'candidate.cpp').read_text()
    for index,(name,_,_) in enumerate(mutants.MUTATIONS):
        code,change=mutants.mutate(candidate,index)
        stem=out/f'mutant-{index+1:02d}-{name}'
        stem.with_suffix('.cpp').write_text(code)
        commands.append(command([cxx,'-isysroot',sdk,'-std=c++20','-O1','-g','-fsanitize=undefined','-fno-sanitize-recover=all','-Wall','-Wextra','-Werror',stem.with_suffix('.cpp'),'-o',stem],stem.with_suffix('.compile.log')))
        candidates=corpus if index!=8 else [c for c in corpus if c['label']=='axis-replacement']
        if index==10:candidates=[next(c for c in corpus if c['label']=='host-change' and c['worlds'][0]['axis']==a) for a in [0,1]]
        commands.append(command([stem],stem.with_suffix('.jsonl'),input=cases.encode(candidates).encode()))
        actual=[json.loads(x) for x in stem.with_suffix('.jsonl').read_text().splitlines()]
        def projection(row):
            return dict(structural(row),trace=[e for e in row['trace'] if e[1] in [23,24]])
        baseline={(x['case'],x['sample']):projection(x) for x in expected_by_variant['candidate']}
        differences=[x for x in actual if projection(x)!=baseline[(x['case'],x['sample'])]]
        assert differences,('surviving mutant',name)
        witness=differences[0];c=next(c for c in corpus if c['id']==witness['case'])
        witness_actual=[projection(x) for x in actual if x['case']==c['id']]
        lean_mutants.append(dict(mutant=index,scenario=dict(id=c['id'],worlds=[lean_world(w,c['subscribers']) for w in c['worlds']])))
        mutant_expected.extend(witness_actual)
        control=next((x for x in actual if projection(x)==baseline[(x['case'],x['sample'])]),None)
        assert control is not None,('missing preservation control',name)
        receipt=dict(preservation_control=projection(control),mutation=change,compiled=True,executed=True,status=0,witness=c,actual=witness_actual,expected=[baseline[(c['id'],i)] for i in range(len(c['worlds']))],mismatches=len(differences),candidate_control='full unmutated corpus matched independent oracle')
        write_json(stem.with_suffix('.witness.json'),receipt);mutant_receipts.append(receipt)
        assert extract.build('candidate')[0]==candidate
        commands.append(command([out/'candidate'],stem.with_suffix('.clean.jsonl'),input=raw))
        assert stem.with_suffix('.clean.jsonl').read_bytes()==(out/'candidate.jsonl').read_bytes()
    (out/'mutant-input.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in lean_mutants))
    for module in ['Mutants','MutationRunner']:
        commands.append(command([lean,'-o',out/f'{module}.olean',BASE/f'{module}.lean'],out/f'{module}-compile.log',env))
    commands.append(command([lean,'--run',BASE/'MutationRunner.lean',out/'mutant-input.jsonl'],out/'mutant-lean.jsonl',env))
    lean_actual=[json.loads(x) for x in (out/'mutant-lean.jsonl').read_text().splitlines()]
    assert lean_actual==mutant_expected,('mutant Lean/native',next(((a,b) for a,b in zip(lean_actual,mutant_expected) if a!=b),None))
    theorem_names=[]
    for module,namespace in [('Timeline','Timeline'),('Typed','Timeline.Typed')]:
        text=(BASE/f'{module}.lean').read_text()
        assert not re.search(r'\b(sorry|admit|native_decide|unsafe)\b',text)
        assert not re.search(r'(?m)^\s*(axiom|opaque)\s',text)
        theorem_names.extend(namespace+'.'+x for x in re.findall(r'(?m)^theorem ([A-Za-z0-9_]+)',text))
    (out/'AxiomAudit.lean').write_text('import Timeline\nimport Typed\n'+''.join('#check '+n+'\n#print axioms '+n+'\n' for n in theorem_names))
    commands.append(command([lean,out/'AxiomAudit.lean'],out/'axioms.log',env))
    audit=(out/'axioms.log').read_text()
    for line in audit.splitlines():
        if 'depends on axioms:' in line:
            axioms=line.split('depends on axioms:',1)[1].strip().strip('[]').replace(',','').split()
            assert set(axioms)<=set(['propext','Classical.choice','Quot.sound']),(line,axioms)
    assert 'sorryAx' not in audit and audit.count('depends on axioms:')+audit.count('does not depend on any axioms')==len(theorem_names)
    write_json(out/'theorem-inventory.json',dict(names=theorem_names,count=len(theorem_names),allowed_foundations=['propext','Classical.choice','Quot.sound']))
    report=dict(scenarios=len(corpus),rows=sum(len(c['worlds']) for c in corpus),labels=dict(collections.Counter(c['label'] for c in corpus)),mutants=len(mutant_receipts),theorems=len(theorem_names),preservation_scenarios=len(preservation_cases),commands=commands)
    write_json(out/'RESULT.json',report)
    return report

if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1]),sys.argv[2],sys.argv[3]),indent=2))
