import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / 'artifacts/css-resumable-font-size-integrated-native-typecheck-v1'
RUNTIME = ROOT / 'artifacts/css-resumable-font-size-integrated-native-typecheck-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


binding = read(Path(__file__).with_name('BINDINGS.json'))
assert binding['execution_enabled'] is True and binding['pending_outcome'] is False
assert binding['owner_manifest_sha256'] and binding['owner_terminal'] and binding['outcome_pins']
assert {'RESULT.json', 'ROOT-TERMINAL.json', 'PAIR-PRE.json', 'POST.json', 'RESTORATION.json', 'APP-PRE.json', 'EXTRA-PRE.json', 'BACKUPS.json', 'BACKUP-CLEANUP.json'} <= set(binding['outcome_pins'])
assert sha((OWNER / 'FILES.json').read_bytes()) == binding['owner_manifest_sha256']
for name, digest in binding['outcome_pins'].items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert sha((RUNTIME / name).read_bytes()) == digest
terminal = read(RUNTIME / 'ROOT-TERMINAL.json')
assert terminal == binding['owner_terminal']
terminal = {'session': terminal['session_id'], 'launch': terminal['start_chunk'], 'terminal': terminal['terminal_chunk'], 'exit': terminal['exit_code'], 'result_sha256': terminal['result_sha256']}
result = read(RUNTIME / 'RESULT.json')
assert terminal['terminal'] and terminal['exit'] == (0 if result['success'] else 1)
assert terminal['result_sha256'] == sha((RUNTIME / 'RESULT.json').read_bytes())
baseline = load('paired_live_baseline', 'artifacts/css-resumable-font-size-integrated-native-typecheck-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
result = read(RUNTIME / 'RESULT.json')
assert result['restoration_verified'] and result['runtime_controls_unchanged']
if result['success']:
    assert result['error'] is None and result['publication_errors'] == []
else:
    assert result['error'] or result['publication_errors']
    if result['error']:
        assert 'FAILURE-TRACEBACK.json' in binding['outcome_pins']
        trace = read(RUNTIME / 'FAILURE-TRACEBACK.json')
        assert trace['error'] == result['error'] and trace['traceback']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups, process_records = [], []
build = RUNTIME / 'candidate-check'
for process_file, cleanup_file in [('build-PROCESS.json', 'build-GROUP-CLEANUP.json'),
                                   ('WAKE-PROCESS.json', 'wake-GROUP-CLEANUP.json')]:
    record = build / process_file
    if not record.exists():
        continue
    group = read(record)['pgid']
    assert str((build / cleanup_file).relative_to(RUNTIME)) in binding['outcome_pins']
    assert read(build / cleanup_file)['owned_group_absent']
    ownership.group_absent(group)
    absent_groups.append(group)
    process_records.append(str(record.relative_to(RUNTIME)))
assert len(absent_groups) == len(set(absent_groups))
assert set(process_records) == {str(path.relative_to(RUNTIME)) for path in RUNTIME.rglob('*PROCESS.json')}
assert all(name in binding['outcome_pins'] for name in process_records)
typecheck = read(OWNER / 'TYPECHECK.json')
for name, pin in typecheck['required_input_hashes'].items():
    assert sha((ROOT / name).read_bytes()) == pin
assessor = load('ownership_live_assessor', 'artifacts/css-resumable-font-size-integrated-native-typecheck-v1/assess.py')
if (build / 'build-RESULT.json').is_file() and (build / 'build.log').is_file():
    assert {'candidate-check/build-RESULT.json', 'candidate-check/build.log', 'candidate-check/ASSESSMENT.json'} <= set(binding['outcome_pins'])
    inner = read(build / 'build-RESULT.json')
    assert inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assessment = assessor.assess((build / 'build.log').read_bytes(), inner['exit'], ROOT, ROOT / 'objdir-full.noindex')
    assert assessment == read(build / 'ASSESSMENT.json')
    assert assessment == result['phase']['cargo']
    if result['success']:
        assert inner['exit'] == 0 and inner['error'] is None and inner['stop_reason'] is None
        assert assessment['success']
else:
    assert not result['success'] and result['phase'] is None
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
assert set(roles) == {'servo/components/style/properties/cascade.rs', 'servo/components/style/custom_properties.rs', 'servo/components/style/properties/mod.rs'}
assert set(capture['additional_sources']) == {'servo/components/style/properties/mod.rs'}
assert not set(capture['additional_sources']).intersection(epoch['pins'])
assert not set(capture['additional_sources']).intersection(epoch['installed_identities'])
claims = capture['payload_claims'] | capture['additional_sources']
restoration = read(RUNTIME / 'RESTORATION.json')
assert set(restoration['sources']) == set(roles)
for name, role in roles.items():
    claim = claims[name]
    assert claim['owned_sha256'] == role['base_sha256']
    assert ownership.claim(ROOT, name, role['base_sha256'], claim['identity']) == claim
    assert restoration['sources'][name] == {'sha256': role['base_sha256'], 'identity': claim['identity']}
    assert read(RUNTIME / 'PAIR-PRE.json')['sources'][name]['identity'] == claim['identity']
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
assert cleanup['verified_original_restoration'] is True
backups = read(RUNTIME / 'BACKUPS.json')
assert cleanup['owned_backup_bytes'] == backups['bytes'] == read(RUNTIME / 'PAIR-PRE.json')['owned_backup_bytes']
assert cleanup['removed'] is result['success'] and cleanup['retained_after_failure'] is (not result['success'])
if cleanup['removed']:
    assert not (RUNTIME / 'backups').exists() and not (RUNTIME / 'backups').is_symlink()
else:
    assert not (RUNTIME / 'backups').is_symlink()
    assert bundle.scan(RUNTIME / 'backups') == backups['owned_inventory']
assert not read(RUNTIME / 'RESTORATION.json')['errors']
assert not read(RUNTIME / 'RESTORATION.json')['owned_processes']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
output = ROOT / 'artifacts/css-resumable-font-size-integrated-native-live-restoration-v1.json'
with output.open('x') as stream:
    json.dump({'independent_live_restoration_verified': True, 'snapshot': observed,
               'application_and_extras_semantically_restored': True,
               'source_and_binary_hashes_restored': True, 'flags_restored': True,
               'controls_unchanged': True, 'backup_removed': cleanup['removed'],
               'retained_backup_inventory_verified': not cleanup['removed'],
               'backup_inventory_sha256': sha((RUNTIME / 'BACKUPS.json').read_bytes()),
               'independently_absent_process_groups': absent_groups,
               'restored_application_metadata': application,
               'owner_result_sha256': sha((RUNTIME / 'RESULT.json').read_bytes()),
               'audit_script_sha256': sha(Path(__file__).read_bytes()),
               'owner_terminal': terminal, 'outcome_pins': binding['outcome_pins'],
               'restored_source_claims': {name: claims[name] for name in roles},
               'native_acceptance': False}, stream, indent=2)
    stream.write('\n')
print('Independent live source, application, controls, index and flags audit passed')
