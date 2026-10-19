import argparse,hashlib,json,os,re,runpy,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--manifest-sha',required=True);ap.add_argument('--lean',required=True);args=ap.parse_args()
assert hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()==args.manifest_sha
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
runtime=('development-build/','imports/dictionary-stream-v1/development-build/','imports/dictionary-stream-v1/provider-bridge-v1/development-build/')
actual={str(p.relative_to(ROOT))for p in ROOT.rglob('*')if p.is_file()and not str(p.relative_to(ROOT)).startswith(runtime)}
assert actual==set(manifest['files'])|{'MANIFEST.json','FREEZE.json'}
for name,digest in manifest['files'].items():
 rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
 path=ROOT/rel;assert not path.is_symlink()and path.resolve().is_relative_to(ROOT)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
lean=Path(args.lean).resolve();tool=json.loads((ROOT/'TOOL.json').read_text())
assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['sha256']
assert subprocess.check_output([lean,'--version'],text=True).strip()==tool['version']
out=ROOT/'development-build';out.mkdir(exist_ok=True);commands=[]
def run(name,command,env=None):
 result=subprocess.run(list(map(str,command)),capture_output=True,text=True,env=env)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 commands.append({'name':name,'exit':result.returncode,'args':list(map(str,command))})
 (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,result.returncode,flush=True)
 assert result.returncode==0,(name,result.stdout[-2000:],result.stderr[-2000:])
 return result.stdout
peer=ROOT/'imports/dictionary-stream-v1'
run('peer-source-rebuild',[sys.executable,peer/'check.py','--lean',lean,'--manifest-sha','4987e143efdf8c7d7b2b034c33fbc48cd33fa3f9a523fa75c44970ecca88b0f6'])
run('language-source-build',[sys.executable,ROOT/'native/build-language-dictionary.py'])
run('language-native-preservation',[sys.executable,ROOT/'native/check-language-dictionary.py'])
olean=out/'lean';olean.mkdir(exist_ok=True);env=dict(os.environ,LEAN_PATH=str(olean));modules={p.stem:p for p in (ROOT/'lean').glob('*.lean')};done=[];reports=0
while len(done)<len(modules):
 progress=False
 for name,path in modules.items():
  if name in done:continue
  source=path.read_text();deps=re.findall(r'^import (\w+)',source,re.M)
  assert all(dep in modules or dep in ['Std','Lean']for dep in deps)
  if any(dep in modules and dep not in done for dep in deps):continue
  assert not re.search(r'\b(sorry|axiom|admit|native_decide|bv_decide)\b',source)
  run('lean-'+name,[lean,'-o',olean/(name+'.olean'),path],env);done.append(name);progress=True
  names=[];namespaces=[]
  for line in source.splitlines():
   opening=re.match(r'^namespace ([\w.]+)',line);ending=re.match(r'^end(?: ([\w.]+))?$',line)
   if opening:namespaces.append(opening.group(1))
   elif ending and namespaces:namespaces.pop()
   theorem=re.match(r'^(?:@\[[^]]*\]\s*)?theorem ([\w.]+)',line)
   if theorem:names.append('.'.join(namespaces+[theorem.group(1)]))
  audit=olean/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
  raw=run('axioms-'+name,[lean,audit],env);assert 'sorryAx'not in raw;reports+=len(names)
  for group in re.findall(r'depends on axioms: \[([^]]*)\]',raw):assert set(map(str.strip,group.split(',')))<={'propext','Classical.choice','Quot.sound',''}
 assert progress
helper=runpy.run_path(str(ROOT/'recorded_native.py'))
expected=helper['observations']((out/'dictionary-stream-language/stream-candidate.stdout').read_text())
actual=[json.loads(line)for line in run('stream-driver',[lean,'--run',modules['StreamDriver'],ROOT/'seeds/stream-lean-fixtures.json'],env).splitlines()]
assert len(actual)==len(expected)==1284
for a,b in zip(actual,expected,strict=True):assert a==b,a['id']
result={'files':len(manifest['files']),'manifest_sha256':args.manifest_sha,'modules':len(done),'standard_axiom_reports':reports,'streams':len(actual),'operations':sum(len(x['steps'])for x in actual),'events':sum(len(y['events'])for x in actual for y in x['steps']),'status':'Fresh offline source-only actual manager/loader language-native/Lean bridge passed; full scope open'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
