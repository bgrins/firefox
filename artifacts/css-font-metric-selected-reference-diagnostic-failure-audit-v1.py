import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / 'artifacts/css-font-metric-selected-reference-diagnostic-run-v1'
RUNTIME = ROOT / 'artifacts/css-font-metric-selected-reference-diagnostic-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ACTUAL = {'kind': 'browser_crash', 'started_lanes': ['typedattr'], 'pins': {'RESULT.json': '17b2a79f121bdbfe9fcf873ab5e159090c7e17c9ee410414d1abc78c8892206b', 'ROOT-OWNER-TERMINAL.json': 'bb15df87f55271dd20363c2739f7c5eaf67153583680a90498d6081636f5a6d3', 'FAILURE-TRACEBACK.json': '73ee76b7bddf8f889f14324206b6e4722692525a944912cb425d6fe87aaabaa5', 'BACKUPS.json': '93311b280fc980d93f295259f9e0c1ee0675277a870bcb0c94e0e26ba55c96d7', 'BACKUP-CLEANUP.json': '6f12623f10ab4b3112d092f8e7e99d9254934b9a3cc26281a9d1ea20afb656d5', 'RESTORATION.json': 'a53f44ea2ed5e9b4a68a2dcd2f2549a8f5a9c7f6be1219e1c216229742d85af5', 'POST.json': 'bfa87ef613b3401e1de0ddfdaa0bc21c7f92d2b662c928e155f903b455583331', 'PAIR-PRE.json': 'a3f44719f8aaa805aa029a18c6d137e3cbfaa1bdd5520e8a0e2b87a873f7327e', 'candidate-build/COMMAND.json': '124f50531a533a2dfd911e5c116c9197a0d96495765a14b726ab7747e4402007', 'candidate-build/RESULT.json': '2d048e1dd930d9c5db9ae7abcc4788a9df870b01a52a81b898ef139920986392', 'candidate-build/build-RESULT.json': '31435a03d50b25e32ef870705d9110d2fcb7bb3fab01f6db8c7ed41a64e68b8e', 'candidate-wpt-typedattr/RESULT.json': 'a51f26e84d1e0d7dcae5918da789204a072f2ff08ecf8d4ef7398c7f3f498936', 'candidate-wpt-typedattr/ASSESSMENT.json': 'cf77ce1bb6d3661a9566716dfc07f704a4926e4f13515d36df048258367481b0', 'candidate-wpt-typedattr/raw.jsonl': 'bc6a67d70b0e7957f60ee65c6737b4b9936f3627d6898b0a2d4e1d059ef5fec5', 'candidate-wpt-typedattr/wpt.log': 'f8bbdeec4e2563f1f34dfd3df7f69129d770da45b7d1577757dbc33dabb2738a'}}
assert ACTUAL, 'Actual terminal evidence is pending'
FAILURE_PINS = ACTUAL['pins']
assert FAILURE_PINS and ACTUAL['kind'] in ('build_failure', 'browser_crash')
assert sha((OWNER / 'FILES.json').read_bytes()) == '7841779ef2d8e52a4db12d39d2dc249f3b894a290dffee286604bcebfb0fc258'
baseline = load('paired_live_baseline', 'artifacts/css-font-metric-selected-reference-diagnostic-run-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
result = read(RUNTIME / 'RESULT.json')
for name, digest in FAILURE_PINS.items():
    assert sha((RUNTIME / name).read_bytes()) == digest
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 31469 and terminal['launch'] == '7d42b5'
assert terminal['terminal'] and terminal['exit'] == 1
assert terminal['result_sha256'] == FAILURE_PINS['RESULT.json']
trace = read(RUNTIME / 'FAILURE-TRACEBACK.json')
assert trace['error'] == result['error'] and trace['traceback']
assert result['error'] and result['phase'] == {}
assert policy['lane_order'] == ['typedattr'] and policy['diagnostic_lane_order'] == []
assert not any(path.name.startswith('original-') for path in RUNTIME.iterdir())
assert not (RUNTIME / 'candidate-OUTCOMES.json').exists()
assert not (RUNTIME / 'COMPARISON.json').exists()
build = RUNTIME / 'candidate-build'
built = read(build / 'build-RESULT.json')
assert built['cleanup_errors'] == [] and built['owned_group_absent']
command = read(build / 'COMMAND.json')
assert command['owner_manifest'] == sha((OWNER / 'FILES.json').read_bytes())
assert command['source_role'] == 'candidate'
assert command['source_sha256'] == {name:row['candidate_sha256'] for name,row in roles.items()}
if ACTUAL['kind'] == 'build_failure':
    assert built['exit'] != 0 or built['error'] is not None or built['stop_reason'] is not None
    assert not (RUNTIME / 'candidate-wpt-typedattr').exists()
    assert not (build / 'RESULT.json').exists()
    started_lanes = []
else:
    assert built['exit'] == 0 and built['stop_reason'] is None and built['error'] is None
    assert result['publication_errors'] == []
    build_result = read(build / 'RESULT.json')
    assert build_result['command_success'] and build_result['preservation_verified'] and build_result['browser_build_performed']
    phase = RUNTIME / 'candidate-wpt-typedattr'
    outcome, assessment = read(phase / 'RESULT.json'), read(phase / 'ASSESSMENT.json')
    assert outcome['preservation_verified'] and outcome['execution_error'] is None
    assert outcome['success'] is False and assessment['complete'] is False
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    assert any(row.get('action') == 'test_end' and row.get('status') == 'CRASH' for row in events)
    started_lanes = ['typedattr']
assert started_lanes == ACTUAL['started_lanes']

assert result['success'] is False and result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups = []
for role in ('candidate',):
    build = RUNTIME / (role + '-build')
    for process_file, cleanup_file in [('build-PROCESS.json', 'build-GROUP-CLEANUP.json'),
                                       ('WAKE-PROCESS.json', 'wake-GROUP-CLEANUP.json')]:
        group = read(build / process_file)['pgid']
        assert read(build / cleanup_file)['owned_group_absent']
        ownership.group_absent(group)
        absent_groups.append(group)
    for lane in started_lanes:
        phase = RUNTIME / (role + '-wpt-' + lane)
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        group = read(phase / 'PROCESS.json')['pgid']
        ownership.group_absent(group)
        absent_groups.append(group)
        temporary = Path(read(phase / 'COMMAND.json')['temporary_root'])
        assert not temporary.exists() and not temporary.is_symlink()
assert len(absent_groups) == len(set(absent_groups)) == 2 + len(started_lanes)
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
               'failure_kind': ACTUAL['kind'], 'started_lanes': started_lanes,
               'independently_absent_process_groups': absent_groups,
               'restored_application_metadata': application,
               'owner_result_sha256': sha((RUNTIME / 'RESULT.json').read_bytes()),
               'audit_script_sha256': sha(Path(__file__).read_bytes()),
               'native_acceptance': False}, stream, indent=2)
    stream.write('\n')
print('Independent live source, application, controls, index and flags audit passed')
