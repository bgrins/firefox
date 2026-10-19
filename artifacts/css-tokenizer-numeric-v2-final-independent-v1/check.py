import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():assert (R/n).is_file() and not (R/n).is_symlink() and sha(R/n)==h,n
s=R/'import';assert sha(s/'FREEZE.json')=='fa8cefc1a301a8ddca2231f495a8a90b04f80d83f6c7f741d01a0eaf902966ad';assert sha(s/'INPUTS.json')=='1766f73914b19f56f0e3a5ae9c89300b7290a5ea1b81ee5e9831f9a9b966c516'
im=json.loads((s/'INPUTS.json').read_text());assert len(im)==51
for n,h in im.items():assert sha(s/n)==h,n
assert sha(s/'native-candidate.patch')=='0591cb8c635623862cd392ffc1f2abb5aef769a4d433285bdc5b40138405656d'
b=R/'benchmark-evidence';assert sha(b/'MANIFEST.json')=='bd8881c8e092af55e040b96fff99c3383c8ec4ae3a1b1922d8c7782860f622fa';assert sha(b/'FREEZE.json')=='3eda5728a9076420c416edbe402b64880e2c3061f81019d3a12834794ce492eb'
bm=json.loads((b/'MANIFEST.json').read_text())
for q in b.iterdir():
 if q.name not in ['FREEZE.json','MANIFEST.json']:assert sha(q)==bm[q.name],q.name
d=json.loads((s/'BENCHMARK-DELTA.json').read_text());final=(s/'numeric-candidate.rs').read_text();old=(b/'numeric-candidate.rs').read_text()
assert final.count(d['inserted_comment'])==1 and final.replace(d['inserted_comment'],'')==old
challenge=(b/'challenge.rs').read_text();assert challenge.count(old)==1;assert challenge.replace(old,final)==(R/'final-challenge.rs').read_text()
tool=json.loads((b/'TOOLCHAIN.json').read_text());rustc=Path(tool['rustc_path']);assert sha(rustc)==tool['rustc_sha256'];assert subprocess.check_output([str(rustc),'--version','--verbose'],text=True)==tool['version']
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True);commands=[]
def run(args):
 r=subprocess.run(args,env=dict(os.environ,PATH=str(rustc.parent)+os.pathsep+os.environ['PATH'],PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
 commands.append(dict(args=args,exit=r.returncode,stdout=r.stdout,stderr=r.stderr));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0,r.stdout+r.stderr;return r
run([sys.executable,str(s/'check.py'),'--run','--output',str(out/'producer')])
r=run([sys.executable,str(R/'independent_bounds.py')]);assert r.stdout==(R/'evidence/INDEPENDENT-BOUNDS.json').read_text();(out/'INDEPENDENT-BOUNDS.json').write_text(r.stdout)
run([str(rustc),'--edition=2021','-O',str(R/'final-challenge.rs'),'-o',str(out/'challenge')]);r=run([str(out/'challenge')]);assert 'PASS 504 independent' in r.stdout
result=dict(authenticated=len(m),producer_inputs=51,producer_replay='debug/release852 plus3mutants and exact source/patch checks pass',independent_bounds='closed forms, all0..255, prerequisites and unequal lengths pass',independent_challenge=504,benchmark_delta='exact two comments',new_timing='not run',status='conditional source approval for root integration; no full numeric correctness claim')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
