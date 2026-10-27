import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/css-attr-non-type-fallback-wpt-runtime-candidate-1'
CAP = ROOT / 'artifacts/css-attr-non-type-fallback-wpt-capsule-v3'
inputs = {}


def read(path):
    data = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return data


def load(path):
    return json.loads(read(path))


manifest = load(CAP / 'FILES.json')
assert inputs[str((CAP / 'FILES.json').relative_to(ROOT))] == 'fc8e9a7cc39e37f17177627386574f7dc18bf69e3e3a700b9509b127fcdd53e1'
for name, digest in manifest.items():
    assert hashlib.sha256(read(CAP / name)).hexdigest() == digest
policy = load(CAP / 'POLICY.json')
selected = load(CAP / 'SELECTED.json')
names = load(CAP / 'CANDIDATE-SUBTESTS.json')
candidate = policy['candidate_test']
assessment = load(RUN / 'ASSESSMENT.json')
assert inputs[str((RUN / 'ASSESSMENT.json').relative_to(ROOT))] == '285d83cf5d0cce8496d490bed7d52a68f920035743a2b8856890bcc4573cdd04'
raw = [json.loads(line) for line in read(RUN / 'raw.jsonl').splitlines()]
actions = collections.Counter(row['action'] for row in raw)
assert actions['suite_start'] == actions['suite_end'] == actions['shutdown'] == 1
assert not [r for r in raw if r.get('level') in ('ERROR', 'CRITICAL') or r['action'] in ('crash', 'assertion_count')]
active = None
started, ended, rows = [], [], []
suite_active = False
for row in raw:
    action = row['action']
    if action == 'suite_start':
        assert not suite_active
        suite_active = True
    elif action == 'test_start':
        assert suite_active and active is None and row['test'] in selected
        active = row['test']
        started.append(active)
    elif action == 'test_status':
        assert suite_active and active == row['test']
        rows.append(row)
    elif action == 'test_end':
        assert suite_active and active == row['test']
        assert row['status'] == ('OK' if selected[active] == 'testharness' else 'PASS')
        ended.append(active)
        active = None
    elif action == 'suite_end':
        assert suite_active and active is None
        suite_active = False
assert not suite_active and active is None
assert collections.Counter(started) == collections.Counter(ended) == collections.Counter(selected.keys())
identities = [(r['test'], r['subtest']) for r in rows]
assert len(identities) == len(set(identities))
new = [r for r in rows if r['test'] == candidate]
old = [r for r in rows if r['test'] != candidate]
assert [r['subtest'] for r in new] == names and len(names) == 34
assert collections.Counter(r['status'] for r in new) == {'PASS': 34}
assert len(old) == 154 and all(r['status'] == 'PASS' for r in old)
assert len([t for t in ended if selected[t] == 'reftest']) == 6
assert assessment['rows'] == rows
assert assessment['complete'] and assessment['execution_preserved']
assert not assessment['errors'] and not assessment['infrastructure_faults']
assert assessment['comparison_gate_passed'] and not assessment['comparison_errors']
command = load(RUN / 'COMMAND.json')
epoch = load(RUN / 'EPOCH.json')
assert hashlib.sha256(read(RUN / 'EPOCH.json')).hexdigest() == command['epoch_sha256'] == assessment['epoch_sha256']
assert command['wrapper_manifest_sha256'] == assessment['capsule_manifest_sha256'] == inputs[str((CAP / 'FILES.json').relative_to(ROOT))]
assert command['phase'] == assessment['phase'] == 'candidate-1'
assert '--headless' in command['command'] and '--processes=1' in command['command']
assert collections.Counter(x.removeprefix('--include=') for x in command['command'] if x.startswith('--include=')) == collections.Counter(selected.keys())
assert assessment['native_sources'] == policy['source_roles']['candidate']
for name, digest in assessment['native_sources'].items():
    assert epoch['pins'][name] == digest
normal = load(RUN / 'NORMAL-BINARIES.json')
for name, digest in normal.items():
    assert epoch['pins'][name] == digest
app = load(RUN / 'APPLICATION-METADATA.json')
assert app == load(RUN / 'APPLICATION-METADATA-POST.json') == assessment['run_binding']
suite = next(r for r in raw if r['action'] == 'suite_start')
assert suite['run_info'] == assessment['run_info']
assert app['browser_build_id'] == suite['run_info']['browser_build_id']
assert app['revision'] == suite['run_info']['revision'] == epoch['semantic_index']['head']
pre = load(RUN / 'PRE.json')
assert pre == load(RUN / 'POST.json')
assert pre['current_raw_stable_during_check'] and pre['working_sources_binaries_research_preserved']
pins = load(RUN / 'INPUT-PINS.json')
assert pins[policy['application_ini']] == app['sha256']
owned = load(RUN / 'OWNED-INPUT-PINS.json')
for name, digest in owned.items():
    assert hashlib.sha256(read(RUN / name)).hexdigest() == digest
fixture = 'tests' + candidate
capture = CAP / ('capture/testing/web-platform/' + fixture)
assert read(RUN / fixture) == read(capture)
sourcepins = load(CAP / 'SOURCE-PINS.json')
assert hashlib.sha256(read(RUN / fixture)).hexdigest() == '6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3'
result = load(RUN / 'RESULT.json')
assert result['exit'] == 0 and result['observation_gate_passed']
assert not result['native_fix_acceptance'] and result['comparison_gate_passed']
assert result['execution_error'] is None and result['preservation_error'] is None
cleanup = load(RUN / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
process = load(RUN / 'PROCESS.json')
read(RUN / 'wpt.log')
read(RUN / 'wptrunner.ini')
read(RUN / 'INDEX-FLAGS.json')
original_dir = ROOT / 'artifacts/css-attr-non-type-fallback-wpt-runtime-original-1'
original = load(original_dir / 'ASSESSMENT.json')
assert command['original_assessment_sha256'] == inputs[str((original_dir / 'ASSESSMENT.json').relative_to(ROOT))] == '49d7c867e4b4255e169ae05d41becb73cd121bba8b126d02d02443c475a397b3'
original_raw = [json.loads(line) for line in read(original_dir / 'raw.jsonl').splitlines()]
original_rows = [r for r in original_raw if r['action'] == 'test_status']
assert original['rows'] == original_rows
def signature(r):
    return (r['test'], r.get('subtest'), r['status'], r.get('expected'), r.get('known_intermittent'))
assert [signature(r) for r in original_rows if r['test'] != candidate] == [signature(r) for r in old]
assert [(r['test'], r['subtest']) for r in original_rows] == identities
assert [signature(r) for r in original_raw if r['action'] == 'test_end'] == [signature(r) for r in raw if r['action'] == 'test_end']
changed = [r['subtest'] for r, n in zip(original_rows, rows) if r['status'] != n['status']]
assert len(changed) == 19
assert all(n['status'] == 'PASS' for n in rows)
assert {k for k in original['run_info'].keys() | assessment['run_info'].keys() if original['run_info'].get(k) != assessment['run_info'].get(k)} == {'browser_build_id'}
original_app = load(original_dir / 'APPLICATION-METADATA.json')
assert original_app['browser_build_id'] == original['run_info']['browser_build_id']
assert original_app['revision'] == app['revision']
original_inputs = load(original_dir / 'INPUT-PINS.json')
assert {k for k in pins.keys() | original_inputs.keys() if pins.get(k) != original_inputs.get(k)} == {policy['application_ini']}
original_owned = load(original_dir / 'OWNED-INPUT-PINS.json')
assert {k for k in owned.keys() | original_owned.keys() if owned.get(k) != original_owned.get(k)} == {'wptrunner.ini'}
assert read(RUN / 'wptrunner.ini').replace(b'runtime-candidate-1', b'runtime-PHASE') == read(original_dir / 'wptrunner.ini').replace(b'runtime-original-1', b'runtime-PHASE')
original_epoch = load(original_dir / 'EPOCH.json')
changed_epoch_pins = {k for k in epoch['pins'].keys() | original_epoch['pins'].keys() if epoch['pins'].get(k) != original_epoch['pins'].get(k)}
assert changed_epoch_pins == set(normal) | set(policy['source_roles']['candidate'])
assert epoch['attribute_fallback_transition'] == {'accepted': False, 'compiled': True, 'last_phase': 'candidate-build-1', 'role': 'candidate'}
summary = {
    'status': 'SAVED_CANDIDATE_AND_COMPARISON_INTERNALLY_CONSISTENT',
    'changed_subtests_fail_to_pass': changed,
    'changed_epoch_pins': sorted(changed_epoch_pins),
    'run_info_only_difference': 'independently bound browser_build_id',
    'actions': dict(actions),
    'new_test_statuses': dict(collections.Counter(r['status'] for r in new)),
    'existing_subtests_passed': len(old),
    'reftests_passed': 6,
    'exact_new_names': names,
    'new_rows': new,
    'candidate_sources': assessment['native_sources'],
    'normal_binaries': normal,
    'application_metadata': app,
    'cleanup_record': cleanup,
    'process_record': process,
    'native_fix_accepted': False,
    'live_source_binary_epoch_process_queries': False,
    'limitations': [
        'Stored pre/post records establish recorded preservation; this audit does not re-observe the transitioning live tree or processes.',
        'Passing synchronous callbacks cover every reached assertion including mutation sequences; raw logs expose one result per callback, not individual assert_equals events.',
        'Existing attr-cycle passes preserve an old oracle, not current-ED conformity for raw nesting.',
        'A finite controlled comparison is not a native proof or exhaustive CSS conformance result.'
    ]
}
(OUT / 'AUDIT.json').write_text(json.dumps(summary, indent=2) + '\n')
(OUT / 'INPUTS.json').write_text(json.dumps(inputs, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': summary['status'], 'new': summary['new_test_statuses'], 'old_assertions': len(old), 'reftests': 6, 'input_files': len(inputs)}))
