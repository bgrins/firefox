import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
REFRESH = ROOT / 'artifacts/css-root-font-cancellation-normal-handoff-raw-index-refresh-runtime-1'
NATIVE = ROOT / 'artifacts/css-root-font-cancellation-normal-handoff-candidate-browser-runtime-v2'
CONTROL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = read(ROOT / 'artifacts/css-root-font-cancellation-normal-handoff-candidate-browser-v2/POLICY.json')
result = read(REFRESH / 'RESULT.json')
epoch = read(CONTROL / 'CURRENT-EPOCH.json')
expected = read(REFRESH / 'PRE-CURRENT-EPOCH.json')
expected['raw_index_observation']['current'] = result['after']
assert epoch == expected == read(REFRESH / 'EPOCH.json')
assert sha(CONTROL / 'CURRENT-EPOCH.json') == result['epoch_sha256']
assert result['updated_only'] == 'raw_index_observation.current'
assert result['accepted_fix_increment'] == 0
for name in ('ROLE.json', 'OWNED.json'):
    assert sha(CONTROL / name) == policy['controls'][name]
assert not (CONTROL / 'SOURCE-TRANSITION.lock').exists()
state = load('refresh_verify_state', policy['state_helper'])
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
assert snapshot == read(REFRESH / 'POST.json') == read(REFRESH / 'PRE.json')
native_post = copy.deepcopy(read(NATIVE / 'POST.json'))
native_post['index']['raw_index'] = result['after']
assert snapshot == native_post
capture = read(ROOT / policy['current_binding']['path'])
for label, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == capture['flag_hashes'][label]
for name, record in read(NATIVE / 'RESTORATION.json')['sources'].items():
    path = ROOT / name
    assert sha(path) == record['sha256']
    assert [path.stat().st_dev, path.stat().st_ino] == record['identity']
for name, pin in policy['source_context_pins'].items():
    assert sha(ROOT / name) == pin
bundle = load('refresh_verify_bundle', policy['bundle_helper'])
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(NATIVE / 'APP-PRE.json'))
assert bundle.semantic({name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}) == bundle.semantic(read(NATIVE / 'EXTRA-PRE.json'))
assert all(sha(ROOT / name) == pin for name, pin in capture['binaries'].items())
report = dict(snapshot=snapshot, raw_only_epoch_change=True, source_app_flags_controls_verified=True,
              result_sha256=sha(REFRESH / 'RESULT.json'), script_sha256=sha(Path(__file__)))
with (REFRESH / 'ROOT-VERIFICATION.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('Independent raw-only refresh and complete preserved state verified')
