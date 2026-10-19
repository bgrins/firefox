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
def sources():
 parents={}
 for entry in read_json(R/'context/IMPORTS.json'):
  root=R/'context'/entry['label'];assert sha(root/'FREEZE.json')==entry['freeze'];assert sha(root/'MANIFEST.json')==entry['manifest']
  parents[entry['label']]=read_json(root/'MANIFEST.json');assert len(parents[entry['label']])==entry['authenticated']
  assert sha(root/'REPORT.md')==parents[entry['label']]['REPORT.md']
 for name,entry in read_json(R/'INHERITED-LEAN.json').items():
  assert sha(R/'lean'/name)==entry['sha256']==parents[entry['parent']]['lean/'+name]
 for q in (R/'vendor').rglob('*'):
  if q.is_file():assert sha(q)==parents['url'][str(q.relative_to(R))]
 for name,pin in read_json(R/'SOURCE-PINS.json').items():
  assert sha(R/'source'/name)==pin==parents['url']['source/'+name]
  assert sha(R/'vendor/cssparser/src'/name)==pin
 assert sha(R/'context/url/TOOLCHAIN.json')==parents['url']['TOOLCHAIN.json']
 old=read_json(R/'context/url/TOOLCHAIN.json');tool=read_json(R/'TOOLCHAIN.json')
 assert {k:v for k,v in old.items() if k!='parser_features'}=={k:v for k,v in tool.items() if k!='parser_features'}
 for name in ['lean','rustc']:
  assert sha(Path(tool[name]))==tool[name+'_sha256'],'toolchain pin '+name
 inv=read_json(R/'LEAN-INVENTORY.json');names=[];new=[]
 assert {q.stem for q in (R/'lean').glob('*.lean')}==set(inv['modules'])|{'Audit'}
 for module in inv['modules']:
  text=(R/'lean'/(module+'.lean')).read_text();ns=re.search(r'^namespace (\w+)',text,re.M)
  found=[(ns.group(1)+'.' if ns else '')+n for n in re.findall(r'^\s*(?:theorem|lemma)\s+(\w+)',text,re.M)];names+=found
  if module in inv['new_modules']:new+=found
 assert names==read_json(R/'AUDIT-NAMES.json') and new==inv['new_names'] and len(names)==inv['theorems'] and len(new)==inv['new_theorems']
 cases=read_json(R/'CASES.json');lines=['import PublicByteWitnesses','namespace HistoryCases','def cases : List (List PublicCache.Byte × List String) := [']
 for i,c in enumerate(cases):lines.append(' ('+str(list(c['input'].encode())).replace(' ','')+','+json.dumps(c['ops'])+')'+(',' if i+1<len(cases) else ''))
 lines += [']','end HistoryCases'];assert (R/'lean/HistoryCases.lean').read_text()=='\n'.join(lines)+'\n'
 return inv
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
m=authenticate()
for q in R.rglob('*.json'):read_json(q)
inv=sources();print('AUTHENTICATED',len(m),'inputs')
if not a.run:sys.exit(0)
assert a.output is not None and not a.output.exists(),'new output required';out=a.output.resolve();assert not out.is_relative_to(R.resolve()),'output must be outside sealed input root';out.mkdir(parents=True);commands=[]
def run(args,log):
 cmd=[sys.executable,'-I','-S',*map(str,args)];r=subprocess.run(cmd,capture_output=True,text=True,env=SAFE_ENV);(out/log).write_text(r.stdout+r.stderr);commands.append({'command':cmd,'exit':r.returncode,'log':log});assert r.returncode==0,(log,r.stdout+r.stderr)
run([R/'native/bindings.py','--output',out/'SOURCE-BINDINGS.json'],'bindings.log');assert sha(out/'SOURCE-BINDINGS.json')==sha(R/'SOURCE-BINDINGS.json')
run([R/'lean_check.py','--output',out/'proof'],'proof.log')
run([R/'native/check.py','--output',out/'native','--olean',out/'proof/lean'],'native.log')
assert authenticate()==m
receipt={'status':'PASS','authenticated_inputs':len(m),'source_definitions':len(read_json(R/'SOURCE-BINDINGS.json')),'proof':read_json(out/'proof/CHECK.json'),'native':read_json(out/'native/CHECK.json'),'commands':commands,'scope':'Constructor-derived projected cache coherence and source-driven primary API observer histories; named provider, entry, metadata, codec, machine and native execution premises retained.'}
(out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',len(inv['modules']),'modules',len(read_json(R/'AUDIT-NAMES.json')),'audits')
