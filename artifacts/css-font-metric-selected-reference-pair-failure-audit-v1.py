import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / 'artifacts/css-font-metric-selected-reference-pair-v1'
RUNTIME = ROOT / 'artifacts/css-font-metric-selected-reference-pair-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FAILURE_PINS = {'RESULT.json': '20c2a710262b43fca3eab2eeacae97b89c57b80663807b62836010135602029e', 'ROOT-OWNER-TERMINAL.json': 'd13c807686a2fcfd32ad3cd7fcb606a0151fabe9c8247bc254778c73afb4bff1', 'FAILURE-TRACEBACK.json': 'e9ac0d311b34e364d1fa61f4d2f0b40aaaeb0adc956f067739ef86f7b280062d', 'BACKUPS.json': '007d0b4e10dfc90f3ff9b8f7771871a9fe794e7a0835054ca80f41666f798b83', 'BACKUP-CLEANUP.json': '6f12623f10ab4b3112d092f8e7e99d9254934b9a3cc26281a9d1ea20afb656d5', 'RESTORATION.json': '085d5fd12ed819666cfaba780e0214136c5aa03f5ddf3b5939e9f35c87a489c7', 'POST.json': '2cd6ccc2bf86d01f3bf3e8233d409853e3736ef01dc29d8e2b68c0266e502943', 'PAIR-PRE.json': '3a4bdd503fdc456fd0a738f59e0ba6553ce7e1d14bd5c479b8c913a329c923d2', 'original-wpt-metric/RESULT.json': 'dbef1486fff5aacaabeeaba010da75b340d83bb0095fa8add9ef7e7099b6735c', 'original-wpt-metric/ASSESSMENT.json': '0b1676c7207b9bea3e0f330f11da96793a56ad46060be0335bc4349f1024660b', 'original-wpt-metric/raw.jsonl': 'd4f4529b0afeda0324a8ecac91eda08e2cc7f45344dcd19e59a7c0f2e37bfc92', 'original-wpt-phase/RESULT.json': '4d9bc9314f55529d9c44c18b63a1209a4e3189b402bc64059137595fe64b611f', 'original-wpt-phase/ASSESSMENT.json': '9cc722bbd0877fa0c615d5c286775e219c7feb7cda1604b7443f06b9ef29599c', 'original-wpt-phase/raw.jsonl': '75121b32944c48d388a3f1e45f245eb359e60755cbcc5b25903898f244bfd5dc', 'original-wpt-typedattr/RESULT.json': '411cd8e9d98567731a9e41ad4cb348b7b57911437a238dbda965fd87c4edc475', 'original-wpt-typedattr/ASSESSMENT.json': 'a0d99a31fdd66cb23d166e803f848f93c4c859dcab53bf7dcbb69161ce12f2b1', 'original-wpt-typedattr/raw.jsonl': '9f4c277381e189ee9336e28aca77ce58757110be0251079eb5c125bf184158ec', 'candidate-wpt-metric/RESULT.json': 'b57cefb57899fbedfe7c0aaab31a93e2921e659d1912e1ae4dd45fd4b8b04952', 'candidate-wpt-metric/ASSESSMENT.json': '12a250424af9bc3af54cf4e7816518dfc902219f7436ca474b1b5f022182f2a4', 'candidate-wpt-metric/raw.jsonl': 'f7ea9038890854e43a930c982143543c1f65a0a393ceee1a8827889412e2da0d', 'candidate-wpt-phase/RESULT.json': 'be655c89e09c2cbde3b0f073710a23a770fb75e1459df558cb5f045ff9a06bf7', 'candidate-wpt-phase/ASSESSMENT.json': '8cdea11bbf9282131e81a4c478cc1c2f01910127c8e8e061305e7dbbf9a137ae', 'candidate-wpt-phase/raw.jsonl': 'ec684c902c81a7e15c164caab408c78658826541b58903b85d9406b8506f80d7', 'candidate-wpt-typedattr/RESULT.json': 'a51f26e84d1e0d7dcae5918da789204a072f2ff08ecf8d4ef7398c7f3f498936', 'candidate-wpt-typedattr/ASSESSMENT.json': '2b62139ab41fb2ad44de36af5232fdd2fd310c46e82cc361da409988a4115fab', 'candidate-wpt-typedattr/raw.jsonl': '5dbde2b2c17c2dcdc3d7df524231b2f2ec718c44495ff0656981f6a57e8a8288'}
assert FAILURE_PINS, 'Actual terminal evidence is pending'
assert sha((OWNER / 'FILES.json').read_bytes()) == 'f213f8160c1c142a0964a99e46ebb483a27b29f5169cda74afb83b185c2dc464'
baseline = load('paired_live_baseline', 'artifacts/css-font-metric-selected-reference-pair-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
result = read(RUNTIME / 'RESULT.json')
for name, digest in FAILURE_PINS.items():
    assert sha((RUNTIME / name).read_bytes()) == digest
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 37339 and terminal['launch'] == '69c55d'
assert terminal['terminal'] and terminal['exit'] == 1
assert terminal['result_sha256'] == FAILURE_PINS['RESULT.json']
trace = read(RUNTIME / 'FAILURE-TRACEBACK.json')
assert trace['error'] == result['error'] and trace['traceback']
assert set(result['phase']) == {'original'} and result['error'] and result['publication_errors'] == []
assert set(result['phase']['original']) == set(policy['lane_order'])
assert not policy['diagnostic_lane_order'] and policy['lane_order'] == ['metric','phase','typedattr']
assert not (RUNTIME / 'candidate-OUTCOMES.json').exists()
assert not (RUNTIME / 'COMPARISON.json').exists()
for role_name in ('original','candidate'):
    build = RUNTIME / (role_name + '-build')
    built = read(build / 'build-RESULT.json')
    assert built['exit'] == 0 and built['stop_reason'] is None and built['error'] is None
    assert built['cleanup_errors'] == [] and built['owned_group_absent']
    command = read(build / 'COMMAND.json')
    assert command['owner_manifest'] == sha((OWNER / 'FILES.json').read_bytes())
    assert command['source_role'] == role_name
    assert command['source_sha256'] == {name:row['base_sha256' if role_name == 'original' else 'candidate_sha256'] for name,row in roles.items()}
    for lane in policy['lane_order']:
        phase = RUNTIME / (role_name + '-wpt-' + lane)
        outcome, assessment = read(phase / 'RESULT.json'), read(phase / 'ASSESSMENT.json')
        assert outcome['preservation_verified'] and outcome['execution_error'] is None
        if role_name == 'original':
            descriptor = result['phase']['original'][lane]
            for key, filename in [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json'),('behavior_sha256','BEHAVIOR-COMPARISON.json')]:
                assert sha((phase / filename).read_bytes()) == descriptor[key]
        if role_name == 'candidate' and lane == 'typedattr':
            assert outcome['success'] is False and assessment['complete'] is False
            events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
            assert any(row.get('action') == 'test_end' and row.get('status') == 'CRASH' for row in events)
        else:
            assert outcome['success'] and assessment['complete'] and assessment['errors'] == []
            assert len(assessment['rows']) == policy['wpt_lanes'][lane]['expected_subtest_count'] and len(assessment['ends']) == 1
            if role_name == 'candidate': assert all(row['status'] == 'PASS' for row in assessment['rows'])

assert result['success'] is False and result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups = []
for role in ('original', 'candidate'):
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
