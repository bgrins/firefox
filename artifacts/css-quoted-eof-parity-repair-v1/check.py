#!/usr/bin/env python3
import argparse, difflib, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--auth-only',action='store_true');args=parser.parse_args()
freeze=json.loads((ROOT/'FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json')==freeze['manifest_sha256'],'manifest mismatch'
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
assert len(manifest)==freeze['files']
assert sha(ROOT/'check.py')==freeze['checker_sha256']
for rel,h in manifest.items():
 p=ROOT/rel;assert not p.is_symlink() and sha(p)==h,rel
print(f'authenticated {len(manifest)} files',flush=True)
if args.auth_only:raise SystemExit(0)
assert args.output is not None,'--output NEWDIR required'
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
config=json.loads((ROOT/'TOOLCHAIN.json').read_text())
for tool in ['rustc','lean']:assert sha(Path(config[tool]))==config[tool+'_sha256'],tool
commands=[]
def run(cmd,cwd=None,env=None,success=True):
 r=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True)
 commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert (r.returncode==0)==success,r.stdout+r.stderr
 return r.stdout+r.stderr
kind=json.loads((ROOT/'KIND.json').read_text())['kind']
file='servo/components/style/custom_properties.rs'
for prefix,original,candidate in [('',ROOT/'original'/file,ROOT/'candidate'/file),('integration/',ROOT/'integration/endpoint-formatted/formatted.rs',ROOT/'integration/candidate.rs')]:
 d=json.loads((ROOT/(prefix+'DELTA.json')).read_text());before=original.read_text();after=candidate.read_text()
 assert sha(original)==d['original_sha256'] and sha(candidate)==d['candidate_sha256']
 assert before.count(d['old'])==1 and before.replace(d['old'],d['new'])==after
 expected=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+file,tofile='b/'+file))
 assert (ROOT/(prefix+'native.patch')).read_text()==expected
 tree=out/('patch-'+('integration' if prefix else 'standalone'));dest=tree/file;dest.parent.mkdir(parents=True);dest.write_text(before)
 run(['patch','--batch','-p1','-i',str(ROOT/(prefix+'native.patch'))],cwd=tree);assert dest.read_text()==after
 run(['patch','--batch','-R','-p1','-i',str(ROOT/(prefix+'native.patch'))],cwd=tree);assert dest.read_text()==before
# Both independently recorded adaptations commute byte-for-byte; this is source composition only.
d=json.loads((ROOT/'integration/DELTA.json').read_text());other=json.loads((ROOT/'integration/OTHER-DELTA.json').read_text());base=(ROOT/'integration/endpoint-formatted/formatted.rs').read_text()
a=base.replace(d['old'],d['new']).replace(other['old'],other['new']);b=base.replace(other['old'],other['new']).replace(d['old'],d['new'])
assert a==b==(ROOT/'integration/both-candidate.rs').read_text()
leanout=out/'lean';leanout.mkdir();env=os.environ.copy();env['LEAN_PATH']=str(leanout)
modules=['TerminalString','ParityRepair' if kind=='parity' else 'ClosureRepair'];audits=[]
for module in modules:
 src=ROOT/'lean'/(module+'.lean');shutil.copyfile(src,leanout/src.name)
 code=src.read_text();assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',code)
 expected=re.findall(r'^#print axioms (\w+)$',code,re.M)
 declared=re.findall(r'^theorem (\w+)\b',code,re.M);assert sorted(expected)==sorted(declared)
 raw=run([config['lean'],'-o',module+'.olean',module+'.lean'],cwd=leanout,env=env)
 lines=[line for line in raw.splitlines() if 'depends on axioms:' in line or 'does not depend on any axioms' in line]
 assert len(lines)==len(expected),(module,len(lines),expected)
 for line in lines:
  name=line.split("'")[1];assert name==module+'.'+name.split('.')[-1]
  if 'depends on axioms:' in line:
   axioms=line.split('[',1)[1].split(']',1)[0].replace(' ','').split(',');assert set(axioms)<= {'propext','Quot.sound','Classical.choice'},line
 audits+=lines
(out/'AXIOMS.txt').write_text('\n'.join(audits)+'\n')
for rel in ['mutant-original.lean','mutant-opposite.lean']:
 shutil.copyfile(ROOT/'lean'/rel,leanout/rel)
 raw=run([config['lean'],rel],cwd=leanout,env=env,success=False)
 assert 'decide' in raw and 'error:' in raw and 'unknown' not in raw.lower(),raw
for label,opts in [('standalone',[]),('endpoint',['--integration']),('both',['--both'])]:
 run([sys.executable,str(ROOT/'native/build.py'),'--output',str(out/label),*opts])
# Fail closed if a checker/helper accidentally changed an authenticated input.
for rel,h in manifest.items():assert sha(ROOT/rel)==h,rel
result={'status':'PASS','files':len(manifest),'lean_modules':len(modules),'axiom_reports':len(audits),'lean_semantic_mutants_rejected':2,'native_variants_per_mode':4,'native_modes':['standalone','endpoint','both'],'cases_per_variant':22,'full_css_or_gecko_proof':False}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
