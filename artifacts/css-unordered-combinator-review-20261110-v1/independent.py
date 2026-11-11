import hashlib, itertools, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
AUTHOR=ROOT.parent/'css-unordered-combinator-20261110-v1'
LEAN=ROOT.parent/'stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(AUTHOR/'SOURCE-ONLY.json')=='860df6b0094d748afdce3f94c6d427d53eecac369c02ef1c4266a8e397a82823'
    manifests={}
    for filename in ['SOURCE-ONLY.json','PROPOSAL-FILES.json','FILES.json']:
        rows=json.loads((AUTHOR/filename).read_text())
        for name,digest in rows.items(): assert sha(AUTHOR/name)==digest, name
        manifests[filename]={'sha256':sha(AUTHOR/filename),'files':len(rows)}
    for filename in ['PRESERVED.json','COMPATIBILITY-SOURCES.json']:
        for row in json.loads((AUTHOR/filename).read_text()):
            assert sha(AUTHOR/row['copy'])==row['sha256']
            assert sha(ROOT.parents[1]/row['source'])==row['sha256'],row['source']
    oracle=json.loads((AUTHOR/'text-transform-oracle.json').read_text())
    def accepted(words):
        if words==['none']: return True
        categories={'capitalize':0,'uppercase':0,'lowercase':0,'full-width':1,'full-size-kana':2}
        return bool(words) and all(w in categories for w in words) and len(set(categories[w] for w in words))==len(words)
    alphabet=['none','capitalize','uppercase','lowercase','full-width','full-size-kana']
    rows=[list(x) for n in range(6) for x in itertools.product(alphabet,repeat=n)]
    assert all(accepted(w)==(w in oracle) for w in rows)
    commands=[]
    with tempfile.TemporaryDirectory(prefix='unordered-review-') as temp:
        scratch=Path(temp); env=dict(os.environ,LEAN_PATH=str(scratch))
        modules=['Grammar','Laws','Program','ProgramLaws','JsonInput','Selections','SelectionLaws','Unordered','UnorderedLaws','ProgramV2','JsonV2']
        for i,module in enumerate(modules):
            shutil.copyfile(AUTHOR/('baseline' if i<5 else '')/(module+'.lean'),scratch/(module+'.lean'))
        shutil.copyfile(ROOT/'Boundary.lean',scratch/'Boundary.lean')
        names=re.findall(r'^theorem (\w+)',(ROOT/'Boundary.lean').read_text(),re.M)
        (scratch/'Audit.lean').write_text('import Boundary\n'+'\n'.join('#print axioms ReviewUnordered.'+n for n in names)+'\n')
        for module in modules+['Boundary','Audit']:
            r=subprocess.run([str(LEAN.resolve()),'-o',module+'.olean',module+'.lean'],cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            log=ROOT/('independent-'+module+'.log');log.write_text(r.stdout)
            commands.append(dict(module=module,exit=r.returncode,log=log.name,sha256=sha(log),scratch=str(scratch)))
            (ROOT/'INDEPENDENT-COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
            assert r.returncode==0 and 'warning:' not in r.stdout and 'error:' not in r.stdout,(module,r.stdout)
        audits=re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",r.stdout)
        assert [n for n,_ in audits]==['ReviewUnordered.'+n for n in names]
        for _,axes in audits: assert {a.strip() for a in axes.split(',') if a.strip()} <= {'propext','Quot.sound','Classical.choice'}
    assert not scratch.exists()
    report=dict(status='PASS',manifests=manifests,independent_oracle_rows=len(rows),boundary_proofs=len(names),compiled_scratch_removed=True)
    (ROOT/'INDEPENDENT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
