import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--output',required=True,type=Path)
a=p.parse_args()
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
out=a.output.resolve()
out.mkdir(parents=True,exist_ok=False)
commands=[]
def run(cmd,cwd=out,success=True):
    r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    commands.append({'command':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert (r.returncode==0)==success,r.stderr+r.stdout
    return r

generated=out/'regeneration';generated.mkdir()
shutil.copytree(ROOT/'source',generated/'source')
(generated/'candidate').mkdir();(generated/'evidence').mkdir()
shutil.copyfile(ROOT/'generate.py',generated/'generate.py')
run([sys.executable,str(generated/'generate.py')])
for name in ['candidate/custom_properties.rs','native.patch']:
    assert (generated/name).read_bytes()==(ROOT/name).read_bytes(),name

run([sys.executable,str(ROOT/'native/build.py'),'--output',str(out/'native')])
cases=json.loads((ROOT/'native/CASES.json').read_text())
rows={v:[json.loads(x) for x in (out/'native'/f'{v}.jsonl').read_text().splitlines()]
      for v in ['original','candidate','missing-correction-mutant']}
for v,rr in rows.items():assert len(rr)==len(cases)
for case,old,new,mutant in zip(cases,rows['original'],rows['candidate'],rows['missing-correction-mutant']):
    assert old['css_hex']==new['css_hex']==mutant['css_hex']
    assert mutant==old
    assert new['status']=='OK'
    if old['status']=='OK': assert new==old
    if case['family'] in ['closed','missing','slash']:
        quote=case['css'].split(', ',1)[1][0]
        assert bytes.fromhex(new['output_hex']).decode()==quote+'example'+quote
    if 'var(--first, known)' in case['css']:
        assert old['refs'][0]==new['refs'][0]==[0,19,13]
    for start,end,fallback in new['refs']:
        assert 0<=start<=end<=new['length']
        if fallback:assert start<fallback<=end-1
counts={v:dict(collections.Counter(x['status'] for x in rr)) for v,rr in rows.items()}
assert counts=={'original':{'OK':18,'PANIC':22},'candidate':{'OK':40},'missing-correction-mutant':{'OK':18,'PANIC':22}}

toolchain=json.loads((ROOT/'LEAN.json').read_text())
lean=Path(toolchain['path'])
assert hashlib.sha256(lean.read_bytes()).hexdigest()==toolchain['sha256']
proof=out/'Endpoints.lean';shutil.copyfile(ROOT/'Endpoints.lean',proof)
r=run([str(lean),str(proof)])
expected=toolchain['theorems']
actual=re.findall(r"'([^']+)' (?:depends on axioms:|does not depend on any axioms)",r.stdout)
assert actual==expected,(actual,expected)
assert 'sorryAx' not in r.stdout and 'warning:' not in r.stdout
mutant=out/'Mutant.lean'
mutant.write_text(proof.read_text().replace('(if removed then 1 else 0)','(if removed then 0 else 0)'))
r=run([str(lean),str(mutant)],success=False)
assert 'error:' in r.stdout or 'error(' in r.stdout

tamper=out/'tamper';tamper.mkdir()
shutil.copyfile(ROOT/'check.py',tamper/'check.py')
(tamper/'MANIFEST.json').write_text(json.dumps({'Endpoints.lean':manifest['Endpoints.lean']}))
(tamper/'Endpoints.lean').write_text('changed\n')
r=run([sys.executable,str(tamper/'check.py'),'--output',str(out/'never-created')],success=False)
assert 'AssertionError: Endpoints.lean' in r.stderr
assert not (out/'never-created').exists()
result={'status':'PASS','authenticated_files':len(manifest),'cases':len(cases),'native':counts,'theorems':len(expected),'native_mutants':1,'Lean_mutants':1,'tamper_rejected_before_imports':True,'scope':'endpoint arithmetic and bounded exact-source execution; provider/caller/whole-parser proof not claimed'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
