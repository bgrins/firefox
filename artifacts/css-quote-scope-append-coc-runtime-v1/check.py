import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


c = load('quote_controller_check', HERE / 'compare.py')
t = load('quote_tests_check', HERE / 'tests.py')
p = load('quote_policy_check', HERE / 'policy.py')
for name, pin in c.read(HERE / 'REFERENCES.json').items():
    assert c.sha(ROOT / name) == pin, name
inputs = c.read(HERE / 'INPUTS.json')
assert inputs['ready'] is False and inputs['admission'] is None and inputs['root_review'] is None
for name, pin in inputs['local_pins'].items():
    assert c.sha(HERE / name) == pin, name
for name in ('build.py', 'process_control.py'):
    assert (HERE / name).read_bytes() == (ROOT / 'artifacts/css-cubic-bezier-calc-range-comparison-v1' / name).read_bytes()
old_tests = (ROOT / 'artifacts/css-integer-stored-range-metadata-validation-v2/tests.py').read_text()
assert (HERE / 'tests.py').read_text() == old_tests.replace("('PASS' if e['test'] in c['reftests'] else 'OK')", "(c['expected_end_only'][e['test']] if e['test'] in c['reftests'] else 'OK')")
old_argv = c.sys.argv
c.sys.argv = ['compare.py', '--run']
try:
    c.main()
except RuntimeError as error:
    assert str(error) == 'Disabled comparison'
else:
    raise AssertionError('disabled controller accepted')
finally:
    c.sys.argv = old_argv

config = c.read(HERE / 'CONFIG.json')
config['reftests'] = list(config['expected_end_only'])
config['guard_sources'] = ['source']
historical = c.read(HERE / 'HISTORICAL-OBSERVATIONS.json')
regressions = c.read(HERE / 'REGRESSIONS.json')
results = {}
dispatches = []
original_popen = t.subprocess.Popen
try:
    with tempfile.TemporaryDirectory(prefix='quote-dispatch-', dir='/private/tmp') as tmp:
        scratch = Path(tmp)
        for phase in config['phases']:
            rows = copy.deepcopy(historical['original' if phase == 'scoped-original' else 'candidate'])
            for row in rows:
                if row['expected'] is None:
                    del row['expected']
            events = [{'action': 'suite_start'}]
            for test in config['tests']:
                test = '/' + test
                events.append({'action': 'test_start', 'test': test})
                events.extend(dict(r, action='test_status') for r in rows if r['test'] == test)
                if test in config['expected_subtests']:
                    end = {'test': test, 'status': 'OK'}
                else:
                    end = copy.deepcopy(next(r for r in regressions if r['test'] == test))
                    end['expected'] = end.pop('effective_expected')
                events.append(dict(end, action='test_end'))
            events.append({'action': 'suite_end'})
            def popen(command, **kwargs):
                assert command[-19:] == config['tests']
                raw = Path(next(v.split('=', 1)[1] for v in command if v.startswith('--log-raw=')))
                raw.write_text(''.join(json.dumps(e) + '\n' for e in events))
                code = 1 if phase == 'scoped-original' else 0
                return types.SimpleNamespace(pid=999999, wait=lambda **kw: code)
            t.subprocess.Popen = popen
            adapter = types.SimpleNamespace(CONFIG=config, HERE=scratch, ROOT=scratch, ENV={}, PYTHON='inert-python',
                BINARY=scratch / 'binary', BINARIES={'binary'}, WPT_CONFIG=scratch / 'wpt.ini', PREFS_ROOT=scratch / 'prefs',
                pins=lambda paths: dict.fromkeys(paths, 'pin'), need=c.need, cancelled=lambda: False, owned_group=None,
                process_control=types.SimpleNamespace(terminate=lambda process: {'owned_group_absent': True}))
            result = t.run(adapter, phase, {'source': 'pin'})
            assert result['complete'] and len(result['rows']) == 64 and len(result['ends']) == 19 and adapter.owned_group is None
            p.check(result, config, phase, p.values(results['candidate-initial']) if results else None)
            results[phase] = result
            dispatches.append({'phase': phase, 'rows': len(result['rows']), 'ends': len(result['ends']), 'exit': result['exit']})
finally:
    t.subprocess.Popen = original_popen

negative = 0
for phase, change in [('candidate-initial', 'status'), ('scoped-original', 'failure-message'),
                      ('scoped-original', 'control-message'), ('candidate-restored', 'message'),
                      ('candidate-initial', 'regression'), ('candidate-initial', 'expectation'),
                      ('candidate-initial', 'duplicate'), ('candidate-initial', 'missing')]:
    bad = copy.deepcopy(results[phase])
    if change == 'status': bad['rows'][0]['status'] = 'FAIL'
    if change == 'failure-message': next(r for r in bad['rows'] if r['status'] == 'FAIL')['message'] = 'other failure'
    if change == 'control-message': next(r for r in bad['rows'] if r['status'] == 'PASS')['message'] = 'changed control'
    if change == 'message': bad['rows'][0]['message'] = 'changed candidate'
    if change == 'regression': next(r for r in bad['ends'] if r['status'] == 'FAIL')['status'] = 'PASS'
    if change == 'expectation': bad['rows'][0]['expected'] = 'FAIL'
    if change == 'duplicate': bad['rows'].append(bad['rows'][0])
    if change == 'missing': bad['ends'].pop()
    try:
        p.check(bad, config, phase, p.values(results['candidate-initial']))
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('corrupt policy admitted: ' + change)

main = next(n for n in ast.parse((HERE / 'compare.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
function = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
    body=ast.parse('baseline = None\nmutation_started = False\nerror = None\n').body + [tail], decorator_list=[])
tail_code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), '<actual-quote-recovery-tail>', 'exec')
tail_cases = []
for case in ('normal', 'initial-failure', 'original-build-failure', 'original-capture-failure',
             'restored-build-failure', 'unknown-first', 'live-group', 'receipt-failure', 'partial-second-write'):
    with tempfile.TemporaryDirectory(prefix='quote-recovery-', dir='/private/tmp') as tmp:
        root = Path(tmp)
        originals = {'first': b'first-candidate', 'second': b'second-candidate'}
        candidates = {'first': b'first-original', 'second': b'second-original'}
        for n, data in originals.items(): (root / n).write_bytes(data)
        pre = {n: {'sha256': c.body_sha(data)} for n, data in originals.items()}
        owned, captures, errors, transitions, receipts, calls = {}, {}, [], [], {}, []
        def quiet():
            if case == 'live-group' and 'build-scoped-original' in calls:
                raise RuntimeError('owned process remains')
        def capture(label):
            calls.append(label)
            if case == 'initial-failure' and label == 'candidate-initial': raise RuntimeError('first rejected')
            if case == 'original-capture-failure' and label == 'scoped-original': raise RuntimeError('original rejected')
            if case == 'unknown-first' and label == 'scoped-original':
                (root / 'first').write_bytes(b'unknown')
                raise RuntimeError('unknown edit')
            captures[label] = {}
        def build(label):
            calls.append('build-' + label)
            if (case == 'original-build-failure' and label == 'scoped-original') or (case == 'restored-build-failure' and label == 'candidate-restored'):
                raise RuntimeError('build failed')
        def write(root, item, data):
            if case == 'partial-second-write' and item['path'] == 'second' and data == candidates['second']:
                c.write_owned(root, item, data[:3])
                raise OSError('partial write')
            c.write_owned(root, item, data)
        def verify(label):
            assert all((root / n).read_bytes() == data for n, data in originals.items())
        def save(name, data):
            if case == 'receipt-failure' and name == 'RESTORATION-INPUT-BINARIES.json': raise OSError('publication failed')
            receipts[name] = copy.deepcopy(data)
        env = dict(vars(c), ROOT=root, pre=pre, originals=originals, candidates=candidates, owned=owned,
            captures=captures, errors=errors, transitions=transitions, quiet=quiet, capture=capture, build=build,
            write_owned=write, verify=verify, save=save, binaries={}, binary_names=set(), state={}, config=config,
            adapter=types.SimpleNamespace(cancelled=lambda: False, owned_group=None), epoch={'semantic_index': {}},
            h=types.SimpleNamespace(index_state=lambda *a: {}, semantic_index=lambda x: x), env={})
        exec(tail_code, env)
        env['exercise']()
        assert receipts['RESULT.json']['success'] == (case == 'normal')
        if case == 'unknown-first':
            assert (root / 'first').read_bytes() == b'unknown' and (root / 'second').read_bytes() == originals['second']
            assert 'build-candidate-restored' not in calls
        elif case == 'live-group':
            assert all((root / n).read_bytes() == data for n, data in candidates.items())
        else:
            assert all((root / n).read_bytes() == data for n, data in originals.items())
        if case == 'receipt-failure':
            assert 'build-candidate-restored' in calls and 'candidate-restored' in captures and len(errors) == 1
        tail_cases.append({'case': case, 'calls': calls, 'success': receipts['RESULT.json']['success']})

nested = [copy.deepcopy(n) for n in main.body if isinstance(n, ast.FunctionDef) and n.name in ('verify', 'build', 'capture')]
for node in nested:
    node.body = [n for n in node.body if not isinstance(n, ast.Nonlocal)]
flow = compile(ast.fix_missing_locations(ast.Module(body=nested, type_ignores=[])), '<actual-recovery-receipt-flow>', 'exec')
receipt_cases = []
for fault in ('candidate-restored-BUILD-PRE.json', 'candidate-restored-BUILD-POST.json',
              'candidate-restored-PRE.json', 'candidate-restored-POST.json', 'guard-failure'):
    with tempfile.TemporaryDirectory(prefix='quote-receipt-', dir='/private/tmp') as tmp:
        root = Path(tmp)
        index = {'head': 'head', 'entries': 'entries', 'cached_diff': 'cached', 'raw_index': 'raw'}
        calls, errors = [], []
        def pins(names):
            return {n: ('unexpected' if fault == 'guard-failure' and n == 'source' else
                        'original' if n == 'source' else 'rebuilt') for n in names}
        def save(name, data):
            if name == fault: raise OSError('verified receipt publication failed')
        env = dict(vars(c), ROOT=root, HERE=root, OBJ=root / 'obj', env={}, roles={'source': 'original'},
            binaries={'binary': 'rebuilt'}, binary_names={'binary'}, owned={}, errors=errors, excluded=[],
            external_diff=c.body_sha(b'outside'), pre={}, mutable=set(), committed={}, initial_index=index, initial_nested=index,
            epoch={'semantic_index': index, 'nested_semantic_index': index, 'staged_working': {},
                'committed_research_working_payloads': {}, 'installed_identities': {}, 'modified_native_paths': [], 'untracked_native': []},
            h=types.SimpleNamespace(index_state=lambda *a: index.copy(), semantic_index=lambda x: x,
                git=lambda *a: b'outside' if '--binary' in a else b'', fingerprint=lambda *a: 'rebuilt'),
            adapter=types.SimpleNamespace(pins=pins, cancelled=lambda: False, owned_group=None), quiet=lambda: None,
            save=save, read=lambda path: {}, ports_free=lambda config: None, state={}, process_control=types.SimpleNamespace(),
            captures={'candidate-initial': {}}, config=config, policy=types.SimpleNamespace(values=lambda r: {}, check=lambda *a: None),
            tests=types.SimpleNamespace(run=lambda *a: calls.append('capture') or {}),
            builder=types.SimpleNamespace(run=lambda *a: calls.append('build')))
        exec(flow, env)
        try:
            env['build']('candidate-restored')
            env['capture']('candidate-restored')
        except RuntimeError:
            assert fault == 'guard-failure' and calls == [] and errors == []
        else:
            assert fault != 'guard-failure' and calls == ['build', 'capture'] and len(errors) == 1
        receipt_cases.append({'case': fault, 'calls': calls, 'errors': errors})

print(json.dumps({'status': 'QUOTE_COC_STATIC_PASS', 'actual_helper_dispatch': dispatches,
    'policy_negatives': negative, 'actual_tail_cases': tail_cases, 'actual_receipt_cases': receipt_cases, 'scratch_removed': True,
    'live_build_browser_git_calls': 0}, indent=2))
