import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile

import run
import launch

policy = json.loads((run.HERE / 'POLICY.json').read_text())
assert policy['execution_enabled'] is False
for name in ['run.py', 'launch.py', 'assess.py', 'records.py']:
    compile((run.HERE / name).read_text(), name, 'exec')
refs = json.loads((run.HERE / 'REFERENCES.json').read_text())
checked, deferred = [], []
for name, digest in refs.items():
    if name.startswith('artifacts/'):
        path = run.ROOT / name
        assert path.is_file() and not path.is_symlink() and run.sha(path) == digest
        checked.append(name)
    else:
        deferred.append(name)
assert len(policy['resources']) == 6 and len(policy['record_kinds']) == len(policy['expected_names']) == 1
if policy['admission'] is None:
    assert policy['binaries'] is None and policy['version'] is None
    try:
        run.authenticate(policy)
    except AssertionError as error:
        assert str(error) == 'Fresh portable admission is pending'
    else:
        raise AssertionError('unbound admission accepted')
else:
    run.authenticate(policy)
a = run.load('synthetic_chrome_assess', run.HERE / 'assess.py')
test_policy = copy.deepcopy(policy)
test_policy['version'] = 'synthetic-test-version'
events = [{'action': 'suite_start', 'run_info': {'product': 'chrome', 'browser_version': test_policy['version']}},
          {'action': 'test_start', 'test': policy['page']},
          {'action': 'test_status', 'test': policy['page'], 'subtest': policy['expected_names'][0], 'status': 'PASS'},
          {'action': 'test_end', 'test': policy['page'], 'status': 'OK'}, {'action': 'suite_end'}]
assert a.assess(events, test_policy, 0)['complete']
failed = copy.deepcopy(events)
failed[2].update(status='FAIL', expected='PASS')
assert a.assess(failed, test_policy, 1)['complete'] and not a.assess(failed, test_policy, 1)['all_callbacks_pass']
negatives = []
for index, key, value in [(0, 'run_info', {'product': 'firefox', 'browser_version': test_policy['version']}),
 (0, 'run_info', {'product': 'chrome', 'browser_version': 'wrong'}), (2, 'subtest', 'other'),
 (2, 'test', 'wrong'), (2, 'status', 'TIMEOUT'), (2, 'expected', 'FAIL'),
 (2, 'known_intermittent', ['FAIL']), (3, 'status', 'ERROR')]:
    bad = copy.deepcopy(events)
    bad[index][key] = value
    negatives.append(bad)
negatives.extend([events[:-1], events + [events[2]], [events[0], events[1], events[3], events[2], events[4]],
 events + [{'action': 'crash'}], events + [{'action': 'log', 'level': 'ERROR', 'message': 'bad'}]])
for bad in negatives:
    assert not a.assess(bad, test_policy, 0)['complete']
assert not a.assess(events, test_policy, 1)['complete']
assert not a.assess(failed, test_policy, 0)['complete']
assert launch.filter_args(['--enable-features=X', '--enable-blink-features=Y', '--enable-unsafe-extension-debugging', '--ignore-certificate-errors', '--headless=new']) == ['--headless=new']
try:
    launch.filter_args(['--no-sandbox'])
except AssertionError:
    pass
else:
    raise AssertionError('sandbox disabling accepted')
collector = run.load('masked_records', run.HERE / 'records.py')
with tempfile.TemporaryDirectory(prefix='masked-records-check-') as temporary:
    directory = Path(temporary) / 'records'
    directory.mkdir(mode=0o700)
    info = directory.stat()
    binding = {'directory': str(directory), 'identity': [info.st_dev, info.st_ino], 'run_id': 'masked_static_record_0001'}
    pass_assessment = a.assess(events, test_policy, 0)
    fail_assessment = a.assess(failed, test_policy, 1)
    assert collector.collect(run.ROOT, directory, binding, policy, fail_assessment)['missing']
    assert not collector.collect(run.ROOT, directory, binding, policy, fail_assessment)['errors']
    assert collector.collect(run.ROOT, directory, binding, policy, pass_assessment)['errors']
    snapshot = {'font': 32, 'opacity': None, 'cssDuration': '2s, 2s', 'timings': [
        {'duration': 2000, 'progress': None, 'time': 750, 'state': 'paused'} for _ in range(2)]}
    observations = {mode: {'kind': 'acyclic', 'mode': mode, 'initial': snapshot,
        'beforeMembership': snapshot, 'afterMembership': snapshot,
        'membership': [{'animation': False, 'effect': False} for _ in range(2)],
        'samples': [{'phase': phase, 'value': -7} for phase in ['first-read', 'passive-frame-1', 'passive-frame-2', 'passive-frame-3']]}
        for mode in ['contextual', 'literal']}
    record = {'run_id': binding['run_id'], 'kind': 'masked-base-acyclic', 'observations': observations}
    path = directory / 'masked-base-acyclic.json'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(record, stream)
    collection = collector.collect(run.ROOT, directory, binding, policy, fail_assessment)
    assert collection['complete'] and collection['records'][path.name]['callback_status'] == 'FAIL'
assert not directory.exists()
result = {'stream_positives': 2, 'stream_negatives': len(negatives) + 2,
    'filter_positive': 1, 'sandbox_negative': 1, 'artifact_references_checked': len(checked),
    'nonartifact_harness_pins_deferred_to_root': deferred if policy['admission'] is None else [],
    'harness_pins_checked_by_saved_admission': policy['admission'] is not None, 'partial_fail_record_retained': True,
    'missing_pass_record_rejected': True, 'wrong_numeric_fail_record_retained': True,
    'browser_executed': False, 'portable_admission_bound': policy['admission'] is not None}
print(json.dumps(result, indent=2))
