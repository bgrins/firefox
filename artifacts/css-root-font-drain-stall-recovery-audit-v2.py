import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / 'artifacts/css-root-font-drain-stall-candidate-browser-v2'
RUN = ROOT / 'artifacts/css-root-font-drain-stall-candidate-browser-runtime-v2'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def absent_groups():
    result = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid='],
                            check=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        pid, pgid = map(int, line.split())
        assert not {pid, pgid} & {14591, 17520, 17521}, (pid, pgid)

manifest = 'f7181c2909625ab159a1353996fdf2bed1da009101443c0912ca2e6fe2fd6d07'
assert sha(OWNER / 'FILES.json') == manifest
for name, row in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == row['sha256'], name
policy = read(OWNER / 'POLICY.json')
capture = read(ROOT / policy['current_binding']['path'])
assert sha(ROOT / policy['current_binding']['path']) == policy['current_binding']['sha256']
pre = read(RUN / 'PAIR-PRE.json')
assert pre['snapshot'] == capture['snapshot']
absent_groups()
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
state = load('recovery_state', policy['state_helper'])
ownership = load('recovery_ownership', policy['ownership_helper'])
bundle = load('recovery_bundle', policy['bundle_helper'])
adapter = load('recovery_adapter', policy['capture_owner']['directory'] + '/baseline.py')
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
index = state.h.index_state(ROOT, env)
assert state.h.semantic_index(index) == state.h.semantic_index(capture['snapshot']['index'])
epoch = adapter.project_epoch(read(CANONICAL / 'CURRENT-EPOCH.json'))
epoch = copy.deepcopy(epoch)
old_raw = epoch['raw_index_observation']['current']
epoch['raw_index_observation']['current'] = index['raw_index']
snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
expected = copy.deepcopy(capture['snapshot'])
expected['index']['raw_index'] = index['raw_index']
assert snapshot == expected
for name, digest in capture['controls'].items():
    assert sha(CANONICAL / name) == digest
roles = read(OWNER / 'SOURCE-ROLES.json')
for name, role in roles.items():
    ownership.claim(ROOT, name, role['base_sha256'], pre['sources'][name]['identity'])
for name, record in policy['accepted_current_payloads'].items():
    ownership.claim(ROOT, name, record['sha256'], record['identity'])
for name, pin in policy['metadata_current_pins'].items():
    assert sha(ROOT / name) == pin
for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
    assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == capture['flag_hashes'][name]
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(RUN / 'APP-PRE.json'))
assert bundle.semantic({n: bundle.entry(ROOT / n) for n in policy['extra_backup_paths']}) == bundle.semantic(read(RUN / 'EXTRA-PRE.json'))
assert bundle.scan(RUN / 'backups') == read(RUN / 'BACKUPS.json')['owned_inventory']
assert state.a.verify_current(state.h, ROOT, env, epoch) == snapshot
absent_groups()
record = {
    'restored_sources': list(roles),
    'application_and_extras_unchanged': True,
    'semantic_index_unchanged': True,
    'raw_index_changed': old_raw != index['raw_index'],
    'old_raw_index': old_raw,
    'observed_snapshot': snapshot,
    'canonical_controls_unchanged': True,
    'owned_process_groups_absent': [14591, 17520, 17521],
    'source_transition_lock_absent': True,
    'backup_inventory_verified': True,
    'backup_retained': True,
    'original_failure_records_preserved': True,
    'native_build_completed': False,
    'browser_tests_run': False,
    'script_sha256': sha(Path(__file__)),
}
with (RUN / 'RECOVERY-AUDIT.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps(record))
