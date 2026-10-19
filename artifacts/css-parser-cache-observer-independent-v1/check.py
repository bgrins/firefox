from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def check(producer):
    assert digest(producer/'FREEZE.json')=='3cf895d0171d7b4c5abb9b29de0e845abb7b2286ae55e6629ecfe837eeb642ad'
    assert digest(producer/'MANIFEST.json')=='e698371f67ca84de27d719691f856f0aaafa407bfaa9dfb81bbffd7b5338f7ea'
    manifest=json.loads((producer/'MANIFEST.json').read_text())
    for n,h in manifest.items():assert digest(producer/n)==h,n
    pins=json.loads((producer/'SOURCE-PINS.json').read_text())
    for n,v in pins.items():assert digest(producer/'source'/n)==v['current'],n
    for n in ['parser.rs','tokenizer.rs','rules_and_declarations.rs']:
        assert (producer/'source/third_party/rust/cssparser/src'/n).read_bytes()==(producer/'vendor/cssparser/src'/n).read_bytes()
    names=['TrackingEpoch.'+n for n in re.findall(r'^theorem (\w+)',(producer/'lean/TrackingEpoch.lean').read_text(),re.M)]
    assert names==json.loads((ROOT/'THEOREMS.json').read_text()) and len(names)==len(set(names))==10
    assert re.findall(r'^#print axioms (\S+)',(producer/'lean/Audit.lean').read_text(),re.M)==names
    commands=json.loads((ROOT/'evidence/COMMANDS.json').read_text())
    audit=next(c['stdout'] for c in commands if c['command'][-1].endswith('/Audit.lean'))
    assert re.findall(r"^'([^']+)' (?:depends on axioms:|does not depend on any axioms)",audit,re.M)==names
    for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',audit):assert set(group.split(', '))<={'propext','Quot.sound','Classical.choice'}
    failures=[c for c in commands if c['exit']]
    assert len(failures)==2
    for c in failures:
        assert 'unsolved goals' in c['stdout'] or 'Type mismatch' in c['stdout']
        assert not any(x in c['stdout'] for x in ['unknown identifier','unexpected token'])
    assert len([c for c in commands if c['command'][-1].endswith('-definitions.lean') and c['exit']==0])==2
    gates=json.loads((ROOT/'evidence/GATES.json').read_text())
    assert len(gates)==6 and gates[0]['exit']==gates[-1]['exit']==0
    assert all(g['exit']!=0 and 'integrity failure' in g['stderr'] for g in gates[1:-1])
    rows=[json.loads(x) for x in (ROOT/'evidence/OBSERVATIONS.jsonl').read_text().splitlines()]
    expected=[]
    for reset in [False,True]:
        for raw,colon in [('var(--x)',False),('width: /* comment */ var(--x)',True),('width: calc(var(--x) + 1px)',True)]:
            expected.append(dict(case='entry-prefix',raw=raw,colon=colon,reset=reset,seen=True))
    expected.extend([dict(case='late-enable',primed=False,seen=True),dict(case='late-enable',primed=True,seen=False)])
    for field in ['sourceURL','sourceMappingURL']:
        for replay in range(3):expected.append(dict(case='comment-replay',field=field,replay=replay,url='A' if replay==0 else 'B',eof=True))
    assert rows==expected
    return dict(authenticated=len(manifest),source_pins=len(pins),exact_theorems=10,native_cases=len(rows),compiled_Lean_semantic_mutants=2,tamper_gates=4,result='PASS')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--producer',type=Path,default=ROOT.parent/'css-parser-cache-observer-admission-v1');ap.add_argument('--replay-output',type=Path);a=ap.parse_args()
    for n,h in json.loads((ROOT/'MANIFEST.json').read_text()).items():assert digest(ROOT/n)==h,n
    result=check(a.producer.resolve())
    if a.replay_output:
        out=a.replay_output.resolve();out.mkdir(parents=True,exist_ok=False);capsule=out/'capsule';capsule.mkdir()
        for n in list(json.loads((a.producer/'MANIFEST.json').read_text()))+['MANIFEST.json','FREEZE.json']:
            target=capsule/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.producer/n,target)
        subprocess.run([sys.executable,str(capsule/'gates.py'),'--output',str(out/'gates')],cwd=out,check=True)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
