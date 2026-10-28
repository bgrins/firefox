import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('pending_bindings', HERE / 'bindings.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
policy = json.loads((HERE / 'POLICY.json').read_text())
sources = json.loads((HERE / 'SOURCE-PINS.json').read_text())
old = json.loads((ROOT / 'artifacts/css-registered-number-pending-validation-v1/SOURCE-PINS.json').read_text())
changed = {name for name in sources if old[name] != sources[name]}
assert changed == {'servo/components/style/custom_properties.rs', 'servo/components/style/properties/cascade.rs',
                   'servo/components/style/properties_and_values/value.rs'}
roles = json.loads((ROOT / 'artifacts/css-registered-admission-preparation-proposal-v3/COMBINED-SOURCE-ROLES.json').read_text())
for name, pin in roles['candidate'].items():
    assert sources[name] == pin['sha256'] == hashlib.sha256((ROOT / pin['capture']).read_bytes()).hexdigest()
assert sources['servo/components/style/properties_and_values/value.rs'] == policy['unchanged_native_sources']['servo/components/style/properties_and_values/value.rs']
for name, pin in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
roster = json.loads((HERE / 'ROSTER.json').read_text())
assert len(roster['candidate_gtests']) == policy['expected_gtests'] == 22
assert policy['expected_source_pending_calls'] == 34
bytes_map = sources | policy['unchanged_native_sources']
epoch = {'semantic_index': {'head': policy['frozen_head']},
         'registered_number_transition': {'role': 'candidate', 'variant': 'prototype-overlay', 'compiled': True, 'accepted': False},
         'pins': dict(bytes_map), 'staged_working': {}, 'committed_research_working_payloads': {}}
b.require_transition(epoch, policy)
b.verify_sources(epoch, policy, sources, bytes_map.get)
rejected = []


def reject(label, action):
    try:
        action()
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError('Accepted: ' + label)


for field, value in [('role', 'original'), ('variant', 'committed-head'), ('compiled', False), ('accepted', True)]:
    changed_epoch = copy.deepcopy(epoch)
    changed_epoch['registered_number_transition'][field] = value
    reject(field, lambda: b.require_transition(changed_epoch, policy))
changed_epoch = copy.deepcopy(epoch)
changed_epoch['semantic_index']['head'] = '0' * 40
reject('wrong-frozen-head', lambda: b.require_transition(changed_epoch, policy))
for name in sources:
    wrong = dict(bytes_map)
    wrong[name] = 'bad'
    reject('source-byte:' + name, lambda: b.verify_sources(epoch, policy, sources, wrong.get))
    changed_epoch = copy.deepcopy(epoch)
    changed_epoch['pins'].pop(name)
    reject('source-epoch-missing:' + name, lambda: b.verify_sources(changed_epoch, policy, sources, bytes_map.get))
for name in policy['unchanged_native_sources']:
    wrong = dict(bytes_map)
    wrong[name] = 'bad'
    reject('collector-byte:' + name, lambda: b.verify_sources(epoch, policy, sources, wrong.get))
    changed_epoch = copy.deepcopy(epoch)
    changed_epoch['committed_research_working_payloads'][name] = 'bad'
    reject('collector-overlapping-pin:' + name, lambda: b.verify_sources(changed_epoch, policy, sources, bytes_map.get))
with tempfile.TemporaryDirectory(prefix='pending-binding-check-', dir='/private/tmp') as temporary:
    root = Path(temporary)
    source = root / 'source'
    source.write_bytes(b'same')
    original_identity = b.identities(root, ['source'])
    assert b.identities(root, ['source']) == original_identity
    (root / 'replacement').write_bytes(b'same')
    (root / 'replacement').replace(source)
    def same_identity():
        assert b.identities(root, ['source']) == original_identity
    reject('same-byte-inode-replacement', same_identity)
    (root / 'link').symlink_to(source)
    reject('symlink-source', lambda: b.identities(root, ['link']))
assert not root.exists()
print(json.dumps({'status': 'SOURCE_BINDING_CONTROLS_PASS', 'negative_controls': rejected,
                  'source_pins': len(sources), 'changed_pins': sorted(changed), 'unchanged_collectors': 6,
                  'gtests': 22, 'source_pending_calls': 34, 'scratch_removed': True,
                  'live_source_epoch_git_binary_queries': False, 'native_execution': False}, indent=2))
