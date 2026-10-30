import configparser
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'artifacts/css-stock-firefox-masked-nine-runtime-1'
OWNER = ROOT / 'artifacts/css-stock-firefox-masked-nine-v1'
references = {}


def read(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    body = path.read_bytes()
    key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    references[key] = {'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
    return body


def load(path):
    return json.loads(read(path))


def pin(path, expected):
    body = read(path)
    assert hashlib.sha256(body).hexdigest() == expected['sha256'], str(path)
    assert len(body) == expected['bytes'], str(path)
    return body


def package(path, expected):
    manifest = read(path / 'FILES.json')
    assert hashlib.sha256(manifest).hexdigest() == expected
    for name, claim in json.loads(manifest).items():
        pin(path / name, claim)


package(OWNER, '28c35122f4e7f8cd0ac60de72dd0e76a13057a0ad1d73838e24be9696dd8e5ce')
policy = load(RUNTIME / 'POLICY.json')
assert policy == load(OWNER / 'POLICY.json')
fixture = ROOT / policy['fixture_manifest']['path']
package(fixture.parent, policy['fixture_manifest']['sha256'])
assert load(fixture.parent / 'ROSTER.json') == policy['roster']
resources = {}
for name, claim in policy['resources'].items():
    body = pin(ROOT / claim['path'], claim)
    resources[name] = {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
body = pin(ROOT / policy['bridge']['path'], policy['bridge'])
resources['/resources/testharnessreport.js'] = {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
assert resources == load(RUNTIME / 'RESOURCES.json')
app = {name: pin(Path(claim['path']), claim) for name, claim in policy['installed_app'].items()}
ini = configparser.ConfigParser()
ini.read_string(app['Resources/application.ini'].decode())
assert ini['App']['Version'] == '158.0'
binding = load(RUNTIME / 'BINDING.json')
raw = {}
for path in sorted(RUNTIME.glob('request-*.json')):
    payload = load(path)
    assert payload['page'] not in raw
    raw[payload['page']] = {'path': str(path.relative_to(ROOT)), 'payload': payload}
assert set(raw) == set(policy['roster']) and len(raw) == 4
pages = []
joins = []
for index, (page, names) in enumerate(policy['roster'].items(), 1):
    saved = load(RUNTIME / f'page-{index}.json')
    assert saved == raw[page]['payload']
    assert set(saved) == {'page', 'run_id', 'status', 'supports', 'tests', 'ua'}
    assert saved['page'] == page and saved['run_id'] == binding['run_id']
    assert [t['name'] for t in saved['tests']] == names
    assert saved['ua'] == 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:158.0) Gecko/20100101 Firefox/158.0'
    assert saved['supports'] == dict(typed_duration=True, literal_duration=True, variables=True)
    assert saved['status'] == dict(status=0, message=None, stack=None)
    for test in saved['tests']:
        assert set(test) == {'name', 'status', 'message', 'stack'}
        assert test['status'] in [0, 1]
        if test['status'] == 0:
            assert test['message'] is None and test['stack'] is None
        else:
            prefix = binding['origin'] + page + '?run=' + binding['run_id'] + '&nonce=' + binding['nonce']
            assert test['stack'].startswith('@' + prefix + ':')
            assert 'opacity=0.75, duration=1000, progress=0.75' in test['message']
            assert 'expected 0.375 +/- 0.0001 but got 0.75' in test['message']
    pages.append(saved)
    joins.append({'raw': raw[page]['path'], 'normalized': str((RUNTIME / f'page-{index}.json').relative_to(ROOT)), 'exact_json_equal': True})
rows = [{'page': page['page'], **test} for page in pages for test in page['tests']]
assert len(rows) == 9 and sum(row['status'] == 0 for row in rows) == 6
assessment = load(RUNTIME / 'ASSESSMENT.json')
expected = dict(complete=True, pages=4, missing_pages=[], callbacks=9, pass_=6, fail=3,
                rows=rows, other_callback_statuses=[], endings=[page['status'] for page in pages],
                all_callbacks_pass=False, all_endings_ok=True, suite_pass=False,
                profile_preference_overrides=False, native_acceptance=False)
expected['pass'] = expected.pop('pass_')
assert assessment == expected
assert load(RUNTIME / 'SERVER-ERRORS.json') == []
result = load(RUNTIME / 'RESULT.json')
assert result == dict(execution_complete=False, error=None, callbacks_pass=6, callbacks_fail=3,
                     pages=4, all_callbacks_pass=False, all_endings_ok=True, suite_pass=False,
                     native_acceptance=False, ordinary_failures_preserved=True,
                     browser_returncode_after_owned_cleanup=-15)
cleanup = load(RUNTIME / 'CLEANUP.json')
assert not cleanup['temporary_removed'] and cleanup['remaining_profile_commands']
assert cleanup['group_operation_error'] == "PermissionError(1, 'Operation not permitted')"
recovery = load(ROOT / 'artifacts/css-stock-firefox-masked-nine-root-cleanup-v1.json')
for name, sha in recovery['original_runtime_hashes'].items():
    assert hashlib.sha256(read(RUNTIME / name)).hexdigest() == sha
assert recovery['original_runner_cleanup_succeeded'] is False
assert recovery['root_cleanup_succeeded'] and recovery['temporary_removed']
assert recovery['remaining_processes'] == [] and recovery['original_runtime_unchanged']
assert recovery['temporary'] == load(RUNTIME / 'TEMPORARY.json')
environment = load(RUNTIME / 'ENVIRONMENT.json')
assert environment['feature_environment_overrides'] is False and environment['user_js_created'] is False
assert policy['profile_preferences'] == {} and policy['feature_overrides'] is False
command = load(RUNTIME / 'COMMAND.json')
assert command[:6] == [policy['installed_app']['MacOS/firefox']['path'], '--headless', '--no-remote', '--new-instance', '--profile', recovery['temporary']['profile']]
assert command[6] == binding['origin'] + next(iter(policy['roster'])) + '?run=' + binding['run_id'] + '&nonce=' + binding['nonce']
projection = dict(observation_complete=True, original_execution_complete=False,
                  root_recovery_complete_as_recorded=True, original_session=21882,
                  original_launch_chunk='fd2635', original_terminal_chunk=None, original_tool_exit=None,
                  installed_metadata=dict(ini['App']), app_pins_verified=True,
                  raw_page_joins=joins, pages=pages, assessment=assessment, result=result,
                  receipt_cleanup=cleanup, root_recovery_receipt=recovery,
                  served_resources=resources, references=references)
print(json.dumps(projection, indent=2, sort_keys=True))
