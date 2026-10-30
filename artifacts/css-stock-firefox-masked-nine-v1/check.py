import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stock_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
policy = json.loads((HERE / 'POLICY.json').read_text())
runner.authenticate(policy)
assert policy['execution_enabled'] is False
pages = list(policy['roster'])


def sample(page, status=0):
    return {'run_id': 'check', 'page': page,
            'tests': [{'name': n, 'status': status, 'message': 'actual message', 'stack': None} for n in policy['roster'][page]],
            'status': {'status': 0, 'message': None, 'stack': None},
            'ua': 'Mozilla/5.0 Firefox/158.0',
            'supports': {'typed_duration': True, 'literal_duration': True, 'variables': True}}


negative = []
for key, value in [('run_id', 'wrong'), ('page', pages[1]), ('tests', []), ('ua', 'Firefox/158.01'), ('supports', {})]:
    row = sample(pages[0])
    row[key] = value
    try:
        runner.validate(row, policy, 'check', pages[0])
    except (AssertionError, KeyError):
        negative.append(key)
    else:
        raise AssertionError(key)
for key, value in [('status', True), ('status', 5), ('name', 'wrong'), ('message', {})]:
    row = sample(pages[0])
    row['tests'][0][key] = value
    try:
        runner.validate(row, policy, 'check', pages[0])
    except AssertionError:
        negative.append('test ' + key)
    else:
        raise AssertionError(key)
for status in range(5):
    runner.validate(sample(pages[0], status), policy, 'check', pages[0])
with tempfile.TemporaryDirectory(prefix='stock-runner-check-', dir='/private/tmp') as directory:
    receiver = runner.Receiver(policy, Path(directory))
    receiver.run_id = 'check'
    receiver.origin = 'http://127.0.0.1:1'
    for name, path, origin in [('nonce', '/report/wrong', receiver.origin),
                               ('origin', '/report/' + receiver.nonce, 'http://elsewhere')]:
        try:
            receiver.receive(path, origin, json.dumps(sample(pages[0])))
        except AssertionError:
            negative.append(name)
        else:
            raise AssertionError(name)
    for index, page in enumerate(pages):
        row = sample(page, 1 if index else 0)
        reply = receiver.receive('/report/' + receiver.nonce, receiver.origin, json.dumps(row))
        assert json.loads((Path(directory) / f'page-{index + 1}.json').read_text()) == row
        assert (reply['next'] is None) == (index == 3)
    result = runner.assessment(receiver.reports, policy)
    assert result['complete'] and result['pass'] == 6 and result['fail'] == 3
    assert not result['all_callbacks_pass'] and result['missing_pages'] == []
    ending_error = [sample(page) for page in pages]
    ending_error[0]['status']['status'] = 1
    separated = runner.assessment(ending_error, policy)
    assert separated['all_callbacks_pass'] and not separated['all_endings_ok'] and not separated['suite_pass']
    partial = runner.assessment(receiver.reports[:1], policy)
    assert not partial['complete'] and partial['missing_pages'] == pages[1:]
    try:
        receiver.receive('/report/' + receiver.nonce, receiver.origin, json.dumps(sample(pages[3])))
    except AssertionError:
        negative.append('duplicate')
    else:
        raise AssertionError('duplicate')
node = shutil.which('node')
assert node, 'Node is required only for the bridge static check'
subprocess.run([node, '--check', str(HERE / 'testharnessreport.js')], check=True)
subprocess.run([node, str(HERE / 'check_bridge.js'), str(HERE / 'testharnessreport.js')], check=True)
print(json.dumps({'fixture_pins': 'exact', 'status_positives': 5, 'exclusive_page_roundtrips': 4,
                  'ordinary_failures_preserved': True, 'partial_reports_explicit': True,
                  'negative_checks': negative, 'browser_launched': False, 'server_bound': False}, indent=2))
