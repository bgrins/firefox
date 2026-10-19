#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys
assert sys.flags.isolated and sys.flags.no_site, 'invoke Python with -I -S'
R=Path(__file__).absolute().parent
SAFE_ENV={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
 out={}
 for key,value in pairs:
  assert key not in out,'duplicate JSON key: '+key
  out[key]=value
 return out
def read_json(path):return json.loads(path.read_text(),object_pairs_hook=unique)
def authenticate():
 assert not R.is_symlink(),'symlink input root'
 for q in R.rglob('*'):
  assert not q.is_symlink(),'symlink input: '+str(q)
  assert q.is_file()or q.is_dir(),'nonregular input: '+str(q)
 f=read_json(R/'FREEZE.json');assert sha(R/'MANIFEST.json')==f['manifest_sha256'],'manifest authentication';assert sha(R/'check.py')==f['checker_sha256'],'checker authentication'
 m=read_json(R/'MANIFEST.json');expected=set(m)|{'MANIFEST.json','FREEZE.json'}
 actual={str(q.relative_to(R))for q in R.rglob('*')if q.is_file()}
 assert actual==expected,'closed input roster mismatch: '+str(sorted(actual^expected))
 expected_dirs={str(parent)for name in expected for parent in Path(name).parents if str(parent)!='.'}
 actual_dirs={str(q.relative_to(R))for q in R.rglob('*')if q.is_dir()}
 assert actual_dirs==expected_dirs,'closed directory roster mismatch'
 for name,pin in m.items():
  p=Path(name);assert not p.is_absolute()and '..'not in p.parts and str(p)==name,'unsafe input path';q=R/p;assert q.resolve().is_relative_to(R.resolve()),'input path escape';assert q.is_file()and sha(q)==pin,'input authentication: '+name
 return m

def source_checks():
 expected_parents={
  'inherited':('0a290a6cbf83b6fa1be729cd13a3aeae23b77a4c6f86718baacbe0655bb83afe','a158bf5fb0be52bb3d252c69e18160e4d3e623a4650204fcff0279eea04fe75a'),
  'entry-audit':('d6ce94276f6bad0be0180f392b476b4d32b6dc68d6c8f85a04a3650deffc2598','978644021cd1c90cc7a10035add1746e3165fb250bd0572de59afbf3e1695e0a')}
 for label,(freeze,manifest) in expected_parents.items():
  parent=R/label;assert sha(parent/'FREEZE.json')==freeze and sha(parent/'MANIFEST.json')==manifest
  pins=read_json(parent/'MANIFEST.json')
  assert {str(p.relative_to(parent)) for p in parent.rglob('*') if p.is_file()}==set(pins)|{'FREEZE.json','MANIFEST.json'}
  assert all(sha(parent/p)==v for p,v in pins.items())
 comparison=read_json(R/'CALLER-SOURCE-COMPARISON.json')
 pins=read_json(R/'entry-audit/SOURCE-PINS.json')
 assert len(comparison['rows'])==len(pins)
 for row,pin in zip(comparison['rows'],pins):
  assert row['path']==pin['path'] and row['audit_source_sha256']==pin['sha256']
  assert row['whole_file_equal'] and row['observed_current_sha256']==pin['sha256']
  if 'full_definition' in row:
   body=row['full_definition'];assert hashlib.sha256(body.encode()).hexdigest()==row['definition_sha256']
   assert body in (R/'entry-audit/source'/row['path']).read_text() and row['full_definition_equal']
 inherited=read_json(R/'inherited/MANIFEST.json')
 for directory in ['source','vendor']:
  assert {str(p.relative_to(R)) for p in (R/directory).rglob('*') if p.is_file()}=={p for p in inherited if p.startswith(directory+'/')}
  for p in (R/directory).rglob('*'):
   if p.is_file():assert sha(p)==inherited[str(p.relative_to(R))]
 for p in (R/'inherited/lean').glob('*.lean'):
  if p.name!='Audit.lean':assert sha(R/'lean'/p.name)==sha(p)
 assert (R/'native/wrapper.rs').read_text().startswith((R/'inherited/native/wrapper.rs').read_text())
 assert sha(R/'native/build.py')==sha(R/'inherited/native/build.py')
 assert sha(R/'TOOLCHAIN.json')==sha(R/'inherited/TOOLCHAIN.json')
 tools=read_json(R/'TOOLCHAIN.json')
 for name in ['lean','rustc']:assert sha(Path(tools[name]))==tools[name+'_sha256']
 inv=read_json(R/'LEAN-INVENTORY.json');names=[];new=[]
 assert {p.stem for p in (R/'lean').glob('*.lean')}==set(inv['modules'])|{'Audit'}
 for module in inv['modules']:
  text=(R/'lean'/(module+'.lean')).read_text();ns=re.search(r'^namespace (\w+)',text,re.M)
  found=[(ns.group(1)+'.' if ns else '')+n for n in re.findall(r'^\s*(?:theorem|lemma)\s+(\w+)',text,re.M)]
  names+=found
  if module in inv['new_modules']:new+=found
 assert names==read_json(R/'AUDIT-NAMES.json') and len(names)==inv['theorems'] and new==inv['new_names']
 assert len(new)==inv['new_theorems']
 cases=read_json(R/'CASES.json')
 lines=['import WrapperEpochs','import WrapperEntry','namespace WrapperCases','def cases : List (List PublicCache.Byte × List String) := [']
 for i,c in enumerate(cases):lines.append(' ('+str(list(c['input'].encode())).replace(' ','')+','+json.dumps(c['ops'])+')'+(',' if i+1<len(cases) else ''))
 lines += [']','end WrapperCases']
 assert (R/'lean/WrapperCases.lean').read_text()=='\n'.join(lines)+'\n'
 return inv

p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
m=authenticate()
for path in R.rglob('*.json'):read_json(path)
inv=source_checks()
print('AUTHENTICATED',len(m),'inputs')
if not a.run:sys.exit(0)
assert a.output is not None and not a.output.exists(),'new output required'
out=a.output.resolve();assert not out.is_relative_to(R.resolve());out.mkdir(parents=True);commands=[]
def run(args,log):
 cmd=[sys.executable,'-I','-S',*map(str,args)]
 result=subprocess.run(cmd,capture_output=True,text=True,env=SAFE_ENV)
 (out/log).write_text(result.stdout+result.stderr)
 commands.append({'command':cmd,'exit':result.returncode,'log':log})
 assert result.returncode==0,(log,result.stdout+result.stderr)
run([R/'inherited/check.py'],'inherited-auth.log')
run([R/'native/bindings.py','--output',out/'SOURCE-BINDINGS.json'],'bindings.log')
assert sha(out/'SOURCE-BINDINGS.json')==sha(R/'SOURCE-BINDINGS.json')
run([R/'lean_check.py','--output',out/'proof'],'proof.log')
run([R/'native/check.py','--output',out/'native','--olean',out/'proof/lean'],'native.log')
assert authenticate()==m
receipt={'status':'PASS','authenticated_inputs':len(m),'source_definitions':len(read_json(R/'SOURCE-BINDINGS.json')),
 'proof':read_json(out/'proof/CHECK.json'),'native':read_json(out/'native/CHECK.json'),'commands':commands,
 'scope':'Actual raw skip/next and constructor-derived projected histories; full metadata, remaining token providers, codec, machine, heap, compiler and broader callback callers remain explicit.'}
(out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(inv['modules']),'modules',len(read_json(R/'AUDIT-NAMES.json')),'audits')
