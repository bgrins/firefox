import hashlib,json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (HERE/n).write_text(json.dumps(v,indent=2)+"\n")
cmd=json.loads((ROOT/'artifacts/css-cssom-integer-rounding-helper-v1/CHECK.json').read_text())['command']
cmd=[str(HERE/'differential.cpp') if v.endswith('/helper.cpp') else str(HERE/'differential.d') if v.endswith('/helper.d') else str(HERE/'differential') if v.endswith('/helper') else v for v in cmd]
r={'command':cmd,'proposal_files_sha256':sha(ROOT/'artifacts/css-cssom-integer-rounding-repair-v2/FILES.json'),'source_sha256':sha(HERE/'differential.cpp'),'conversion_sha256':sha(HERE/'conversion.inc')}
try:
 with (HERE/'compile.log').open('w') as f: r['compile_exit']=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
 assert r['compile_exit']==0
 dep=(HERE/'differential.d').read_text().replace('\\\n',' ')
 deps=dep.split(':',1)[1].split()
 r['dependencies']={n:sha(ROOT/n) for n in deps}
 r['binary_sha256']=sha(HERE/'differential')
 with (HERE/'stdout.log').open('w') as out,(HERE/'stderr.log').open('w') as err: r['run_exit']=subprocess.run([str(HERE/'differential')],cwd=ROOT,stdout=out,stderr=err).returncode
 assert r['run_exit']==0
 assert not (HERE/'stderr.log').read_bytes()
finally:
 products=[HERE/'differential',HERE/'differential.d',HERE/'differential.dSYM']
 r['removed_products']={str(f.relative_to(HERE)):sha(f) for p in products for f in (sorted(p.rglob('*')) if p.is_dir() else [p]) if f.is_file()}
 for p in products:
  if p.is_dir(): shutil.rmtree(p)
  elif p.exists(): p.unlink()
 r['products_absent']=all(not p.exists() for p in products)
 save('CHECK.json',r)
print(json.dumps({k:r[k] for k in ['compile_exit','run_exit','products_absent']},indent=2))
print((HERE/'stdout.log').read_text())
