import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-root-font-cancellation-trace-candidate-browser-v1'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def function(source, name):
    return next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == name)


before = (PARENT / 'baseline.py').read_text()
after = (HERE / 'candidate/baseline.py').read_text()
run_before = (PARENT / 'run.py').read_text()
run_after = (HERE / 'candidate/run.py').read_text()
for name in ('prepare', 'observe', 'current_capture', 'require_role', 'require_app_inventory', 'metadata_guard', 'environment'):
    assert ast.get_source_segment(before, function(before, name)) == ast.get_source_segment(after, function(after, name))
assert ast.dump(ast.Module(body=function(before, 'guard').body[1:], type_ignores=[]), include_attributes=False) == ast.dump(ast.Module(body=function(after, 'guard').body[1:], type_ignores=[]), include_attributes=False)
assert run_after.replace('baseline.require_ready(policy, ownership, sys.argv[2])', 'baseline.require_ready(policy)').replace('baseline.guard(policy, ownership, roles, sys.argv[2])', 'baseline.guard(policy, ownership, roles)') == run_before
assert 'validate_policy' not in ast.get_source_segment(after, function(after, 'require_ready'))
assert 'validate_policy' in ast.get_source_segment(after, function(after, 'prepare'))
closure = load('unchanged_closure', PARENT / 'closure.py')
parent_policy = read(PARENT / 'POLICY.json')
ownership = load('actual_ownership', ROOT / parent_policy['ownership_helper'])
scratch = Path(tempfile.mkdtemp(prefix='css-static-admission-check-', dir='/private/tmp'))
records = []


def case(label, mutation=None, boundary=1, mode='--run'):
    root = scratch / label
    owner = root / 'owner'; owner.mkdir(parents=True)
    capsule = root / 'capsule'; capsule.mkdir()
    (capsule / 'input').write_text('immutable evidence')
    (capsule / 'FILES.json').write_text(json.dumps({'input': {'sha256': sha(capsule / 'input'), 'bytes': (capsule / 'input').stat().st_size}}))
    (root / 'external').write_text('external evidence')
    (root / 'receipt.json').write_text('{}')
    capture = {'checkpoint_receipt': {'path': 'receipt.json', 'sha256': sha(root / 'receipt.json')}}
    (root / 'capture.json').write_text(json.dumps(capture))
    capsule_binding = {'directory': 'capsule', 'manifest_sha256': sha(capsule / 'FILES.json')}
    policy = {'owner_directory': 'owner', 'execution_enabled': True, 'candidate_execution_enabled': True,
              'activation_pending': [], 'ownership_helper': parent_policy['ownership_helper'],
              'current_binding': {'path': 'capture.json', 'sha256': sha(root / 'capture.json')},
              'source_binding': capsule_binding, 'capture_owner': capsule_binding, 'capture_source_owner': capsule_binding,
              'suite_bindings': {}, 'wpt_lanes': {}, 'required_typecheck_inputs': {}, 'metadata_current_pins': {},
              'preserved_absent_metadata': ['absent'], 'preserved_absent_resources': [],
              'references': {'external': sha(root / 'external')}, 'wpt': {}}
    policy['intermediate_consumed_inputs'] = closure.external_inputs(root, policy, {})
    (owner / 'POLICY.json').write_text(json.dumps(policy))
    (owner / 'SOURCE-ROLES.json').write_text('{}')
    (owner / 'baseline.py').write_text(after)
    (owner / 'run.py').write_text(run_after)
    (owner / 'closure.py').write_bytes((PARENT / 'closure.py').read_bytes())
    (owner / 'check.py').write_text('semantic validator fixture marker')
    manifest = {path.name: {'sha256': sha(path), 'bytes': path.stat().st_size} for path in owner.iterdir()}
    (owner / 'FILES.json').write_text(json.dumps(manifest))
    manifest_sha = sha(owner / 'FILES.json')
    counts = {'semantic': 0, 'ready': 0, 'live_body_entered': 0}

    def semantic(value):
        counts['semantic'] += 1
        assert value == policy

    def module_loader(name, path):
        if name == 'published_ownership':
            return ownership
        if name == 'published_checks':
            return SimpleNamespace(validate_policy=semantic)
        assert name == 'ready_consumed_closure'
        return closure

    scope = dict(HERE=owner, ROOT=root, sha=sha, read=read, load=module_loader)
    exec(compile(ast.Module(body=[function(after, 'prepare'), function(after, 'require_ready')], type_ignores=[]), '<actual prepare and pin reauthentication>', 'exec'), scope)

    def ready(value, actual_ownership, digest):
        counts['ready'] += 1
        if mutation is not None and counts['ready'] == boundary:
            if mutation == 'owner-file':
                (owner / 'baseline.py').write_text('changed code')
            elif mutation == 'owner-manifest':
                (owner / 'FILES.json').write_text('{}')
            elif mutation == 'external-file':
                (root / 'external').write_text('changed evidence')
            elif mutation == 'capture':
                (root / 'capture.json').write_text('{}')
            elif mutation == 'capsule-manifest':
                (capsule / 'FILES.json').write_text('{}')
            elif mutation == 'absence':
                (root / 'absent').write_text('unexpected')
            elif mutation == 'dangling-absence-link':
                (root / 'absent').symlink_to(root / 'missing')
            elif mutation == 'policy-object':
                value['references']['external'] = '0' * 64
            elif mutation == 'closed-gate':
                value['candidate_execution_enabled'] = False
            else:
                raise AssertionError(mutation)
        scope['require_ready'](value, actual_ownership, digest)

    def guard(value, actual_ownership, roles, digest):
        local = dict(require_ready=ready, policy=value, ownership=actual_ownership, roles=roles, manifest=digest)
        exec(compile(ast.Module(body=function(after, 'guard').body[:1], type_ignores=[]), '<actual guard readiness call>', 'exec'), local)
        counts['live_body_entered'] += 1
        return (None,) * 6

    baseline = SimpleNamespace(prepare=scope['prepare'], require_ready=ready, guard=guard)
    main = function(run_after, 'main')
    stop = next(i for i, node in enumerate(main.body) if isinstance(node, ast.Assign) and 'baseline.guard(' in ast.unparse(node.value))
    prefix = copy.deepcopy(main)
    prefix.body = prefix.body[:stop + 1]
    run_scope = dict(sys=SimpleNamespace(argv=['fixture.py', mode, manifest_sha]), HERE=owner, ROOT=root,
                     load=lambda name, path: baseline)
    exec(compile(ast.Module(body=[prefix], type_ignores=[]), '<actual driver admission prefix>', 'exec'), run_scope)
    try:
        run_scope['main']()
    except (AssertionError, KeyError, RuntimeError):
        assert mutation is not None
        assert counts['semantic'] == 1 and counts['live_body_entered'] == 0
        records.append({'case': label, 'rejected': True, 'boundary': boundary, **counts})
    else:
        assert mutation is None
        assert counts == ({'semantic': 1, 'ready': 2, 'live_body_entered': 1} if mode == '--run' else {'semantic': 1, 'ready': 0, 'live_body_entered': 0})
        records.append({'case': label, 'rejected': False, **counts})


try:
    case('run-positive')
    case('check-positive', mode='--check')
    for mutation in ['owner-file', 'owner-manifest', 'external-file', 'capture', 'capsule-manifest', 'absence', 'dangling-absence-link', 'policy-object', 'closed-gate']:
        case(mutation, mutation)
    case('changed-between-readiness-boundaries', 'external-file', boundary=2)
finally:
    shutil.rmtree(scratch)

print(json.dumps({'cases': records, 'unchanged_live_guard_body_and_observe': True,
                  'driver_only_two_call_signature_changes': True, 'semantic_validator_is_counting_double': True,
                  'native_live_body_not_executed': True, 'real_manifest_ownership_and_closure_used': True,
                  'scratch_removed': not scratch.exists(), 'no_native_or_browser_operations': True}, indent=2))
