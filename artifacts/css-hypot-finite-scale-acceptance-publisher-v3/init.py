import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
inputs = json.loads((HERE/'INPUTS.json').read_bytes())
assert inputs['execution_enabled'] is True and inputs['final_validation_ready'] is True
assert ROOT/inputs['signing_directory'] == HERE
assert inputs['activation_pending'] == []
checkpoint = json.loads((ROOT/inputs['research_checkpoint']['final_check']).read_bytes())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/inputs['research_checkpoint']['final_check']) == inputs['research_checkpoint']['final_check_sha256']
assert checkpoint['head'] == inputs['initial_head'] and checkpoint['signature_verified'] and checkpoint['runtime_epoch_synchronized']
assert checkpoint['pending_hypot_native_payload_preserved'] is True
assert checkpoint['accepted_fixes']==147 and checkpoint['tracked_fixes']==148
assert checkpoint['final_validation']==inputs['expected_final_validation']
for name,pin in inputs['research_commit_payloads'].items():
    body=subprocess.check_output(['git','show',inputs['initial_head']+':'+name],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
    assert hashlib.sha256(body).hexdigest()==pin
subprocess.run(['git','-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',inputs['initial_head']],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),check=True)
for name,pin in inputs['references'].items(): assert sha(ROOT/name) == pin
assert sha(HERE/'commit.py') == inputs['commit_helper_sha256']
import importlib.util
spec=importlib.util.spec_from_file_location('hypot_acceptance_evidence',HERE/'evidence.py')
evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
assert evidence.verify(ROOT,inputs)['targets_pass']==16
runtime = ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == inputs['initial_epoch']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == inputs['initial_head']
assert epoch['hypot_finite_scale_transition']['role'] == 'candidate'
assert epoch['hypot_finite_scale_transition']['compiled'] and not epoch['hypot_finite_scale_transition']['accepted']
assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs',*inputs['native_source_paths']])
assert epoch['staged_working'] == {}
for marker, expected in inputs['preserved_accepted_markers'].items(): assert epoch[marker] == expected
superseded=inputs['accepted_source_supersession']
assert superseded['fix']==145 and superseded['path']=='servo/components/style/values/generics/calc.rs'
assert epoch['hypot_finite_scale_transition']['supersedes_source_pin']==superseded
assert inputs['preserved_accepted_markers']['accepted_round_context_quotient']['files'][superseded['path']]==superseded['sha256']
historical_commit=inputs['preserved_accepted_markers']['accepted_round_context_quotient']['native_commit']
for revision in (historical_commit,inputs['initial_head']):
    body=subprocess.check_output(['git','show',revision+':'+superseded['path']],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
    assert hashlib.sha256(body).hexdigest()==superseded['sha256']
for marker, expected in inputs['preserved_accepted_transitions'].items(): assert epoch[marker]==expected
native_pins=json.loads((HERE/'native-selection.json').read_bytes())['source_pins']
assert set(native_pins).intersection(inputs['preserved_accepted_payload'])=={superseded['path']}
for path, item in inputs['preserved_accepted_payload'].items():
    expected=native_pins[path] if path==superseded['path'] else item['sha256']
    st=(ROOT/path).lstat()
    assert [st.st_dev,st.st_ino] == item['identity'] and sha(ROOT/path) == expected
    assert epoch['pins'][path] == expected and epoch['installed_identities'][path] == item['identity']
assert not os.path.lexists(ROOT/inputs['retired_path'])
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
audit=json.loads((ROOT/inputs['untracked_audit']).read_bytes())
landing={p for p in json.loads((HERE/'native-selection.json').read_bytes())['files'] if p.startswith('testing/web-platform/tests/')}
assert len(landing)==1 and not landing.intersection(audit['paths'])
raw=subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false','ls-files','--others','--exclude-standard','-z'],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
untracked=sorted(p.decode() for p in raw.split(b'\0') if p)
assert set(untracked)==set(audit['paths'])|landing
assert len(audit['paths'])==563 and len(untracked)==564
assert landing=={'testing/web-platform/tests/css/css-values/hypot-finite-scale.html'}
with (HERE/'INITIAL-UNTRACKED.json').open('x') as stream:json.dump({'paths':untracked,'audit_sha256':sha(ROOT/inputs['untracked_audit']),'only_added':sorted(landing)},stream,indent=2)
for n,b in controls.items():
    with (HERE/('PRE-'+n)).open('xb') as stream: stream.write(b)
with (HERE/'init-driver.log').open('x') as log:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),'init'],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),stdout=log,stderr=subprocess.STDOUT,check=True)
assert all((runtime/n).read_bytes() == b for n,b in controls.items())
print('Initialized reviewed final promoted epoch; canonical controls unchanged')
