import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import struct
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / 'artifacts'
R = A / 'css-name-repeat-context-baseline-runtime-v1'
E = A / 'css-round-infinite-value-step-runtime-v1'
F = A / 'css-name-repeat-context-repair-v3'
S = A / 'css-name-repeat-context-baseline-capture-review-v1'


def body(path):
    assert path.is_relative_to(A) and stat.S_ISREG(path.lstat().st_mode)
    return path.read_bytes()


def unique(pairs):
    assert len(dict(pairs)) == len(pairs)
    return dict(pairs)


def constant(value):
    raise ValueError(value)


loads = lambda text: json.loads(text, object_pairs_hook=unique, parse_constant=constant)
read = lambda path: loads(body(path))
sha = lambda path: hashlib.sha256(body(path)).hexdigest()
refs = {
    'artifacts/css-name-repeat-context-baseline-runtime-v1/FILES.json': 'b20c44a3b2459410288d930a1844b1b5072be643156ac70e6afb4dfe19fd93e2',
    'artifacts/css-name-repeat-context-baseline-capture-review-v1/FILES.json': '5e724e90aaeaa613bf10d72a0a59ce7080cb71e853ae9096379bf905e1b4c7eb',
    'artifacts/css-round-infinite-value-step-runtime-v1/FILES.json': '736a7240a8105a2e765a93b0d6862ce808e010fb77953869575e9188ba86fc5a',
    'artifacts/css-name-repeat-context-repair-v3/FILES.json': '454359c092351c37d751f6fcdb21b75cb7959233dfc05523183d84bb8fbeb259',
}
for name, digest in refs.items():
    path = ROOT / name
    assert sha(path) == digest
    for member, value in read(path).items():
        assert not Path(member).is_absolute() and '..' not in Path(member).parts
        assert sha(path.parent / member) == value
source_refs = read(S / 'REFERENCES.json')
for name in ('capture.py', 'classify.py', 'INPUTS.json'):
    assert sha(R / name) == source_refs[str((R / name).relative_to(ROOT))]
binding = read(R / 'ROOT-REVIEW-BINDING.json')
assert binding['root_review_adopted'] and binding['inputs_sha256'] == sha(R / 'INPUTS.json')
assert binding['review_files_sha256'] == refs[str((S / 'FILES.json').relative_to(ROOT))]
assert binding['native_candidate_applied'] is False
assert read(R / 'ROOT-EXECUTION.json') == {'session': 66325, 'status': 'RUNNING',
    'command': 'python3 -I -S artifacts/css-name-repeat-context-baseline-runtime-v1/capture.py'}
completion = read(R / 'ROOT-COMPLETION.json')
assert completion == {'capture_session': 66325, 'capture_exit': 0,
    'capture_completion_chunk': 'c1e061', 'classifier_session': None,
    'classifier_tool_chunk': '7c15cc', 'classifier_exit': 0,
    'status': 'BASELINE_CAPTURE_AND_CLASSIFICATION_COMPLETE',
    'native_candidate_applied': False, 'build_performed': False}
before = read(R / 'BEFORE.json')
assert before == read(E / 'FINAL.json') and before['pins'] == read(E / 'FINAL-PINS.json')
test = 'testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
url = '/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
baseline = dict(before['pins'])
assert len(baseline) == 609
for name in (test, test.replace('/tests/', '/meta/') + '.ini'):
    assert name not in baseline
    baseline[name] = None
assert baseline == read(R / 'BASELINE-PINS.json') == read(R / 'FINAL-PINS.json')
assert read(R / 'FINAL.json') == read(R / 'PRE-FLIGHT.json') == dict(before, pins=baseline)
names = read(F / 'ROSTER.json')
config = read(E / 'CONFIG.json')
config.update(tests=[test], expected_subtests={url: names}, reftests=[], install={},
              expected_total=10, files_expected_count=1)
assert config == read(R / 'CONFIG.json')
assert len(before['snapshot']['sources']) == len(config['guard_sources']) == 72
assert len(before['installed_tests']) == 23
assert len(config['index_expectations']['staged_paths']) == len(config['index_expectations']['staged_payload_sha256']) == 925
assert len(set(config['modified_native_paths']) | {'servo/components/style/values/generics/calc.rs'}) == 43
owned = read(R / 'OWNED-TESTS.json')
assert set(owned) == {test} and set(owned[test]) == {'identity', 'sha256'}
assert len(owned[test]['identity']) == 2 and all(type(n) is int for n in owned[test]['identity'])
assert tuple(owned[test]['identity']) not in {tuple(v['identity']) for v in before['installed_tests'].values()}
assert owned[test]['sha256'] == sha(F / Path(test).name) == '81e4da216fbf4cd31a500f4b4d8156bd633205000823a4f12057ce0c6cb5d3f3'
active = dict(baseline, **{test: owned[test]['sha256']})
assert read(R / 'PRE-CAPTURE.json') == dict(before, pins=active)
architecture = read(R / 'ARCHITECTURE.json')
assert architecture['status'] == 'SUPPORTED_64_BIT_PHASE_BINARIES'
assert set(architecture['binary_pins']) == set(architecture['binaries']) and len(architecture['binaries']) == 2
for name, value in architecture['binaries'].items():
    assert value['sha256'] == architecture['binary_pins'][name] == baseline[name]
    header = struct.unpack('<8I', bytes.fromhex(value['header_hex']))
    assert value['bits'] == 64 and header[0] == 0xFEEDFACF and header[1] == value['cpu_type'] == 16777228
helper = A / 'css-accepted-119-121-122-install-runtime-v1/tests.py'
assert sha(helper) == '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5'
pure = [node for node in ast.parse(body(helper)).body if isinstance(node, ast.FunctionDef)
        and node.name in ('infrastructure_faults', 'lifecycle', 'exit_matches_results')]
assert len(pure) == 3
api = {}
exec(compile(ast.Module(body=pure, type_ignores=[]), '<pure lifecycle checks>', 'exec'), api)
events = [loads(line) for line in body(R / 'wpt-diagnostic/raw.json').splitlines()]
run = read(R / 'wpt-diagnostic/RUN.json')
assert run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
    '--log-raw=' + str(R / 'wpt-diagnostic/raw.json'), test]
assert run['complete'] is True and run['before'] == run['after'] == active
assert not api['infrastructure_faults'](events) and run['infrastructure_faults'] == []
assert api['lifecycle'](events, config)
assert sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1
for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
    assert run[key] == [e for e in events if e.get('action') == action]
assert len(run['starts']) == len(run['ends']) == 1 and run['ends'][0]['status'] == 'OK'
assert len(run['rows']) == len(set(names)) == 10 and [r['subtest'] for r in run['rows']] == names
assert all(r['test'] == url for r in run['rows'] + run['starts'] + run['ends'])
assert Counter(r['status'] for r in run['rows']) == {'PASS': 2, 'FAIL': 8}
assert run['exit'] == 1 and api['exit_matches_results'](run['exit'], run['rows'] + run['ends'])
controls = {names[4], names[9]}
observations = []
for row in run['rows']:
    if row['subtest'] in controls:
        assert row['status'] == 'PASS'
    else:
        assert row['status'] == 'FAIL' and row['expected'] == 'PASS' and row['known_intermittent'] == []
        assert row['message'] == 'assert_true: target name-repeat: declaration admission expected true got false'
        assert row['stack'].startswith('assign@http://web-platform.test:18000/css/css-grid/subgrid/subgrid-contextual-name-repeat.html:49:14\n')
        observations.append({'test': url, 'subtest': row['subtest'],
            'classification': 'TARGET_ADMISSION_FAILURE', 'later_history_reached': False})
assert read(R / 'CLASSIFICATION.json') == {'status': 'NAME_REPEAT_BASELINE_CLASSIFIED',
    'counts': {'PASS': 2, 'FAIL': 8}, 'subtests': 10, 'harnesses_ok': 1,
    'admission_failures': 8, 'observations': observations, 'issues': [],
    'known_bug': 2037744, 'required_failure_count': None, 'native_acceptance': False}
assert read(R / 'wpt-diagnostic/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
assert read(R / 'CLEANUP.json') == {'removed': [test], 'errors': [], 'capture_error': None}
assert read(R / 'CAPTURE.json') == {'status': 'COMPLETE_DIAGNOSTIC_CAPTURE', 'subtests': 10,
    'harnesses': 1, 'wpt_exit': 1, 'native_candidate_applied': False, 'classification_pending': True}
assert read(R / 'ROOT-FINAL-CHECK.json') == {'status': 'NAME_REPEAT_BASELINE_PRESERVATION_PASS',
    'roles': 611, 'sources': 72, 'installed_identities': 23, 'staged_paths': 925,
    'native_paths': 43, 'temporary_tests_removed': 1, 'capture_error': None,
    'final_pins_sha256': sha(R / 'FINAL-PINS.json'), 'native_acceptance': False}
refs[str((R / 'ROOT-FINAL-CHECK.json').relative_to(ROOT))] = sha(R / 'ROOT-FINAL-CHECK.json')
check = {'status': 'NAME_REPEAT_BASELINE_TERMINAL_REVIEW_GO',
    'capture_session': 66325, 'capture_exit': 0, 'classifier_session': None,
    'classifier_tool_chunk': '7c15cc', 'classifier_exit': 0, 'raw_records': len(events),
    'counts': {'PASS': 2, 'FAIL': 8}, 'harnesses_ok': 1, 'admission_failures': 8,
    'later_target_histories_reached': False, 'roles': 611, 'sources': 72,
    'installed_identities': 23, 'staged_payloads': 925, 'native_paths': 43,
    'fixtures_removed': 1, 'capture_preservation_blockers': [],
    'native_acceptance': False, 'live_inputs_read': False, 'live_actions': False}
for name, value in [('CHECK.json', check), ('REFERENCES.json', refs)]:
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(check, indent=2))
