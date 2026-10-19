from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,difflib
assert sys.flags.isolated and sys.flags.no_site
r=Path(__file__).absolute().parent
assert not r.is_symlink()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(xs):
 d={}
 for k,v in xs:
  assert k not in d,'duplicate JSON key'
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=unique)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
for q in r.rglob('*'):assert not q.is_symlink() and (q.is_file() or q.is_dir())
f=read(r/'FREEZE.json');assert sha(r/'MANIFEST.json')==f['manifest_sha256'] and sha(r/'check.py')==f['checker_sha256']
m=read(r/'MANIFEST.json');expected=set(m)|{'MANIFEST.json','FREEZE.json'}
assert {str(q.relative_to(r)) for q in r.rglob('*') if q.is_file()}==expected
assert {str(q.relative_to(r)) for q in r.rglob('*') if q.is_dir()}=={str(d) for q in expected for d in Path(q).parents if str(d)!='.'}
for name,h in m.items():assert not Path(name).is_absolute() and '..' not in Path(name).parts and sha(r/name)==h
for q in r.rglob('*.json'):read(q)
original=(r/'source/servo/components/style/custom_properties_map.rs').read_text();candidate=(r/'candidate-custom_properties_map.rs').read_text()
old='        loop {\n            let (name, value) = match self.current_iter.next()';assert original.count(old)==1
s=original.replace(old,old.replace('loop {',"'properties: loop {"));old='                if descendant.own_properties.contains_key(name) {\n                    continue;\n                }';assert s.count(old)==1
assert s.replace(old,old.replace('continue;',"continue 'properties;"))==candidate
patch=''.join(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),fromfile='a/servo/components/style/custom_properties_map.rs',tofile='b/servo/components/style/custom_properties_map.rs'));assert patch==(r/'proposed-native.patch').read_text()
assert 'const SMALL_THRESHOLD: usize = 8;' in original and 'const ANCESTOR_COUNT_LIMIT: usize = 4;' in original
for row in read(r/'SOURCE-PINS.json'):
 if row['origin']=='current local read-only snapshot':assert sha(r/'source'/row['path'])==row['sha256']
html=(r/'custom-property-enumeration-shadowing.html').read_text();assert html.split('<script>')[1].split('</script>')[0]==(r/'probe.js').read_text();assert html.count('test(t =>')==6 and 'for (const count of [8, 9])' in html
print('AUTHENTICATED',len(m),'inputs; source-shaped finite model and unexecuted WPT only')
if a.output is None:sys.exit(0)
out=a.output.resolve();assert not out.exists() and not out.is_relative_to(r.resolve());tools=read(r/'TOOLS.json');assert sha(Path(tools['node']))==tools['node_sha256'];out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};rows=[]
for cmd,log in [([sys.executable,'-I','-S',str(r/'model_witness.py')],'model.json'),([tools['node'],'--check',str(r/'probe.js')],'syntax.log')]:
 v=subprocess.run(cmd,capture_output=True,text=True,env=env);(out/log).write_text(v.stdout+v.stderr);assert v.returncode==0;rows.append({'command':cmd,'exit':v.returncode,'log':log})
assert (out/'model.json').read_bytes()==(r/'MODEL-WITNESS.json').read_bytes()
(out/'CHECK.json').write_text(json.dumps({'status':'PASS','commands':rows,'browser':'UNEXECUTED','native_rust':'NOT EXECUTED','universal_proof':'NOT CLAIMED'},indent=2)+'\n')
print('PASS finite model replay and JavaScript syntax')
