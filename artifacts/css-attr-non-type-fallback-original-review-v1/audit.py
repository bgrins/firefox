import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/css-attr-non-type-fallback-wpt-runtime-original-1'
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
assert inputs[str((RUN / 'ASSESSMENT.json').relative_to(ROOT))] == '49d7c867e4b4255e169ae05d41becb73cd121bba8b126d02d02443c475a397b3'
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
assert collections.Counter(r['status'] for r in new) == {'FAIL': 19, 'PASS': 15}
assert len(old) == 154 and all(r['status'] == 'PASS' for r in old)
assert len([t for t in ended if selected[t] == 'reftest']) == 6
assert assessment['rows'] == rows
assert assessment['complete'] and assessment['execution_preserved']
assert not assessment['errors'] and not assessment['infrastructure_faults']
assert not assessment['comparison_gate_passed']
command = load(RUN / 'COMMAND.json')
epoch = load(RUN / 'EPOCH.json')
assert hashlib.sha256(read(RUN / 'EPOCH.json')).hexdigest() == command['epoch_sha256'] == assessment['epoch_sha256']
assert command['wrapper_manifest_sha256'] == assessment['capsule_manifest_sha256'] == inputs[str((CAP / 'FILES.json').relative_to(ROOT))]
assert command['phase'] == assessment['phase'] == 'original-1'
assert '--headless' in command['command'] and '--processes=1' in command['command']
assert collections.Counter(x.removeprefix('--include=') for x in command['command'] if x.startswith('--include=')) == collections.Counter(selected.keys())
assert assessment['native_sources'] == policy['source_roles']['original']
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
assert result['exit'] == 1 and result['observation_gate_passed']
assert not result['native_fix_acceptance'] and not result['comparison_gate_passed']
assert result['execution_error'] is None and result['preservation_error'] is None
cleanup = load(RUN / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
process = load(RUN / 'PROCESS.json')
read(RUN / 'wpt.log')
read(RUN / 'wptrunner.ini')
read(RUN / 'INDEX-FLAGS.json')
summary = {
    'status': 'SAVED_ORIGINAL_EVIDENCE_INTERNALLY_CONSISTENT',
    'actions': dict(actions),
    'new_test_statuses': dict(collections.Counter(r['status'] for r in new)),
    'existing_subtests_passed': len(old),
    'reftests_passed': 6,
    'exact_new_names': names,
    'new_rows': new,
    'original_sources': assessment['native_sources'],
    'normal_binaries': normal,
    'application_metadata': app,
    'cleanup_record': cleanup,
    'process_record': process,
    'native_fix_accepted': False,
    'live_source_binary_epoch_process_queries': False,
    'limitations': [
        'Stored pre/post records establish recorded preservation; this audit does not re-observe the transitioning live tree or processes.',
        'Failed test callbacks stop at first assertion: consuming properties, other mutual-cycle participants, later mutation phases and later registered-property checks are not observations from those failed callbacks.',
        'Existing attr-cycle passes preserve an old oracle, not current-ED conformity for raw nesting.',
        'A completed original run is not a candidate comparison or native proof.'
    ]
}
(OUT / 'AUDIT.json').write_text(json.dumps(summary, indent=2) + '\n')
(OUT / 'INPUTS.json').write_text(json.dumps(inputs, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': summary['status'], 'new': summary['new_test_statuses'], 'old_assertions': len(old), 'reftests': 6, 'input_files': len(inputs)}))
