import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('build_failure_review', HERE / 'verify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
config = read(HERE / 'POLICY.json')
assert config['execution_enabled'] is False
for name, record in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == record['sha256']
runtime = ROOT / config['runtime_directory']
for name, digest in config['saved_runtime_inputs'].items():
    assert sha(runtime / name) == digest
for name in config['absent_paths']:
    assert not (runtime / name).exists() and not (runtime / name).is_symlink()
data = [read(runtime / 'CANDIDATE-RESULT.json'), read(runtime / 'candidate-build/build-RESULT.json'),
        read(runtime / 'RESTORATION.json'), read(runtime / 'BACKUP-CLEANUP.json'), 1]
module.failure_join(*data)
negative = []
for label, index, key, value in [
    ('false success', 0, 'success', True), ('wrong error', 0, 'error', 'other'),
    ('browser phase', 0, 'candidate_phase', {}), ('publication error', 0, 'publication_errors', ['x']),
    ('restoration false', 0, 'restoration_verified', False), ('changed controls', 0, 'runtime_controls_unchanged', False),
    ('staged mutation', 0, 'empty_staging_preserved', False), ('native acceptance', 0, 'native_fix_acceptance', True),
    ('build passed', 1, 'exit', 0), ('different build error', 1, 'exit', 101),
    ('build group live', 1, 'owned_group_absent', False), ('cleanup error', 1, 'cleanup_errors', ['x']),
    ('process error', 1, 'error', 'timeout'), ('cancelled', 1, 'stop_reason', 'TERMINATION_REQUESTED'),
    ('restore errors', 2, 'errors', ['x']), ('owned process', 2, 'owned_processes', {'x': 1}),
    ('unverified backup', 3, 'verified_original_restoration', False),
    ('already removed', 3, 'removed', True), ('not retained', 3, 'retained_after_failure', False),
]:
    bad = copy.deepcopy(data)
    bad[index][key] = value
    try:
        module.failure_join(*bad)
    except AssertionError:
        negative.append(label)
    else:
        raise AssertionError(label)
try:
    module.failure_join(*data[:4], 0)
except AssertionError:
    negative.append('wrong terminal exit')
else:
    raise AssertionError('wrong terminal exit')
previous = (ROOT / 'artifacts/css-contextual-duration-masked-snapshot-root-review-v1/verify.py').read_text()
current = (HERE / 'verify.py').read_text()
begin = '    for name, role in roles.items():'
end = "    assert backup['removed'] and not backup['retained_after_failure']"
block = previous[previous.index(begin):previous.index(end)]
assert current[current.index(begin):current.index(begin) + len(block)] == block
begin = "    if observation['before'] != observation['after']:"
assert previous[previous.index(begin):] == current[current.index(begin):]
assert current.index('state.a.verify_current') < current.index('shutil.rmtree')
assert current.index("bundle.scan(PAIR / 'backups')") < current.index('shutil.rmtree')
assert "assert set(restoration['sources']) == set(roles)" in current
assert "owner.claim(ROOT, name, role['base_sha256'], claim['identity'])" in current
pre = read(runtime / 'CANDIDATE-PRE.json')
roles = read(ROOT / config['owner_directory'] / 'SOURCE-ROLES.json')
assert len(roles) == len(data[2]['sources']) == 7
for name, role in roles.items():
    assert data[2]['sources'][name]['sha256'] == role['base_sha256'] == pre['sources'][name]['base_sha256']
    assert data[2]['sources'][name]['identity'] == pre['sources'][name]['identity']
snapshot = copy.deepcopy(pre['snapshot'])
snapshot['index']['raw_index'] = read(runtime / 'RAW-INDEX-OBSERVATION.json')['after']
assert snapshot == read(runtime / 'POST.json')
assert data[3]['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(runtime / 'BACKUPS.json')['bytes'] == 1008605176
print(json.dumps({'actual_failure_join': True, 'negative_controls': negative,
                  'seven_saved_source_preimages_and_inodes': True, 'saved_snapshot_raw_only': True,
                  'unchanged_source_app_fullstate_block': True, 'unchanged_raw_epoch_rollback_tail': True,
                  'live_guard_or_backup_delete_executed': False}, indent=2))
