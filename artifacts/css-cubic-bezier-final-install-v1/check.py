import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load('install_check', HERE / 'install.py')
p = load('install_policy_check', HERE / 'policy.py')
tests = load('install_tests_check', HERE / 'tests.py')
old = p.archived_candidate(c.ROOT, tests, c.read(HERE / 'HISTORICAL.json'))
policy = c.read(HERE / 'COMPARISON-POLICY.json')
candidate = copy.deepcopy(old)
targets = []
for i, r in enumerate(candidate):
    if r['test'].endswith(('timing-functions-syntax-valid.html', 'timing-functions-syntax-computed.html')) and (
        'steps(calc(1), jump-none)' in r['subtest'] or
        'cubic-bezier(calc(-2), calc(0.7 / 2), calc(1.5), calc(0))' in r['subtest']):
        targets.append(i)
        r.pop('expected')
assert p.compare(old, candidate, policy)['target_pass'] == 38
negative = 0
for i in range(113):
    bad = copy.deepcopy(candidate)
    bad[i]['status'] = 'FAIL' if bad[i]['status'] == 'PASS' else 'PASS'
    try:
        p.compare(old, bad, policy)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('changed status admitted')
for i in targets:
    bad = copy.deepcopy(candidate)
    bad[i]['expected'] = 'FAIL'
    try:
        p.compare(old, bad, policy)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('stale target expectation admitted')
ordinary = next(i for i in range(113) if i not in targets)
for field, value in [('expected', 'FAIL'), ('message', 'different'), ('known_intermittent', [])]:
    bad = copy.deepcopy(candidate)
    if bad[ordinary].get(field) == value:
        value = ['PASS'] if field == 'known_intermittent' else 'different-value'
    bad[ordinary][field] = value
    try:
        p.compare(old, bad, policy)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('control corruption admitted')
for bad in (candidate[:-1], candidate + [candidate[0]]):
    try:
        p.compare(old, bad, policy)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('roster corruption admitted')

main = next(n for n in ast.parse((HERE / 'install.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
code = compile(ast.fix_missing_locations(ast.Module(body=[tail], type_ignores=[])), '<actual-install-tail>', 'exec')
scenarios = []
for fault in ('none', 'build', 'capture', 'final_guard', 'epoch_publication', 'result_publication',
              'restoration_receipt', 'partial_write', 'unknown_native', 'unknown_metadata', 'live_group'):
    with tempfile.TemporaryDirectory(prefix='cubic-install-tail-', dir='/private/tmp') as td:
        root = Path(td)
        originals = {'native': b'native original', 'new-wpt': None, 'one.ini': b'one original', 'two.ini': b'two original'}
        candidates = {n: (n + ' candidate').encode() for n in originals}
        for n, data in originals.items():
            if data is not None:
                (root / n).write_bytes(data)
        pre = {n: {'sha256': c.body_sha(data)} if data is not None else None for n, data in originals.items()}
        post = {n: {'sha256': c.body_sha(data)} for n, data in candidates.items()}
        records = {'BEFORE.json': {'index': {'raw_index': 'original'}}}
        adapter = types.SimpleNamespace(cancelled=lambda: False, owned_group=None)
        calls = []
        ns = dict(vars(c), ROOT=root, HERE=root, NATIVE='native', pre=pre, post=post, candidates=candidates,
            originals=originals, owned={}, captures={}, errors=[], transitions=[], state={},
            build_attempted=False, mutation_started=False, success=False, error=None, adapter=adapter,
            binaries={}, binary_names=set(), env={}, inputs={'admission': None},
            epoch={'semantic_index': {}, 'installed_identities': {}, 'counts': {}},
            h=types.SimpleNamespace(index_state=lambda *a: {}, semantic_index=lambda x: x, fingerprint=lambda *a: 'binary'))
        def quiet():
            c.need(adapter.owned_group is None, 'group live')
        def build(label):
            ns['build_attempted'] = True
            calls.append('build-' + label)
            if fault == 'build' and label == 'candidate':
                raise RuntimeError('build failed')
        def capture(label):
            calls.append('capture')
            if fault == 'live_group':
                adapter.owned_group = 123
                raise RuntimeError('group live')
            if fault.startswith('unknown_'):
                (root / ('native' if fault == 'unknown_native' else 'one.ini')).write_bytes(b'unknown')
                raise RuntimeError('unknown edit')
            if fault in ('capture', 'restoration_receipt'):
                raise RuntimeError('capture failed')
            ns['captures'][label] = [None] * 113
        def verify(label, recover_receipt=False):
            if fault == 'final_guard' and label == 'FINAL.json':
                raise RuntimeError('guard failed')
            records[label] = {'modified_native_paths': [], 'index': {'raw_index': 'current'}}
            return {}
        def save(label, value):
            if ((fault == 'epoch_publication' and label == 'CURRENT-EPOCH.json') or
                (fault == 'result_publication' and label == 'RESULT.json') or
                (fault == 'restoration_receipt' and label == 'RESTORATION-INPUT-BINARIES.json')):
                records[label] = 'partial publication'
                raise OSError('publication failed')
            records[label] = copy.deepcopy(value)
        def write(root, item, body):
            if fault == 'partial_write' and item['path'] == 'one.ini':
                c.write_owned(root, item, body[:2])
                raise OSError('partial write')
            c.write_owned(root, item, body)
        ns.update(quiet=quiet, build=build, capture=capture, verify=verify, save=save,
                  read=lambda path: records[path.name], write_owned=write)
        exec(code, ns)
        assert ns['success'] == (fault == 'none')
        if fault == 'none':
            assert all((root / n).read_bytes() == b for n, b in candidates.items())
            assert calls == ['build-candidate', 'capture']
        elif fault not in ('unknown_native', 'unknown_metadata', 'live_group'):
            assert all(not (root / n).exists() if b is None else (root / n).read_bytes() == b for n, b in originals.items())
            if ns['build_attempted']:
                assert 'build-restored' in calls
        else:
            assert 'build-restored' not in calls and ns['errors']
            if fault != 'live_group':
                assert not (root / 'new-wpt').exists()
        if fault == 'restoration_receipt':
            assert 'build-restored' in calls and any('restoration binary receipt' in x for x in ns['errors'])
        if fault != 'none':
            assert records['FAILURE.json']['success'] is False
        scenarios.append(fault)
print(json.dumps({'status': 'CUBIC_FINAL_INSTALL_STATIC_PASS', 'historical_rows_reparsed': 113,
    'policy_negatives': negative, 'actual_tail_cases': scenarios, 'scratch_removed': True,
    'browser_or_native_operations': False}, indent=2))
