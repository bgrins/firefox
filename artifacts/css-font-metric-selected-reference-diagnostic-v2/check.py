import difflib, hashlib, json, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'artifacts/css-font-metric-selected-reference-producer-v1'
BASE=ROOT/'artifacts/css-font-metric-synthesis-producer-v1/base'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roles=['servo/components/style/properties/cascade.rs','servo/components/style/custom_properties.rs']
for path,pin in json.loads((HERE/'REFERENCES.json').read_text()).items():assert sha(ROOT/path)==pin,path
s=(HERE/'candidate'/roles[0]).read_text();original=(PARENT/'candidate'/roles[0]).read_text()
stripped=s[:s.index('        fn write_metric_diagnostic(')]+s[s.index('        fn reset(&mut self) {'):]
stripped=stripped.replace('        let mut diagnostic_progress = None;\n','',1)
stripped=stripped.replace('                let progress = context.drive_metric_action(','                match context.drive_metric_action(',1)
stripped=stripped.replace('                    &mut font_publication_demand,\n                );\n                match &progress {','                    &mut font_publication_demand,\n                ) {',1)
stripped=stripped.replace('                    _ => {\n                        diagnostic_progress = Some(progress);\n                        break result;\n                    },','                    _ => break result,',1)
a=stripped.index('        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {')
b=stripped.index('        assert!(matches!(',a)
stripped=stripped[:a]+stripped[b:]
assert stripped==original,'Only diagnostic insertion/progress retention may differ'
assert (HERE/'candidate'/roles[1]).read_bytes()==(PARENT/'candidate'/roles[1]).read_bytes()
assert s.count('context.write_metric_diagnostic(')==1
for name,base,portable in [('PARENT-DELTA.patch',PARENT/'candidate',False),('native.patch',BASE,True)]:
 delta=''
 for role in roles:
  before,after=base/role,HERE/'candidate'/role
  delta+=''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='a/'+role if portable else str(before.relative_to(ROOT)),tofile='b/'+role if portable else str(after.relative_to(ROOT))))
 assert delta==(HERE/name).read_text()
for filename,count in [('TEST-RESULT.json',13),('NO-ACTION-RESULT.json',3)]:
 report=json.loads((HERE/filename).read_text())
 assert report['candidate_sha256']==sha(HERE/'candidate'/roles[0])
 assert report['provider_sha256']==sha(HERE/'candidate'/roles[1])
 assert report['servo_arc_sha256']==sha(ROOT/'servo/components/servo_arc/lib.rs')
 assert report['stable_deref_trait_sha256']==sha(ROOT/'third_party/rust/stable_deref_trait/src/lib.rs')
 for name,pin in report.get('test_inputs_sha256',report.get('inputs_sha256',{})).items():assert sha(HERE/name)==pin
 assert report['scratch_removed'] and not Path(report['scratch']).exists()
 for name,row in report['records'].items():
  if name=='std_only_arc_as_ptr':
   assert row['compile_exit']!=0 and 'E0599' in row['compile_stderr'] and 'as_ptr' in row['compile_stderr']
  else:
   assert row['compile_exit']==0
   assert (row['run_exit']==0)==(name=='positive')
 assert str(count)+' passed' in report['records']['positive']['stdout']
c=json.loads((HERE/'TOOLCHAIN.json').read_text());assert sha(Path(c['rustfmt']))==c['rustfmt_sha256'];assert sha(ROOT/c['config'])==c['config_sha256']
r=subprocess.run([c['rustfmt'],'--check','--edition','2024','--config-path',str(ROOT/c['config']),str(HERE/'candidate'/roles[0])],capture_output=True,text=True);assert r.returncode==0,r.stderr
with tempfile.TemporaryDirectory(prefix='metric-diagnostic-patch-') as temporary:
 scratch=Path(temporary)
 for role in roles:
  q=scratch/role;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((BASE/role).read_bytes())
 for reverse in (False,True):
  r=subprocess.run(['patch','-p1','--fuzz=0']+(['-R'] if reverse else []),input=(HERE/'native.patch').read_bytes(),cwd=scratch,capture_output=True)
  assert r.returncode==0 and not any(x in r.stdout.lower() for x in [b'offset',b'fuzz',b'failed',b'reject']),r.stdout
  for role in roles:assert (scratch/role).read_bytes()==((BASE if reverse else HERE/'candidate')/role).read_bytes()
assert not scratch.exists()
print(json.dumps({'exact_diagnostic_only':True,'provider_unchanged':True,'retained_and_logging_tests':13,'actual_dependency_no_action_tests':3,'compiled_behavioral_false_controls':4,'actual_arc_api_compile_rejection':1,'format':True,'patch_roundtrip':True,'scratch_removed':True,'native_typecheck':False}))

assert 'use std::sync::Arc;' not in (HERE/'TestSupport.rs').read_text()
assert 'use servo_arc::Arc;' in (HERE/'TestSupport.rs').read_text()
old=ROOT/'artifacts/css-font-metric-selected-reference-diagnostic-v1/candidate'/roles[0]
compat=''.join(difflib.unified_diff(old.read_text().splitlines(True),(HERE/'candidate'/roles[0]).read_text().splitlines(True),fromfile=str(old.relative_to(ROOT)),tofile=str((HERE/'candidate'/roles[0]).relative_to(ROOT))))
assert compat==(HERE/'COMPATIBILITY-DELTA.patch').read_text()
