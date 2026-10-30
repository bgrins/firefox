import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-partial-base-installed-browsers-v1'
FIXTURE = ROOT / 'artifacts/css-contextual-duration-partial-base-observation-v1'
OWNER_SHA = '44bb6db62a77b9f3aa54adf528edaff6aa6702143f5361ead4807e5efc5e97e0'
REFERENCES = {}


def read(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    body = path.read_bytes()
    name = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    REFERENCES[name] = dict(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
    return body


def load(path):
    return json.loads(read(path))


def package(path, expected):
    body = read(path / 'FILES.json')
    assert hashlib.sha256(body).hexdigest() == expected
    for name, pin in json.loads(body).items():
        data = read(path / name)
        assert hashlib.sha256(data).hexdigest() == (pin['sha256'] if isinstance(pin, dict) else pin)
        if isinstance(pin, dict):
            assert len(data) == pin['bytes']


package(OWNER, OWNER_SHA)
package(FIXTURE, '3c85673b74ac2a647592889ca98a2e5da58b07ede7dd13eb029e06effce5e146')
policy = load(OWNER / 'POLICY.json')
spec = importlib.util.spec_from_file_location('partial_reader', OWNER / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
read(HERE / 'recompute.js')
results = {}
for browser, seal, session, terminal in [
    ('firefox', 'c3a58b509fc43ed7195aed35c3c84c021db1de024b689cc96dfabc8c236dfd44', 79902, 'b84267'),
    ('chrome', 'c302c7a4b53babe5438442e51e9ed2b81fb1cda7d1c7d244e3313c28cf2dd4bc', 94472, '97cd2c'),
]:
    runtime = ROOT / policy['browsers'][browser]['output']
    package(runtime, seal)
    assert load(runtime / 'POLICY.json') == policy
    binding = load(runtime / 'BINDING.json')
    payload = load(runtime / 'REPORT.json')
    raw = list(runtime.glob('request-*.json'))
    assert len(raw) == 1 and load(raw[0]) == payload
    report = module.validate(payload, binding['run_id'], browser)
    served = {}
    for name, pin in policy['resources'].items():
        body = read(ROOT / pin['path'])
        assert hashlib.sha256(body).hexdigest() == pin['sha256']
        if name == '/observe.html':
            body += b'\n<script src="/report.js" defer></script>\n'
        served[name] = dict(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
    assert served == load(runtime / 'RESOURCES.json')
    computed = json.loads(subprocess.check_output(
        ['node', str(HERE / 'recompute.js'), str(FIXTURE / 'observe.js')],
        input=json.dumps(report).encode(), cwd=ROOT))
    assert [row['id'] for row in computed] == [row['id'] for row in report['observations']]
    assert [row['checks'] for row in computed] == [row['referenceChecks'] for row in report['observations']]
    result = load(runtime / 'RESULT.json')
    cleanup = load(runtime / 'CLEANUP.json')
    assert load(runtime / 'SERVER-ERRORS.json') == []
    assert all(result[key] for key in ['execution_complete', 'observation_complete', 'cleanup_complete', 'report_received'])
    assert result['error'] is None and result['native_acceptance'] is False and result['contextual_timing_verdict'] is None
    assert result['reference_checks_pass'] == all(check['passed'] for row in computed for check in row['checks'])
    assert cleanup['initial_group']['owned_group_absent'] and cleanup['remaining_profile_commands'] == [] and cleanup['temporary_removed']
    root = load(runtime / 'ROOT-TERMINAL.json')
    assert (root['session_id'], root['terminal_chunk'], root['exit']) == (session, terminal, 0)
    assert root['owner_manifest_sha256'] == OWNER_SHA
    assert root['result_sha256'] == hashlib.sha256(read(runtime / 'RESULT.json')).hexdigest()
    assert root['owned_processes_absent'] and root['temporary_absent'] and root['reference_checks_independently_recomputed']
    assert root['contextual_timing_verdict'] is None and root['native_acceptance'] is False
    environment = load(runtime / 'ENVIRONMENT.json')
    assert not environment['feature_environment_overrides'] and not environment['user_js_created']
    command = load(runtime / 'COMMAND.json')
    temporary = load(runtime / 'TEMPORARY.json')
    assert command[0] == policy['browsers'][browser]['binary'] and temporary['profile'] in ' '.join(command)
    assert command[-1] == binding['origin'] + '/observe.html?run=' + binding['run_id'] + '&nonce=' + binding['nonce']
    results[browser] = dict(userAgent=report['userAgent'], report=report, recomputed_reference_checks=computed,
                            result=result, cleanup=cleanup, root_terminal=root, raw_normalized_equal=True)

app_hashes = {}
for name, pin in policy['browsers']['firefox']['app_pins'].items():
    body = read(Path(pin['path']))
    assert hashlib.sha256(body).hexdigest() == pin['sha256'] and len(body) == pin['bytes']
    app_hashes[name] = pin['sha256']
pin = policy['browsers']['chrome']['inventory']
body = read(ROOT / pin['path'])
assert hashlib.sha256(body).hexdigest() == pin['sha256']
inventory = json.loads(body)
relative = str(Path(policy['browsers']['chrome']['binary']).relative_to(inventory['root']))
binary = [row for row in inventory['entries'] if row['path'] == relative]
assert len(binary) == 1 and binary[0]['sha256'] == policy['browsers']['chrome']['binary_sha256']
table = []
for browser, outcome in results.items():
    for row in outcome['report']['observations']:
        table.append(dict(browser=browser, id=row['id'], initial_opacity=row['initial']['opacity'],
            initial_css_duration=row['initial']['cssDuration'], initial_effect_duration=row['initial']['timings'][1]['duration'],
            first_and_passive_opacity=[sample['opacity'] for sample in row['samples']],
            later_css_duration=row['beforeMembership']['cssDuration'], later_effect_duration=row['beforeMembership']['timings'][1]['duration'],
            later_effect_progress=row['beforeMembership']['timings'][1]['progress'],
            details_equal_across_membership=row['beforeMembership'] == row['afterMembership'], membership=row['membership']))
print(json.dumps(dict(results=results, table=table, references=REFERENCES,
    installed_firefox_hashes_independently_read=app_hashes, current_chrome_inventory_reread=False,
    contextual_timing_verdict=None, native_acceptance=False), indent=2, sort_keys=True))
