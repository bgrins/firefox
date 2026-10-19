import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument('--output',type=Path,required=True)
p.add_argument('--benchmark',action='store_true')
a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text())
assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():
 q=R/n
 assert q.is_file() and not q.is_symlink() and sha(q)==h,n
src=R/'import'
assert sha(src/'FREEZE.json')=='35e217b262d26fe09f3d74166f4d9a698dfdbbca085f750fef118d0a8e4a170d'
assert sha(src/'INPUTS.json')=='2559cfe8afcc921c4ddb0acb0574af49e515a7e70b66dc133d02f65a99af40d1'
for n,h in json.loads((src/'INPUTS.json').read_text()).items(): assert sha(src/n)==h,n
for n,h in json.loads((R/'DRAFT-PINS.json').read_text()).items(): assert sha(src/n)==h and sha(R/'draft-inputs'/n)==h,n
tool=json.loads((R/'TOOLCHAIN.json').read_text());rustc=Path(tool['rustc_path'])
assert sha(rustc)==tool['rustc_sha256']
assert subprocess.check_output([str(rustc),'--version','--verbose'],text=True)==tool['version']
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
commands=[]
def run(args,cwd=out):
 r=subprocess.run(args,cwd=cwd,env=dict(os.environ,PATH=str(rustc.parent)+os.pathsep+os.environ['PATH'],PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
 commands.append(dict(args=args,exit=r.returncode,stdout=r.stdout,stderr=r.stderr));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode==0,r.stdout+r.stderr
 return r
run([sys.executable,str(src/'check.py'),'--run','--output',str(out/'producer')])
g=out/'generation';g.mkdir();shutil.copytree(R/'draft-inputs',g/'draft-inputs')
for n in ['prepare_checks.py','DRAFT-PINS.json']: shutil.copyfile(R/n,g/n)
run([sys.executable,str(g/'prepare_checks.py')])
for n in ['challenge.rs','benchmark.rs']: assert (g/n).read_bytes()==(R/n).read_bytes(),n
run([str(rustc),'--edition=2021','-O',str(g/'challenge.rs'),'-o',str(out/'challenge')])
r=run([str(out/'challenge')]);assert 'PASS 504 independent' in r.stdout
if a.benchmark:
 run([str(rustc),'--edition=2021','-O',str(g/'benchmark.rs'),'-o',str(out/'benchmark')])
 r=run([str(out/'benchmark')]);assert len(r.stdout.splitlines())==54
 (out/'benchmark.txt').write_text(r.stdout)
result=dict(authenticated=len(m),producer_replay='passed',independent_challenge=504,benchmark='executed without performance threshold' if a.benchmark else 'historical raw samples authenticated; no new timing requested',native_browser='not executed',verdict='v1 correctness review conditional; normal-path optimization recommended')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
