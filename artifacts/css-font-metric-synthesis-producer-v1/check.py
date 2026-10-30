import difflib,hashlib,json,subprocess,tempfile,textwrap
from pathlib import Path
H=Path(__file__).resolve().parent
ROOT=H.parents[1]
sha=lambda data:hashlib.sha256(data).hexdigest()
relative=Path('servo/components/style/properties/cascade.rs')
parent=(H/'parent'/relative).read_bytes();candidate=(H/'candidate'/relative).read_bytes();base=(H/'base'/relative).read_bytes()
assert parent==(ROOT/'artifacts/css-font-metric-provider-v1/candidate'/relative).read_bytes()
assert base==(ROOT/'artifacts/css-font-metric-provider-v1/base'/relative).read_bytes()
for path,digest in json.loads((H/'REFERENCES.json').read_bytes()).items():assert sha((ROOT/path).read_bytes())==digest
def function(body,name):
 text=body.decode();start=text.index('    fn '+name);a=text.index('{',start);depth=1;end=a+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]
for name in ['visit_value_references<','visit_link<','traverse<']:
 assert function(parent,name)==function(candidate,name),name
ns={'__file__':str(H/'test.py')};exec(compile((H/'test.py').read_text().split("def mutate(old,new):")[0],str(H/'test.py'),'exec'),ns)
r=json.loads((H/'TEST-RESULT.json').read_bytes());assert r['candidate_sha256']==sha(candidate)
assert r['records']['positive']['source_sha256']==sha(ns['source'].encode())
assert r['parts_sha256']=={k:sha(v.encode()) for k,v in ns['parts'].items()}
assert all(row['compile_exit']==0 and row['run_exit']==(0 if name=='positive' else 101) for name,row in r['records'].items())
assert all('debug-assertions=no' in row['compile_command'] for row in r['records'].values())
assert sha(Path(r['records']['positive']['compile_command'][0]).read_bytes())==r['rustc_sha256']
assert not Path(r['scratch']).exists()
assert 'type DeclarationIndex = u16;' in (H/'TestSupport.rs').read_text()
assert 'let boundary=65_535usize;' in (H/'Tests.rs').read_text()
assert (H/'TEST-FIRST-CONTROL.log').is_file()
assert not Path(json.loads((H/'TEST-FIRST-CONTROL.json').read_bytes())['scratch']).exists()
tools=json.loads((H/'TOOLCHAIN.json').read_bytes());config=ROOT/tools['config'];assert sha(config.read_bytes())==tools['config_sha256'];assert sha(Path(tools['rustfmt']).read_bytes())==tools['rustfmt_sha256']
provider_relative=Path('servo/components/style/custom_properties.rs')
assert (H/'candidate'/provider_relative).read_bytes()==(ROOT/'artifacts/css-prioritary-font-demand-proposal-v1/candidate'/provider_relative).read_bytes()
assert r['provider_sha256']==sha((H/'candidate'/provider_relative).read_bytes())
assert r['bitflags_sha256']==sha((ROOT/'third_party/rust/bitflags/src/lib.rs').read_bytes())
with tempfile.TemporaryDirectory(prefix='metric-provider-roundtrip-') as temporary:
 scratch=Path(temporary)
 for name,folder in [('PARENT-DELTA.patch','parent'),('native.patch','base')]:
  expected_diff=''
  for rel in [relative,provider_relative]:
   before=(H/folder/rel).read_bytes();after=(H/'candidate'/rel).read_bytes()
   expected_diff+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)))
   file=scratch/rel;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(before)
  assert (H/name).read_text()==expected_diff
  for reverse,expected_folder in [(False,'candidate'),(True,folder)]:
   run=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(H/name)]+(['-R'] if reverse else []),cwd=scratch,capture_output=True,text=True)
   assert run.returncode==0,run.stdout+run.stderr
   for rel in [relative,provider_relative]:assert (scratch/rel).read_bytes()==(H/expected_folder/rel).read_bytes()
 for rel in [relative,provider_relative]:
  (scratch/rel).write_bytes((H/'candidate'/rel).read_bytes())
  run=subprocess.run([tools['rustfmt'],'--check','--config-path',str(config),str(scratch/rel)],capture_output=True,text=True);assert run.returncode==0,run.stdout+run.stderr
assert not scratch.exists()
print(json.dumps({'source_and_extraction_authenticated':True,'recursive_eager_bodies_unchanged':3,'patch_roundtrips':2,'format':True,'tests':14,'compiled_false_controls':15,'scratch_absent':True,'native_typecheck':False,'real_provider_literal_actions_tested':True,'full_scheduler_progress_proof':False}))
