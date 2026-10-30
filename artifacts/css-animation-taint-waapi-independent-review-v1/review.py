import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT / 'artifacts/css-animation-taint-waapi-observation-v1'
OWNER = ROOT / 'artifacts/css-animation-taint-waapi-installed-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def recalibrate(rows):
    program = r'''
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const boundary = source.lastIndexOf('(async () => {');
if (boundary < 0) throw Error('Missing collection boundary');
const context = {window: {}, navigator: {userAgent: 'saved replay'}};
vm.createContext(context);
vm.runInContext(source.slice(0, boundary), context);
let input = '';
process.stdin.on('data', data => input += data);
process.stdin.on('end', () => {
  const revive = (_key, value) => value && typeof value === 'object' &&
    Object.keys(value).length === 1 && 'nonfinite' in value ? Number(value.nonfinite) : value;
  const rows = JSON.parse(input, revive);
  process.stdout.write(JSON.stringify(rows.map(row => context.calibration(row))));
});
'''
    result = subprocess.run(['node', '-e', program, str(FIXTURE / 'observe.js')],
                            input=json.dumps(rows), text=True, capture_output=True,
                            check=True, timeout=15)
    return json.loads(result.stdout)


def review(browser):
    refs = read(HERE / 'REFERENCES.json')
    for name, expected in refs.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    for name, pin in read(FIXTURE / 'FILES.json').items():
        assert sha((FIXTURE / name).read_bytes()) == (pin['sha256'] if isinstance(pin, dict) else pin), name
    runtime = ROOT / f'artifacts/css-animation-taint-waapi-{browser}-runtime-1'
    inputs = {}
    def record(name):
        path = runtime / name
        assert path.is_file() and not path.is_symlink()
        body = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = {'sha256': sha(body), 'bytes': len(body)}
        return json.loads(body)
    policy = record('POLICY.json')
    assert policy == read(HERE / 'OWNER-POLICY.json') and policy['execution_enabled'] is True
    assert policy['profile_preferences'] == {} and policy['feature_overrides'] is False
    resources = {}
    for name, pin in policy['resources'].items():
        body = (ROOT / pin['path']).read_bytes()
        assert sha(body) == pin['sha256']
        if name == '/observe.html':
            body += b'\n<script src="/report.js" defer></script>\n'
        resources[name] = {'sha256': sha(body), 'bytes': len(body)}
    assert record('RESOURCES.json') == resources
    result = record('RESULT.json')
    cleanup = record('CLEANUP.json')
    errors = record('SERVER-ERRORS.json')
    terminal = record('ROOT-TERMINAL.json')
    expected = {'firefox': (82087, '667f1a', 0), 'chrome': (58909, '74eea5', 0)}[browser]
    assert (terminal['session'], terminal['terminal_chunk'], terminal['exit_code']) == expected
    assert terminal['owned_group_absent'] and terminal['profile_commands_absent'] and terminal['temporary_absent']
    assert result['animation_taint_policy_verdict'] is None and result['native_acceptance'] is False
    binding = record('BINDING.json')
    temporary = record('TEMPORARY.json')
    command = record('COMMAND.json')
    assert command[0] == policy['browsers'][browser]['binary']
    from urllib.parse import urlencode
    assert command[-1] == binding['origin'] + '/observe.html?' + urlencode({'run': binding['run_id'], 'nonce': binding['nonce']})
    assert temporary['profile'] in command or '--user-data-dir=' + temporary['profile'] in command
    environment = record('ENVIRONMENT.json')
    assert environment['feature_environment_overrides'] is False and environment['user_js_created'] is False
    payload = record('REPORT.json')
    requests = list(runtime.glob('request-*.json'))
    assert len(requests) == 1 and record(requests[0].name) == payload
    spec = importlib.util.spec_from_file_location('saved_waapi_schema', OWNER / 'run.py')
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    report = owner.validate(payload, binding['run_id'], browser)
    recalculated = recalibrate(report['observations'])
    assert recalculated == [row['referenceChecks'] for row in report['observations']]
    reference_pass = all(check['passed'] for checks in recalculated for check in checks)
    assert result['reference_checks_pass'] == reference_pass
    assert result['observation_complete'] == (report['status'] == 'complete')
    assert result['cleanup_complete'] == cleanup.get('temporary_removed', False)
    assert result['execution_complete'] == (result['error'] is None and not errors and cleanup.get('temporary_removed', False))
    for name, pin in inputs.items():
        assert sha((ROOT / name).read_bytes()) == pin['sha256']
    return {'browser': browser, 'inputs': inputs, 'collection': report['status'],
            'owner_result': result, 'reported_root_terminal': terminal,
            'raw_request': requests[0].name, 'user_agent': report['userAgent'],
            'reference_checks_recomputed_from_pinned_javascript': recalculated,
            'reference_checks_pass': reference_pass, 'observations': report['observations'],
            'normative_policy_verdict': None, 'live_app_or_process_recheck': False}


if __name__ == '__main__':
    assert len(sys.argv) == 3 and sys.argv[1] in ('firefox', 'chrome')
    output = Path(sys.argv[2])
    assert output.name == sys.argv[2] and output.suffix == '.json'
    result = review(sys.argv[1])
    with (HERE / output).open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'browser': result['browser'], 'collection': result['collection'],
                      'reference_checks_pass': result['reference_checks_pass'],
                      'sinks': {row['mode']: {'before': row['before']['sink'],
                        'active': [s['sink'] for s in row['activeSamples']],
                        'cancelled': [s['sink'] for s in row['cancelSamples']]}
                        for row in result['observations']}, 'normative_policy_verdict': None}))
