import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / 'artifacts/css-contextual-duration-finite-depth-original-v1'
RUNTIME = ROOT / 'artifacts/css-contextual-duration-finite-depth-original-runtime-1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha(OWNER / 'FILES.json') == '8fbb65615b84a4c0c2389fed44a74446c8ef3a809bf5740d1e804268d473192a'
for name, digest in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == digest
policy = read(OWNER / 'POLICY.json')
load('same_element_saved_admission', OWNER / 'admission.py').validate(policy)
phase = RUNTIME / 'original-wpt'
result = read(RUNTIME / 'RESULT.json')
inner = read(phase / 'RESULT.json')
assert result['lifecycle_complete'] and result['preservation_verified'] and not result['source_or_canonical_mutation']
assert result['record_errors'] == [] and not result['native_fix_accepted']
for name, field in [('raw.jsonl', 'raw_sha256'), ('ASSESSMENT.json', 'assessment_sha256'), ('RESULT.json', 'result_sha256')]:
    assert sha(phase / name) == result['phase'][field]
assert inner['success'] and inner['preservation_verified'] and inner['execution_error'] is None
before = read(RUNTIME / 'PRE.json')
assert before == read(RUNTIME / 'POST.json') == read(phase / 'PRE.json') == read(phase / 'POST.json')
assert before == read(ROOT / policy['restored_runtime'] / 'POST.json')
metadata = read(phase / 'APPLICATION-METADATA.json')
assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == policy['prepared_application_metadata']
built = read(ROOT / policy['build_epoch'])
assert read(phase / 'BINARY-PINS.json') == {name: built['pins'][name] for name in policy['rebuilt_binaries']}
settings = dict(policy['wpt'], tests={page: 'testharness' for page in policy['wpt']['expected_subtests']}, held_subtests={})
settings['regression_subtests'] = settings['expected_subtests']
settings['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
assert settings == read(phase / 'ASSESSMENT-POLICY.json')
assessor = load('same_element_original_assessor', OWNER / 'assess.py')
checks = load('same_element_raw_checks', ROOT / settings['checks_helper'])
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
observed = assessor.assess(events, inner['exit'], settings, checks, run_binding=metadata)
assert observed == read(phase / 'ASSESSMENT.json') and observed['complete'] and not observed['errors']
assert len(observed['rows']) == 4 and len(observed['ends']) == 1 and observed['ends'][0]['status'] == 'OK'
assert result['callbacks_passed'] == sum(row['status'] == 'PASS' for row in observed['rows'])
assert result['callbacks_failed'] == sum(row['status'] == 'FAIL' for row in observed['rows'])
collection = load('same_element_original_records', OWNER / 'records.py').collect(
    ROOT, RUNTIME / 'progress-records', read(RUNTIME / 'PROGRESS-BINDING.json'), policy, observed)
assert collection == read(RUNTIME / 'PROGRESS-RECORDS.json')
assert collection['complete'] and not collection['missing'] and not collection['errors'] and len(collection['records']) == 4
assert result['records_complete'] == result['observation_complete'] == collection['complete']
cleanup = read(phase / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
for name, item in settings['resources'].items():
    assert sha(phase / 'tests' / name) == item['sha256']
assert sha(phase / 'metadata/MANIFEST.json') == settings['manifest']['sha256']
for name, item in settings['metadata'].items():
    if item['sha256'] is None:
        assert not (phase / 'metadata' / name).exists()
    else:
        assert sha(phase / 'metadata' / name) == item['sha256']
roster = read(RUNTIME / 'OBSERVED-ROSTER.json')
assert roster['owner_sha256'] == sha(OWNER / 'FILES.json') and roster['phase'] == result['phase']
assert roster['observed_subtest_count'] == 4 and roster['expected_subtests'] == settings['expected_subtests']
records = {}
comparison = load('depth_calibration', ROOT / 'artifacts/css-contextual-duration-finite-depth-candidate-v1/comparison.py')
for filename in policy['record_kinds']:
    current = read(RUNTIME / 'progress-records' / filename)
    comparison.require_original_calibration(current['observations'])
    records[filename] = {'record': current, 'literal_and_initial_calibration_verified': True}
print(json.dumps({'actual_outer_session': 81249, 'actual_outer_terminal': '88aff8', 'actual_outer_exit': 0,
                  'raw_replay_exact': True, 'saved_pre_post_app_binary_joins_exact': True,
                  'saved_cleanup_complete': True, 'browser_exit': inner['exit'],
                  'callbacks_passed': result['callbacks_passed'], 'callbacks_failed': result['callbacks_failed'],
                  'complete_records': 4, 'records': records, 'rows': observed['rows'],
                  'fresh_current_state_check_performed': False, 'native_acceptance': False}, indent=2))
