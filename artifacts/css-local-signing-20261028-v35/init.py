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
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in inputs['references'].items(): assert sha(ROOT/name) == pin
assert sha(HERE/'commit.py') == inputs['commit_helper_sha256']
runtime = ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == inputs['initial_epoch']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == inputs['initial_head']
assert epoch['line_height_transition']['role'] == 'candidate'
assert epoch['line_height_transition']['compiled'] and not epoch['line_height_transition']['accepted']
assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs','servo/components/style/values/specified/font.rs'])
assert epoch['staged_working'] == {}
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
for n,b in controls.items():
    with (HERE/('PRE-'+n)).open('xb') as stream: stream.write(b)
with (HERE/'init-driver.log').open('x') as log:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),'init'],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),stdout=log,stderr=subprocess.STDOUT,check=True)
assert all((runtime/n).read_bytes() == b for n,b in controls.items())
print('Initialized reviewed final promoted epoch; canonical controls unchanged')
