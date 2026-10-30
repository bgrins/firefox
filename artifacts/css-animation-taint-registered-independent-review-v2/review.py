import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT / 'artifacts/css-animation-taint-registered-scope-v2'
OWNER = ROOT / 'artifacts/css-animation-taint-registered-installed-v2'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def reconstruct(payload, binding):
    program = r'''
const fs = require('fs');
const vm = require('vm');
let input = '';
process.stdin.on('data', data => input += data);
process.stdin.on('end', async () => {
  const revive = (_key, value) => value && typeof value === 'object' &&
    Object.keys(value).length === 1 && 'nonfinite' in value ? Number(value.nonfinite) : value;
  const {payload, binding} = JSON.parse(input, revive);
  let completion, captured;
  const context = {
    URLSearchParams,
    location: {search: '?' + new URLSearchParams({run: binding.run_id, nonce: binding.nonce})},
    navigator: {userAgent: payload.report.userAgent},
    window: {registeredTaintObservations: Object.fromEntries(payload.report.observations.map(row => [row.mode, row.record]))},
    add_completion_callback: fn => { if (completion) throw Error('duplicate completion'); completion = fn; },
    fetch: async (url, options) => {
      if (captured || url !== '/report/' + binding.nonce || options.method !== 'POST' ||
          options.headers['Content-Type'] !== 'application/json') throw Error('transport mismatch');
      captured = JSON.parse(options.body);
      return {ok: true};
    },
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
  if (!completion) throw Error('missing completion');
  await completion(payload.report.observations.map(row => row.wpt), payload.report.harness);
  if (!captured) throw Error('missing reconstructed report');
  process.stdout.write(JSON.stringify(captured));
});
'''
    result = subprocess.run(['node', '-e', program, str(OWNER / 'report.js')],
                            input=json.dumps({'payload': payload, 'binding': binding}),
                            text=True, capture_output=True, check=True, timeout=15)
    return json.loads(result.stdout)


def review(browser):
    refs = read(HERE / 'REFERENCES.json')
    for name, expected in refs.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    for name, pin in read(OWNER / 'FILES.json').items():
        assert sha((OWNER / name).read_bytes()) == (pin['sha256'] if isinstance(pin, dict) else pin), name
    for name, pin in read(FIXTURE / 'FILES.json').items():
        assert sha((FIXTURE / name).read_bytes()) == (pin['sha256'] if isinstance(pin, dict) else pin), name
    runtime = ROOT / f'artifacts/css-animation-taint-registered-{browser}-runtime-2'
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
    expected = read(HERE / 'TERMINALS.json')[browser]
    assert expected is not None, 'Actual terminal binding pending'
    expected = tuple(expected)
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
    process = record('PROCESS.json')
    assert type(process['pid']) is int and process['pid'] == process['pgid']
    assert temporary['profile'] == temporary['path'] + '/profile'
    assert cleanup['initial_group']['owned_group_absent'] and not cleanup['initial_group']['remaining_members']
    assert not cleanup['remaining_profile_commands']
    environment = record('ENVIRONMENT.json')
    assert environment['feature_environment_overrides'] is False and environment['user_js_created'] is False
    payload = record('REPORT.json')
    requests = list(runtime.glob('request-*.json'))
    assert len(requests) == 1 and record(requests[0].name) == payload
    spec = importlib.util.spec_from_file_location('saved_registered_schema', OWNER / 'run.py')
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    report = owner.validate(payload, binding['run_id'], browser)
    reconstructed = reconstruct(payload, binding)
    assert reconstructed == payload
    recalculated = reconstructed['report']['observations']
    reference_pass = all(check['passed'] for row in recalculated for check in row['referenceChecks'])
    controls_pass = all(row['activeExpectation']['matches'] for row in recalculated if row['mode'] == 'literal')
    assert result['active_control_expectations_pass'] == controls_pass
    callback_statuses = {row['mode']: row['wpt']['status'] for row in report['observations']}
    harness_status = report['harness']['status']
    assert result['reference_checks_pass'] == reference_pass
    assert result['observation_complete'] == (report['status'] == 'complete')
    assert result['cleanup_complete'] == cleanup.get('temporary_removed', False)
    assert result['execution_complete'] == (result['error'] is None and not errors and cleanup.get('temporary_removed', False))
    seals = read(HERE / 'RUNTIME-SEALS.json')
    seal = seals.get(browser)
    if seal is not None:
        manifest = runtime / 'FILES.json'
        assert sha(manifest.read_bytes()) == seal['sha256']
        frozen = read(manifest)
        assert len(frozen) == seal['payloads']
        for name, pin in frozen.items():
            path = runtime / name
            assert path.is_file() and not path.is_symlink()
            expected = pin['sha256'] if isinstance(pin, dict) else pin
            assert sha(path.read_bytes()) == expected
            inputs[str(path.relative_to(ROOT))] = {'sha256': expected, 'bytes': path.stat().st_size}
    for name, pin in inputs.items():
        assert sha((ROOT / name).read_bytes()) == pin['sha256']
    return {'browser': browser, 'inputs': inputs, 'collection': report['status'],
            'owner_result': result, 'reported_root_terminal': terminal,
            'raw_request': requests[0].name, 'user_agent': report['userAgent'],
            'report_reconstructed_from_pinned_reporter': True,
            'calibration_and_expectations_recomputed_from_pinned_javascript': recalculated,
            'callback_statuses': callback_statuses, 'harness_status': harness_status,
            'wpt_suite_pass': harness_status == 0 and all(status == 0 for status in callback_statuses.values()),
            'active_control_expectations_pass': controls_pass,
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
                      'active_control_expectations_pass': result['active_control_expectations_pass'],
                      'callback_statuses': result['callback_statuses'], 'harness_status': result['harness_status'],
                      'sinks': {row['mode']: {phase['label']: phase['readings'] for phase in row['record']['phases']}
                        for row in result['observations'] if row['record'] is not None},
                      'normative_policy_verdict': None}))
