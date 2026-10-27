import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


controller = load('compare')
inputs = json.loads((HERE / 'INPUTS.json').read_text())
assert not inputs['ready'] and inputs['continuation_binding'] is None and inputs['root_review'] is None
run = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'compare.py'), '--run'], capture_output=True, text=True)
assert run.returncode == 1 and 'Disabled comparison' in run.stderr
main = next(n for n in ast.parse((HERE / 'compare.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
function = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
    body=ast.parse('error = None\n').body + [tail], decorator_list=[])
code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), '<actual-continuation-tail>', 'exec')
results = []
for case in ['normal', 'candidate-failure', 'restored-build-failure', 'receipt-failure', 'unknown-native', 'unknown-test', 'live-group']:
    with tempfile.TemporaryDirectory(prefix='steps-continuation-', dir='/private/tmp') as temp:
        root = Path(temp)
        originals = {'native': b'original', 'test': b'old-test', 'new': None}
        candidates = {'native': b'candidate', 'test': b'new-test', 'new': b'new'}
        owned = {}
        for name, body in candidates.items():
            (root / name).write_bytes(body)
            st = (root / name).lstat()
            owned[name] = {'path': name, 'identity': [st.st_dev, st.st_ino], 'owned_sha256': controller.body_sha(body)}
        errors, transitions, captures, calls, saved = [], [], {'original': {}}, [], {}
        def quiet():
            if case == 'live-group' and calls:
                raise RuntimeError('owned group remains')
        def capture(label):
            calls.append(label)
            captures[label] = {}
            if label == 'candidate':
                if case == 'unknown-native':
                    (root / 'native').write_bytes(b'unknown')
                if case == 'unknown-test':
                    (root / 'test').write_bytes(b'unknown')
                if case != 'normal' and case != 'receipt-failure' and case != 'restored-build-failure':
                    raise RuntimeError('candidate rejected')
        def build(label):
            calls.append('build-' + label)
            if case == 'restored-build-failure':
                raise RuntimeError('build failed')
        def save(name, value):
            if case == 'receipt-failure' and name == 'RESTORATION-INPUT-BINARIES.json':
                raise OSError('receipt failed')
            saved[name] = copy.deepcopy(value)
        def verify(label):
            assert all((root / n).read_bytes() == b if b is not None else not (root / n).exists() for n, b in originals.items())
            return {}
        env = dict(vars(controller), ROOT=root, NATIVE='native', originals=originals, owned=owned,
            captures=captures, errors=errors, transitions=transitions, quiet=quiet, capture=capture,
            build=build, save=save, verify=verify, mutation_started=True, build_attempted=True,
            baseline={}, binaries={}, binary_names=set(), state={}, env={},
            adapter=types.SimpleNamespace(cancelled=lambda: False, owned_group=None),
            epoch={'semantic_index': {}}, h=types.SimpleNamespace(index_state=lambda *args: {}, semantic_index=lambda x: x))
        exec(code, env)
        env['exercise']()
        result = saved['RESULT.json']
        assert result['success'] == (case == 'normal')
        assert 'build-candidate' not in calls
        if case not in ['live-group', 'unknown-native']:
            assert 'build-restored' in calls and (root / 'native').read_bytes() == originals['native']
        if case == 'receipt-failure':
            assert 'restored' in calls and len(errors) == 1 and errors[0].startswith('restoration binary receipt:')
        if case == 'unknown-test':
            assert (root / 'test').read_bytes() == b'unknown' and not (root / 'new').exists()
        results.append({'case': case, 'calls': calls, 'result': result})

tree = ast.parse((HERE / 'build.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
outer_with = next(n for n in fn.body if isinstance(n, ast.With))
outer_try = next(n for n in outer_with.body if isinstance(n, ast.Try))
final = outer_try.finalbody
start = next(i for i, n in enumerate(final) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'group_absent' for t in n.targets))
fragment = compile(ast.fix_missing_locations(ast.Module(body=final[start:start+2], type_ignores=[])), '<actual-build-cleanup>', 'exec')
for fail in [None, 'build', 'wake']:
    state = {'build': 1, 'wake': 2}
    calls = []
    def terminate(process):
        calls.append(process.name)
        if process.name == fail:
            raise RuntimeError('group still present')
        return {'owned_group_absent': True, 'method': 'synthetic-positive-absence'}
    env = {'state': state, 'cleanup_errors': [], 'process': types.SimpleNamespace(name='build'),
           'wake': types.SimpleNamespace(name='wake', poll=lambda: 0), 'save': lambda *args: None,
           'process_control': types.SimpleNamespace(terminate=terminate)}
    exec(fragment, env)
    assert calls == ['build', 'wake']
    assert state == ({} if fail is None else {fail: 1 if fail == 'build' else 2})
    assert bool(env['cleanup_errors']) == (fail is not None)
print(json.dumps({'status': 'CONTINUATION_STATIC_PASS', 'tail_cases': results, 'cleanup_cases': 3,
                  'disabled_refusal': True, 'scratch_removed': True, 'browser_or_native_execution': False}, indent=2))
