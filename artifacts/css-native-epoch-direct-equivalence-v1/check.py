import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('equivalence', HERE / 'equivalence.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
bodies = {name: (ROOT / path).read_bytes() for name, (path, _) in helper.INPUTS.items()}
documents = helper.authenticate(bodies)
actual = helper.verify_saved(ROOT)
assert actual['whole_epoch_equal_after_normalization']
assert actual['whole_snapshot_equal_after_normalization']
assert not actual['live_checks_performed'] and not actual['diagnostic_execution_authorized']
rejected = []


def reject(name, callback, message):
    try:
        callback()
    except ValueError as error:
        assert message in str(error), (name, str(error))
        rejected.append(name)
    else:
        raise AssertionError('accepted: ' + name)


def mutation(name, path, value, message):
    changed = copy.deepcopy(documents)
    target = changed
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    reject(name, lambda: helper._compare(changed), message)


for name in helper.INPUTS:
    changed = dict(bodies)
    changed[name] += b'\n'
    reject('exact-byte-pin-' + name, lambda: helper.authenticate(changed), 'input hash: ' + name)

mutation('wrong-native-origin-epoch', ['native_receipt', 'epoch_sha256'], '0' * 64, 'receipt epoch')
mutation('wrong-original-receipt', ['original_capture', 'prior_receipt_sha256'], '0' * 64, 'original receipt')
mutation('rewritten-current-authority', ['current_capture', 'checkpoint', 'epoch_sha256'], helper.INPUTS['current_epoch'][1], 'unchanged native receipt')
mutation('wrong-current-receipt-pin', ['current_capture', 'checkpoint_receipt', 'sha256'], '0' * 64, 'current receipt pin')
mutation('wrong-original-terminal', ['original_terminal', 'capture_sha256'], '0' * 64, 'original capture terminal')
mutation('terminal-bool-as-exit', ['current_terminal', 'exit_code'], False, 'current capture terminal')
mutation('terminal-float-as-session', ['current_terminal', 'session_id'], 51957.0, 'current capture terminal')
mutation('wrong-native-head', ['current_epoch', 'semantic_index', 'head'], '0' * 40, 'current native HEAD')
mutation('wrong-original-raw-join', ['original_capture', 'audit', 'index', 'raw_index'], '0' * 64, 'original snapshot raw join')
mutation('wrong-current-raw-join', ['current_capture', 'snapshot', 'index', 'raw_index'], '0' * 64, 'current snapshot raw join')
mutation('malformed-permitted-raw-field', ['current_epoch', 'raw_index_observation', 'current'], 0, 'current raw digest')
mutation('other-epoch-field', ['current_epoch', 'raw_index_observation', 'prior_comparison_raw_drift_cause'], 'different', 'whole epoch equivalence')
mutation('epoch-integer-as-bool', ['current_epoch', 'counts', 'native_modified_paths'], False, 'whole epoch equivalence')
mutation('epoch-integer-as-float', ['current_epoch', 'counts', 'native_modified_paths'], 0.0, 'whole epoch equivalence')
mutation('source-inode-change', ['current_epoch', 'installed_identities', 'Cargo.lock', 1], 276330035, 'whole epoch equivalence')
mutation('nested-raw-not-exempt', ['current_capture', 'snapshot', 'nested_index', 'raw_index'], '0' * 64, 'whole snapshot equivalence')
mutation('new-snapshot-field', ['current_capture', 'snapshot', 'invented'], True, 'whole snapshot equivalence')
mutation('snapshot-boolean-as-int', ['current_capture', 'snapshot', 'working_sources_binaries_research_preserved'], 1, 'current snapshot claims')
mutation('other-control-change', ['current_capture', 'controls', 'OWNED.json'], '0' * 64, 'other controls unchanged')
reject('duplicate-json-key', lambda: helper.decode(b'{"x":1,"x":2}'), 'duplicate JSON key')
reject('nonfinite-json', lambda: helper.decode(b'{"x":NaN}'), 'nonfinite JSON')
reject('overflow-to-infinity', lambda: helper.decode(b'{"x":1e999}'), 'Out of range float')
for left, right in [(False, 0), (True, 1), (1, 1.0)]:
    reject('typed-equivalence-' + repr(left) + '-' + repr(right), lambda: helper.equal(left, right, 'typed mismatch'), 'typed mismatch')

output = {
    'scope': 'actual saved equivalence plus exact-pin and internal semantic-comparator controls; no live validation',
    'actual': actual,
    'rejected_controls': rejected,
    'rejected_count': len(rejected),
    'inputs': {str((ROOT / path).relative_to(ROOT)): pin for path, pin in helper.INPUTS.values()},
    'tested_code': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ('equivalence.py', 'check.py')},
}
print(json.dumps(output, indent=2, sort_keys=True))
