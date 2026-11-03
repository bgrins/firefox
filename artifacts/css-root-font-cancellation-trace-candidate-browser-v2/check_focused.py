import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = read(HERE / 'POLICY.json')
roles = read(HERE / 'SOURCE-ROLES.json')
checker = load('focused_production_check', HERE / 'check.py')
for name, origin in read(HERE / 'ORIGINS.json').items():
    assert sha(ROOT / origin['path']) == origin['sha256']
    assert (HERE / name).read_bytes() == (ROOT / origin['path']).read_bytes()
assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
capture = read(ROOT / policy['current_binding']['path'])
terminal = read(ROOT / policy['capture_binding']['path'])
source = ROOT / policy['source_binding']['directory']
source_roles = read(source / 'SOURCE-ROLES.json')
tree = ast.parse((HERE / 'check.py').read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_policy')
prefix_end = next(i for i, n in enumerate(function.body) if isinstance(n, ast.Assert) and 'compile_prerequisite' in ast.unparse(n))
prefix = copy.deepcopy(function.body[:prefix_end])
removed = 0
for node in prefix:
    if isinstance(node, ast.If):
        kept = []
        for item in node.orelse:
            if isinstance(item, ast.Assign) and '.validate_current(' in ast.unparse(item):
                removed += 1
            else:
                kept.append(item)
        node.orelse = kept
assert removed == 1
prefix_code = compile(ast.Module(body=prefix, type_ignores=[]), '<actual binding guards, semantic call excluded>', 'exec')
role_start = next(i for i, n in enumerate(function.body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'expected_roles')
role_end = next(i for i in range(role_start, len(function.body)) if isinstance(function.body[i], ast.For))
role_code = compile(ast.Module(body=function.body[role_start:role_end], type_ignores=[]), '<actual five-role guards>', 'exec')


def binding_guards(p, t):
    def saved_read(path):
        return t if path == ROOT / p['capture_binding']['path'] else read(path)
    exec(prefix_code, dict(policy=p, ROOT=ROOT, HERE=HERE, read=saved_read, sha=sha))


def role_guards(p, r):
    exec(role_code, dict(policy=p, roles=r, source=source, source_roles=source_roles, ROOT=ROOT))


closure = load('focused_actual_closure', HERE / 'closure.py')


def closure_guards(p):
    actual = closure.external_inputs(ROOT, p, roles)
    assert actual == p['intermediate_consumed_inputs']
    for name, pin in actual.items():
        path = ROOT / name
        if pin is None:
            assert not path.exists() and not path.is_symlink()
        else:
            assert sha(path) == pin, name
    return len(actual)


binding_guards(policy, terminal)
role_guards(policy, roles)
count = closure_guards(policy)
for row in roles.values():
    for kind in ('base', 'candidate'):
        assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
claims = capture['payload_claims'] | capture['additional_sources']
for name, row in roles.items():
    assert claims[name]['owned_sha256'] == row['base_sha256']
assert policy['accepted_current_payloads'] == {n: {'sha256': v['owned_sha256'], 'identity': v['identity']} for n, v in capture['payload_claims'].items()}
assert policy['controls'] == capture['controls']
assert capture['checkpoint'] == read(ROOT / capture['checkpoint_receipt']['path'])
assert capture['authority_kind'] == 'signed-native-publication'
assert capture['refresh_binding'] == policy['refresh_lineage']
assert capture['snapshot'] == read(ROOT / policy['refresh_lineage']['directory'] / 'POST.json')
old = read(ROOT / 'artifacts/css-resumable-font-selection-integrated-pair-v1/POLICY.json')
assert policy['source_context_pins'] == dict(old['source_context_pins'], **{'layout/style/GeckoBindings.cpp': roles['layout/style/GeckoBindings.cpp']['base_sha256']})
prior = read(ROOT / 'artifacts/css-root-font-cancellation-trace-candidate-browser-v1/POLICY.json')
for key in ('wpt', 'wpt_lanes', 'lane_order', 'diagnostic_lane_order', 'archived_original', 'archive'):
    assert policy[key] == prior[key]
assert (HERE / 'ORIGINAL8.json').read_bytes() == (ROOT / 'artifacts/css-root-font-cancellation-trace-candidate-browser-v1/ORIGINAL8.json').read_bytes()
negative = []


def rejects(label, function):
    try:
        function()
    except (AssertionError, KeyError):
        negative.append(label)
    else:
        raise AssertionError('accepted ' + label)


for key in ('launch_chunk', 'session_id', 'terminal_chunk', 'exit_code', 'capture_sha256', 'capture_owner_manifest', 'full_current_state_verified'):
    changed = copy.deepcopy(terminal)
    changed[key] = None
    rejects('terminal ' + key, lambda: binding_guards(policy, changed))
for name in terminal['canonical_source_claims']:
    changed = copy.deepcopy(terminal)
    changed['canonical_source_claims'][name]['identity'][1] += 1
    rejects('canonical receipt inode ' + name, lambda: binding_guards(policy, changed))
for name in roles:
    changed = copy.deepcopy(roles)
    changed[name]['candidate_sha256'] = '0' * 64
    rejects('candidate role ' + name, lambda: role_guards(policy, changed))
changed = copy.deepcopy(policy)
changed['additional_source_paths'].append('layout/style/GeckoBindings.cpp')
rejects('canonical classified as additional', lambda: role_guards(changed, roles))
for label in ('omitted consumed input', 'changed consumed input'):
    changed = copy.deepcopy(policy)
    key = policy['current_binding']['path']
    if label.startswith('omitted'):
        del changed['intermediate_consumed_inputs'][key]
    else:
        changed['intermediate_consumed_inputs'][key] = '0' * 64
    rejects(label, lambda: closure_guards(changed))

driver = ast.parse((HERE / 'run.py').read_text())
main = next(n for n in driver.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
loop = next(n for n in main.body if isinstance(n, ast.For) and ast.unparse(n.iter) == 'roles.items()')
start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'admitted')
claim_code = compile(ast.Module(body=loop.body[start:start + 3], type_ignores=[]), '<actual captured ownership claim>', 'exec')
ownership = load('actual_ownership', ROOT / policy['ownership_helper'])
with tempfile.TemporaryDirectory(prefix='css-trace-five-role-check-', dir='/private/tmp') as scratch:
    root = Path(scratch)
    for name in roles:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'owned source fixture')
        digest = sha(path)
        claim = ownership.claim(root, name, digest)
        saved = {'payload_claims': {}, 'additional_sources': {}}
        group = 'additional_sources' if name in policy['additional_source_paths'] else 'payload_claims'
        saved[group][name] = claim
        scope = dict(ROOT=root, name=name, record={'base_sha256': digest}, claims={}, ownership=ownership,
                     baseline=SimpleNamespace(current_capture=lambda _: saved), policy={})
        exec(claim_code, scope)
        path.rename(path.with_suffix('.retained'))
        path.write_bytes(b'owned source fixture')
        try:
            exec(claim_code, scope)
        except RuntimeError as error:
            assert 'owned identity: ' + name in str(error)
            negative.append('same-byte replaced inode ' + name)
        else:
            raise AssertionError(name)
assert not root.exists()
result = {'success': True, 'consumed_inputs': count, 'references': len(policy['references']),
          'source_roles': 5, 'canonical_roles': 3, 'additional_roles': 2,
          'inherited_production_origins': len(read(HERE / 'ORIGINS.json')),
          'negative_controls': negative, 'scratch_removed': True,
          'full_validate_policy_executed': False, 'live_guard_executed': False,
          'unchanged_stream_staging_archive_suites_rerun': False,
          'scope': 'Actual extracted cheap capture/role guards and production closure/ownership; root --run performs complete semantic validation and all live guards.',
          'tested_inputs': {n: sha(HERE / n) for n in ('POLICY.json', 'PRECONDITIONS.json', 'SOURCE-ROLES.json', 'ORIGINS.json', 'run.py', 'baseline.py', 'check.py', 'check_focused.py', 'closure.py', 'admission.py')}}
with (HERE / 'CHECK-FOCUSED.json').open('x') as stream:
    json.dump(result, stream, sort_keys=True, indent=2)
    stream.write('\n')
print(json.dumps(result, sort_keys=True))
