import hashlib,json,subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'artifacts/css-pseudo-animation-query-runtime-20261110-v2'
entries=json.loads((AUTHOR/'PREPARATION-FILES.json').read_text())
manifest=entries if isinstance(entries,dict) else {row['path']:row['sha256'] for row in entries}
assert len(manifest)==len(entries)
assert hashlib.sha256((AUTHOR/'PREPARATION-FILES.json').read_bytes()).hexdigest()=='ab6216dbc94ed6e369d0bfd28179ef9799d86a870895dbe27da8d427ea21a636'
for name,digest in manifest.items():
 assert hashlib.sha256((AUTHOR/name).read_bytes()).hexdigest()==digest,name
with tempfile.TemporaryDirectory(dir=ROOT/'artifacts',prefix='query-runtime-review-scratch-') as directory:
 scratch=Path(directory)
 for name in manifest:
  target=scratch/name
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(AUTHOR/name,target)
 result=subprocess.run([sys.executable,'-I','-B',str(scratch/'check.py')],cwd=ROOT,capture_output=True,text=True)
 (HERE/'REPLAY.json').write_text(result.stdout)
 (HERE/'replay.stderr').write_text(result.stderr)
 assert result.returncode==0,result.stderr
 parsed=json.loads(result.stdout)
 assert parsed['status']=='PASS'
 for name in ['driver-controls.py','parser-controls.py']:
  r=subprocess.run([sys.executable,'-I','-B',str(scratch/name)],cwd=ROOT,capture_output=True,text=True)
  assert r.returncode==0,r.stderr
  (HERE/(name.removesuffix('.py')+'-replay.json')).write_text(r.stdout)
assert all(hashlib.sha256((AUTHOR/n).read_bytes()).hexdigest()==h for n,h in manifest.items())
print(json.dumps({'status':'PASS','manifest_sha256':hashlib.sha256((AUTHOR/'PREPARATION-FILES.json').read_bytes()).hexdigest(),'authenticated_files':len(manifest),'scratch_removed':not scratch.exists(),'author_inputs_preserved':True},indent=2))
