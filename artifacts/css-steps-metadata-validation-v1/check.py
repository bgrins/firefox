import ast
import copy
import hashlib
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


v = load('metadata_validation', HERE / 'validate.py')
common = load('metadata_common_check', v.ROOT / v.COMMON)
roster = v.read(HERE / 'ROSTER.json')
before = [{'test': t, 'subtest': n, 'status': 'PASS'} for t, names in roster.items() for n in names]
targets = [i for i, r in enumerate(before) if 'steps(calc(1), jump-none)' in r['subtest']]
for i in targets:
    before[i]['expected'] = 'FAIL'
control = next(i for i, r in enumerate(before) if 'steps(calc(-10), start)' in r['subtest'])
before[control]['expected'] = 'FAIL'
after = copy.deepcopy(before)
for i in targets:
    del after[i]['expected']
assert v.check_rows(before, after, roster)['rows'] == 44
negative_count = 0
for mutate in (
    lambda a: a.pop(),
    lambda a: a.append(copy.deepcopy(a[0])),
    lambda a: a[targets[0]].update(status='FAIL'),
    lambda a: a[targets[0]].update(expected='FAIL'),
    lambda a: a[targets[1]].update(message='changed'),
    lambda a: a[targets[1]].update(known_intermittent=['PASS']),
    lambda a: a[control].pop('expected'),
    lambda a: a[0].update(status='FAIL'),
    lambda a: a[0].update(message='changed'),
    lambda a: a[0].update(known_intermittent=['FAIL']),
):
    changed = copy.deepcopy(after)
    mutate(changed)
    try:
        v.check_rows(before, changed, roster)
    except RuntimeError:
        negative_count += 1
    else:
        raise AssertionError('bad rows accepted')

tree = ast.parse((HERE / 'validate.py').read_text())
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try))
code = compile(ast.Module(body=[tail], type_ignores=[]), '<actual-validation-tail>', 'exec')
tail_cases = []
for fault in ('none', 'capture', 'compare', 'post_guard', 'final_guard', 'publication', 'second_write', 'unknown_edit', 'live_group'):
    with tempfile.TemporaryDirectory(prefix='steps-metadata-control-', dir='/private/tmp') as td:
        root = Path(td)
        originals = {'one.ini': b'old one', 'two.ini': b'old two'}
        candidates = {n: b'new ' + b for n, b in originals.items()}
        for n, b in originals.items():
            (root / n).write_bytes(b)
        paths = {n: {'preimage': {'sha256': hashlib.sha256(b).hexdigest()}} for n, b in originals.items()}
        adapter = types.SimpleNamespace(owned_group=None)
        records = {}
        def quiet():
            v.need(adapter.owned_group is None, 'live group')
        def verify(label):
            if (fault, label) in (('post_guard', 'CANDIDATE-AFTER.json'), ('final_guard', 'FINAL.json')):
                raise RuntimeError(fault)
            records[label] = True
            return {}
        def save(name, value):
            if fault == 'publication' and name == 'RESULT.json':
                raise OSError('publication')
            records[name] = value
        def run(*args):
            if fault == 'live_group':
                adapter.owned_group = 123
                raise RuntimeError('cleanup rejected')
            if fault == 'unknown_edit':
                (root / 'one.ini').write_bytes(b'unknown')
                raise RuntimeError('unknown edit')
            if fault == 'capture':
                raise RuntimeError(fault)
            return {'rows': after}
        def compare(*args):
            if fault == 'compare':
                raise RuntimeError(fault)
            return v.check_rows(*args)
        def write(root, item, body):
            if fault == 'second_write' and item['path'] == 'two.ini':
                common.write_owned(root, item, body[:2])
                raise OSError('partial write')
            common.write_owned(root, item, body)
        ns = dict(v.__dict__, ROOT=root, paths=paths, candidates=candidates, originals=originals,
            owned={}, errors=[], success=False, error=None, terminated=False, adapter=adapter,
            original_rows=before, roster=roster, read=lambda p: {}, quiet=quiet, verify=verify, save=save,
            check_rows=compare, tests=types.SimpleNamespace(run=run),
            common=types.SimpleNamespace(write_owned=write, restore_owned=common.restore_owned, ports_free=lambda c: None),
            epoch={'semantic_index': {}}, env={},
            h=types.SimpleNamespace(index_state=lambda *args: {}, semantic_index=lambda x: x))
        exec(code, ns)
        assert ns['success'] == (fault == 'none')
        if fault == 'none':
            assert all((root / n).read_bytes() == b for n, b in candidates.items())
        elif fault == 'live_group':
            assert all((root / n).read_bytes() == b for n, b in candidates.items()) and ns['errors']
        elif fault == 'unknown_edit':
            assert (root / 'one.ini').read_bytes() == b'unknown' and (root / 'two.ini').read_bytes() == originals['two.ini'] and ns['errors']
        else:
            assert all((root / n).read_bytes() == b for n, b in originals.items()) and not ns['errors']
        tail_cases.append(fault)
print(json.dumps({'status': 'STEPS_METADATA_STATIC_CHECKS_PASS', 'row_negatives': negative_count,
    'actual_tail_cases': tail_cases, 'scratch_removed': True, 'browser_or_live_mutation': False}, indent=2))
