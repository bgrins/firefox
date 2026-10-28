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
initial = json.loads((HERE / 'INITIAL-EPOCH.json').read_text())
expected_sources = {
    'servo/components/style/custom_properties.rs': '3e8627d4eb4ae65ec68e84209bc016c7125f706a2ad6b90b144e0dbf39e5e786',
    'servo/components/style/properties/cascade.rs': '2b90f1076fed1803250214b41577dff55b31c84bef7feee27bcdd8da9448d6a6',
}
assert set(epoch['modified_native_paths']) == set(initial['modified_native_paths']) == set(expected_sources)
assert all(epoch['pins'][name] == initial['pins'][name] == pin for name, pin in expected_sources.items())
assert epoch['registered_number_transition'] == initial['registered_number_transition'] == {
    'role': 'candidate', 'variant': 'registered-provider-default-v4', 'compiled': True,
    'accepted': False, 'last_phase': 'provider-default-candidate-build-2',
}
for key in ['installed_identities', 'untracked_native', 'nested_semantic_index', 'accepted_registered_zoom']:
    assert epoch[key] == initial[key], key
nonartifact = lambda e: {n: pin for n, pin in e['pins'].items() if not n.startswith('artifacts/')}
assert nonartifact(epoch) == nonartifact(initial)
parent = initial['semantic_index']['head']
assert epoch['accepted_registered_zoom']['native_commit'] == '0f40801f1418318e51f81b4e273c758a9a24b3e4'
for ident in ['cycle-model', 'initial-independence', 'provider-observations', 'provider-repair', 'checkpoint']:
    receipt = json.loads((HERE / (ident + '-receipt.json')).read_text())
    assert receipt['signature_verified'] and receipt['working_bodies_and_nested_index_preserved']
    assert receipt['parent'] == parent
    assert all(name.startswith('artifacts/') and name != 'artifacts/css-spec-lean' and not name.startswith('artifacts/css-spec-lean/') for name in receipt['files'])
    parent = receipt['commit']
assert receipt['commit'] == epoch['semantic_index']['head']
candidate_evidence = ROOT / 'artifacts/css-registered-provider-expanded-observation-runtime-candidate-1'
assert hashlib.sha256((candidate_evidence / 'FILES.json').read_bytes()).hexdigest() == 'd91ae11c920ec7c99a1decf652a3ee41432f25e00a19e1403984caf569b949a0'
manifest = json.loads((candidate_evidence / 'FILES.json').read_text())['files']
for name in ['RESULT.json', 'ASSESSMENT.json', 'COMPARISON.json']:
    assert hashlib.sha256((candidate_evidence / name).read_bytes()).hexdigest() == manifest[name]['sha256']
candidate_result = json.loads((candidate_evidence / 'RESULT.json').read_text())
assert candidate_result['observation_gate_passed'] and candidate_result['exact_staging_preserved'] and not candidate_result['native_fix_acceptance']
controls = {n: (RUNTIME / n).read_bytes() for n in ['ROLE.json', 'OWNED.json']}
expected_controls = {'ROLE.json': 'c4902d49770e51e39379d53780504a9e2aac0d9c8a2307a44c743b7dea8c3a27', 'OWNED.json': '521d3fcb200cf7dff5f45e23fe1cf564a8d254423a5051a915e7828821282c2f'}
assert all(hashlib.sha256(body).hexdigest() == expected_controls[n] for n, body in controls.items())
path = RUNTIME / 'CURRENT-EPOCH.json'
old = path.read_bytes()
assert hashlib.sha256(old).hexdigest() == '32282c6b8a3a67b9c69e5c40ddba572a9d30a9fc4f72e02f1b78ec855e2a3188'
claim = ownership.claim(ROOT, str(path.relative_to(ROOT)), hashlib.sha256(old).hexdigest())
try:
    assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
    ownership.write_owned(ROOT, claim, epoch_bytes)
    state.a.verify_current(state.h, ROOT, ENV, json.loads(path.read_bytes()))
    assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
except BaseException:
    ownership.write_owned(ROOT, claim, old)
    raise
with (HERE / 'FINAL-CHECK.json').open('x') as stream:
    json.dump({'head': receipt['commit'], 'signatures_verified': True,
               'runtime_epoch_synchronized': True, 'native_dirty_paths': 2, 'provider_candidate_accepted': False, 'candidate_browser_executed': True, 'candidate_browser_evidence': 'artifacts/css-registered-provider-expanded-observation-runtime-candidate-1/FILES.json',
               'accepted_fixes': 138, 'tracked_fixes': 139, 'held_excluded': 120,
               'current_epoch_sha256': hashlib.sha256(epoch_bytes).hexdigest()}, stream, indent=2)
    stream.write('\n')
print('Signed checkpoint and runtime epoch verified', receipt['commit'])
