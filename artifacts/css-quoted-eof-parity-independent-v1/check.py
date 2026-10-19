from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def decode(raw,quote):
    assert raw[0]==quote
    content=[];i=1
    while i<len(raw):
        c=raw[i];i+=1
        if c==quote:return ''.join(content),raw[i:]
        if c=='\\':
            if i==len(raw):break
            c=raw[i];i+=1
        content.append(c)
    return ''.join(content),''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--replay-output',type=Path);args=parser.parse_args()
    for name,pin in json.loads((ROOT/'MANIFEST.json').read_text()).items():assert sha(ROOT/name)==pin,name
    dep=json.loads((ROOT/'DEPENDENCIES.json').read_text());parent=(ROOT/dep['producer']).resolve()
    assert sha(parent/'FREEZE.json')==dep['freeze'] and sha(parent/'MANIFEST.json')==dep['manifest']
    manifest=json.loads((parent/'MANIFEST.json').read_text())
    for name,pin in manifest.items():assert sha(parent/name)==pin,name
    assert len(manifest)==180
    kind=dep['kind'];module='ParityRepair' if kind=='parity' else 'ClosureRepair'
    names=[]
    for name in ['TerminalString',module]:
        names += [name+'.'+n for n in re.findall(r'^theorem (\w+)',(parent/'lean'/f'{name}.lean').read_text(),re.M)]
    audited=re.findall(r"^'([^']+)'",(ROOT/'evidence/AXIOMS.txt').read_text(),re.M)
    assert len(audited)==len(set(audited)) and set(names)==set(audited)
    assert len(names)==(20 if kind=='parity' else 19)
    file='servo/components/style/custom_properties.rs'
    for prefix,oldpath,newpath in [('',parent/'original'/file,parent/'candidate'/file),('integration/',parent/'integration/endpoint-formatted/formatted.rs',parent/'integration/candidate.rs')]:
        delta=json.loads((parent/(prefix+'DELTA.json')).read_text());old=oldpath.read_text();new=newpath.read_text()
        assert old.count(delta['old'])==1 and old.replace(delta['old'],delta['new'])==new
        patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+file,tofile='b/'+file))
        assert patch==(parent/(prefix+'native.patch')).read_text()
    own=json.loads((parent/'integration/DELTA.json').read_text());other=json.loads((parent/'integration/OTHER-DELTA.json').read_text())
    base=(parent/'integration/endpoint-formatted/formatted.rs').read_text()
    assert base.replace(own['old'],own['new']).replace(other['old'],other['new'])==base.replace(other['old'],other['new']).replace(own['old'],own['new'])==(parent/'integration/both-candidate.rs').read_text()
    fixture_checks=0
    for quote in ['"',"'"]:
        for n in range(5):
            for terminal in [False,True]:
                raw=quote+'example'+'\\'*n+(quote if terminal else '')
                independent,_=decode(raw,quote)
                fixture='example'+'\\'*(n//2)+(quote if terminal and n%2==1 else '')
                assert independent==fixture
                fixture_checks+=1
        assert decode(quote,quote)==('','')
        fixture_checks+=1
    original_failures={f'{q}-{n}-{t}' for q in ['double','single'] for n,t in [(1,1),(2,0),(3,1),(4,0)]}
    for mode in ['standalone','endpoint','both']:
        outputs={}
        for variant in ['original','candidate','mutant-original','mutant-opposite']:
            rows=[json.loads(line) for line in (ROOT/'evidence'/mode/(variant+'.jsonl')).read_text().splitlines()]
            assert len(rows)==22 and len({row['id'] for row in rows})==22
            outputs[variant]={row['id'] for row in rows if not row['ok']}
        assert outputs['original']==outputs['mutant-original']==original_failures
        remaining=set() if mode=='both' else {n for n in original_failures if n.endswith('-1' if kind=='parity' else '-0')}
        assert outputs['candidate']==remaining
        target={f'{q}-1-0' if kind=='parity' else f'{q}-0-1' for q in ['double','single']}
        assert target<=outputs['mutant-opposite']
    if args.replay_output:
        root=args.replay_output.resolve();root.mkdir(parents=True,exist_ok=False);copy=root/'source';copy.mkdir()
        for name in list(manifest)+['MANIFEST.json','FREEZE.json']:
            dest=copy/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(parent/name,dest)
        subprocess.run([sys.executable,str(copy/'check.py'),'--output',str(root/'output')],cwd=root,check=True)
    print(json.dumps({'status':'PASS','kind':kind,'authenticated_inputs':len(manifest),'exact_audits':len(names),'independent_terminal_fixture_checks':fixture_checks,'configurations':3,'native_variants_each':4,'source_composition':'commutes','browser_candidate_gate':'OPEN'}))
if __name__=='__main__':main()
