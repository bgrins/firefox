import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok, why):
    if not ok:
        raise RuntimeError(why)

inputs = read(D / 'INPUTS.json')
R = ROOT / inputs['runtime']
for name, digest in inputs['pins'].items():
    assert sha(ROOT / name) == digest
assert sha(R / 'DRAFT-FILES.json') == '82f7cbd8f1eac699cd50e30eb65c22e0751c5c6fe4c38e927642efbd10a2ab64'
for name, digest in read(R / 'DRAFT-FILES.json').items():
    assert sha(R / name) == digest
for name, digest in read(R / 'REFERENCES.json').items():
    assert sha(ROOT / name) == digest
c, result = read(R / 'CONFIG.json'), read(R / 'wpt-baseline/RUN.json')
events = [json.loads(line) for line in (R / 'wpt-baseline/raw.json').read_text().splitlines()]
rows = [e for e in events if e.get('action') == 'test_status']
starts = [e for e in events if e.get('action') == 'test_start']
ends = [e for e in events if e.get('action') == 'test_end']
assert rows == result['rows'] and starts == result['starts'] and ends == result['ends']
assert result['complete'] is False and result['exit'] == 1
assert result['before'] == result['after'] and len(result['before']) == 307
expected = c['expected_subtests']
assert len(expected) == 9 and sum(map(len, expected.values())) == 104
assert Counter(e['test'] for e in starts) == Counter(e['test'] for e in ends) == Counter({t: 1 for t in expected})
assert all(e['status'] == 'OK' for e in ends)
assert sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1
suite = next(e for e in events if e.get('action') == 'suite_start')
assert suite['run_info']['os'] == 'mac' and suite['run_info']['revision'] == c['head']
assert sorted(t for names in suite['tests'].values() for t in names) == sorted(expected)
assert len({(r['test'], r['subtest']) for r in rows}) == len(rows) == 104
active = set()
for event in events:
    if event.get('action') == 'test_start':
        assert event['test'] not in active
        active.add(event['test'])
    elif event.get('action') == 'test_status':
        assert event['test'] in active
    elif event.get('action') == 'test_end':
        assert event['test'] in active
        active.remove(event['test'])
assert not active

spec = importlib.util.spec_from_file_location('corrected_tests', D / 'tests.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
assert tests.infrastructure_faults(events) == result['infrastructure_faults'] == []
assert read(R / 'wpt-baseline/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
ordering = {}
for test, names in expected.items():
    actual = [r['subtest'] for r in rows if r['test'] == test]
    assert len(actual) == len(names) == len(set(names)) and set(actual) == set(names)
    if actual != names:
        ordering[test] = {'expected': names, 'actual': actual}
assert set(ordering) == {'/shadow-dom/offsetParent-across-shadow-boundaries.html'}
tests.require_phase(SimpleNamespace(CONFIG=c, need=need), 'baseline', result)
main = '/css/cssom-view/offset-integer-precision.html'
main_failures = [r for r in rows if r['test'] == main and r['status'] == 'FAIL']
assert {r['subtest']: r['message'] for r in main_failures} == c['baseline_failures']
assert all(r.get('expected') == 'PASS' and r.get('known_intermittent') == [] for r in main_failures)
control_failures = [r for r in rows if r['test'] != main and r['status'] == 'FAIL']
assert len(main_failures) == 6 and len(control_failures) == 4
metadata_expected = {
    '/css/cssom-view/offsetTop-offsetLeft-nested-offsetParents.html': {
        'Verifies that offsetTop and offsetLeft only go up one offsetParent when there are multiple nested offsetParents.'},
    '/css/cssom-view/subpixel-sizes-and-offsets.tentative.html': {
        "clientLeft and clientTop don't round 44.9", "clientLeft and clientTop don't round 44.5", "clientLeft and clientTop don't round 44.1"}}
assert {(r['test'], r['subtest']) for r in control_failures} == {(t, n) for t, names in metadata_expected.items() for n in names}
for test, names in metadata_expected.items():
    path = 'testing/web-platform/meta' + test + '.ini'
    text = (D / Path(path).name).read_text()
    assert sha(D / Path(path).name) == result['before'][path]
    for name in names:
        section = text.split('  [' + name + ']\n', 1)[1].split('\n  [', 1)[0]
        if 'nested-offsetParents' in test:
            assert section == '    expected:\n      if os == "linux": PASS\n      FAIL\n'
        else:
            assert section.strip() == 'expected: FAIL'
assert all('expected' not in r and r.get('known_intermittent') == [] for r in control_failures)

phase = read(D / 'BASELINE-BUILD.json')
assert phase == read(R / 'STATE.json')['phases']['baseline']
assert phase['build_exit'] == 0 and phase['source_before_build'] == phase['source_after_build']
snapshot = phase['source_after_build']
assert snapshot['sources'] == {**c['head_pins'], **c['baseline_pins']}
before = read(R / 'BEFORE.json')
for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
    assert snapshot[key] == before[key]
assert all(result['before'][name] == digest for name, digest in snapshot['sources'].items())
assert all(result['before'][name] == digest for name, digest in phase['binary_pins'].items())
fixture = next(iter(c['install']))
roles = {**read(R / 'RESOURCES.json'), **c['head_pins'], **c['baseline_pins'],
         fixture: sha(R / c['install'][fixture]), **phase['binary_pins']}
assert result['before'] == roles

old = (R / 'tests.py').read_text()
replacement = "        actual = [r['subtest'] for r in rows if r['test'] == test]\n        complete = complete and len(actual) == len(names) == len(set(names)) and set(actual) == set(names)\n"
assert (D / 'tests.py').read_text() == old.replace("        complete = complete and [r['subtest'] for r in rows if r['test'] == test] == names\n", replacement)
run_node = next(n for n in ast.parse((D / 'tests.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'run')
loop = next(n for n in run_node.body if isinstance(n, ast.For) and isinstance(n.target, ast.Tuple))
code = compile(ast.Module(body=[loop], type_ignores=[]), 'exact-name-set', 'exec')
def identities(test_rows):
    scope = dict(c=c, rows=test_rows, complete=True)
    exec(code, scope)
    return scope['complete']
assert identities(rows) and identities(list(reversed(rows)))
assert not identities(rows[:-1]) and not identities(rows + [rows[0]])
assert not identities([{**rows[0], 'subtest': 'foreign'}] + rows[1:])
receipt = {'status': 'BASELINE_REVALIDATED', 'original_complete': False,
           'revalidated_complete': True, 'runtime_failure_preserved': True,
           'runtime_restoration_assessed': False, 'runtime': inputs['runtime'],
           'raw_sha256': sha(R / 'wpt-baseline/raw.json'), 'run_sha256': sha(R / 'wpt-baseline/RUN.json'),
           'draft_sha256': sha(R / 'DRAFT-FILES.json'), 'corrected_parser_sha256': sha(D / 'tests.py'),
           'build_phase_sha256': sha(D / 'BASELINE-BUILD.json'), 'counts': dict(Counter(r['status'] for r in rows)),
           'exact_subtests': 104, 'files_ok': 9, 'stable_pins': 307,
           'main': {'PASS': 18, 'FAIL': 6}, 'controls': {'PASS': 76, 'metadata_expected_FAIL': 4},
           'order_differences': ordering, 'control_failures': control_failures,
           'baseline_binary_pins': phase['binary_pins'], 'identity_faults_rejected': 3,
           'candidate_observed': False, 'native_acceptance': False}
(D / 'BASELINE-REVALIDATED.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k not in ('control_failures', 'order_differences')}))
