import json
import struct
from fractions import Fraction as Q
from pathlib import Path
import oracle
import mutants
import domain

def load_rows(path):return [json.loads(x) for x in path.read_text().splitlines()]
def exact_bits(value):return Q(struct.unpack('f',struct.pack('I',value))[0])
def preparation(events):
    result=[]
    for e in events:
        inputs=[]
        if e['event']=='ROOT':inputs=[(e['doc']*10000+e['element'],e['zoom'],e['size'],e['form'],e['value'])]
        elif e['event']=='READ':
            if e['role'] not in (0,3):inputs.append((e['owner'],e['zoom'],e['size'],e['form'],e['value']))
            inputs += [(e['parentOwner'],e['parentZoom'],e['parentSize'],e['parentForm'],e['parentValue']),(10000,1,e['initialSize'],e['initialForm'],e['initialValue'])]
        traces=[]
        for owner,z,size,form,value in inputs:
            if form!=3:continue
            size=oracle.mul(size,z)
            traces.append([[2,owner,0,0],[1,owner,oracle.bits(size),0],[31,0,oracle.bits(size),oracle.bits(value)]])
        result.append({'preparation':traces})
    return result

def run(native,lean):
    events=json.loads((native/'events.json').read_text());sem=oracle.semantic_expectations(events)
    admission=domain.admit(events);ids={x['id'] for x in admission}
    variants=[('original','original',0),('candidate','candidate',0)]+[(n,'candidate',i) for i,n in mutants.NAMES.items()]
    allrows={};summary={};witnesses={};prep=preparation(events)
    for name,variant,m in variants:
        actual=load_rows(native/name/'raw.jsonl');expected=oracle.observe(events,variant,m)
        assert len(actual)==len(expected)
        for i,(a,b) in enumerate(zip(actual,expected)):assert a==b,(name,i,a,b)
        setup=load_rows(native/name/'stderr.txt')
        assert setup==prep,(name,'preparation mismatch')
        indexed={a['id']:a for a in actual if a['event']=='read'};allrows[name]=indexed
        model=[line.split() for line in (lean/(name+'.txt')).read_text().splitlines()]
        assert {int(x[0]) for x in model}==ids
        for row in model:
            ident=int(row[0]);raw=indexed[ident]
            observed,exposed,cache=map(Q,(row[1],row[2],row[5]))
            assert observed==exact_bits(raw['scaled_bits']),(name,ident,'scaled')
            assert exposed==exact_bits(raw['exposed_bits']),(name,ident,'exposed')
            assert cache==exact_bits(raw['cache_bits']),(name,ident,'cache')
            assert (row[7]=='true')==raw['used'],(name,ident,'usage')
            assert Q(row[8])==sem[ident],(name,ident,'independent semantic result')
            trace=raw['trace'];cachetrace=[x for x in trace if x[0]==40]
            provider=[x for x in trace if x[0]==20]
            if cachetrace:kind,owner=3,cachetrace[-1][1]
            else:
                owner=provider[-1][1]
                kind=2 if owner==10000 else 0 if owner==raw['owner'] else 1
            assert (int(row[3]),int(row[4]))==(kind,owner),(name,ident,'source identity')
            assert (row[6]=='true')==bool(cachetrace),(name,ident,'cache mark')
        bad=[i for i in ids if exact_bits(indexed[i]['exposed_bits'])!=sem[i]]
        if name=='candidate':assert not bad
        elif name!='original':assert bad,(name,'no semantic mutant witness')
        witnesses[name]=[dict(id=i,expected=str(sem[i]),actual=str(exact_bits(indexed[i]['exposed_bits'])),raw=indexed[i]) for i in bad[:3]]
        summary[name]={'events':len(actual),'reads':len(indexed),'leanRows':len(model),'semanticDifferences':len(bad),'fullTraceOracle':True,'preparationOracle':True}
    controls=[e['id'] for e in events if e['event']=='READ' and (e['unit']!=0 or e['role'] not in (0,3))]
    for ident in controls:assert allrows['original'][ident]==allrows['candidate'][ident],('preservation',ident)
    result=dict(variants=summary,preservation=len(controls),exactAdmitted=len(ids),rejectedDomains=domain.rejected_domains(),mutantWitnesses=witnesses)
    return result
if __name__=='__main__':
    import sys
    result=run(Path(sys.argv[1]),Path(sys.argv[2]));print(json.dumps(result,indent=2))
