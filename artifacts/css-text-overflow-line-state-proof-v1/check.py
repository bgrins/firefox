#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import cases
import extract
import generate_lean
import lean_mutations
import mutations
import oracle


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def command(argv,log,*,stdin=None,env=None,timeout=180):
    with log.open('w') as out:
        run=subprocess.run(list(map(str,argv)),input=stdin,text=True,stdout=out,
            stderr=subprocess.STDOUT,env=env,timeout=timeout)
    if run.returncode:
        raise RuntimeError(f'{argv[0]} exited {run.returncode}: {log}')
    return run.returncode


def parse_rows(path,lean=False):
    rows={}
    for line in path.read_text().splitlines():
        fields=line.split('\t')
        if lean:
            version,a,b,mode,events=fields;key=(version,int(a),int(b),mode)
        else:
            a,b,mode,events=fields;key=(int(a),int(b),mode)
        assert key not in rows
        rows[key]=json.loads(events)
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--native-only',action='store_true')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    replay_inputs=json.loads((BASE/'REPLAY-INPUTS-v1.json').read_text())
    for name,digest in replay_inputs.items():assert sha(BASE/name)==digest,name
    for source in ['LineModel.lean','LineTheorems.lean']:
        assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',(BASE/source).read_text())
    source_binding=json.loads((BASE/'NATIVE-BINDING-v1.json').read_text())
    for version in ['original','candidate']:
        assert extract.extract(version)[2]==source_binding['versions'][version]
    original=(BASE/'source/original/TextOverflow.cpp').read_text()
    candidate=(BASE/'source/candidate/TextOverflow.cpp').read_text()
    process,_,_=extract.complete(candidate,'void TextOverflow::ProcessLine(')
    reverted=process.replace('  mIStart.mISize = mIStart.mIntrinsicISize;\n','').replace('  mIEnd.mISize = mIEnd.mIntrinsicISize;\n','')
    assert candidate.replace(process,reverted)==original
    tools=json.loads((BASE/'TOOLCHAIN-v1.json').read_text())
    compiler=Path(tools['compiler']);sdk=Path(tools['sdk']);lean=Path(tools['lean'])
    assert sha(Path(sys.executable))==tools['python_sha256']
    assert str(compiler.resolve())==tools['compiler_realpath']
    assert sha(compiler)==tools['compiler_sha256']
    assert sha(sdk/'SDKSettings.json')==tools['sdk_settings_sha256']
    assert sha(lean)==tools['lean_sha256']
    inputs=cases.cases();encoded=cases.encode(inputs)
    write_json(out/'cases.json',inputs);(out/'input.txt').write_text(encoded)
    expected={name:{k:v for c in inputs for k,v in oracle.run(c,name=='candidate').items()}
        for name in ['original','candidate']}
    native={};bindings={};mutation_receipts={}
    names=['original','candidate']+mutations.NATIVE
    for name in names:
        variant=name if name in expected else 'candidate'
        mutation=None if name in expected else mutations.native_mutation(name)
        code,binding=extract.capsule(variant,mutation);bindings[name]=binding
        path=out/(name+'.cpp');path.write_text(code)
        argv=[compiler,'-std=c++17','-O1','-g','-fsanitize=undefined','-fno-sanitize-recover=all',
              '-Wall','-Wextra','-Werror','-Wdangling','-Wno-unused-function','-isysroot',sdk,path,'-o',out/name]
        command(argv,out/(name+'-compile.log'))
        command([out/name],out/(name+'.tsv'),stdin=encoded,timeout=30)
        rows=parse_rows(out/(name+'.tsv'));assert rows.keys()==expected['candidate'].keys()
        native[name]=rows
        if name in expected:
            assert rows==expected[name],name
        else:
            changed=[k for k in rows if rows[k]!=expected['candidate'][k]]
            assert changed,name
            mutation_receipts[name]={'selected_cases':len(inputs),'selected_rows':len(rows),
                'changed_rows':len(changed),'first_changed_key':changed[0],
                'first_expected':expected['candidate'][changed[0]],'first_mutant':rows[changed[0]],
                'compile_exit':0,'run_exit':0}
    ordinary_ids={c['id'] for c in inputs if c['domain']=='ordinary'}
    reuse={}
    for name in expected:
        pairs=[k for k in native[name] if k[0] in ordinary_ids and k[2]=='reuse']
        bad=[k for k in pairs if native[name][k][1:]!=native[name][(*k[:2],'fresh')][1:]]
        output=lambda events:[event for event in events if event[0] in [3,4]]
        output_bad=[k for k in pairs if output(native[name][k])!=output(native[name][(*k[:2],'fresh')])]
        post_bad=[k for k in pairs if native[name][k][-1]!=native[name][(*k[:2],'fresh')][-1]]
        pre_bad=[k for k in pairs if native[name][k][0]!=native[name][(*k[:2],'fresh')][0]]
        reuse[name]={'ordinary_lines':len(pairs),'different_lines':len(bad),'keys':bad,
          'different_output_lines':len(output_bad),'different_poststate_lines':len(post_bad),
          'different_preentry_debug_rows':len(pre_bad),
          'comparison':'All events after the pre-entry debug record; output-only and final-state counts reported separately. Clip/clip fast returns and clamp diagnostics excluded.'}
    assert reuse['candidate']['different_lines']==0
    assert reuse['original']['different_lines']>0
    receipt={'cases':len(inputs),'native_rows_per_variant':len(expected['candidate']),
             'native_variants':len(names),'native_oracle_exact':True,
             'replay_inputs_sha256':sha(BASE/'REPLAY-INPUTS-v1.json'),'reuse_vs_fresh':reuse,
             'native_mutations':mutation_receipts}
    write_json(out/'binding.json',bindings)
    if not args.native_only:
        env={**os.environ,'LEAN_PATH':str(out)}
        command([lean,'-o',out/'LineModel.olean',BASE/'LineModel.lean'],out/'lean-model.log',env=env)
        command([lean,BASE/'LineTheorems.lean'],out/'lean-theorems.log',env=env)
        proof=(out/'lean-theorems.log').read_text()
        assert proof.count("'LineModel.")==20
        assert 'sorryAx' not in proof
        for axioms in re.findall(r'depends on axioms: \[(.*?)\]',proof):
            assert set(axioms.split(', ')) <= {'propext','Classical.choice','Quot.sound'}
        (out/'Fixtures.lean').write_text(generate_lean.generate(inputs))
        command([lean,'--run',out/'Fixtures.lean'],out/'lean.tsv',env=env)
        leanrows=parse_rows(out/'lean.tsv',lean=True)
        merged={(version,*k):v for version,rows in expected.items() for k,v in rows.items()}
        assert leanrows==merged
        receipt.update(lean_rows=len(leanrows),lean_oracle_exact=True,theorems=20,
            lean_mutations=lean_mutations.check(BASE,out,lean,command))
    write_json(out/'receipt.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['native_mutations','lean_mutations','reuse_vs_fresh']},sort_keys=True))

if __name__=='__main__':main()
