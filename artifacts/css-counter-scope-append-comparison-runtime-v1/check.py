import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load('counter_compare_check', HERE / 'compare.py')
p = load('counter_policy_check', HERE / 'policy.py')
t = load('counter_tests_check', HERE / 'tests.py')
old = ROOT / 'artifacts/css-quote-scope-append-coc-runtime-v2'
for name in ('build.py', 'tests.py', 'process_control.py'):
    assert (HERE / name).read_bytes() == (old / name).read_bytes()
for name, pin in c.read(HERE / 'REFERENCES.json').items():
    assert c.sha(ROOT / name) == pin
inputs = c.read(HERE / 'INPUTS.json')
assert inputs['ready'] is False and inputs['admission'] is None and inputs['root_review'] is None
for name, pin in inputs['local_pins'].items():
    assert c.sha(HERE / name) == pin
argv = c.sys.argv
try:
    c.sys.argv = ['compare.py', '--run']
    c.main()
except RuntimeError as error:
    assert str(error) == 'Disabled comparison'
else:
    raise AssertionError('disabled admission')
finally:
    c.sys.argv = argv

tree = ast.parse((HERE / 'compare.py').read_text())
old_tree = ast.parse((old / 'compare.py').read_text())
functions = lambda tree: {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
actual, previous = functions(tree), functions(old_tree)
for name in ('verify', 'write_owned', 'restore_owned', 'index_interval', 'index_flags', 'ports_free', 'quiet'):
    assert ast.dump(actual[name]) == ast.dump(previous[name]), name

config = c.read(c.PROPOSAL / 'CONFIG.json')
config['guard_sources'] = ['source']
config['reftests'] = list(config['expected_end_only'])
historical = {'rows': c.read(c.PROPOSAL / 'HISTORICAL-OBSERVATIONS.json')}
results, captures, dispatches = {}, {}, []
original_popen = t.subprocess.Popen
try:
    with tempfile.TemporaryDirectory(prefix='counter-dispatch-', dir='/private/tmp') as tmp:
        scratch = Path(tmp)
        for phase in config['phases']:
            original = phase.startswith('original')
            rows = copy.deepcopy(historical['rows'])
            if not original:
                for row in rows:
                    row['status'] = 'PASS'
                    row.pop('expected', None)
                    row.pop('message', None)
            rows += [{'test': p.QUOTE, 'subtest': name, 'status': 'PASS', 'known_intermittent': []}
                     for name in config['expected_subtests'][p.QUOTE]]
            events = [{'action': 'suite_start'}]
            for test in config['tests']:
                test = '/' + test
                events.append({'action': 'test_start', 'test': test})
                events.extend(dict(row, action='test_status') for row in rows if row['test'] == test)
                events.append({'action': 'test_end', 'test': test,
                               'status': config['expected_end_only'].get(test, 'OK')})
            events.append({'action': 'suite_end'})
            def popen(command, **kwargs):
                assert command[-10:] == config['tests']
                raw = Path(next(v.split('=', 1)[1] for v in command if v.startswith('--log-raw=')))
                raw.write_text(''.join(json.dumps(e) + '\n' for e in events))
                return types.SimpleNamespace(pid=999999, wait=lambda **kw: 1 if original else 0)
            t.subprocess.Popen = popen
            adapter = types.SimpleNamespace(CONFIG=config, HERE=scratch, ROOT=scratch, ENV={}, PYTHON='inert',
                BINARY=scratch / 'binary', BINARIES={'binary'}, WPT_CONFIG=scratch / 'config', PREFS_ROOT=scratch,
                pins=lambda names: dict.fromkeys(names, 'pin'), need=c.need, cancelled=lambda: False, owned_group=None,
                process_control=types.SimpleNamespace(terminate=lambda process: {'owned_group_absent': True}))
            result = t.run(adapter, phase, {'source': 'pin'})
            p.check(result, config, phase, captures, historical)
            captures[phase] = p.values(result)
            results[phase] = result
            dispatches.append({'phase': phase, 'rows': len(result['rows']), 'ends': len(result['ends']), 'exit': result['exit']})
finally:
    t.subprocess.Popen = original_popen

negatives = []
for phase, fault in [('original-initial', 'wrong-failure'), ('original-initial', 'initial-calibration'),
                     ('candidate-first', 'target-failure'), ('candidate-first', 'quote-failure'),
                     ('candidate-first', 'regression'), ('original-restored', 'message'),
                     ('candidate-final', 'optional-field'), ('candidate-final', 'missing')]:
    bad = copy.deepcopy(results[phase])
    if fault in ('wrong-failure', 'initial-calibration'):
        next(r for r in bad['rows'] if r['status'] == 'FAIL')['message'] = fault
    if fault == 'target-failure': bad['rows'][0]['status'] = 'FAIL'
    if fault == 'quote-failure': next(r for r in bad['rows'] if r['test'] == p.QUOTE)['status'] = 'FAIL'
    if fault == 'regression': next(r for r in bad['ends'] if r['status'] == 'PASS')['status'] = 'FAIL'
    if fault == 'message': bad['rows'][0]['message'] = 'different history'
    if fault == 'optional-field': bad['rows'][0]['known_intermittent'] = None
    if fault == 'missing': bad['ends'].pop()
    try: p.check(bad, config, phase, captures, historical)
    except RuntimeError: negatives.append(fault)
    else: raise AssertionError(fault)

main = actual['main']
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
body = ast.parse('mutation_started = False\nerror = None\ncomplete = False\nbuild_attempted = False\n').body
body += [copy.deepcopy(actual['transition']), copy.deepcopy(actual['outcome']), copy.deepcopy(tail)]
body += ast.parse('return complete').body
exercise = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=body, decorator_list=[])
code = compile(ast.fix_missing_locations(ast.Module(body=[exercise], type_ignores=[])), '<actual-counter-tail>', 'exec')
tail_checks = []
for fault in ('none', 'initial-capture', 'candidate-build', 'original-build', 'final-capture',
              'partial-write', 'unknown-source', 'live-group', 'source-receipt', 'recovery-receipt',
              'success-receipt', 'final-guard'):
    with tempfile.TemporaryDirectory(prefix='counter-tail-', dir='/private/tmp') as tmp:
        root = Path(tmp)
        originals = {'first': b'original-first', 'second': b'original-second'}
        candidates = {'first': b'candidate-first', 'second': b'candidate-second'}
        for name, value in originals.items(): (root / name).write_bytes(value)
        pre = {n: {'sha256': c.body_sha(value)} for n, value in originals.items()}
        owned, captures, errors, transitions, calls, receipts = {}, {}, [], [], [], {}
        def quiet():
            if fault == 'live-group' and 'build-candidate-first' in calls: raise RuntimeError('live owned group')
        def verify(label):
            calls.append('verify-' + label)
            if fault == 'final-guard' and label == 'FINAL.json': raise RuntimeError('final guard')
        def capture(label, recovering=False):
            calls.append(label)
            if (fault == 'initial-capture' and label == 'original-initial') or (fault == 'final-capture' and label == 'candidate-final'):
                raise RuntimeError('capture failure')
            if fault == 'unknown-source' and label == 'candidate-first':
                (root / 'first').write_bytes(b'external-edit')
                raise RuntimeError('external edit')
            captures[label] = {}
        def build(label, recovering=False):
            calls.append('build-' + label)
            if (fault in ('candidate-build', 'live-group', 'recovery-receipt') and label == 'candidate-first') or (fault == 'original-build' and label == 'original-restored'):
                raise RuntimeError('build failure')
        def write(root, item, data):
            if fault == 'partial-write' and item['path'] == 'second' and data == candidates['second']:
                c.write_owned(root, item, data[:3])
                raise OSError('partial write')
            c.write_owned(root, item, data)
        def save(name, value):
            if (fault == 'source-receipt' and name == 'candidate-first-SOURCES.json') or (fault == 'recovery-receipt' and name == 'RECOVERY-INPUT-BINARIES.json'):
                raise OSError('receipt failure')
            if fault == 'success-receipt' and name == 'RESULT.json':
                (root / name).write_text('{partial')
                raise OSError('partial success publication')
            receipts[name] = copy.deepcopy(value)
            (root / name).write_text(json.dumps(value))
        scope = dict(vars(c), ROOT=root, HERE=root, pre=pre, originals=originals, candidates=candidates,
            owned=owned, captures=captures, errors=errors, transitions=transitions, quiet=quiet, verify=verify,
            capture=capture, build=build, write_owned=write, save=save, binaries={}, binary_names=set(), state={},
            adapter=types.SimpleNamespace(cancelled=lambda: False, owned_group=None), config=config,
            epoch={'semantic_index': {}}, h=types.SimpleNamespace(index_state=lambda *a: {}, semantic_index=lambda x: x), env={})
        exec(code, scope)
        complete = scope['exercise']()
        assert complete == (fault == 'none')
        if fault == 'none':
            assert all((root / n).read_bytes() == value for n, value in candidates.items())
            assert [x for x in calls if x.startswith('build-')] == ['build-candidate-first', 'build-original-restored', 'build-candidate-final']
        elif fault == 'unknown-source':
            assert (root / 'first').read_bytes() == b'external-edit' and (root / 'second').read_bytes() == originals['second']
            assert 'build-failure-original' not in calls
        elif fault == 'live-group':
            assert all((root / n).read_bytes() == value for n, value in candidates.items())
            assert 'build-failure-original' not in calls
        else:
            assert all((root / n).read_bytes() == value for n, value in originals.items())
            if fault != 'initial-capture': assert 'build-failure-original' in calls and 'failure-original' in captures
        if fault == 'success-receipt': assert receipts['FAILURE.json']['success'] is False
        tail_checks.append({'case': fault, 'complete': complete, 'calls': calls})

print(json.dumps({'status': 'COUNTER_OCOC_STATIC_PASS', 'actual_helper_dispatches': dispatches,
    'policy_negative_controls': negatives, 'actual_tail_cases': tail_checks,
    'preservation_ownership_index_helpers_exact': True, 'live_calls': False, 'scratch_removed': True}, indent=2))
