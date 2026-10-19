import argparse
import tempfile
import shutil
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

BASE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def run(args,log,*,stdin=None,env=None,allow_failure=False,timeout=180):
    with Path(log).open('w') as stream:
        result=subprocess.run(list(map(str,args)),input=stdin,text=True,stdout=stream,
            stderr=subprocess.STDOUT,env=env,timeout=timeout)
    if not allow_failure and result.returncode:
        raise RuntimeError(f'exit {result.returncode}: {log}')
    return result.returncode


def read_rows(path):
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    assert len({r['id'] for r in rows})==len(rows)
    return {r['id']:r for r in rows}


def validate(rows):
    assert [c['id'] for c in rows]==list(range(len(rows)))
    for c in rows:
        if not c['mode']:
            assert all(__import__('math').isfinite(oracle.unbits(n)) for n in c['bits'])
            continue
        assert 0<=c['begin']<=c['end']<=len(c['tokens'])<=1000
        assert all(-1<=a<=1000000 for a in c['tokens'])
        assert c['split']==-1 or c['begin']<=c['split']<=c['end']
        if c['domain']=='saturation':
            boundaries.validate_saturation(c)
        else:
            assert abs(c['initial'])+sum(max(0,a) for a in c['tokens'])+10000<2**30-1
        if c['domain']=='negative-intrinsic':boundaries.validate_negative(c)
        if c['mode'] in [6,7,8]:assert c['width']>0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    pins=json.loads((BASE/'REPLAY-INPUTS-v1.json').read_text())
    for name,digest in pins.items():assert sha(BASE/name)==digest,name
    sys.path.insert(0,str(BASE))
    global cases, extract, lean_mutations, mutations, oracle, boundaries
    import cases
    import extract
    import lean_mutations
    import mutations
    import oracle
    import boundaries
    write(out/'INPUT-PINS.json',pins)
    tools=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
    assert sha(tools['compiler'])==tools['compiler_sha256']
    assert str(Path(tools['compiler']).resolve())==tools['compiler_realpath']
    assert sha(Path(tools['sdk'])/'SDKSettings.json')==tools['sdk_settings_sha256']
    assert sha(tools['lean'])==tools['lean_sha256']
    assert sha(sys.executable)==tools['python_sha256']
    original=(BASE/'source/original.cpp').read_text();candidate=(BASE/'source/candidate.cpp').read_text()
    signature='static gfxFloat AdvanceToNextTab(gfxFloat aX, gfxFloat aTabWidth,\n                                 gfxFloat aMinAdvance) {\n'
    guard='  if (aTabWidth == 0.0) {\n    return aX;\n  }\n'
    assert candidate==original.replace(signature,signature+guard) and original.count(signature)==1
    assert 'typedef double gfxFloat;' in (BASE/'source/gfxTypes.h').read_text()
    coord=(BASE/'source/nsCoord.h').read_text()
    for declaration in ['using nscoord = int32_t;','inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;',
                        'inline constexpr nscoord nscoord_MIN = -nscoord_MAX;']:
        assert declaration in coord and declaration in (BASE/'adapter.cpp').read_text()
    rows=cases.cases();validate(rows);encoded=cases.encode(rows)
    (out/'inputs.txt').write_text(encoded);write(out/'cases.json',rows)
    expected={v:{c['id']:oracle.run(c,v=='candidate') for c in rows} for v in ['original','candidate']}
    write(out/'expected.json',expected)
    actual={};mutation_receipts={};bindings={}
    for name in ['original','candidate']+mutations.NATIVE:
        version=name if name in expected else 'candidate'
        code,binding=extract.capsule(version,None if name in expected else mutations.native_mutation(name))
        bindings[name]=binding
        if name in expected:
            for entry in binding:
                body=(BASE/entry['source']).read_text()[entry['start']:entry['end']]
                assert hashlib.sha256(body.encode()).hexdigest()==entry['sha256']
                assert code.count(body)==1,entry['signature']
        source=out/(name+'.cpp');source.write_text(code)
        flags=['-std=c++17','-O1','-g','-isysroot',tools['sdk'],'-fsanitize=undefined,float-cast-overflow',
               '-fno-sanitize-recover=all','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wdangling']
        run([tools['compiler'],*flags,source,'-o',out/name],out/(name+'-compile.log'))
        run([out/name],out/(name+'.jsonl'),stdin=encoded,timeout=30)
        got=read_rows(out/(name+'.jsonl'));assert got.keys()==expected['candidate'].keys()
        actual[name]=got
        if name in expected:
            bad=[i for i in got if got[i]!=expected[name][i]]
            write(out/(name+'-mismatches.json'),bad);assert not bad,(name,bad[:5])
        else:
            changed=[i for i in got if got[i]!=expected['candidate'][i]];assert changed,name
            mutation_receipts[name]=dict(compile_exit=0,run_exit=0,full_corpus=len(rows),changed=len(changed),
                 witness_id=changed[0],expected=expected['candidate'][changed[0]],mutant=got[changed[0]])
        print(name,'PASS',flush=True)
    write(out/'binding.json',bindings)
    source=(BASE/'Tab.lean').read_text()
    for filename in ['Tab.lean','Bridge.lean','Main.lean']:
        assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',(BASE/filename).read_text())
    names=re.findall(r'\btheorem\s+(\w+)',source+(BASE/'Bridge.lean').read_text());assert len(names)==len(set(names))
    env={**os.environ,'LEAN_PATH':str(out)}
    run([tools['lean'],'-o',out/'Tab.olean',BASE/'Tab.lean'],out/'lean-model.log',env=env)
    run([tools['lean'],'-o',out/'Bridge.olean',BASE/'Bridge.lean'],out/'lean-bridge.log',env=env)
    audit=out/'Audit.lean';audit.write_text('import Bridge\n'+'\n'.join('#print axioms Tab.'+n for n in names)+'\n')
    run([tools['lean'],audit],out/'axioms.log',env=env)
    audittext=(out/'axioms.log').read_text();assert audittext.count("'Tab.")==len(names) and 'sorryAx' not in audittext
    for axioms in re.findall(r'depends on axioms: \[(.*?)\]',audittext):
        assert set(axioms.split(', '))<={'propext','Classical.choice','Quot.sound'}
    lean_rows=[c for c in rows if c['mode'] and c['kind']==0 and c['letter']==0 and c['flags']==0 and c['domain']!='saturation']
    lean_input=cases.encode(lean_rows);(out/'lean-inputs.txt').write_text(lean_input)
    for name in ['original','candidate']:
        run([tools['lean'],'--run',BASE/'Main.lean',name],out/('lean-'+name+'.jsonl'),stdin=lean_input,env=env)
        got=read_rows(out/('lean-'+name+'.jsonl'));assert got.keys()=={c['id'] for c in lean_rows}
        bad=[i for i in got if got[i]!=actual[name][i]]
        write(out/('lean-'+name+'-mismatches.json'),bad);assert not bad,(name,bad[:5])
    lean_receipt=lean_mutations.check(BASE,out,tools['lean'],run)
    diagnostics={}
    for name,changed_source,sig in [
        ('missing-body',candidate.replace(signature,'static gfxFloat RenamedTab('),signature),
        ('duplicate-body',candidate+'\n'+extract.complete(candidate,signature)[0],signature)]:
        try:extract.complete(changed_source,sig)
        except AssertionError:diagnostics[name]='REJECTED'
        else:raise AssertionError(name)
    bad=[dict(c) for c in rows];bad[-1]['end']=1001
    try:validate(bad)
    except AssertionError:diagnostics['invalid-range']='REJECTED'
    else:raise AssertionError('invalid range')
    with tempfile.TemporaryDirectory(prefix='tab-auth-') as tmp:
        corrupt=Path(tmp)
        for name in [*pins,'check.py','REPLAY-INPUTS-v1.json']:
            target=corrupt/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(BASE/name,target)
        marker=corrupt/'IMPORT-SIDE-EFFECT'
        helper=corrupt/'cases.py'
        helper.write_text("from pathlib import Path\nPath("+repr(str(marker))+").write_text('executed')\n"+helper.read_text())
        exitcode=run([sys.executable,corrupt/'check.py','--out',corrupt/'output'],
            out/'corrupt-import.log',allow_failure=True)
        assert exitcode!=0 and not marker.exists()
        assert 'AssertionError: cases.py' in (out/'corrupt-import.log').read_text()
        diagnostics['corrupt-helper-before-import']='REJECTED_WITHOUT_SIDE_EFFECT'
    badpins=dict(pins);key=next(iter(badpins));badpins[key]='0'*64
    assert sha(BASE/key)!=badpins[key];diagnostics['corrupt-pin']='REJECTED'
    for name,digest in pins.items():assert sha(BASE/name)==digest,name
    differences=[i for i in actual['candidate'] if actual['candidate'][i]!=actual['original'][i]]
    nonzero_ids=[c['id'] for c in rows if (oracle.unbits(c['bits'][1])!=0 if c['mode']==0 else c['width']!=0)]
    assert all(actual['candidate'][i]==actual['original'][i] for i in nonzero_ids)
    boundary_receipt=boundaries.check_results(rows,actual)
    write(out/'BOUNDARIES.json',boundary_receipt)
    receipt=dict(status='PASS',cases_per_native_variant=len(rows),native_variants=2+len(mutations.NATIVE),
        exact_extractions=len(bindings['candidate']),native_mutations=mutation_receipts,
        boundary_controls=boundary_receipt,
        lean_cases_per_variant=len(lean_rows),lean_variants=2,theorems=names,
        lean_mutations=lean_receipt,diagnostics=diagnostics,original_candidate_differences=len(differences),
        unchanged_nonzero_cases=len(nonzero_ids),provider_assumptions=True,universal_cpp_refinement=False,
        ieee_formal_proof=False,asan_executed=False,compiler_flags=flags,source_pins=len(pins))
    write(out/'SUMMARY.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if not isinstance(v,(dict,list))}),flush=True)


if __name__=='__main__':main()
