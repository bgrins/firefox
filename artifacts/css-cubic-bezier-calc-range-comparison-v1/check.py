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
assert inputs['ready'] is False and inputs['build_binding'] is not None and inputs['root_review'] is None

binding = inputs['build_binding']
assert hashlib.sha256((ROOT / binding['path']).read_bytes()).hexdigest() == binding['sha256']
build_admission = json.loads((ROOT / binding['path']).read_text())
assert build_admission['status'] == 'COMMITTED_STEPS_BUILD_VERIFIED' and build_admission['exit'] == 0
for ref in [build_admission['epoch'], *build_admission['evidence']]:
    assert hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest() == ref['sha256']
compiled_epoch = json.loads((ROOT / build_admission['epoch']['path']).read_text())
assert set(build_admission['binaries']) == expected_roles
assert all(compiled_epoch['pins'][n] == h for n, h in build_admission['binaries'].items())
assert compiled_epoch['pins'][controller.NATIVE] == build_admission['sources'][controller.NATIVE]
for name, digest in inputs['local_pins'].items():
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
for name, item in json.loads((controller.PROPOSAL / 'FILES.json').read_text()).items():
    assert hashlib.sha256((controller.PROPOSAL / name).read_bytes()).hexdigest() == (item['sha256'] if isinstance(item, dict) else item), name
preimages = json.loads((HERE / 'PREIMAGES.json').read_text())
postimages = json.loads((HERE / 'POSTIMAGES.json').read_text())
for name, item in preimages.items():
    if item is not None:
        side = 'after-steps-original' if name == controller.NATIVE else 'original'
        assert hashlib.sha256((controller.PROPOSAL / side / name).read_bytes()).hexdigest() == item['sha256']
for name, item in postimages.items():
    side = 'after-steps-candidate' if name == controller.NATIVE else 'candidate'
    assert hashlib.sha256((controller.PROPOSAL / side / name).read_bytes()).hexdigest() == item['sha256']

refusal = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'compare.py'), '--run'], capture_output=True, text=True)
assert refusal.returncode == 1 and 'Disabled comparison' in refusal.stderr
(out / 'disabled.log').write_text(refusal.stdout + refusal.stderr)
p = json.loads((HERE / 'COMPARISON-POLICY.json').read_text())
rows = [r | {'status': 'PASS' if i % 2 else 'FAIL', 'expected': 'PASS', 'message': None if i % 2 else 'synthetic control failure', 'known_intermittent': []}
        for i, r in enumerate(p['exact_fresh_control_identities'])]
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
for index in range(113):
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
for key, value in [('expected', 'FAIL'), ('known_intermittent', ['FAIL'])]:
    bad = copy.deepcopy(candidate)
    next(r for r in bad if (r['test'], r['subtest']) in required)[key] = value
    try:
        policy.check(bad, p, 'candidate', baseline)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('target metadata corruption admitted')
for phase, field, value in [('candidate', 'message', 'changed control diagnostic'), ('restored', 'status', 'PASS')]:
    bad = copy.deepcopy(candidate if phase == 'candidate' else rows)
    bad[0][field] = value
    try:
        policy.check(bad, p, phase, baseline)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('exact outcome corruption admitted')

# Replay the actual try/finally body with scratch files and fake capture/build callbacks.
main = next(n for n in ast.parse((HERE / 'compare.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
function = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
    body=ast.parse('baseline = None\nmutation_started = False\nerror = None\n').body + [tail], decorator_list=[])
code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), '<actual-comparison-tail>', 'exec')
scenarios = []
for case in ['normal', 'original-failure', 'candidate-build-failure', 'candidate-capture-failure', 'restored-build-failure', 'unknown-native', 'unknown-test', 'live-group', 'restoration-receipt-failure']:
    with tempfile.TemporaryDirectory(prefix='bezier-tail-', dir='/private/tmp') as tmp:
        root = Path(tmp)
        names = ['native', 'new-test']
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
                (root / ('native' if case == 'unknown-native' else 'new-test')).write_bytes(b'unknown edit')
                raise RuntimeError('unknown edit observed')
        def build(label):
            calls.append('build-' + label)
            if case == label + '-build-failure':
                raise RuntimeError('build rejected')
        def verify(label):
            if label == 'FINAL.json':
                assert all((not (root / n).exists()) if b is None else (root / n).read_bytes() == b for n, b in originals.items())
            return {}
        def save_result(name, data):
            if case == 'restoration-receipt-failure' and name == 'RESTORATION-INPUT-BINARIES.json':
                raise OSError('injected receipt publication failure')
            results[name] = copy.deepcopy(data)
        env = dict(vars(controller), ROOT=root, NATIVE='native', pre=pre, candidates=candidates, originals=originals,
            owned=owned, captures=captures, errors=errors, transitions=transitions, quiet=quiet, capture=capture,
            build=build, verify=verify, build_attempted=True, binaries={}, binary_names=set(), state={},
            adapter=types.SimpleNamespace(cancelled=lambda: False, owned_group=None),
            epoch={'semantic_index': {}}, h=types.SimpleNamespace(index_state=lambda *a: {}, semantic_index=lambda x: x),
            env={}, save=save_result)
        exec(code, env)
        env['exercise']()
        result = results['RESULT.json']
        assert result['success'] == (case == 'normal')
        if case not in ['unknown-native', 'unknown-test', 'live-group', 'restoration-receipt-failure']:
            assert all((not (root / n).exists()) if b is None else (root / n).read_bytes() == b for n, b in originals.items())
        if case == 'restoration-receipt-failure':
            assert 'build-restored' in calls and 'restored' in captures
            assert any('restoration binary receipt:' in e for e in result['recovery_errors'])
            assert result['source_transitions'] == ['candidate', 'restored']
        if case == 'unknown-native':
            assert (root / 'native').read_bytes() == b'unknown edit' and not (root / 'new-test').exists()
        if case == 'unknown-test':
            assert (root / 'new-test').read_bytes() == b'unknown edit'
        if case == 'live-group':
            assert (root / 'native').read_bytes() == candidates['native'] and (root / 'new-test').exists()
        scenarios.append({'case': case, 'result': result, 'scratch_removed_after_context': True})
(out / 'TAIL-SCENARIOS.json').write_text(json.dumps(scenarios, indent=2) + '\n')
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

nested = [copy.deepcopy(n) for n in main.body if isinstance(n, ast.FunctionDef) and n.name in ('verify', 'build', 'capture')]
assert len(nested) == 3
for node in nested:
    node.body = [n for n in node.body if not isinstance(n, ast.Nonlocal)]
flow_code = compile(ast.fix_missing_locations(ast.Module(body=nested, type_ignores=[])), '<actual-verify-build-capture>', 'exec')
publication_results = []
for failed_receipt in ['restored-BUILD-PRE.json', 'restored-BUILD-POST.json', 'restored-PRE.json', 'restored-POST.json', 'guard-failure']:
    with tempfile.TemporaryDirectory(prefix='bezier-publication-', dir='/private/tmp') as tmp:
        scratch = Path(tmp)
        calls, errors = [], []
        index = {'head': 'head', 'entries': 'entries', 'cached_diff': 'cached'}
        def pins(names):
            return {n: ('unexpected' if failed_receipt == 'guard-failure' and n == 'source' else
                        'original' if n == 'source' else 'rebuilt') for n in names}
        def git(*args):
            return b'outside' if '--binary' in args else b''
        def save(name, value):
            if name == failed_receipt:
                raise OSError('injected successful-guard receipt failure')
        env = dict(vars(controller), ROOT=scratch, HERE=scratch, OBJ=scratch / 'obj', env={},
            roles={'source': 'original'}, binaries={'binary': 'rebuilt'}, binary_names={'binary'}, owned={},
            errors=errors, excluded=[], external_diff=controller.body_sha(b'outside'),
            pre={}, epoch={'semantic_index': index, 'nested_semantic_index': index, 'staged_working': {},
                          'committed_research_working_payloads': {}, 'installed_identities': {},
                          'modified_native_paths': [], 'untracked_native': []},
            h=types.SimpleNamespace(index_state=lambda *a: index.copy(), semantic_index=lambda x: x,
                                    git=git, fingerprint=lambda *a: 'rebuilt'),
            adapter=types.SimpleNamespace(pins=pins, cancelled=lambda: False, owned_group=None),
            quiet=lambda: None, save=save, read=lambda p: {}, ports_free=lambda c: None, state={}, process_control=types.SimpleNamespace(),
            captures={'original': {}}, policy=types.SimpleNamespace(values=lambda rows: {}, check=lambda *a: None),
            tests=types.SimpleNamespace(run=lambda *a: calls.append('capture-restored') or {'rows': []}),
            builder=types.SimpleNamespace(run=lambda *a: calls.append('build-restored')))
        exec(flow_code, env)
        try:
            env['build']('restored')
            env['capture']('restored')
        except RuntimeError:
            assert failed_receipt == 'guard-failure' and calls == [] and errors == []
        else:
            assert failed_receipt != 'guard-failure'
            assert calls == ['build-restored', 'capture-restored'] and len(errors) == 1
            assert errors[0].startswith('preservation receipt ' + failed_receipt + ':')
        publication_results.append({'case': failed_receipt, 'calls': calls, 'recovery_errors': errors})
(out / 'RESTORED-VERIFICATION-PUBLICATION.json').write_text(json.dumps(publication_results, indent=2) + '\n')

(out / 'CHECK.json').write_text(json.dumps({'status': 'CUBIC_BEZIER_COMPARISON_STATIC_PASS', 'policy_negative_cases': negative, 'binary_gate_negatives': 8,
    'actual_tail_scenarios': len(scenarios), 'actual_build_cleanup_scenarios': 3, 'actual_restored_verification_scenarios': len(publication_results), 'disabled_refusal': True, 'synthetic_not_browser': True}, indent=2) + '\n')
print('PASS: disabled refusal, policy corruptions, nine actual-tail scratch scenarios')
