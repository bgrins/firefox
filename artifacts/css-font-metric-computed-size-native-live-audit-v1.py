import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / 'artifacts/css-font-metric-computed-size-native-typecheck-v1'
RUNTIME = ROOT / 'artifacts/css-font-metric-computed-size-native-typecheck-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha((OWNER / 'FILES.json').read_bytes()) == '9f52f3e563187ce94eb459fed2423b74bc4d355a73bdf10db0f819e3a9be3d82'
baseline = load('paired_live_baseline', 'artifacts/css-font-metric-computed-size-native-typecheck-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups = []
build = RUNTIME / 'candidate-check'
for process_file, cleanup_file in [('build-PROCESS.json', 'build-GROUP-CLEANUP.json'),
                                   ('WAKE-PROCESS.json', 'wake-GROUP-CLEANUP.json')]:
    group = read(build / process_file)['pgid']
    assert read(build / cleanup_file)['owned_group_absent']
    ownership.group_absent(group)
    absent_groups.append(group)
typecheck = read(OWNER / 'TYPECHECK.json')
for name, pin in typecheck['required_input_hashes'].items():
    assert sha((ROOT / name).read_bytes()) == pin
assessor = load('ownership_live_assessor', 'artifacts/css-font-metric-computed-size-native-typecheck-v1/assess.py')
inner = read(build / 'build-RESULT.json')
assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
assert inner['error'] is None and inner['stop_reason'] is None
assessment = assessor.assess((build / 'build.log').read_bytes(), inner['exit'], ROOT, ROOT / 'objdir-full.noindex')
assert assessment['success'] and assessment == read(build / 'ASSESSMENT.json')
assert assessment == result['phase']['cargo']
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
assert cleanup['removed'] and cleanup['verified_original_restoration'] and not (RUNTIME / 'backups').exists()
assert not read(RUNTIME / 'RESTORATION.json')['errors']
assert not read(RUNTIME / 'RESTORATION.json')['owned_processes']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
output = RUNTIME / 'ROOT-LIVE-RESTORATION.json'
with output.open('x') as stream:
    json.dump({'independent_live_restoration_verified': True, 'snapshot': observed,
               'application_and_extras_semantically_restored': True,
               'source_and_binary_hashes_restored': True, 'flags_restored': True,
               'controls_unchanged': True, 'backup_removed': True,
               'independently_absent_process_groups': absent_groups,
               'restored_application_metadata': application,
               'owner_result_sha256': sha((RUNTIME / 'RESULT.json').read_bytes()),
               'audit_script_sha256': sha(Path(__file__).read_bytes()),
               'native_acceptance': False}, stream, indent=2)
    stream.write('\n')
print('Independent live source, application, controls, index and flags audit passed')
