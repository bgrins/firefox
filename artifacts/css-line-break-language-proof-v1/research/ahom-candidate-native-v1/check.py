import argparse,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--manifest-sha',required=True);ap.add_argument('--replay',action='store_true');a=ap.parse_args()
excludes=('build/','imports/complex-encoding-diagnostic-v1/build/','imports/complex-encoding-diagnostic-v1/imports/bridge-v1/development-build/','imports/lf-complex-stream-diagnostic-v1/build/','imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/development-build/','imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/development-build/','imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/provider-bridge-v1/development-build/')
def auth():
 raw=(R/'MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==a.manifest_sha
 m=json.loads(raw)
 for n,h in m['files'].items():
  q=R/n;assert not Path(n).is_absolute()and '..'not in Path(n).parts and not q.is_symlink()and q.resolve().is_relative_to(R)
  assert hashlib.sha256(q.read_bytes()).hexdigest()==h,n
 actual={str(q.relative_to(R))for q in R.rglob('*')if q.is_file()and not str(q.relative_to(R)).startswith(excludes)}
 assert actual==set(m['files'])|{'MANIFEST.json','FREEZE.json'}
 return len(m['files'])
n=auth();print('authenticated',n,flush=True)
O=R/'build';O.mkdir(exist_ok=True)
def run(name,args):
 with (O/(name+'.log')).open('w')as log:r=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);print(name,'passed',flush=True)
run('source-binding',[sys.executable,R/'source-binding.py'])
if a.replay:
 tools=json.loads((R/'imports/complex-encoding-diagnostic-v1/TOOLS.json').read_text())
 run('baseline-source-replay',[sys.executable,R/'imports/lf-complex-stream-diagnostic-v1/check.py','--manifest-sha','6ef82e8a2e9befbcb0981742b8142b6e40b3d083bf4e1951853f5b80ff7f2c2f','--lean',tools['lean']['path']])
 run('candidate-source-replay',[sys.executable,R/'run-candidate.py'])
 run('candidate-kernel',[sys.executable,R/'check-kernel.py'])
 assert json.loads((O/'RESULT.json').read_text())==json.loads((R/'evidence/RESULT.json').read_text())
 assert json.loads((O/'kernel/RESULT.json').read_text())==json.loads((R/'evidence/KERNEL-RESULT.json').read_text())
assert auth()==n
print('independent candidate capsule passed',flush=True)
