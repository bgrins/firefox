import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('pending_transition_check', HERE / 'transition.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
policy = t.read(HERE / 'POLICY.json')
head = t.source_roles(ROOT, policy['packages']['head']['path'])
live = t.source_roles(ROOT, policy['packages']['live']['path'])
pending = t.source_roles(ROOT, policy['packages']['pending_tests']['path'], 1, 'SOURCE-ROLES.json')
restoration = t.read(ROOT / policy['runtime'] / 'RESTORATION-PLAN.json')
original, before, planned = t.expected_sources(policy, 'pending-tests', restoration, head, live, pending)
epoch = t.read(ROOT / 'artifacts/css-local-signing-20261027-v15/checkpoint-EPOCH.json')
assert len(planned) == 50
assert t.verify_pending_validation(ROOT, policy, planned, epoch) == policy['packages']['pending_validation']['manifest_sha256']
records = []


def reject(name, action):
    try:
        action()
    except RuntimeError:
        records.append(name)
    else:
        raise AssertionError('Accepted: ' + name)


package_name = policy['packages']['pending_validation']['path']
sources = t.read(ROOT / package_name / 'SOURCE-PINS.json')
for name in sources:
    changed = dict(planned)
    changed[name] = 'bad'
    reject('planned-source:' + name, lambda: t.verify_pending_validation(ROOT, policy, changed, epoch))
with tempfile.TemporaryDirectory(prefix='pending-transition-controls-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    package = scratch / package_name
    package.mkdir(parents=True)
    for name in ['POLICY.json', 'SOURCE-PINS.json', 'ROSTER.json']:
        (package / name).write_bytes(t.body(ROOT / package_name / name))
    overlay = scratch / policy['packages']['pending_tests']['path']
    overlay.mkdir(parents=True)
    (overlay / 'ROSTER.json').write_bytes(t.body(ROOT / policy['packages']['pending_tests']['path'] / 'ROSTER.json'))
    assert t.verify_pending_validation(scratch, policy, planned, epoch) == policy['packages']['pending_validation']['manifest_sha256']
    for label, name, mutate in [
        ('wrong-head', 'POLICY.json', lambda d: d.update(frozen_head='0' * 40)),
        ('wrong-collector-guard', 'POLICY.json', lambda d: d.update(unchanged_native_sources={})),
        ('wrong-source-count', 'POLICY.json', lambda d: d.update(expected_source_pins=19)),
        ('wrong-call-inventory', 'POLICY.json', lambda d: d.update(expected_source_pending_calls=33)),
        ('standalone-acceptance', 'POLICY.json', lambda d: d.update(standalone_native_acceptance=True)),
        ('wrong-roster', 'ROSTER.json', lambda d: d['candidate_gtests'].__setitem__(0, 'Wrong.Test')),
        ('missing-source', 'SOURCE-PINS.json', lambda d: d.pop(next(iter(d)))),
        ('obsolete-collector', 'SOURCE-PINS.json', lambda d: d.update({'servo/components/style/properties_and_values/value.rs': 'df04db6365a7e57309c6901b7fde47a8378162c06778c8ec6373d797e542762f'})),
    ]:
        path = package / name
        original_bytes = t.body(path)
        changed = json.loads(original_bytes)
        mutate(changed)
        path.write_bytes(t.encoded(changed))
        reject(label, lambda: t.verify_pending_validation(scratch, policy, planned, epoch))
        path.write_bytes(original_bytes)
assert not scratch.exists()
print(json.dumps({'status': 'PENDING_VALIDATOR_PLAN_CONTROLS_PASS', 'negative_controls': records,
                  'planned_sources': 50, 'validator_sources': 20, 'gtests': 22, 'source_pending_calls': 34,
                  'scratch_removed': True, 'live_queries_or_transition_execution': False}, indent=2))
