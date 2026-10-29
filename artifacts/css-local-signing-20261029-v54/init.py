import hashlib
import json
import os
import runpy
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
inputs = json.loads((HERE/'INPUTS.json').read_bytes())
assert inputs['execution_enabled'] is True and inputs['final_validation_ready'] is True
assert ROOT/inputs['signing_directory'] == HERE
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in inputs['references'].items(): assert sha(ROOT/name) == pin
runpy.run_path(str(HERE/'final_validation.py'))['verify'](ROOT,inputs)
assert sha(HERE/'commit.py') == inputs['commit_helper_sha256']
runtime = ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == inputs['initial_epoch']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == inputs['initial_head']
assert epoch['shadow_move_context_transition']['role'] == 'candidate'
assert epoch['shadow_move_context_transition']['compiled'] and not epoch['shadow_move_context_transition']['accepted']
assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs',*inputs['native_source_paths'], *inputs['deleted_preimages']])
assert epoch['staged_working'] == {}
for marker, expected in inputs['preserved_accepted_markers'].items(): assert epoch[marker] == expected
for marker, expected in inputs['preserved_accepted_transitions'].items(): assert epoch[marker] == expected
native_pins=json.loads((HERE/'native-selection.json').read_bytes())['source_pins']
assert not set(native_pins).intersection(inputs['preserved_accepted_payload'])
assert set(inputs['native_source_paths']) == {'dom/base/Element.cpp', 'dom/base/ShadowRoot.cpp', 'dom/base/ShadowRoot.h'}
assert len(inputs['preserved_accepted_payload']) == 20
runpy.run_path(str(HERE/'deletion.py'))['verify'](ROOT,inputs,epoch,json.loads((HERE/'native-selection.json').read_bytes()),inputs['initial_head'])
for path, item in inputs['preserved_accepted_payload'].items():
    st=(ROOT/path).lstat()
    assert [st.st_dev,st.st_ino] == item['identity'] and sha(ROOT/path) == item['sha256']
    assert epoch['pins'][path] == item['sha256'] and epoch['installed_identities'][path] == item['identity']
assert not os.path.lexists(ROOT/inputs['retired_path'])
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
audit=json.loads((ROOT/inputs['untracked_audit']).read_bytes())
landing={p for p in json.loads((HERE/'native-selection.json').read_bytes())['files'] if p.startswith('testing/web-platform/tests/')}
assert len(landing)==4 and not landing.intersection(audit['paths'])
raw=subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false','ls-files','--others','--exclude-standard','-z'],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
untracked=sorted(p.decode() for p in raw.split(b'\0') if p)
assert set(untracked)==set(audit['paths'])|landing
with (HERE/'INITIAL-UNTRACKED.json').open('x') as stream:json.dump({'paths':untracked,'audit_sha256':sha(ROOT/inputs['untracked_audit']),'only_added':sorted(landing)},stream,indent=2)
for n,b in controls.items():
    with (HERE/('PRE-'+n)).open('xb') as stream: stream.write(b)
with (HERE/'init-driver.log').open('x') as log:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),'init'],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),stdout=log,stderr=subprocess.STDOUT,check=True)
assert all((runtime/n).read_bytes() == b for n,b in controls.items())
print('Initialized reviewed final promoted epoch; canonical controls unchanged')
