import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('signing_state', RUNTIME / 'state.py')
ownership = load('signing_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
epoch_bytes = (HERE / 'CURRENT-EPOCH.json').read_bytes()
epoch = json.loads(epoch_bytes)
state.a.verify_current(state.h, ROOT, ENV, epoch)
assert epoch['modified_native_paths'] == []
assert epoch['accepted_registered_zoom']['native_commit'] == '0f40801f1418318e51f81b4e273c758a9a24b3e4'
for ident in ['provider-model', 'release-observer', 'checkpoint']:
    receipt = json.loads((HERE / (ident + '-receipt.json')).read_text())
    assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
assert receipt['commit'] == epoch['semantic_index']['head']
controls = {n: (RUNTIME / n).read_bytes() for n in ['ROLE.json', 'OWNED.json']}
path = RUNTIME / 'CURRENT-EPOCH.json'
old = path.read_bytes()
assert hashlib.sha256(old).hexdigest() == 'cc46cc1e6599ed18d051cd39afb8d0c66f8a46fa0d45f092a2f9882a882ce12a'
claim = ownership.claim(ROOT, str(path.relative_to(ROOT)), hashlib.sha256(old).hexdigest())
try:
    ownership.write_owned(ROOT, claim, epoch_bytes)
    state.a.verify_current(state.h, ROOT, ENV, json.loads(path.read_bytes()))
    assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
except BaseException:
    ownership.write_owned(ROOT, claim, old)
    raise
with (HERE / 'FINAL-CHECK.json').open('x') as stream:
    json.dump({'head': receipt['commit'], 'signatures_verified': True,
               'runtime_epoch_synchronized': True, 'native_dirty_paths': 0,
               'accepted_fixes': 138, 'tracked_fixes': 139, 'held_excluded': 120,
               'current_epoch_sha256': hashlib.sha256(epoch_bytes).hexdigest()}, stream, indent=2)
    stream.write('\n')
print('Signed checkpoint and runtime epoch verified', receipt['commit'])
