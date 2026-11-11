import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent.parent
SOURCE=ROOT/'artifacts/css-pseudo-animation-transient-recascade-20261110-v3'
RUNTIME=ROOT/'artifacts/css-pseudo-animation-transient-recascade-runtime-20261110-v3'
INITIAL=ROOT/'artifacts/css-pseudo-animation-transient-recascade-runtime-20261110-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_manifest=json.loads((SOURCE/'SOURCE-ONLY.json').read_text())
runtime_manifest=json.loads((RUNTIME/'RUN-INPUTS.json').read_text())
assert sha(SOURCE/'SOURCE-ONLY.json')=='d79e802f50a8193e2f45297c3ea2f0e5ad906979551db4b28116c8abddb05138'
assert sha(RUNTIME/'RUN-INPUTS.json')=='b81b1a21cb270cf75a25f6a440402120c0272b30888de9d6c12e4ceca2bd03d7'
for directory,manifest in [(SOURCE,source_manifest),(RUNTIME,runtime_manifest)]:
 for name,digest in manifest.items(): assert sha(directory/name)==digest,name
roles=json.loads((RUNTIME/'SOURCE-ROLES.json').read_text())
assert set(roles)==set(json.loads((INITIAL/'SOURCE-ROLES.json').read_text()))
enum=json.loads((RUNTIME/'ENUM-AMENDMENT.json').read_text());marker=json.loads((RUNTIME/'MARKER-AMENDMENT.json').read_text())
assert len(enum['replacements'])==2 and sum(len(v) for v in enum['replacements'].values())==4
assert marker['path']=='servo/ports/geckolib/glue.rs'
changed=[]
for name in roles:
 expected=(INITIAL/'candidate'/name).read_text()
 for old,new in enum['replacements'].get(name,[]):
  assert expected.count(old)==1 and new=='PseudoStyleType::'+old.split('::')[1].capitalize()
  expected=expected.replace(old,new)
 if name==marker['path']:
  assert expected.count(marker['insertion_before'])==1
  expected=expected.replace(marker['insertion_before'],marker['insertion']+marker['insertion_before'])
 assert expected==(RUNTIME/'candidate'/name).read_text(),name
 assert (INITIAL/'source'/name).read_bytes()==(RUNTIME/'source'/name).read_bytes()
 if (INITIAL/'candidate'/name).read_bytes()!=(RUNTIME/'candidate'/name).read_bytes(): changed.append(name)
assert sorted(changed)==['dom/base/nsDOMWindowUtils.cpp','layout/style/ServoStyleSet.cpp','servo/ports/geckolib/glue.rs']
unchanged=['run.py','freeze.py','bundle.py','process.py','analyze.py','driver-analyze.py','recascade-analyze.py','parser-controls.py','driver-controls.py','recascade-controls.py','DRIVER-ASSERTIONS.json','RECASCADE-ASSERTIONS.json','EXPECTED-BASELINE.json','EXPECTED-CALLBACKS.json','EXPECTED-CHANGES.json']
for name in unchanged:assert (INITIAL/name).read_bytes()==(RUNTIME/name).read_bytes(),name
for name in ['pseudo-compose-cssom-lifetime.html','pseudo-compose-underlying.html','test_missing_pseudo_animation_query.html','test_missing_pseudo_animation_recascade.html','test-source-pins.json','manifest-sort.py']:
 assert (INITIAL/'runtime-inputs'/name).read_bytes()==(RUNTIME/'runtime-inputs'/name).read_bytes(),name
assert (RUNTIME/'candidate/dom/base/test/mochitest.toml').read_bytes()==(INITIAL/'candidate/dom/base/test/mochitest.toml').read_bytes()
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
checks={}
with tempfile.TemporaryDirectory(prefix='recascade-v3-review-') as directory:
 scratch=Path(directory)
 for label,origin,manifest in [('source',SOURCE,source_manifest),('runtime',RUNTIME,runtime_manifest)]:
  dest=scratch/label;dest.mkdir()
  for name in manifest:
   path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/name,path)
  if label=='runtime': shutil.copyfile(origin/'RUN-INPUTS.json',dest/'RUN-INPUTS.json')
  checker=dest/'check.py';text=checker.read_text()
  if label=='source':old='ROOT = HERE.parent.parent'
  else:old='ROOT = HERE.parents[1]'
  assert text.count(old)==1
  code=text.replace(old,'ROOT = Path('+repr(str(ROOT))+')')
  launcher='import sys; sys.argv='+repr([str(checker)]+(['--frozen'] if label=='runtime' else []))+'; exec(compile('+repr(code)+', '+repr(str(checker))+', \"exec\"), {\"__file__\": '+repr(str(checker))+', \"__name__\": \"__main__\"})'
  result=subprocess.run([sys.executable,'-B','-c',launcher],cwd=ROOT,env=env,capture_output=True,text=True)
  (HERE/(label+'-check.log')).write_text(result.stdout+result.stderr)
  assert result.returncode==0,result.stderr
  checks[label]={'exit':result.returncode,'copied_checker_root_locator_only':True,'checker_sha256':sha(checker)}
for directory,manifest in [(SOURCE,source_manifest),(RUNTIME,runtime_manifest)]:
 for name,digest in manifest.items():assert sha(directory/name)==digest,name
report={'status':'PASS','source_manifest':sha(SOURCE/'SOURCE-ONLY.json'),'runtime_frozen_manifest':sha(RUNTIME/'RUN-INPUTS.json'),'source_inputs':len(source_manifest),'runtime_inputs':len(runtime_manifest),'changed_candidate_paths':changed,'four_enum_tokens_and_marker_branch_only':True,'unchanged_runtime_and_parser_paths':unchanged,'checks':checks,'scratch_removed':not scratch.exists(),'native_build':False,'browser_execution':False}
(HERE/'AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
