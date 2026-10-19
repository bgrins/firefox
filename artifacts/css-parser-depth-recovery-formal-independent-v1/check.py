from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def body_end(source,start):
    i=source.index('{',start);depth=0
    while i<len(source):
        if source.startswith('//',i):
            end=source.find('\n',i);i=len(source) if end<0 else end;continue
        if source.startswith('/*',i):
            nested=1;i+=2
            while nested:
                if source.startswith('/*',i):nested+=1;i+=2
                elif source.startswith('*/',i):nested-=1;i+=2
                else:i+=1
                assert i<=len(source)
            continue
        if source[i]=='"':
            match=re.match(r'"(?:\\.|[^"\\])*"',source[i:],re.S)
            assert match
            i+=match.end();continue
        if source[i]=="'":
            match=re.match(r"'(?:\\(?:u\{[a-fA-F0-9]+\}|.)|[^'\\\n])'",source[i:])
            if match:i+=match.end();continue
        if source[i]=='{':depth+=1
        elif source[i]=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    raise AssertionError('unclosed body')

def check(producer):
    assert digest(producer/'FREEZE.json')=='370fcdbd856c3eed9f7f4455afe64c46de1d507d2e1aa5896726c61d6d955438'
    assert digest(producer/'MANIFEST.json')=='df42a2abae2f36a0506ce7873412f891edb805f557a1e5626d06ea4a7ec76c6d'
    manifest=json.loads((producer/'MANIFEST.json').read_text())
    for n,h in manifest.items():assert digest(producer/n)==h,n
    original=(producer/'original/third_party/rust/cssparser/src/parser.rs').read_text()
    candidate=(producer/'candidate/third_party/rust/cssparser/src/parser.rs').read_text()
    anchor='    if parser.current_block_depth >= parser.nested_block_limit && parser.nested_block_limit != 0 {\n'
    added='        parser.consume_until_end_of_block(block_type);\n'
    assert original.count(anchor)==1
    assert original.replace(anchor,anchor+added)==candidate
    bodies={}
    for name in ['parse_nested_block','consume_until_end_of_block','closing','take_at_start_of']:
        needle="pub fn parse_nested_block<'i, F, T, E>(" if name=='parse_nested_block' else 'fn '+name+'('
        start=candidate.index(needle);end=body_end(candidate,start)
        bodies[name]=hashlib.sha256(candidate[start:end].encode()).hexdigest()
    model=(producer/'lean/Recovery.lean').read_text()
    names=['Recovery.'+n for n in re.findall(r'^theorem (\w+)',model,re.M)]
    assert names==json.loads((producer/'THEOREMS.json').read_text()) and len(names)==21
    audit=(ROOT/'evidence/AXIOMS.txt').read_text()
    assert re.findall(r"^'([^']+)' (?:depends on axioms:|does not depend on any axioms)",audit,re.M)==names
    for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',audit):assert set(group.split(', ')) <= {'propext','Quot.sound','Classical.choice'}
    commands=json.loads((ROOT/'evidence/COMMANDS.json').read_text())
    failures=[c for c in commands if c['exit']]
    assert len(failures)==2
    for c in failures:
        raw=c['stdout']+c['stderr']
        assert 'unsolved goals' in raw and 'is false' in raw
        assert not any(x in raw for x in ['unknown identifier','unexpected token','failed to synthesize'])
    native=json.loads((ROOT/'evidence/NATIVE-COMMANDS.json').read_text())
    bad=[c for c in native if c['exit']]
    assert len(bad)==2 and all(c['exit']==101 and 'assertion `left == right` failed' in c['stderr'] for c in bad)
    a=[json.loads(l) for l in (ROOT/'evidence/original-observations.jsonl').read_text().splitlines()]
    b=[json.loads(l) for l in (ROOT/'evidence/candidate-observations.jsonl').read_text().splitlines()]
    assert len(a)==len(b)==24
    differences=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert differences==[2,13,14,15,16,18]
    assert b[2]['accepted']==['red'] and a[2]['accepted']==['red','blue']
    assert b[13]['remaining']==b[14]['remaining']==' color:green;'
    assert all(b[i]['remaining']=='tail' and not b[i]['callback_invoked'] for i in (15,16,17))
    assert b[18]['remaining']=='' and not b[18]['callback_invoked']
    for variant in ['original','candidate']:
        checksum=json.loads((ROOT/'evidence'/('checksum.'+variant+'.json')).read_text())
        assert checksum['files']['src/parser.rs']==digest(producer/variant/'third_party/rust/cssparser/src/parser.rs')
    return dict(authenticated=len(manifest),exact_theorems=21,full_bodies=bodies,native_rows_per_variant=24,changed_rows=differences,semantic_mutants={'native':2,'Lean':2},result='PASS')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--producer',type=Path,default=ROOT.parent/'css-parser-depth-recovery-repair-v1');parser.add_argument('--replay-output',type=Path)
    args=parser.parse_args()
    for n,h in json.loads((ROOT/'MANIFEST.json').read_text()).items():assert digest(ROOT/n)==h,n
    result=check(args.producer.resolve())
    if args.replay_output:
        out=args.replay_output.resolve();out.mkdir(parents=True,exist_ok=False);capsule=out/'capsule';capsule.mkdir()
        for n in list(json.loads((args.producer/'MANIFEST.json').read_text()))+['MANIFEST.json','FREEZE.json']:
            target=capsule/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(args.producer/n,target)
        subprocess.run([sys.executable,str(capsule/'check.py'),'--output',str(out/'replay')],check=True,cwd=out)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
