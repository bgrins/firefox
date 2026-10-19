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
def predecessor():
 auth=read_json(R/'predecessor/AUTHENTICATION.json')
 assert sha(R/'predecessor/FREEZE.json')==auth['freeze_sha256']
 assert sha(R/'predecessor/MANIFEST.json')==auth['manifest_sha256']
 old=read_json(R/'predecessor/MANIFEST.json')
 assert len(old)==auth['authenticated_inputs']==436
 copies=read_json(R/'predecessor/PROVIDER-COPY.json')
 assert copies['manifest_sha256']==auth['manifest_sha256']
 for name,pin in copies['copied'].items():
  assert old[name]==pin and sha(R/name)==pin, name
 for name,pin in read_json(R/'INHERITED-LEAN.json').items():
  assert old['lean/'+name]==pin and sha(R/'lean'/name)==pin, name
 for name in ['CASES.json','SOURCE-BINDINGS.json','SOURCE-PINS.json','TOOLCHAIN.json']:
  assert sha(R/'predecessor'/name)==old[name],name
 cases=read_json(R/'CASES.json');base=read_json(R/'predecessor/CASES.json')
 assert len(base)==57 and len(cases)==59 and cases[:57]==base
 assert cases[:58]==read_json(R/'predecessor/CASES-58-before-bulk.json')
 assert read_json(R/'CASE-ADMISSION.json')['base_cases']==57
def validator_history():
 history=R/'validator-history'
 pins=read_json(history/'EXTERNAL-PINS.json')
 for name in ['MANIFEST.json','FREEZE.json']:
  assert sha(history/name)==pins[name]
 old=read_json(history/'MANIFEST.json')
 assert sha(history/'native/check_states.py')==old['native/check_states.py']
 assert sha(history/'native/check.py')==old['native/check.py']
 transfer=read_json(R/'V1-TRANSFER.json')
 assert set(transfer['unchanged'])==set(old)-set(transfer['changed'])
 for name,pin in transfer['unchanged'].items():
  assert old[name]==pin and sha(R/name)==pin,name
 assert len(read_json(R/'LEAN-INVENTORY.json')['modules'])==51
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();m=authenticate();predecessor();validator_history();print('AUTHENTICATED',len(m),'inputs')
if not a.run:sys.exit(0)
assert a.output is not None and not a.output.exists(),'new output required';out=a.output.resolve();assert not out.is_relative_to(R.resolve()),'output must be outside sealed input root';out.mkdir(parents=True);commands=[]
def run(args,log):
 cmd=[sys.executable,'-I','-S',*map(str,args)];r=subprocess.run(cmd,capture_output=True,text=True,env=SAFE_ENV);(out/log).write_text(r.stdout+r.stderr);commands.append({'command':cmd,'exit':r.returncode,'log':log});assert r.returncode==0,(log,r.stdout+r.stderr)
for name,pin in json.loads((R/'SOURCE-PINS.json').read_text()).items():
 base=Path(name).name;assert sha(R/'source'/base)==pin;assert sha(R/'vendor/cssparser/src'/base)==pin
run([R/'native/fields.py','--output',out/'FIELD-BINDINGS.json'],'fields.log');assert sha(out/'FIELD-BINDINGS.json')==sha(R/'FIELD-BINDINGS.json')
run([R/'native/bindings.py','--output',out/'SOURCE-BINDINGS.json'],'bindings.log');assert sha(out/'SOURCE-BINDINGS.json')==sha(R/'SOURCE-BINDINGS.json')
inv=json.loads((R/'LEAN-INVENTORY.json').read_text());names=[];new=[]
for module in inv['modules']:
 text=(R/'lean'/(module+'.lean')).read_text();ns=re.search(r'^namespace (\w+)',text,re.M).group(1);found=[ns+'.'+n for n in re.findall(r'^\s*(?:theorem|lemma)\s+(\w+)',text,re.M)];names+=found
 if module in inv['new_modules']:new+=found
assert names==json.loads((R/'AUDIT-NAMES.json').read_text())and new==inv['new_names']and len(names)==inv['theorems']and len(new)==inv['new_theorems']
for name,pin in json.loads((R/'INHERITED-LEAN.json').read_text()).items():assert sha(R/'lean'/name)==pin
run([R/'lean_check.py','--output',out/'proof'],'proof.log')
run([R/'native/check.py','--output',out/'native','--olean',out/'proof/lean'],'native.log')
assert authenticate()==m
receipt={'status':'PASS','authenticated_inputs':len(m),'field_declarations':len(read_json(R/'FIELD-BINDINGS.json')),'source_definitions':len(json.loads((R/'SOURCE-BINDINGS.json').read_text())),'proof':json.loads((out/'proof/CHECK.json').read_text()),'native':json.loads((out/'native/CHECK.json').read_text()),'commands':commands,'scope':'Actual mutable helper/URL-loop state and raw capture model; exact fixed native step/capture correspondence. Canonical codec, usize, packed headroom, allocation/compiler and public-history premises remain explicit in SOURCE-ADMISSION.md.'};(out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',len(inv['modules']),'modules',len(names),'audits; 59 native cases in three modes; four native and four Lean mutants')
