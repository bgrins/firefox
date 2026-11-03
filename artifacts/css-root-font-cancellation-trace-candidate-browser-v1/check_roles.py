import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load('trace_preparation_check', HERE / 'check.py')
policy = checker.read(HERE / 'POLICY.json')
roles = checker.read(HERE / 'SOURCE-ROLES.json')
count = checker.validate_policy(policy)
source = ROOT / policy['source_binding']['directory']
source_roles = checker.read(source / 'SOURCE-ROLES.json')
tree = ast.parse((HERE / 'check.py').read_text())
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'validate_policy')
start = next(i for i, node in enumerate(function.body) if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'expected_roles')
end = next(i for i in range(start, len(function.body)) if isinstance(function.body[i], ast.For))
role_code = compile(ast.Module(body=function.body[start:end], type_ignores=[]), '<actual four-role admission>', 'exec')


def role_guard(value, current_roles):
    exec(role_code, dict(policy=value, roles=current_roles, source=source, source_roles=source_roles, ROOT=ROOT))


role_guard(policy, roles)
negative_roles = []
for label in ['missing-canonical-role', 'canonical-misclassified-additional', 'wrong-canonical-context', 'wrong-candidate-source']:
    bad, changed = copy.deepcopy(policy), copy.deepcopy(roles)
    name = 'servo/components/style/matching.rs'
    if label == 'missing-canonical-role':
        changed.pop(name)
    elif label == 'canonical-misclassified-additional':
        bad['additional_source_paths'].append(name)
    elif label == 'wrong-canonical-context':
        bad['source_context_pins'][name] = '0' * 64
    else:
        changed[name]['candidate_sha256'] = '0' * 64
    checker.rejected(lambda: role_guard(bad, changed))
    negative_roles.append(label)

driver = ast.parse((HERE / 'run.py').read_text())
main = next(node for node in driver.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
loop = next(node for node in main.body if isinstance(node, ast.For) and ast.unparse(node.iter) == 'roles.items()')
start = next(i for i, node in enumerate(loop.body) if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'admitted')
claim_code = compile(ast.Module(body=loop.body[start:start + 3], type_ignores=[]), '<actual mixed-source ownership claim>', 'exec')
ownership = load('actual_claim_ownership', ROOT / policy['ownership_helper'])
checked_claims = []
with tempfile.TemporaryDirectory(prefix='css-trace-four-roles-', dir='/private/tmp') as scratch:
    root = Path(scratch)
    for name in roles:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'owned fixture source')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        claim = ownership.claim(root, name, digest)
        capture = {'payload_claims': {}, 'additional_sources': {}}
        group = 'additional_sources' if name in policy['additional_source_paths'] else 'payload_claims'
        capture[group][name] = claim
        scope = dict(ROOT=root, name=name, record={'base_sha256': digest}, claims={}, ownership=ownership,
                     baseline=SimpleNamespace(current_capture=lambda _: capture), policy={})
        exec(claim_code, scope)
        assert scope['claims'][name] == claim
        path.rename(path.with_suffix('.retained'))
        path.write_bytes(b'owned fixture source')
        try:
            exec(claim_code, scope)
        except Exception as error:
            assert 'owned identity: ' + name in str(error)
        else:
            raise AssertionError('same-byte replacement admitted')
        checked_claims.append({'path': name, 'claim_group': group, 'same_byte_inode_replacement_rejected': True})
assert not root.exists()
historical = checker.read(ROOT / 'artifacts/css-root-font-cancellation-archive-current-v1.json')
for name, row in roles.items():
    group = 'additional_sources' if name in policy['additional_source_paths'] else 'payload_claims'
    assert historical[group][name]['owned_sha256'] == row['base_sha256']
assert policy['current_binding'] is policy['capture_owner'] is policy['capture_binding'] is None
assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
print(json.dumps({'pending_saved_admission': True, 'inputs': count, 'role_guards_rejected': negative_roles,
                  'actual_driver_claims': checked_claims, 'historical_capture_schema_only': True,
                  'fresh_admission_pending': True, 'conditional_on_residual_candidate34': True,
                  'scratch_removed': True, 'unchanged_suites_not_rerun': True, 'live_operations': False}, sort_keys=True))
