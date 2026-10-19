import argparse,hashlib,json,os,re,runpy,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--manifest-sha',required=True);ap.add_argument('--lean',required=True);args=ap.parse_args()
assert hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()==args.manifest_sha
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for name,digest in manifest['files'].items():
 rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
 path=ROOT/rel;assert not path.is_symlink()and path.resolve().is_relative_to(ROOT)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
for path in ROOT.rglob('*'):
 if path.is_file():
  name=str(path.relative_to(ROOT));assert name in manifest['files']or name in ['MANIFEST.json','FREEZE.json']or name.startswith(('development-build/','provider-bridge-v1/development-build/')),name
out=ROOT/'development-build';out.mkdir(exist_ok=True);tools=json.loads((ROOT/'TOOLS.json').read_text());lean=Path(args.lean).resolve()
assert hashlib.sha256(lean.read_bytes()).hexdigest()==tools['lean_sha256']
assert subprocess.check_output([lean,'--version'],text=True).strip()==tools['lean_version']
for name,version_args in [('clang',['--version']),('rustc',['--version','--verbose']),('cargo',['--version'])]:
 executable=Path(tools[name]);assert hashlib.sha256(executable.read_bytes()).hexdigest()==tools[name+'_sha256']
 assert subprocess.check_output([executable,*version_args],text=True).strip()==tools[name+'_version']
assert hashlib.sha256((Path(tools['sdk'])/'SDKSettings.json').read_bytes()).hexdigest()==tools['sdk_settings_sha256']
assert hashlib.sha256((Path(tools['libcxx_include'])/'__config').read_bytes()).hexdigest()==tools['libcxx_config_sha256']
env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');commands=[]
def run(name,args,input=None,extra_env=None):
 result=subprocess.run(list(map(str,args)),input=input,capture_output=True,text=True,env=env if extra_env is None else extra_env,timeout=240)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 commands.append({'stage':name,'args':list(map(str,args)),'exit':result.returncode});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n');print(name,result.returncode,flush=True)
 assert result.returncode==0,(name,result.stdout[-3000:],result.stderr[-3000:])
 return result.stdout
for script in ['native/build-prerequisites.py','native/build-loader-prerequisites.py','native/build-loader-stream.py','native/check-manager-source-binding.py','native/check-resource-source-binding.py','native/extract-loader.py']:
 run(Path(script).stem,[sys.executable,ROOT/script])
run('manager-build',[tools['clang'],'-std=c++20','-isysroot',tools['sdk'],'-isystem',tools['libcxx_include'],'-O1','-g','-fsanitize=undefined',out/'loader/manager-loader.cpp',out/'rust/libmapped_hyph.a','-o',out/'loader/manager-loader'])
dictionary=ROOT/'source/providers/intl/locales/en-US/hyphenation/hyph_en_US.hyf'
inputs=(ROOT/'seeds/ownership-model-input.txt').read_text();assert len(inputs.splitlines())==1220
hashes={'original':'c69120e12d02fc9d35d470f1410974f568ed2440d2e8740b9662074ea25ce452','candidate':'4f3e43727bdeeb5628b9548e5d897d0aee0dd0e64b4a588fa3e943065aee668e','standalone':'3a6de29b833b9e215ee27aacfc4a7252cc7fef4577363c4fb6b6253823228e79'}
for flavor in hashes:
 raw=run('stream-'+flavor,[out/'loader-stream'/('stream-'+flavor),dictionary],inputs)
 assert not (out/('stream-'+flavor+'.stderr')).read_text()
 assert hashlib.sha256(raw.encode()).hexdigest()==hashes[flavor],flavor
manager=run('manager-run',[out/'loader/manager-loader',dictionary],(ROOT/'seeds/manager-inputs.txt').read_text())
assert not (out/'manager-run.stderr').read_text()
assert hashlib.sha256(manager.encode()).hexdigest()=='f8f99cac71062ed19875d1dcfbe2b25e08e194b8e794f5c2d7ef781663c0c946'
reports=0;module_groups=[]
def compile_group(directory,names,label):
 global reports
 olean=out/label;olean.mkdir(exist_ok=True)
 for path in olean.glob('*.olean'):path.unlink()
 le=dict(env,LEAN_PATH=str(olean));done=[]
 def compile(name):
  global reports
  if name in done:return
  path=directory/(name+'.lean');source=path.read_text();assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',source),name
  for dep in re.findall(r'^import (\w+)',source,re.M):
   if (directory/(dep+'.lean')).exists():compile(dep)
  run(label+'-'+name,[lean,'-o',olean/(name+'.olean'),path],extra_env=le);done.append(name)
  namespace=re.findall(r'^namespace ([\w.]+)',source,re.M);prefix=namespace[0]+'.'if namespace else''
  theorems=re.findall(r'^(?:@\[[^\n]*\]\s*)?theorem ([\w.]+)',source,re.M)
  audit=olean/(name+'Axioms.lean');audit.write_text('import '+name+'\n'+'\n'.join('#print axioms '+prefix+n for n in theorems)+'\n')
  output=run(label+'-'+name+'-axioms',[lean,audit],extra_env=le)
  assert 'sorryAx'not in output
  for group in re.findall(r'depends on axioms: \[([^]]*)\]',output):assert set(map(str.strip,group.split(',')))<={'propext','Classical.choice','Quot.sound',''}
  reports+=len(theorems)
 for name in names:compile(name)
 module_groups.append({'label':label,'modules':done});return le
manager_env=compile_group(ROOT/'lean-stream',['DictionaryManagerWitness','DictionaryLoader'],'manager-lean')
model=run('manager-lean-driver',[lean,'--run',ROOT/'lean-stream/DictionaryManagerDriver.lean',ROOT/'seeds/manager-inputs.txt'],extra_env=manager_env);assert model==manager
stream_env=compile_group(ROOT/'stream-model/lean',['StreamDriver'],'stream-lean')
output=run('stream-lean-driver',[lean,'--run',ROOT/'stream-model/lean/StreamDriver.lean',ROOT/'stream-model/evidence/ownership-lean-fixtures.json'],extra_env=stream_env)
actual=[json.loads(line)for line in output.splitlines()]
for case in actual:
 for step in case['steps']:
  for item in step['state']['items']:
   if item['owner']is None:item['offset']=0
parse=runpy.run_path(str(ROOT/'stream-model/observations.py'))['native_observations']
expected=parse((out/'stream-candidate.stdout').read_text());assert actual==expected
assert (out/'stream-candidate.stdout').read_bytes()==(ROOT/'stream-model/evidence/ownership-lean-native.txt').read_bytes()
result={'manifest_sha256':args.manifest_sha,'files':len(manifest['files']),'module_groups':module_groups,'standard_axiom_reports':reports,'fixed_manager_cases':334,'fixed_stream_cases_per_variant':1220,'candidate_operations':sum(len(c['steps'])for c in actual),'candidate_semantic_events':sum(len(s['events'])for c in actual for s in c['steps']),'status':'fresh offline source-only Rust/ICU/native/Lean replay passed; complete manager+loader+Hyphenate+stream bounded join; provider/source/heap/IPC/caller/font full refinement remains open'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
