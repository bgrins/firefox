import argparse,hashlib,json,os,re,runpy,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--manifest-sha',required=True);p.add_argument('--lean',type=Path);p.add_argument('--output',type=Path);p.add_argument('--authenticate-only',action='store_true');a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate():
 assert sha(R/'MANIFEST.json')==a.manifest_sha
 files=json.loads((R/'MANIFEST.json').read_text())['files']
 actual={str(p.relative_to(R))for p in R.rglob('*')if p.is_file()}
 assert actual==set(files)|{'MANIFEST.json','FREEZE.json'}
 for name,digest in files.items():
  rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
  q=R/rel;assert not q.is_symlink()and q.resolve().is_relative_to(R)and sha(q)==digest,name
 return len(files)
count=authenticate()
for imported in json.loads((R/'IMPORT.json').read_text()):
 manifest=R/imported['manifest_copy'];assert sha(manifest)==imported['manifest_sha256']
 original=json.loads(manifest.read_text())['files']
 for name,digest in imported['copied'].items():
  assert original[name]==digest and sha(R/name)==digest,name
helper=runpy.run_path(str(R/'extract.py'))
bindings=helper['records']()
assert bindings==json.loads((R/'SOURCE-BINDING.json').read_text())
if a.authenticate_only:print('authenticated',count,'inputs and',len(bindings),'complete native definitions');raise SystemExit
assert a.lean and a.output
lean=a.lean.resolve();assert sha(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert out!=R and R not in out.parents;out.mkdir(parents=True,exist_ok=False)
env=dict(os.environ,LEAN_PATH=str(out));modules={p.stem:p for p in (R/'lean').glob('*.lean')};done=[];rows=[]
while len(done)<len(modules):
 progress=False
 for name,path in modules.items():
  if name in done:continue
  source=path.read_text();deps=re.findall(r'^import (\w+)',source,re.M)
  assert all(x in modules or x in ['Std','Lean']for x in deps)
  if any(x in modules and x not in done for x in deps):continue
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',source)
  result=subprocess.run([lean,'-o',out/(name+'.olean'),path],env=env,cwd=path.parent,capture_output=True,text=True)
  (out/(name+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,(name,result.stdout,result.stderr)
  ns=re.search(r'^namespace ([\w.]+)',source,re.M);prefix=ns[1]+'.'if ns else''
  names=re.findall(r'^(?:@\[[^\n]*\]\s*)?theorem ([\w.]+)',source,re.M)
  audit=out/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+prefix+x for x in names)+'\n')
  result=subprocess.run([lean,audit],env=env,cwd=out,capture_output=True,text=True)
  (out/(name+'-axioms.log')).write_text(result.stdout+result.stderr);assert result.returncode==0 and not result.stderr
  reports=re.findall(r"'[^']+' (?:does not depend on any axioms|depends on axioms: \[[^\]]*\])",result.stdout)
  residue=result.stdout
  for report in reports:residue=residue.replace(report,'',1)
  assert not residue.strip()and len(reports)==len(names)
  for theorem,report in zip(names,reports):
   assert report.startswith("'"+prefix+theorem+"' ")
   group=re.search(r'depends on axioms: \[([^]]*)\]',report,re.S)
   if group:assert set(map(str.strip,group[1].split(',')))<={'propext','Classical.choice','Quot.sound',''}
  rows.append({'module':name,'theorems':len(names)});done.append(name);progress=True
 assert progress
assert authenticate()==count
result={'files':count,'modules':len(done),'theorem_reports':sum(x['theorems']for x in rows),'rows':rows,'source_definitions':len(bindings),'native_build':False,'scope':'Exact model request chronology/bounds, nested source schedule, persistent query session and conditional consumer projection; native source/response/lifetime/font admission remains open.'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
