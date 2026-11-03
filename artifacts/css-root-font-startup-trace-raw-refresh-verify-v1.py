import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
REFRESH = ROOT / 'artifacts/css-root-font-startup-trace-raw-index-refresh-runtime-1'
NATIVE = ROOT / 'artifacts/css-root-font-startup-trace-candidate-browser-runtime-v1'
CONTROL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert len(sys.argv) == 2 and len(sys.argv[1]) == 64
ownership = load('refresh_verify_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
refresh_owner = ROOT / 'artifacts/css-root-font-startup-trace-raw-index-refresh-v1'
ownership.authenticate(refresh_owner, '8c5273502b3b5ebaa872e900a35bcacfb73020b2dad7e3188bca2298076c4d86')
refresh_policy = read(refresh_owner / 'POLICY.json')
assert sha(REFRESH / 'RESULT.json') == sys.argv[1]
native_policy_path = 'artifacts/css-root-font-startup-trace-candidate-browser-v1/POLICY.json'
assert sha(ROOT / native_policy_path) == refresh_policy['references'][native_policy_path]
assert sha(NATIVE / 'ROOT-LIVE-RESTORATION.json') == refresh_policy['live_audit']['sha256']
policy = read(ROOT / native_policy_path)
result = read(REFRESH / 'RESULT.json')
assert result['old_epoch_sha256'] == refresh_policy['controls']['CURRENT-EPOCH.json'] == sha(REFRESH / 'PRE-CURRENT-EPOCH.json')
assert result['before'] == refresh_policy['raw_before']
assert result['frozen_pair_after'] == refresh_policy['raw_after']
assert result['head'] == refresh_policy['head'] and result['preservation_verified']
assert result['signed_commit_receipt'] == refresh_policy['signed_receipt']
assert result['existing_head_signature_verified'] and result['restoration_independently_verified']
assert not result['native_fix_acceptance']
epoch = read(CONTROL / 'CURRENT-EPOCH.json')
expected = read(REFRESH / 'PRE-CURRENT-EPOCH.json')
expected['raw_index_observation']['current'] = result['after']
assert epoch == expected == read(REFRESH / 'EPOCH.json')
assert sha(CONTROL / 'CURRENT-EPOCH.json') == result['epoch_sha256']
assert result['updated_only'] == 'raw_index_observation.current'
assert result['accepted_fix_increment'] == 0
for name in ('ROLE.json', 'OWNED.json'):
    assert sha(CONTROL / name) == policy['controls'][name]
assert not (CONTROL / 'SOURCE-TRANSITION.lock').exists() and not (CONTROL / 'SOURCE-TRANSITION.lock').is_symlink()
for pgid in read(NATIVE / 'ROOT-LIVE-RESTORATION.json')['independently_absent_process_groups']:
    ownership.group_absent(pgid)
assert not (NATIVE / 'backups').exists() and not (NATIVE / 'backups').is_symlink()
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
