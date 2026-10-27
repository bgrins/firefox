import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/css-attr-raw-nested-wpt-runtime-candidate-1'
ORIGINAL = ROOT / 'artifacts/css-attr-raw-nested-wpt-runtime-original-1'
BUILD = ROOT / 'artifacts/css-attr-raw-nested-native-runtime-v1/candidate-build-1'
CAPSULE = ROOT / 'artifacts/css-attr-raw-nested-wpt-capsule-v2'
PROPOSAL = ROOT / 'artifacts/css-attr-raw-nested-repair-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RUN / 'ASSESSMENT.json') == '699e5f5c09d04a5b2814b849a462e1e117863b6f740d345f95ea85b8aa2a7d2e'
assert sha(CAPSULE / 'FILES.json') == '899ac6bf679be24c98815edf15fa7c1d6c5d145e6d20266821416d461ed7323d'
for name, pin in read(CAPSULE / 'FILES.json').items():
    assert sha(CAPSULE / name) == (pin['sha256'] if isinstance(pin, dict) else pin), name
assert sha(PROPOSAL / 'FILES.json') == '0f3b2b6d970fc0a5ffca89190d97726b8eacdd121f574b14a2b5e735a1828866'
for name, pin in read(PROPOSAL / 'FILES.json').items():
    assert sha(PROPOSAL / name) == pin, name
policy = read(CAPSULE / 'POLICY.json')
assessment = read(RUN / 'ASSESSMENT.json')
events = [json.loads(line) for line in (RUN / 'raw.jsonl').read_text().splitlines()]
counts = Counter(e['action'] for e in events)
assert counts['suite_start'] == counts['suite_end'] == counts['shutdown'] == 1
assert counts['test_start'] == counts['test_end'] == len(policy['tests']) == 16
positions = {action: next(i for i, e in enumerate(events) if e['action'] == action)
             for action in ('suite_start', 'suite_end', 'shutdown')}
assert positions['suite_start'] < positions['suite_end'] < positions['shutdown']
active, started, ended, identities = set(), set(), set(), set()
rows, endings = [], []
for index, event in enumerate(events):
    action = event['action']
    assert action not in ('crash', 'assertion_count')
    assert not (action == 'log' and event.get('level') in ('ERROR', 'CRITICAL'))
    if action not in ('test_start', 'test_status', 'test_end'):
        continue
    assert positions['suite_start'] < index < positions['suite_end']
    name = event['test']
    assert name in policy['tests']
    if action == 'test_start':
        assert name not in started
        started.add(name)
        active.add(name)
    elif action == 'test_status':
        assert name in active and policy['tests'][name] == 'testharness'
        identity = (name, event['subtest'])
        assert identity not in identities
        identities.add(identity)
        rows.append(event)
    else:
        assert name in active and name not in ended
        active.remove(name)
        ended.add(name)
        assert event['status'] == ('OK' if policy['tests'][name] == 'testharness' else 'PASS')
        endings.append(event)
assert not active and started == ended == set(policy['tests'])
expected_targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}
expected_regressions = {(test, name) for test, names in policy['regression_subtests'].items() for name in names}
assert len(expected_targets) == 66 and len(expected_regressions) == 329
assert expected_targets.isdisjoint(expected_regressions)
assert identities == expected_targets | expected_regressions
assert rows == assessment['rows'] and endings == assessment['ends']
targets = [r for r in rows if (r['test'], r['subtest']) in expected_targets]
regressions = [r for r in rows if (r['test'], r['subtest']) in expected_regressions]
assert Counter(r['status'] for r in targets) == {'PASS': 65, 'FAIL': 1}
assert Counter(r['status'] for r in regressions) == {'PASS': 329}
assert len([e for e in endings if policy['tests'][e['test']] == 'reftest']) == 6
signature = [{'kind': e['action'], 'test': e['test'], 'subtest': e.get('subtest'),
              'status': e['status'], 'expected': e.get('expected', e['status']),
              'expected_field_present': 'expected' in e,
              'known_intermittent': e.get('known_intermittent', []),
              'intermittent_field_present': 'known_intermittent' in e}
             for e in rows + endings if e['test'] not in policy['target_subtests']]
signature.sort(key=lambda e: (e['test'], e['kind'], e['subtest'] or ''))
assert signature == assessment['regression_signature'] and len(signature) == 343
failures = [r for r in rows if r['status'] == 'FAIL']
assert failures == assessment['unexpected']
assert all(r.get('expected', r['status']) == 'PASS' and r.get('known_intermittent', []) == [] for r in rows)
old = '/css/css-values/attr-cycle.html'
new = '/css/css-values/attr-raw-nested-cycle.html'
assert Counter(r['status'] for r in targets if r['test'] == old) == {'PASS': 36, 'FAIL': 1}
assert Counter(r['status'] for r in targets if r['test'] == new) == {'PASS': 29}
assert {r['subtest'] for r in failures if r['test'] == old} == {
    'CSS Values and Units Test: attr 28'}
calls = []
for role in ('base', 'candidate'):
    text = (PROPOSAL / (role + '/testing/web-platform/tests' + old)).read_text()
    calls.append(re.findall(r'^\s*(test_attr_(?:no_)?cycle\(.*\);)\s*$', text, re.MULTILINE))
assert len(calls[0]) == len(calls[1]) == 37
assert [i for i, (before, after) in enumerate(zip(*calls)) if before != after] == [3, 29]
epoch = read(RUN / 'EPOCH.json')
command = read(RUN / 'COMMAND.json')
assert sha(RUN / 'EPOCH.json') == assessment['epoch_sha256'] == command['epoch_sha256']
assert command['wrapper_manifest_sha256'] == assessment['capsule_manifest_sha256'] == sha(CAPSULE / 'FILES.json')
assert assessment['native_sources'] == {name: epoch['pins'][name] for name in assessment['native_sources']}
base = read(PROPOSAL / 'BASE.json')
assert assessment['native_sources']['servo/components/style/properties/cascade.rs'] == sha(PROPOSAL / 'candidate/servo/components/style/properties/cascade.rs')
assert assessment['native_sources']['servo/components/style/custom_properties.rs'] == base['helper_sha256']
binaries = read(RUN / 'NORMAL-BINARIES.json')
assert binaries == {name: epoch['pins'][name] for name in binaries}
assert read(RUN / 'PRE.json') == read(RUN / 'POST.json')
assert read(RUN / 'PRE.json')['working_sources_binaries_research_preserved']
metadata = read(RUN / 'APPLICATION-METADATA.json')
assert metadata == read(RUN / 'APPLICATION-METADATA-POST.json') == assessment['run_binding']
suite = events[positions['suite_start']]
assert suite['run_info'] == assessment['run_info']
assert suite['run_info']['browser_build_id'] == metadata['browser_build_id']
assert suite['run_info']['revision'] == metadata['revision'] == epoch['semantic_index']['head']
inputs = read(RUN / 'INPUT-PINS.json')
owned = read(RUN / 'OWNED-INPUT-PINS.json')
for name, item in read(CAPSULE / 'SOURCE-PINS.json').items():
    if item['exists']:
        assert sha(CAPSULE / item['capture']) == item['sha256']
    if name.startswith('testing/web-platform/meta/'):
        wanted = item.get('sha256')
        assert inputs[name] == wanted
        key = 'metadata/' + name.removeprefix('testing/web-platform/meta/')
        assert owned.get(key) == wanted
for name, expected in [(old, '442ccf89e78528baf9a713051b23e907015f132b463aaf578107fab2d5453326'),
                       (new, '1bdb97be472700e499e7abc27bf38a7249fbcd14d6b45a366ba5500fb3f7bf46')]:
    source = PROPOSAL / ('candidate/testing/web-platform/tests' + name)
    assert sha(source) == owned['tests' + name] == expected
    assert inputs[str(source.relative_to(ROOT))] == expected
assert inputs['objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini'] == metadata['sha256']
assert owned['wptrunner.ini'] == sha(RUN / 'wptrunner.ini')
assert owned['metadata/MANIFEST.json'] == sha(CAPSULE / 'SUBSET-MANIFEST.json')
cleanup = read(RUN / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
result = read(RUN / 'RESULT.json')
assert result['exit'] == 1 and not result['observation_gate_passed']
assert not result['comparison_gate_passed'] and not result['native_fix_acceptance']
assert result['execution_error'] is None and result['preservation_error'] is None
assert assessment['complete'] and assessment['execution_preserved']
assert not assessment['errors'] and not assessment['infrastructure_faults']
assert assessment['comparison_errors'] == ['candidate target fixture still fails']
assert sha(ORIGINAL / 'ASSESSMENT.json') == command['original_assessment_sha256'] == '56c633d1f7b1946126c20b790d1f646d18e689f5b1289757d7aed67c0c0f9627'
original = read(ORIGINAL / 'ASSESSMENT.json')
assert assessment['regression_signature'] == original['regression_signature']
assert {k: v for k, v in assessment['run_info'].items() if k != 'browser_build_id'} == {k: v for k, v in original['run_info'].items() if k != 'browser_build_id'}
row_map = lambda value: {(r['test'], r['subtest']): r['status'] for r in value}
before_rows, after_rows = row_map(original['rows']), row_map(rows)
assert before_rows.keys() == after_rows.keys()
repaired = sorted(k for k in before_rows if before_rows[k] == 'FAIL' and after_rows[k] == 'PASS')
new_failure = sorted(k for k in before_rows if before_rows[k] == 'PASS' and after_rows[k] == 'FAIL')
assert len(repaired) == 13
assert new_failure == [(old, 'CSS Values and Units Test: attr 28')]
assert sum(before_rows[k] == after_rows[k] for k in before_rows) == 381
assert failures[0]['message'] == 'assert_equals: Value \'attr(data-foo type(*), abc)\', where \'data-foo=attr(data-foo\' should be valid for the property \'--x\'. expected "abc" but got "\\\"attr(data-foo\\\""'
old_epoch = read(ORIGINAL / 'EPOCH.json')
assert epoch['pins'].keys() == old_epoch['pins'].keys()
changed_pins = sorted(k for k in epoch['pins'] if epoch['pins'][k] != old_epoch['pins'][k])
assert changed_pins == sorted([*binaries, 'servo/components/style/properties/cascade.rs'])
old_inputs = read(ORIGINAL / 'INPUT-PINS.json')
assert inputs.keys() == old_inputs.keys()
assert [k for k in inputs if inputs[k] != old_inputs[k]] == ['objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini']
old_owned = read(ORIGINAL / 'OWNED-INPUT-PINS.json')
assert owned.keys() == old_owned.keys()
assert [k for k in owned if owned[k] != old_owned[k]] == ['wptrunner.ini']
assert sha(BUILD / 'EPOCH.json') == sha(RUN / 'EPOCH.json')
assert read(BUILD / 'POST.json') == read(RUN / 'PRE.json')
build = read(BUILD / 'build-RESULT.json')
assert build['exit'] == 0 and build['stop_reason'] is None and build['error'] is None
assert not build['cleanup_errors'] and build['owned_group_absent']
publication = read(BUILD / 'RESULT.json')
assert publication['command_success'] and publication['preservation_verified']
assert publication['error'] is None and not publication['publication_errors']
assert publication['source_role'] == 'candidate'
report = {'status': 'SAVED_RAW_CANDIDATE_FAILED_COMPARISON_INTERNALLY_CONSISTENT', 'actions': dict(counts),
          'target_counts': {'PASS': 65, 'FAIL': 1}, 'target_identities': sorted(expected_targets),
          'regression_identities': sorted(expected_regressions), 'regression_PASS': 329,
          'reftest_PASS': 6, 'failures': failures, 'saved_pre_post_exact': True,
          'saved_source_binary_metadata_bindings': True, 'cleanup_record_passed': True,
          'existing_oracle_call_changes_only': [3, 29], 'regression_signature_rows': 343,
          'live_state_or_process_rechecked': False, 'accepted_fix_increment': 0,
          'original_failures_repaired': repaired, 'new_failure': new_failure,
          'changed_epoch_pins': changed_pins, 'source_regression_conclusion': 'UNRESOLVED_EOF_ORACLE',
          'build_epoch_exact': True}
with (HERE / 'AUDIT.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
pins = {str(p.relative_to(ROOT)): sha(p) for p in sorted(RUN.iterdir()) if p.is_file()}
pins.update({str(p.relative_to(ROOT)): sha(p) for p in sorted(BUILD.iterdir()) if p.is_file()})
pins[str(ORIGINAL.relative_to(ROOT) / 'ASSESSMENT.json')] = sha(ORIGINAL / 'ASSESSMENT.json')
pins[str(CAPSULE.relative_to(ROOT) / 'FILES.json')] = sha(CAPSULE / 'FILES.json')
with (HERE / 'INPUTS.json').open('x') as stream:
    json.dump(pins, stream, indent=2)
    stream.write('\n')
print('Saved candidate audit passed: comparison FAILED;13 repaired,one new failure;329 regressions+6refs preserved')
