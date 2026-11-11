import hashlib,json,shutil,subprocess,sys,tempfile,os,difflib
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=ROOT/'artifacts/css-pseudo-animation-composed-recascade-runtime-20261110-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
assert sha(SOURCE/'PREPARATION-FILES.json')=='5b144be619bbae0aa139b1e58db692740ac3fc6ae7dec7c9c22b0ecfb9434e5d'
manifest=load(SOURCE/'PREPARATION-FILES.json');assert all(sha(SOURCE/n)==h for n,h in manifest.items())
origin=load(SOURCE/'COMPOSED-ORIGIN.json');prior=ROOT/origin['runtime'];native=ROOT/origin['source']
old=(prior/'run.py').read_text();new=(SOURCE/'run.py').read_text()
assert ''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/run.py',tofile='b/run.py'))==(SOURCE/'COMPOSED-RUN-DELTA.patch').read_text()
assert old[old.index('def restore('):]==new[new.index('def restore('):]
for name in ['bundle.py','process.py','analyze.py','driver-analyze.py','recascade-analyze.py','freeze.py','DRIVER-ASSERTIONS.json','RECASCADE-ASSERTIONS.json','EXPECTED-BASELINE.json']:
 assert (SOURCE/name).read_bytes()==(prior/name).read_bytes()
inv=load(SOURCE/'COMPOSED-ASSERTIONS.json');assert inv==load(native/'ASSERTIONS.json')
rows=[r for t in inv['tasks'] for r in t['assertions']]
assert len(rows)==122 and len(inv['tasks'])==5
assert sum(r['classification']=='probe' for r in rows)==3
assert sum(r['classification']=='setup' for r in rows)==33
assert all((r['name'].startswith('Probe: '))==(r['classification']=='probe') for r in rows)
with tempfile.TemporaryDirectory(prefix='composed-runtime-independent-') as temporary:
 scratch=Path(temporary)
 for n,h in manifest.items():
  f=scratch/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/n,f)
 # Preserve copied checker bytes; only its repository locator is adapted in memory.
 script="import sys; from pathlib import Path; p=Path(sys.argv[1]); source=p.read_text(); old='ROOT = HERE.parents[1]'; assert source.count(old)==1; source=source.replace(old,'ROOT = Path('+repr(sys.argv[2])+')'); sys.argv=[str(p)]; exec(compile(source,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})"
 r=subprocess.run([sys.executable,'-I','-B','-c',script,str(scratch/'check.py'),str(ROOT)],cwd=scratch,capture_output=True,text=True,timeout=180,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
 (HERE/'source-replay.stdout').write_text(r.stdout);(HERE/'source-replay.stderr').write_text(r.stderr)
 assert r.returncode==0,(r.stdout,r.stderr)
 result=json.loads(r.stdout);assert result['controls']=={'parser-controls':30,'driver-controls':23,'recascade-controls':23,'composed-controls':41}
 assert all(sha(scratch/n)==h for n,h in manifest.items())
assert all(sha(SOURCE/n)==h for n,h in manifest.items())
(HERE/'REVIEW.json').write_text(json.dumps({'status':'PASS','preparation_manifest':sha(SOURCE/'PREPARATION-FILES.json'),'inputs':len(manifest),'source_replay':result,'exact_runtime_delta':True,'restore_function_and_helpers_unchanged':True,'compiled_or_browser_execution':False,'scratch_removed':not scratch.exists()},indent=2)+'\n')
