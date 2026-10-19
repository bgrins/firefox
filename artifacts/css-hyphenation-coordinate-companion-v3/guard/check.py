import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--manifest-sha',required=True);p.add_argument('--lean',type=Path);p.add_argument('--output',type=Path);p.add_argument('--authenticate-only',action='store_true');a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate():
 assert sha(R/'MANIFEST.json')==a.manifest_sha
 m=json.loads((R/'MANIFEST.json').read_text())['files']
 actual={str(x.relative_to(R))for x in R.rglob('*')if x.is_file()}
 assert actual==set(m)|{'MANIFEST.json','FREEZE.json'}
 for name,digest in m.items():
  q=R/name;assert not q.is_symlink()and q.resolve().is_relative_to(R)and sha(q)==digest,name
 return len(m)
count=authenticate()
original=(R/'source/original-gfxTextRun.cpp').read_text();candidate=(R/'source/candidate-gfxTextRun.cpp').read_text()
old='prevMostRecentWordBoundary < oldHyphenBufferLength';new='prevMostRecentWordBoundary < bufferRange.start'
assert original.count(old)==1 and candidate==original.replace(old,new)
if a.authenticate_only:print('authenticated',count,'inputs and complete native delta');raise SystemExit
assert a.lean and a.output
assert sha(a.lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert out!=R and R not in out.parents;out.mkdir(parents=True,exist_ok=False)
modules={x.stem:x for x in (R/'lean').glob('*.lean')};done=[];rows=[];env=dict(os.environ,LEAN_PATH=str(out))
while len(done)<len(modules):
 progress=False
 for name,path in modules.items():
  if name in done:continue
  text=path.read_text();deps=re.findall(r'^import (\w+)',text,re.M)
  assert all(x in modules or x in ['Std','Lean']for x in deps)
  if any(x in modules and x not in done for x in deps):continue
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',text)
  run=subprocess.run([a.lean,'-o',out/(name+'.olean'),path],env=env,capture_output=True,text=True)
  (out/(name+'.log')).write_text(run.stdout+run.stderr);assert run.returncode==0,(name,run.stdout)
  prefix=re.search(r'^namespace ([\w.]+)',text,re.M);prefix=prefix[1]+'.'if prefix else''
  names=re.findall(r'^(?:@\[[^\n]*\]\s*)?theorem ([\w.]+)',text,re.M)
  audit=out/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+prefix+x for x in names)+'\n')
  run=subprocess.run([a.lean,audit],env=env,capture_output=True,text=True);assert run.returncode==0 and not run.stderr
  (out/(name+'-axioms.log')).write_text(run.stdout)
  reports=re.findall(r"'[^']+' (?:does not depend on any axioms|depends on axioms: \[[^\]]*\])",run.stdout)
  residue=run.stdout
  for report in reports:residue=residue.replace(report,'',1)
  assert not residue.strip()and len(reports)==len(names)
  for theorem,line in zip(names,reports):
   assert line.startswith("'"+prefix+theorem+"' ")
   used=re.search(r'depends on axioms: \[([^]]*)\]',line,re.S)
   if used:assert set(map(str.strip,used[1].split(',')))<={'propext','Classical.choice','Quot.sound',''}
  done.append(name);rows.append({'module':name,'theorems':len(names)});progress=True
 assert progress
assert authenticate()==count
result={'files':count,'modules':len(done),'theorem_reports':sum(x['theorems']for x in rows),'results':rows,'scope':'Model guard admission plus exact source delta; no native build or whole native/provider verification.'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='results'}))
