import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
a = argparse.ArgumentParser()
a.add_argument('--output', type=Path, required=True)
out = a.parse_args().output.resolve()
assert not out.exists()
out.mkdir()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

controller = load('steps_check_controller', HERE / 'compare.py')
policy = load('steps_check_policy', HERE / 'policy.py')
expected_roles = {
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
    'objdir-full.noindex/dist/bin/gtest/XUL',
}
assert controller.BINARY_ROLES == expected_roles
main_ast = next(n for n in ast.parse((HERE / 'compare.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
gate = next(n.value.args[0] for n in main_ast.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and n.value.args and isinstance(n.value.args[-1], ast.Constant) and n.value.args[-1].value == 'exact four binary roles')
gate_code = compile(ast.fix_missing_locations(ast.Expression(body=gate)), '<actual-four-binary-gate>', 'eval')
signed = {'pins': dict.fromkeys(expected_roles | {'servo/components/style/values/specified/easing.rs'}, 'old')}
def admitted(names, pins=signed):
    return eval(gate_code, {'binary_names': names, 'BINARY_ROLES': controller.BINARY_ROLES, 'signed': pins})
assert admitted(expected_roles)
binary_negatives = [expected_roles - {n} for n in expected_roles]
binary_negatives += [expected_roles | {'servo/components/style/values/specified/easing.rs'},
                    (expected_roles - {'objdir-full.noindex/dist/bin/gtest/XUL'}) | {'unrelated/XUL'}]
assert all(not admitted(names) for names in binary_negatives)
assert not admitted(expected_roles, {'pins': {n: 'old' for n in expected_roles if not n.endswith('dist/bin/gtest/XUL')}})
# The actual nonbinary guard must still reject an unrelated source change.
source_gate = next(n.value.args[0] for n in main_ast.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and n.value.args and isinstance(n.value.args[-1], ast.Constant) and n.value.args[-1].value == 'signed nonbinary epoch preserved')
source_code = compile(ast.fix_missing_locations(ast.Expression(body=source_gate)), '<actual-nonbinary-gate>', 'eval')
epoch = {'pins': signed['pins'] | dict.fromkeys(expected_roles, 'rebuilt')}
assert eval(source_code, {'signed': signed, 'epoch': epoch, 'binary_names': expected_roles})
epoch['pins']['servo/components/style/values/specified/easing.rs'] = 'unexpected'
assert not eval(source_code, {'signed': signed, 'epoch': epoch, 'binary_names': expected_roles})

inputs = json.loads((HERE / 'INPUTS.json').read_text())
assert inputs['ready'] is False and inputs['owner_build_binding'] is None and inputs['root_review'] is None
refusal = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'compare.py'), '--run'], capture_output=True, text=True)
assert refusal.returncode == 1 and 'Disabled comparison' in refusal.stderr
(out / 'disabled.log').write_text(refusal.stdout + refusal.stderr)
p = json.loads((HERE / 'COMPARISON-POLICY.json').read_text())
rows = copy.deepcopy(p['unchanged_control_rows'])
for item in p['candidate_mandatory_pass']:
    rows.append(item | {'status': 'FAIL', 'expected': 'PASS', 'message': 'synthetic first failure', 'known_intermittent': []})
baseline = policy.check(rows, p, 'original')
candidate = copy.deepcopy(rows)
required = {(r['test'], r['subtest']) for r in p['candidate_mandatory_pass']}
for r in candidate:
    if (r['test'], r['subtest']) in required:
        r.update(status='PASS', message=None)
policy.check(candidate, p, 'candidate', baseline)
policy.check(rows, p, 'restored', baseline)
negative = 0
for index in range(77):
    bad = copy.deepcopy(candidate)
    bad[index]['status'] = 'FAIL' if bad[index]['status'] == 'PASS' else 'PASS'
    try:
        policy.check(bad, p, 'candidate', baseline)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('status corruption admitted')
for bad in [candidate[:-1], candidate + [candidate[0]]]:
    try:
        policy.check(bad, p, 'candidate', baseline)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('identity corruption admitted')
# Replay the actual try/finally body with scratch files and fake capture/build callbacks.
main = next(n for n in ast.parse((HERE / 'compare.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
function = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
    body=ast.parse('baseline = None\nmutation_started = False\nerror = None\n').body + [tail], decorator_list=[])
code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), '<actual-comparison-tail>', 'exec')
scenarios = []
for case in ['normal', 'original-failure', 'candidate-build-failure', 'candidate-capture-failure', 'restored-build-failure', 'unknown-native', 'unknown-first-test', 'live-group']:
    with tempfile.TemporaryDirectory(prefix='steps-tail-', dir='/private/tmp') as tmp:
        root = Path(tmp)
        names = ['native', 'test-first', 'test-second', 'new-test']
        originals = {n: None if n == 'new-test' else (n + '-original').encode() for n in names}
        candidates = {n: (n + '-candidate').encode() for n in names}
        for n, data in originals.items():
            if data is not None:
                (root / n).write_bytes(data)
        pre = {n: {'sha256': controller.body_sha(b)} if b is not None else None for n, b in originals.items()}
        owned, captures, errors, transitions, results, calls = {}, {}, [], [], {}, []
        def quiet():
            if case == 'live-group' and 'candidate' in calls:
                raise RuntimeError('owned group remains')
        def capture(label):
            calls.append(label)
            captures[label] = {}
            if (case == 'original-failure' and label == 'original') or (case == 'candidate-capture-failure' and label == 'candidate'):
                raise RuntimeError('capture rejected')
            if label == 'candidate' and case.startswith('unknown-'):
                (root / ('native' if case == 'unknown-native' else 'test-first')).write_bytes(b'unknown edit')
                raise RuntimeError('unknown edit observed')
        def build(label):
            if case == label + '-build-failure':
                raise RuntimeError('build rejected')
        def verify(label):
            if label == 'FINAL.json':
                assert all((not (root / n).exists()) if b is None else (root / n).read_bytes() == b for n, b in originals.items())
            return {}
        env = dict(vars(controller), ROOT=root, NATIVE='native', pre=pre, candidates=candidates, originals=originals,
            owned=owned, captures=captures, errors=errors, transitions=transitions, quiet=quiet, capture=capture,
            build=build, verify=verify, build_attempted=True, binaries={}, binary_names=set(), state={},
            adapter=types.SimpleNamespace(cancelled=lambda: False, owned_group=None),
            epoch={'semantic_index': {}}, h=types.SimpleNamespace(index_state=lambda *a: {}, semantic_index=lambda x: x),
            env={}, save=lambda name, data: results.update({name: copy.deepcopy(data)}))
        exec(code, env)
        env['exercise']()
        result = results['RESULT.json']
        assert result['success'] == (case == 'normal')
        if case not in ['unknown-native', 'unknown-first-test', 'live-group']:
            assert all((not (root / n).exists()) if b is None else (root / n).read_bytes() == b for n, b in originals.items())
        if case == 'unknown-native':
            assert (root / 'native').read_bytes() == b'unknown edit' and not (root / 'new-test').exists()
        if case == 'unknown-first-test':
            assert (root / 'test-first').read_bytes() == b'unknown edit'
            assert (root / 'test-second').read_bytes() == originals['test-second'] and not (root / 'new-test').exists()
        if case == 'live-group':
            assert (root / 'native').read_bytes() == candidates['native'] and (root / 'new-test').exists()
        scenarios.append({'case': case, 'result': result, 'scratch_removed_after_context': True})
(out / 'TAIL-SCENARIOS.json').write_text(json.dumps(scenarios, indent=2) + '\n')
(out / 'CHECK.json').write_text(json.dumps({'status': 'STEPS_COMPARISON_STATIC_PASS', 'policy_negative_cases': negative, 'binary_gate_negatives': 8,
    'actual_tail_scenarios': len(scenarios), 'disabled_refusal': True, 'synthetic_not_browser': True}, indent=2) + '\n')
print('PASS: disabled refusal,79 policy corruptions,8 actual-tail scratch scenarios')
