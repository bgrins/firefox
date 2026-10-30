import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / 'artifacts/css-hyphenation-ownership-native-pair-v1'
RUNTIME = ROOT / 'artifacts/css-hyphenation-ownership-native-pair-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha((OWNER / 'FILES.json').read_bytes()) == '1a5490029693ea49aa591b0902f2d4a185d71a3954ee88edf0cc4b89d4d369d2'
baseline = load('paired_live_baseline', 'artifacts/css-hyphenation-ownership-native-pair-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
FAILURE_PINS = {'RESULT.json': 'e8d46acd85f7945f46dff59f1e97312899dba443c8788583f8ffe5f052b4770e', 'ROOT-OWNER-TERMINAL.json': '7290711bddac7cc256bd74053c75812422fbc47216d737ad999506c60ba4fe97', 'FAILURE-TRACEBACK.json': '1a27d6e7189b4a9a218ef202d0d7532ac744ae519e4297be627d0c3da2df7e03', 'BACKUPS.json': 'b71bdb3539a32157ff41ef856a2df123490079cf0eae36b3592b1953fdc8a8c8', 'BACKUP-CLEANUP.json': '6f12623f10ab4b3112d092f8e7e99d9254934b9a3cc26281a9d1ea20afb656d5', 'RESTORATION.json': '98ccbeb52e5ef54cac2e5c04e86f597be25c89ab45ce9f43e5d82ddf98284c86', 'POST.json': 'ceae2be6f0b0ae1752b8d8ca4ef4da3ec95e1f90d9e030107a9568839fc6b129', 'PAIR-PRE.json': 'be80b8b06cc5efbd7e36b13740cc8caab84c75215268ff75b1aa1ee1c666fff9'}
result = read(RUNTIME / 'RESULT.json')
for name, digest in FAILURE_PINS.items():
    assert sha((RUNTIME / name).read_bytes()) == digest
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal == {'session': 27391, 'launch': '71c531', 'terminal': True,
                    'terminal_chunk': 'aa5684', 'exit': 1,
                    'result_sha256': FAILURE_PINS['RESULT.json']}
trace = read(RUNTIME / 'FAILURE-TRACEBACK.json')
assert trace['error'] == 'AssertionError()'
assert 'line 167, in main\n    assert free() >= 27 * 1024**3' in trace['traceback']
assert set(result['phase']) == {'original'}
assert set(result['phase']['original']) == set(policy['lane_order'] + policy['diagnostic_lane_order'])
assert result['error'] == 'AssertionError()' and result['publication_errors'] == []
assert not any(path.name.startswith('candidate-') for path in RUNTIME.iterdir())
built = read(RUNTIME / 'original-build/build-RESULT.json')
assert built['exit'] == 0 and built['stop_reason'] is None and built['error'] is None
assert built['cleanup_errors'] == [] and built['owned_group_absent']
build_command = read(RUNTIME / 'original-build/COMMAND.json')
assert build_command['owner_manifest'] == sha((OWNER / 'FILES.json').read_bytes())
assert build_command['source_role'] == 'original'
assert build_command['source_sha256'] == {name: role['base_sha256'] for name, role in roles.items()}
for lane, descriptor in result['phase']['original'].items():
    phase = RUNTIME / ('original-wpt-' + lane)
    for key, filename in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'),
                          ('result_sha256', 'RESULT.json'), ('behavior_sha256', 'BEHAVIOR-COMPARISON.json')]:
        assert sha((phase / filename).read_bytes()) == descriptor[key]
    outcome = read(phase / 'RESULT.json')
    assessment = read(phase / 'ASSESSMENT.json')
    assert outcome['success'] and outcome['preservation_verified'] and outcome['execution_error'] is None
    assert assessment['complete'] and assessment['errors'] == []
    expected_count, expected_ends = {'target': (169, 1), 'regression': (720, 21), 'context': (8, 1)}[lane]
    assert assessment['observed_subtest_count'] == expected_count and len(assessment['ends']) == expected_ends

assert result['success'] is False and result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups = []
for role in ('original',):
    build = RUNTIME / (role + '-build')
    for process_file, cleanup_file in [('build-PROCESS.json', 'build-GROUP-CLEANUP.json'),
                                       ('WAKE-PROCESS.json', 'wake-GROUP-CLEANUP.json')]:
        group = read(build / process_file)['pgid']
        assert read(build / cleanup_file)['owned_group_absent']
        ownership.group_absent(group)
        absent_groups.append(group)
    for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
        phase = RUNTIME / (role + '-wpt-' + lane)
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        group = read(phase / 'PROCESS.json')['pgid']
        ownership.group_absent(group)
        absent_groups.append(group)
        temporary = Path(read(phase / 'COMMAND.json')['temporary_root'])
        assert not temporary.exists() and not temporary.is_symlink()
for name, digest in policy['controls'].items():
    assert sha((CANONICAL / name).read_bytes()) == digest
baseline.metadata_guard(policy)
for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
    assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
state = load('paired_live_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
epoch = read(CANONICAL / 'CURRENT-EPOCH.json')
index = state.h.index_state(ROOT, ENV)
assert state.h.semantic_index(index) == epoch['semantic_index']
adjusted = copy.deepcopy(epoch)
adjusted['raw_index_observation']['current'] = index['raw_index']
observed = state.a.verify_current(state.h, ROOT, ENV, adjusted)
expected = copy.deepcopy(capture['snapshot'])
expected['index']['raw_index'] = index['raw_index']
assert observed == expected == read(RUNTIME / 'POST.json')
for label, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert sha(state.h.git(path, ENV, 'ls-files', '-v', '-z')) == capture['flag_hashes'][label]
for name, role in roles.items():
    assert sha((ROOT / name).read_bytes()) == role['base_sha256']
    claim = read(RUNTIME / 'PAIR-PRE.json')['sources'][name]
    assert [(ROOT / name).stat().st_dev, (ROOT / name).stat().st_ino] == claim['identity']
bundle = load('paired_live_bundle', policy['bundle_helper'])
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(RUNTIME / 'APP-PRE.json'))
extras = {name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}
assert bundle.semantic(extras) == bundle.semantic(read(RUNTIME / 'EXTRA-PRE.json'))
assert all(sha((ROOT / name).read_bytes()) == digest for name, digest in capture['binaries'].items())
metadata = load('paired_live_metadata', policy['wpt']['metadata_helper'])
application = metadata.application_metadata(ROOT / policy['wpt']['application_ini'], policy['restored_application_revision'])
semantic_metadata = lambda row: {key: value for key, value in row.items() if key not in ('entry_identity', 'identity')}
assert semantic_metadata(application) == semantic_metadata(capture['application_metadata'])
cleanup = read(RUNTIME / 'BACKUP-CLEANUP.json')
assert cleanup['removed'] is False and cleanup['retained_after_failure'] is True
assert cleanup['verified_original_restoration'] is True
backups = read(RUNTIME / 'BACKUPS.json')
assert cleanup['owned_backup_bytes'] == backups['bytes'] == 1008605176
assert not (RUNTIME / 'backups').is_symlink()
assert bundle.scan(RUNTIME / 'backups') == backups['owned_inventory']
assert not read(RUNTIME / 'RESTORATION.json')['errors']
assert not read(RUNTIME / 'RESTORATION.json')['owned_processes']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
output = RUNTIME / 'ROOT-LIVE-RESTORATION.json'
with output.open('x') as stream:
    json.dump({'independent_live_restoration_verified': True, 'snapshot': observed,
               'application_and_extras_semantically_restored': True,
               'source_and_binary_hashes_restored': True, 'flags_restored': True,
               'controls_unchanged': True, 'backup_removed': False, 'retained_backup_inventory_verified': True,
               'backup_inventory_sha256': FAILURE_PINS['BACKUPS.json'],
               'owner_terminal': terminal, 'failure_pins': FAILURE_PINS,
               'independently_absent_process_groups': absent_groups,
               'restored_application_metadata': application,
               'owner_result_sha256': sha((RUNTIME / 'RESULT.json').read_bytes()),
               'audit_script_sha256': sha(Path(__file__).read_bytes()),
               'native_acceptance': False}, stream, indent=2)
    stream.write('\n')
print('Independent live source, application, controls, index and flags audit passed')
