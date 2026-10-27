import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = HERE.parent / 'css-svg-length-readiness-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RUNTIME / 'FILES.json') == '127eaaddad7d9e7060d6575aa3d9bce6b500e4db9bcbd38ada53678816ba1b07'
manifest = read(RUNTIME / 'FILES.json')
assert len(manifest) == 22
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
for name, digest in read(RUNTIME / 'REFERENCES.json').items():
    assert sha(ROOT / name) == digest, name
state, root = read(RUNTIME / 'STATE.json'), read(RUNTIME / 'ROOT-FINAL-CHECK.json')
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
assert before == final and len(before['snapshot']['sources']) == 50 and len(before['pins']) == 369
assert state['status'] == 'terminal' and state['complete'] and state['preserved']
assert state['native_changes'] is False and 'failure' not in state and 'preservation_failure' not in state
assert root['status'] == 'REPRODUCED_AND_PRESERVED' and root['exit'] == 0 and root['session'] == 23760
assert root['state_sha256'] == sha(RUNTIME / 'STATE.json') and root['final_sha256'] == sha(RUNTIME / 'FINAL.json')
c = read(RUNTIME / 'CONFIG.json')
epoch = ROOT / c['epoch']
assert sha(epoch / 'FILES.json') == c['epoch_manifest_sha256']
assert before['snapshot'] == read(epoch / 'FINAL.json')
pins = read(epoch / 'FINAL-PINS.json')
for name, item in read(ROOT / c['proposal'] / 'SOURCE-PINS.json').items():
    assert name not in pins or pins[name] == item['sha256']
    pins[name] = item['sha256']
assert before['pins'] == pins
cap = read(RUNTIME / 'capture/RESULT.json')
payload = read(RUNTIME / 'capture/payload.json')
assert cap['observations'] == [payload] and cap['before'] == cap['after'] == pins
assert cap['status'] == 'terminal' and cap['profile_removed'] and cap['cleanup_errors'] == []
assert cap['process_cleanup']['terminal'] and cap['process_cleanup']['noLiveGroup']
assert cap['process_cleanup']['errors'] == []
assert not (RUNTIME / 'capture/profile').exists()
spec = importlib.util.spec_from_file_location('validator', RUNTIME / 'validate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.validate(payload) == read(RUNTIME / 'SUMMARY.json')
assert payload['compatMode'] == 'CSS1Compat' and len(payload['rows']) == 6
rows = []
for raw, identity in zip(payload['rows'], [(b, o) for b in ('scalar', 'list') for o in ('value', 'to-px', 'to-percentage')]):
    assert (raw['binding'], raw['operation']) == identity
    assert raw['warm'] == raw['reset'] == {'host': [200, 100], 'svg': [200, 100], 'value': 100}
    assert raw['after']['host'] == raw['after']['svg'] == [400, 100]
    assert raw['controlGeometry'] == {'host': [400, 100], 'svg': [400, 100]}
    assert raw['first'] == raw['repeated']
    operation = raw['operation']
    current = 100 / (400 / 100) if operation == 'to-percentage' else 50 * (400 / 100)
    unit = 5 if operation == 'to-px' else 2
    specified = 50 if operation == 'value' else current
    expected = {'observed': current, 'unit': unit, 'specified': specified}
    assert raw['control'] == expected and raw['expected'] == current
    if operation == 'value':
        assert raw['first'] == expected and raw['after']['value'] == 200
    else:
        stale = 50 * (200 / 100) if operation == 'to-px' else 100 / (200 / 100)
        assert raw['first'] == {'observed': stale, 'unit': unit, 'specified': stale}
        assert raw['after']['specified'] == stale and raw['after']['unit'] == unit
        assert raw['after']['value'] == (stale if unit == 5 else stale * (400 / 100))
        assert stale != current
    rows.append({'binding': identity[0], 'operation': operation, 'expected': current,
                 'observed': raw['first']['observed'], 'post_layout_value': raw['after']['value'],
                 'matches_old_context_witness': operation != 'value'})
assert state['counts'] == root['counts'] == {'PASS': 2, 'FAIL': 4, 'UNCALIBRATED': 0}
assert state['calibrated'] == state['stable'] == root['calibrated'] == root['stable'] == 6
assert state['getter_controls_pass'] == root['getter_controls_pass'] == 2
result = {'runtime_manifest_sha256': sha(RUNTIME / 'FILES.json'), 'payload_sha256': sha(RUNTIME / 'capture/payload.json'),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'), 'rows': rows,
          'calibrated': 6, 'stable': 6, 'getter_controls_pass': 2, 'conversion_mismatches': 4,
          'source_guards': 50, 'pins': 369, 'historical_preservation_verified': True,
          'native_factor_values_traced': False, 'accepted_new_fixes': 0}
(HERE / 'RESULTS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
