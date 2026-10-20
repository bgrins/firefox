import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S without -O')
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'runtime-capture'
sha = lambda b: hashlib.sha256(b).hexdigest()

def require(ok, message):
    if not ok:
        raise SystemExit(message)

def read(name):
    return json.loads((RUN / name).read_text())

def rows_map(rows):
    result = {(r['test'], r['subtest']): (r['status'], r.get('expected', r['status'])) for r in rows}
    require(len(result) == len(rows), 'Duplicate subtest')
    return result

def ends_map(rows):
    result = {r['test']: (r['status'], r.get('expected', r['status'])) for r in rows}
    require(len(result) == len(rows), 'Duplicate test end')
    return result

def analyze():
    expected = json.loads((ROOT / 'EXPECTED-PINS.json').read_text())
    capture = json.loads((ROOT / 'CAPTURE.json').read_text())
    require(capture['stable_during_capture'] and not capture['runtime_modified'], 'Capture receipt')
    actual = {p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file()}
    require(actual == set(capture['files']), 'Runtime capture roster')
    for name, pin in capture['files'].items():
        require(sha((RUN / name).read_bytes()) == pin, 'Captured input: ' + name)
    for name, pin in expected['inputs'].items():
        require(sha((RUN / name).read_bytes()) == pin, 'Reviewed input: ' + name)
    inputs, before, final, state = [read(n + '.json') for n in ['INPUTS', 'BEFORE', 'FINAL', 'STATE']]
    prepared_prefix = 'artifacts/' + expected['runtime_directory'] + '/'
    for name, pin in inputs['pins'].items():
        if name.startswith(prepared_prefix):
            require(sha((RUN / name[len(prepared_prefix):]).read_bytes()) == pin,
                    'Prepared runtime input changed: ' + name)
    require(state['status'] == 'terminal' and state['accepted'] is False and 'failure' not in state, 'Terminal success')
    require(state['variant'] == 'v4-without-fix102' and state['exact_oracle_match'], 'Variant/oracle receipt')
    for field in ['source_restored', 'other_native_unchanged', 'head_unchanged', 'index_unchanged']:
        require(state[field] is True, field)
    for name, field in [('wpt-lint', 'wpt_lint_exit'), ('format-check', 'format_check_exit'),
                        ('candidate-build', 'candidate_build_exit'), ('restore-build', 'restore_build_exit')]:
        require(state[field] == read(name + '.json')['exit'] == 0, name)
        require((RUN / (name + '.log')).is_file(), 'Missing log: ' + name)
    for name in ['candidate-build', 'restore-build']:
        require(read(name + '.json')['command'] == ['./mach', 'build', 'binaries'], 'Build command')
    for key in ['head', 'index_diff_sha256', 'index_entries_sha256']:
        require(before[key] == final[key] == inputs[key], 'Historical input/before/final: ' + key)
    require(inputs['staged_paths'] == 229, 'Staged research count')
    for key in ['sources', 'fixed_native_pins']:
        require(before[key] == final[key], 'Restoration: ' + key)
    require(before['fixed_native_pins'] == inputs['fixed_native_pins'], 'Fixed native inputs')
    require(final['temporary_tests_absent'] is True, 'Temporary test restoration')
    require(read('RESTORED.json') == {**final['sources'], **final['fixed_native_pins']}, 'RESTORED receipt')
    sources = read('PREPARATION.json')['controlled_sources']
    require(len(sources) == 5 and set(sources) == set(before['sources']), 'Five source roster')
    run = read('standalone/RUN.json')
    require(run['complete'] and run['before'] == run['after'], 'WPT stable/complete')
    for source in sources:
        original = (RUN / 'original' / source).read_bytes()
        require(sha(original) == before['sources'][source] == final['sources'][source], 'Original role: ' + source)
        require((RUN / 'source-before' / source).read_bytes() == original, 'Pre-run source bytes')
        candidate = (RUN / 'candidate' / source).read_bytes()
        require(sha(candidate) == run['before'][source], 'Candidate runtime role: ' + source)
        own_key = 'artifacts/' + expected['runtime_directory'] + '/candidate/' + source
        require(inputs['pins'][own_key] == sha(candidate), 'Prepared candidate pin')
    require(run['before']['dom/base/DOMRect.cpp'] == expected['pre102_domrect_sha256'], 'Temporary DOMRect')
    require(final['sources']['dom/base/DOMRect.cpp'] == expected['restored_domrect_sha256'], 'Restored DOMRect')
    for source, pin in before['fixed_native_pins'].items():
        require(run['before'][source] == pin, 'Fixed native during WPT: ' + source)
    for name, pin in run['before'].items():
        if pin is None or name.startswith('objdir-full.noindex/'):
            continue
        require(sha((RUN / 'standalone/inputs' / name).read_bytes()) == pin, 'Captured WPT dependency: ' + name)
    events = [json.loads(line) for line in (RUN / 'standalone/raw.json').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    ends = [e for e in events if e.get('action') == 'test_end']
    require(rows == run['rows'] and ends == run['ends'], 'Raw WPT correspondence')
    require(sum(e.get('action') == 'suite_end' for e in events) == 1, 'Suite completion')
    require(len(rows) == 74 and len(ends) == 23, '74/23 coverage')
    tests = read('TESTS.json')
    require(set(ends_map(ends)) == {'/' + str(Path(t).relative_to('testing/web-platform/tests')) for t in tests}, 'Test roster')
    oracle = read('ORACLE.json')
    actual_rows, oracle_rows = rows_map(rows), rows_map(oracle['rows'])
    require(actual_rows == oracle_rows and ends_map(ends) == ends_map(oracle['ends']), 'Exact keyed integer-only oracle')
    require(run['exit'] == oracle['exit'] == read('standalone-wpt.json')['exit'] == 1, 'Expected WPT exit 1')
    require(state['candidate'] == {'exit': 1, 'complete': True, 'subtests': 74, 'files': 23}, 'Driver summary')
    own = '/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html'
    transformed = '/css/cssom-view/getBoundingClientRect-transformed-edge-precision.html'
    groups = {}
    for name, predicate in [('untransformed', lambda t: t == own),
                            ('transformed', lambda t: t == transformed),
                            ('existing', lambda t: t not in [own, transformed])]:
        selected = [v for (t, _), v in actual_rows.items() if predicate(t)]
        groups[name] = {'total': len(selected), 'PASS': sum(v[0] == 'PASS' for v in selected),
                        'expected_FAIL': sum(v == ('FAIL', 'FAIL') for v in selected),
                        'unexpected_FAIL': sum(v == ('FAIL', 'PASS') for v in selected)}
    require(groups == {'untransformed': {'total': 4, 'PASS': 4, 'expected_FAIL': 0, 'unexpected_FAIL': 0},
                       'transformed': {'total': 4, 'PASS': 2, 'expected_FAIL': 0, 'unexpected_FAIL': 2},
                       'existing': {'total': 66, 'PASS': 64, 'expected_FAIL': 2, 'unexpected_FAIL': 0}}, 'Outcome partition')
    return {'status': 'STANDALONE_WITHOUT_102_FINITE_GATE_PASS', 'producer_evidence': True,
            'independent_review': False, 'native_accepted': False, 'timing_performed': False,
            'subtests': 74, 'files': 23, 'expected_wpt_exit': 1, 'groups': groups,
            'source_roles': {'tested_pre102_DOMRect': expected['pre102_domrect_sha256'],
                             'restored_fix102_DOMRect': expected['restored_domrect_sha256']},
            'historical_head': final['head'], 'staged_paths_preserved': inputs['staged_paths'],
            'fixed_native_files': len(before['fixed_native_pins']),
            'runtime_binaries': {n: pin for n, pin in run['before'].items() if n.startswith('objdir-full.noindex/')},
            'limits': ['Shared build, not an isolated upstream build.',
                       'Historical source/index checks are contemporaneous receipts, not current HEAD/index assertions.',
                       'Staged content/mode/stage preservation does not establish raw index metadata identity.',
                       'No timing or broader acceptance follows. Historical binaries are hash receipts, not archived binaries.']}

require(sys.argv[1:] in ([], ['--check']), 'Usage: analyze.py [--check]')
result = analyze()
text = json.dumps(result, indent=2, sort_keys=True) + '\n'
if sys.argv[1:] == ['--check']:
    require((ROOT / 'COMPARISON.json').read_text() == text, 'Comparison differs')
else:
    (ROOT / 'COMPARISON.json').write_text(text)
print(json.dumps({'status': result['status'], 'subtests': result['subtests'], 'files': result['files']}))
