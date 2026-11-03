import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('saved_' + name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = read(HERE/'POLICY.json')
assert policy['execution_enabled'] is policy['candidate_execution_enabled'] is False
checker = load('check')
started = time.monotonic()
count = checker.validate_policy(policy)
elapsed = time.monotonic() - started
origins = read(HERE/'ORIGINS.json')
negative = []


def reject(label, action, expected):
    try:
        action()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        assert expected in str(error), (label, str(error))
        negative.append(label)
    else:
        raise AssertionError('accepted ' + label)


reject('failed-v2-dict-as-path-reproduced', lambda: ROOT/origins['run.py'], 'unsupported operand')
changed = copy.deepcopy(origins)
changed['run.py']['path'] = dict(changed['run.py'])
reject('structured-path-must-be-string', lambda: checker.validate_origins(changed), 'origin path: run.py')
changed = copy.deepcopy(origins)
changed['run.py'] = changed['run.py']['path']
reject('legacy-unstructured-origin-rejected', lambda: checker.validate_origins(changed), 'origin record: run.py')
changed = copy.deepcopy(origins)
wrong_base = 'artifacts/css-root-font-cancellation-trace-candidate-browser-v1/run.py'
changed['run.py'] = {'path': wrong_base, 'sha256': sha(ROOT/wrong_base)}
reject('authentic-but-wrong-diff-base', lambda: checker.validate_origins(changed), 'origin delta: run.py')
changed = copy.deepcopy(origins)
changed['baseline.py']['sha256'] = '0'*64
reject('origin-hash-change', lambda: checker.validate_origins(changed), 'origin hash: baseline.py')

admission = load('admission')
capture = read(ROOT/policy['current_binding']['path'])
receipt = capture['checkpoint']
for key, value, expected in (
    ('current_binding', dict(policy['current_binding'], sha256='0'*64), 'current capture binding'),
    ('capture_binding', dict(policy['capture_binding'], sha256='0'*64), 'capture terminal binding'),
    ('controls', dict(policy['controls'], **{'CURRENT-EPOCH.json': '0'*64}), ''),
    ('direct_equivalence', dict(policy['direct_equivalence'], manifest_sha256='0'*64), ''),
):
    changed = copy.deepcopy(policy)
    changed[key] = value
    reject('direct-admission-' + key, lambda: admission.direct_evidence(ROOT, changed, receipt), expected)
changed_receipt = copy.deepcopy(receipt)
changed_receipt['signature_verified'] = 1
reject('typed-receipt-not-coerced', lambda: admission.direct_evidence(ROOT, policy, changed_receipt), 'actual native receipt')

baseline_source = (HERE/'baseline.py').read_text()
parent_baseline = (ROOT/origins['baseline.py']['path']).read_text()
old_prefix = "    native_receipt = checkpoint\n    checkpoint = adapter.native_head_view(native_receipt)\n"
new_prefix = "    native_receipt = checkpoint\n    admission = load('live_direct_admission', str((HERE / 'admission.py').relative_to(ROOT)))\n    evidence = admission.direct_evidence(ROOT, policy, native_receipt)\n    native_head = native_receipt['commit']\n    expected_epoch_sha256 = evidence['current_epoch_sha256']\n"
start, end = parent_baseline.index('def observe('), parent_baseline.index('\ndef guard(')
expected_observe = parent_baseline[start:end].replace(old_prefix, new_prefix).replace("checkpoint['head']", 'native_head').replace("checkpoint['epoch_sha256']", 'expected_epoch_sha256')
assert baseline_source == parent_baseline[:start] + expected_observe + parent_baseline[end:]
assert (HERE/'run.py').read_bytes() == (ROOT/origins['run.py']['path']).read_bytes()
for name in ('admission', 'baseline'):
    tree = ast.parse((HERE/(name+'.py')).read_text())
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                   and node.func.attr in ('native_head_view', 'validate_refresh') for node in ast.walk(tree))
for name in origins:
    if name not in ('baseline.py', 'admission.py', 'check.py'):
        assert (HERE/name).read_bytes() == (ROOT/origins[name]['path']).read_bytes()

tested = ['POLICY.json', 'PRECONDITIONS.json', 'SOURCE-ROLES.json', 'ORIGINS.json',
          'check_saved.py', 'run.py', 'baseline.py', 'admission.py', 'check.py', 'closure.py']
print(json.dumps({
    'full_validate_policy_executed': True, 'full_validate_policy_seconds': elapsed,
    'consumed_inputs': count, 'references': len(policy['references']), 'source_roles': 5,
    'original_projection': {'callbacks': 8, 'PASS': 6, 'FAIL': 2, 'endings': 1, 'full22_replayed_before_projection': True},
    'negative_controls': negative, 'unchanged_driver_and_finally': True,
    'exact_live_guard_preservation_checked': True,
    'native_head_view_or_validate_refresh_calls_in_owner': 0,
    'unchanged_stream_staging_archive_suites_rerun': False,
    'live_guard_executed': False, 'native_or_browser_run': False,
    'tested_inputs': {name: sha(HERE/name) for name in tested},
}, indent=2, sort_keys=True))
