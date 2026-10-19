import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import bridge
import corpus
import run

BASE=Path(__file__).resolve().parent


def replace_once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def definitions():
    f=corpus.face;c=corpus.case
    return [
      ('restore-fourteen',c('restore-fourteen',[f(3584),f(2560)]),[0],[1]),
      ('positive-only',c('positive-only',[f(-3584),f(-2560)],target=-3072),[0],[1]),
      ('negative-only',c('negative-only',[f(3584),f(2560)]),[0],[1]),
      ('italic-fourteen',c('italic-fourteen',[f(3072),f(3584)],target=25600),[0],[1]),
      ('positive-strict',c('positive-strict',[f(3072),f(2560)],target=2816),[0],[1]),
      ('negative-strict',c('negative-strict',[f(-3072),f(-2560)],target=-2816),[0],[1]),
      ('default-eleven',c('default-eleven',[],operation=8),[3584,14],[2816,11]),
      ('remove-containment',c('remove-containment',[f(2560,3584),f(3328)]),[0],[1]),
      ('erase-italic-advantage',c('erase-italic-advantage',[f(25600),f(2816)],target=25600),[0],[1,0]),
      ('override-oblique-only',c('override-oblique-only',[f(256),f(3072)],target=25600,allow=0),[0],[1]),
    ]


def mutate_native(source,name):
    if name=='default-eleven':
        return replace_once(source,'StyleFontStyle::DEFAULT_OBLIQUE_DEGREES = 14;','StyleFontStyle::DEFAULT_OBLIQUE_DEGREES = 11;')
    old=bridge.block(source,'double StyleDistance(');body=old
    if name in ('restore-fourteen','positive-only','negative-only'):
        body=replace_once(body,'kObliqueSearchThreshold = 11.0','kObliqueSearchThreshold = 14.0')
        if name=='positive-only':body=replace_once(body,'targetAngle >= kObliqueSearchThreshold','targetAngle >= 11.0')
        if name=='negative-only':body=replace_once(body,'targetAngle <= -kObliqueSearchThreshold','targetAngle <= -11.0')
    elif name=='italic-fourteen':body=replace_once(body,'double targetAngle = kObliqueSearchThreshold;','double targetAngle = 14.0;')
    elif name=='positive-strict':body=replace_once(body,'targetAngle >= kObliqueSearchThreshold','targetAngle > kObliqueSearchThreshold')
    elif name=='negative-strict':body=replace_once(body,'targetAngle <= -kObliqueSearchThreshold','targetAngle < -kObliqueSearchThreshold')
    elif name=='remove-containment':
        needle='if (maxAngle >= targetAngle) {\n      return 0.0;\n    }'
        assert body.count(needle)==2
        body=body.replace(needle,'if (maxAngle >= targetAngle) {\n      return 100.0;\n    }')
    elif name=='erase-italic-advantage':body=replace_once(body,'return 0.0;  // styles match exactly ==> 0','return aTargetStyle.IsItalic() ? 1.0 : 0.0;  // semantic mutation')
    elif name=='override-oblique-only':body=replace_once(body,'targetAngle = 0.0;','targetAngle = kObliqueSearchThreshold;')
    else:raise ValueError(name)
    assert old!=body
    return replace_once(source,old,body)


def mutate_lean(source,name):
    if name=='default-eleven':return replace_once(source,'def defaultOblique : Int := 3584','def defaultOblique : Int := 2816')
    before,rest=source.split('def nativeDistance',1)
    model,after=rest.split('theorem positive_visit_bounds',1)
    if name=='restore-fourteen':
        model=model.replace('then threshold else 0','then 3584 else 0').replace('target ≥ threshold','target ≥ 3584').replace('target ≤ -threshold','target ≤ -3584')
    elif name=='positive-only':model=model.replace('then threshold else 0','then 3584 else 0').replace('target ≤ -threshold','target ≤ -3584')
    elif name=='negative-only':model=model.replace('then threshold else 0','then 3584 else 0').replace('target ≥ threshold','target ≥ 3584')
    elif name=='italic-fourteen':model=replace_once(model,'then threshold else 0','then 3584 else 0')
    elif name=='positive-strict':model=replace_once(model,'target ≥ threshold','target > threshold')
    elif name=='negative-strict':model=replace_once(model,'target ≤ -threshold','target < -threshold')
    elif name=='remove-containment':model=model.replace('else if hi ≥ target then 0','else if hi ≥ target then 25600')
    elif name=='erase-italic-advantage':model=replace_once(model,'if target = lo ∨ target = hi then 0','if target = lo ∨ target = hi then (if target = italicTag then 256 else 0)')
    elif name=='override-oblique-only':model=replace_once(model,'then threshold else 0','then threshold else threshold')
    else:raise ValueError(name)
    return before+'def nativeDistance'+model+'theorem positive_visit_bounds'+after


def lean_witness(source,c):
    defs=source.split('theorem positive_visit_bounds')[0]
    if c['operation']==8:body='#eval IO.println s!"{defaultOblique},{defaultOblique / scale}"\n'
    else:
        terms=[f'nativeDistance pivot ({f[0]}) ({f[1]}) ({c["target"]}) {"true" if c["allow"] else "false"}' for f in c['faces']]
        body='def scores : List Int := ['+', '.join(terms)+']\n'
        body+='def winners : List Nat := (List.range scores.length).filter (fun i => scores.all (fun s => scores[i]! ≤ s))\n'
        body+='#eval IO.println s!"{repr scores}|{repr winners}"\n'
    return defs+body+'\nend Threshold\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(BASE/'mutation-development'));args=parser.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
    native=bridge.generate('B',(BASE/'driver.cpp').read_text());lean=(BASE/'Threshold.lean').read_text()
    reference=run.compile_native(native,'reference',out,tc)
    receipts=[]
    for i,(name,c,expected,changed) in enumerate(definitions()):
        c['id']=i
        ref=run.execute(reference,[c],out,name+'-reference')[0]
        assert ref['selected']==expected,(name,'reference',ref['selected'],expected)
        mutated=mutate_native(native,name)
        binary=run.compile_native(mutated,name,out,tc)
        actual=run.execute(binary,[c],out,name+'-mutated')[0]
        assert actual['selected']==changed,(name,'mutant',actual['selected'],changed)
        assert actual['selected']!=ref['selected']
        mutated_lean=mutate_lean(lean,name)
        failure=out/(name+'-rejected.lean');failure.write_text(mutated_lean)
        r=subprocess.run([tc['lean'],str(failure)],text=True,capture_output=True,timeout=120)
        (out/(name+'-rejected.log')).write_text(r.stdout+r.stderr)
        assert r.returncode!=0 and 'error:' in r.stdout,(name,'theorem mutation unexpectedly passed')
        witnesses={}
        for suffix,src in [('reference',lean),('mutated',mutated_lean)]:
            p=out/(name+'-'+suffix+'.lean');p.write_text(lean_witness(src,c))
            result=subprocess.run([tc['lean'],str(p)],text=True,capture_output=True,timeout=60)
            (out/(name+'-'+suffix+'-lean.log')).write_text(result.stdout+result.stderr)
            assert result.returncode==0,(name,suffix,result.stdout)
            witnesses[suffix]=result.stdout
        assert witnesses['reference']!=witnesses['mutated'],name
        if c['operation']!=8:
            import re
            for suffix,want in [('reference',expected),('mutated',changed)]:
                match=re.search(r'\|\[(.*?)\]',witnesses[suffix]);assert match,(name,witnesses[suffix])
                got=[int(x) for x in match[1].split(',') if x.strip()]
                assert got==sorted(want),(name,suffix,got,want)
        else:
            assert witnesses['reference'].strip()=='3584,14'
            assert witnesses['mutated'].strip()=='2816,11'
        receipts.append(dict(name=name,input=c,expected_reference=expected,expected_mutation=changed,native_reference=ref,native_mutation=actual,native_reference_exit=0,native_mutation_exit=0,lean_theorem_exit=r.returncode,lean_witnesses=witnesses,lean_witness_exits=[0,0],mutated_native_sha256=hashlib.sha256(mutated.encode()).hexdigest()))
        print(name,'PASS',flush=True)
    (out/'MUTATIONS-v1.json').write_text(json.dumps(dict(status='PASS',mutants=receipts),indent=2)+'\n')

if __name__=='__main__':main()
