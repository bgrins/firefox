import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from support_b import oracle

BASE=Path(__file__).resolve().parent


def materialize_witnesses(mutations):
    text=(BASE/'Witnesses.lean').read_text()
    expressions={
        'weighted-addition':'weightedChoice xs',
        'swap-width-style':'(successive faceStyle faceWidth faceWeight xs).map Face.identity',
        'swap-style-weight':'(successive faceWidth faceWeight faceStyle xs).map Face.identity',
        'float-combined-key':'roundedChoice xs',
        'sentinel-rank-zero':'(xs.filter (fun f => decide (fallbackOrder.le f.key zeroKey ∧ ¬fallbackOrder.le zeroKey f.key))).map Face.identity',
        'drop-presentation':'globalChoice lt isZero (withoutPresentation xs)',
        'mismatched-zero-perfect':'globalChoice lt falseZero xs',
        'shared-nonstrict':'globalChoice le (fun _ => false) xs',
        'drop-equal':'globalChoice lt (fun _ => false) xs',
        'remove-clearing':'noClear xs',
        'reverse-unshared':'chosen xs.reverse',
    }
    rows=[]
    for row in mutations:
        c=row['case'];name=row['name'].replace('-','_');faces=[]
        ids=list(range(len(c['faces'])))
        if c['operation'] in (1,3):ids.reverse()
        for i in ids:
            f=c['faces'][i];coords=oracle.coordinates(c,f,'A')
            scaled=[x*256 for x in coords];assert all(x.denominator==1 for x in scaled)
            presentation=int(bool(c['presentation']) and bool(f[9])!=(c['presentation']>=3))
            faces.append('⟨'+str(i)+', ⟨'+', '.join(map(str,[presentation]+[int(x) for x in scaled]))+'⟩⟩')
        text+=f'def input_{name} : List Face := ['+', '.join(faces)+']\n'
        text+=f'def mutant_{name} (xs : List Face) := '+expressions[row['name']]+'\n'
        expected=row['expected']['selected'];actual=row['mutant']['selected']
        reference=f'(chosen input_{name}).head?.toList' if c['operation']==4 else f'chosen input_{name}'
        text+=f'theorem witness_{name} : {reference} = {expected} ∧ mutant_{name} input_{name} = {actual} ∧ {reference} ≠ mutant_{name} input_{name} := by decide\n'
        text+=f'#eval ("{name}", chosen input_{name}, mutant_{name} input_{name})\n\n'
        rows.append(dict(name=row['name'],raw_case=c,scaled_coordinates=faces,expected=expected,mutant=actual))
    text+='end PriorityWitness\n'
    return text,rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(BASE/'lean-development'));p.add_argument('--mutations',default=str(BASE/'mutation-development/MUTATIONS.json'));args=p.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'support_b/TOOLCHAIN-v1.json').read_text())
    source=(BASE/'Priority.lean').read_text();witnesses,rows=materialize_witnesses(json.loads(Path(args.mutations).read_text()))
    audited=source+'\n'+witnesses
    names=['Priority.'+n for n in re.findall(r'^theorem (\w+)',source,re.M)]+['PriorityWitness.'+n for n in re.findall(r'^theorem (\w+)',witnesses,re.M)]
    audited+='\n'+''.join(f'#print axioms {name}\n' for name in names)
    assert not re.search(r'\b(sorry|axiom|unsafe|native_decide)\b',source+witnesses)
    path=out/'Audited.lean';path.write_text(audited)
    r=subprocess.run([tc['lean'],str(path)],text=True,capture_output=True,timeout=180)
    (out/'Lean.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,r.stdout[-6000:]
    assert 'sorryAx' not in r.stdout
    for dependencies in re.findall(r'depends on axioms: \[([^\]]*)\]',r.stdout):
        assert set(x.strip() for x in dependencies.split(',') if x.strip()) <= {'propext','Classical.choice','Quot.sound'}
    assert len(re.findall(r"'(?:Priority|PriorityWitness)\.[^']+'",r.stdout))==len(names)
    (out/'WITNESSES.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'RESULT.json').write_text(json.dumps(dict(status='PASS',theorems=len(names),universal_theorems=len(names)-len(rows),successful_semantic_witnesses=len(rows),source_sha256=hashlib.sha256(audited.encode()).hexdigest()),indent=2)+'\n')
    print('PASS',len(names),'theorems',len(rows),'successful semantic witnesses')

if __name__=='__main__':main()
