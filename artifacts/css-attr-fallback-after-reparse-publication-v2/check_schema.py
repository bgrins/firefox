import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-attr-fallback-after-reparse-publication-v1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


negatives = []


def reject(name, action):
    try:
        action()
    except (AssertionError, KeyError):
        negatives.append(name)
    else:
        raise AssertionError(name)


policy = read(HERE / 'POLICY.json')
assert policy['enabled_modes'] == []
assert all(policy[key] is None for key in ('bindings', 'pair_binding', 'stage', 'runtime_output'))
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path
for name in ('run.py', 'publish.py', 'transform.py', 'delivery.py', 'STAGES.json', 'PAIR-BINDING.json', 'native.patch'):
    assert (HERE / name).read_bytes() == (PARENT / name).read_bytes(), name
old, new = (PARENT / 'evidence.py').read_text(), (HERE / 'evidence.py').read_text()
expected = old.replace('css-attr-fallback-after-reparse-publication-v1/PAIR-BINDING.json',
                       'css-attr-fallback-after-reparse-publication-v2/PAIR-BINDING.json')
expected = expected.replace("capture['snapshot']['index']['working_diff'] == ''",
                            "capture['snapshot']['index']['working_diff'] == hashlib.sha256(b'').hexdigest()")
assert new == expected
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
evidence = load('corrected_evidence', HERE / 'evidence.py')
prior = load('prior_evidence', PARENT / 'evidence.py')
stage, = read(HERE / 'STAGES.json')['stages']
source = evidence.ROLE
typed_capsule = ROOT / 'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1'
binding = read(HERE / 'PAIR-BINDING.json')
assert all(binding[key] is None for key in ('typed_native_receipt', 'current_capture', 'current_epoch_sha256'))
tree = ast.parse((HERE / 'check.py').read_text())
start = next(i for i, node in enumerate(tree.body)
             if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'source_info')
end = next(i for i in range(start, len(tree.body)) if isinstance(tree.body[i], ast.With))
exec(compile(ast.Module(body=tree.body[start:end], type_ignores=[]), '<exact future-binding fixture>', 'exec'))
assert len(negatives) == 17
actual_path = ROOT / 'artifacts/css-keyframe-font-unit-native-current-v2.json'
actual = read(actual_path)
empty = hashlib.sha256(b'').hexdigest()
assert actual['snapshot']['index']['cached_diff'] == actual['snapshot']['index']['working_diff'] == empty
assert capture['snapshot']['index'] == {key: actual['snapshot']['index'][key]
                                      for key in ('cached_diff', 'working_diff')}
actual_shape = copy.deepcopy(capture)
actual_shape['snapshot'] = actual['snapshot']
evidence.require_future(future, receipt, actual_shape, source_info)
reject('prior predicate rejects real clean digest schema',
       lambda: prior.require_future(future, receipt, capture, source_info))
raw_empty = copy.deepcopy(capture)
raw_empty['snapshot']['index'].update(cached_diff='', working_diff='')
prior.require_future(future, receipt, raw_empty, source_info)
reject('former raw-empty positive now rejected',
       lambda: evidence.require_future(future, receipt, raw_empty, source_info))
assert "'explicit_taint_reparse_publication'" in (HERE / 'check.py').read_text()
assert "['explicit_taint_reparse_publication']" in (ROOT / 'artifacts/css-explicit-taint-typed-reparse-publication-v1/transform.py').read_text()
sources = {source}
test, = stage['create_tests']
start = next(i for i, node in enumerate(tree.body)
             if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 't')
end = next(i for i in range(start, len(tree.body))
           if isinstance(tree.body[i], ast.Assign) and ast.unparse(tree.body[i].targets[0]) == 'owner')
exec(compile(ast.Module(body=tree.body[start:end], type_ignores=[]), '<exact pure transform fixture>', 'exec'))
assert len(negatives) == 21
print(json.dumps({'positive_shapes': 2, 'pure_install_commit_checks': 2, 'rejecting_controls': negatives,
                  'former_false_positive_demonstrated': True,
                  'actual_capture': {'path': str(actual_path.relative_to(ROOT)), 'sha256': sha(actual_path)},
                  'clean_diff_digest': empty, 'references': len(policy['references']),
                  'full_historical_replay_repeated': False,
                  'seven_lifecycle_payloads_byte_identical': True,
                  'future_authority_pending': True, 'native_git_browser_actions': False}, sort_keys=True))
