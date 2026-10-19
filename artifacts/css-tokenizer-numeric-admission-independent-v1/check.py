import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--lean',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():assert (R/n).is_file() and not (R/n).is_symlink() and sha(R/n)==h,n
s=R/'import';assert sha(s/'FREEZE.json')=='4b39737baf7af4e7d1670ee7fdd5344feb6e793fb07890fddd4fa06d3cde68fb';assert sha(s/'MANIFEST.json')=='ca2d9144be8d8d2e5a8a7c398607db79692ac84c0298e27757f2300d776f8145'
im=json.loads((s/'MANIFEST.json').read_text());assert len(im)==384
for n,h in im.items():assert sha(s/n)==h,n
add=R/'provider-addendum';assert sha(add/'FREEZE.json')=='0c2db67df470e826f2d7481b40fd6aeda6b73e8023dd36ba98728f2c0a111ef4';assert sha(add/'MANIFEST.json')==json.loads((add/'FREEZE.json').read_text())['manifest_sha256']
for n,h in json.loads((add/'MANIFEST.json').read_text()).items():assert sha(add/n)==h,n
lean=a.lean.resolve();assert sha(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert not out.exists()
r=subprocess.run([sys.executable,str(s/'check.py'),'--lean',str(lean),'--output',str(out)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
result=json.loads((out/'RESULT.json').read_text())
for key,value in {'authenticated':384,'modules':20,'theorem_audits':130,'native_cases':90,'native_to_lean_rows':81,'native_semantic_mutants':4,'lean_semantic_mutants':4,'complete_source_definitions':16}.items():assert result[key]==value,(key,result)
review=dict(authenticated_review_inputs=len(m),component=result,source='original arithmetic8a5925e2; not live v2',provider_addendum='authenticated; scanner from_ident derive expansion remains admitted',verdict='conditional original-source lexical/decoded-unit component accepted',current_source_transfer='required separately',numeric_value_correctness='not proved')
(out/'INDEPENDENT.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(review))
