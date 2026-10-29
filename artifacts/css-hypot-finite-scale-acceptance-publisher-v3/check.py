import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = read(HERE/'INPUTS.json')
assert inputs['execution_enabled'] and inputs['publication_enabled'] and inputs['final_validation_ready'] and inputs['activation_pending']==[]
assert inputs['previous_accepted_fixes']==147 and inputs['fix']==149
assert len(inputs['preserved_accepted_payload'])==27
for name,pin in {**inputs['references'],**inputs['evidence_pins'],**inputs['prior_checkpoint_evidence'],**inputs['ledger_preimages']}.items():assert sha(ROOT/name)==pin,name
assert sha(HERE/'commit.py')==inputs['commit_helper_sha256']
assert sha(HERE/'readout/render.py')==inputs['readout_renderer_sha256']
for path in HERE.rglob('*.py'):ast.parse(path.read_text())
selection=read(HERE/'native-selection.json')
assert set(selection['files'])==set(selection['source_pins'])=={'servo/components/style/values/generics/calc.rs','testing/web-platform/tests/css/css-values/hypot-finite-scale.html'}
accept=read(ROOT/inputs['acceptance_path'])
assert accept['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT' and accept['root_acceptance_approved']
assert accept['payload_sha256']==sha(HERE/'native-selection.json') and accept['evidence_pins']==inputs['evidence_pins']
assert accept['approved_roadmap'].encode().endswith((ROOT/'artifacts/css-continuation-roadmap-20261028-v1/PLAN.md').read_bytes())
cp=read(ROOT/inputs['research_checkpoint']['final_check'])
assert cp['head']==inputs['initial_head'] and cp['current_epoch_sha256']==inputs['initial_epoch']
assert cp['signature_verified'] and cp['runtime_epoch_synchronized'] and cp['pending_hypot_native_payload_preserved']
assert cp['final_validation']==inputs['expected_final_validation']
runtime=ROOT/'artifacts/css-registered-number-native-runtime-v1'
assert sha(runtime/'CURRENT-EPOCH.json')==inputs['initial_epoch']
epoch=read(runtime/'CURRENT-EPOCH.json')
assert epoch['semantic_index']['head']==inputs['initial_head'] and epoch['staged_working']=={}
for marker,value in inputs['preserved_accepted_markers'].items():assert epoch[marker]==value
for marker,value in inputs['preserved_accepted_transitions'].items():assert epoch[marker]==value
for name,record in inputs['preserved_accepted_payload'].items():
    expected=selection['source_pins'].get(name,record['sha256'])
    assert sha(ROOT/name)==expected==epoch['pins'][name]
    st=(ROOT/name).lstat();assert [st.st_dev,st.st_ino]==record['identity']
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def git(*args):return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=ROOT,env=env)
assert git('rev-parse','HEAD').decode().strip()==inputs['initial_head']
assert not git('diff','--cached','--name-only')
for name,pin in inputs['research_commit_payloads'].items():assert hashlib.sha256(git('show',inputs['initial_head']+':'+name)).hexdigest()==pin
subprocess.run(['git','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',inputs['initial_head']],cwd=ROOT,env=env,check=True)
audit=read(ROOT/inputs['untracked_audit'])
untracked={name.decode() for name in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if name}
assert len(untracked)==564 and len(audit['paths'])==563
assert untracked==set(audit['paths'])|{'testing/web-platform/tests/css/css-values/hypot-finite-scale.html'}
assert len(audit['project_files'])==68 and audit['unrelated_count']==495
for row in audit['project_files']:
    st=(ROOT/row['path']).lstat();assert [st.st_dev,st.st_ino]==row['identity'];assert sha(ROOT/row['path'])==row['sha256']
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
spec=importlib.util.spec_from_file_location('hypot_publisher_evidence',HERE/'evidence.py');evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
observed=evidence.verify(ROOT,inputs)
assert sha(runtime/'CURRENT-EPOCH.json')==inputs['initial_epoch']
print(json.dumps({'status':'READY_FOR_ROOT_REVIEW','references_and_bindings_authenticated':True,'source_claims':27,'untracked_before':564,'baseline_untracked':563,'project_claims':68,'recorded_raw_replay':observed,'canonical_mutation':False,'owner_execution':False}))
