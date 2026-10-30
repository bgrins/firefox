import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-registered-color-initial-independence-installed-v1'
OWNER_SHA = '92ea11dca59760bc1d844916f076cb1b3160c99c1f5b0ddf15f035fc3d7a6a8f'
RUNS = {
    'firefox': ('26585ad74eeee4edb503e508163f95dbb2ba4014b6d516f255d2264bbee4f8b8', 81304, '770ecd', 'da081e'),
    'chrome': ('a3631cb4b7c2fc33b9a1597d28f666fe70bc2e15e29095cfe646a13ab2f52dc0', 4630, 'b97df2', 'aba37a'),
}
refs = {}

def pin(path, expected=None):
    body = path.read_bytes()
    actual = hashlib.sha256(body).hexdigest()
    if expected is not None:
        assert actual == expected, str(path)
    refs[str(path.relative_to(ROOT))] = {'sha256': actual, 'bytes': len(body)}
    return body

def read(path):
    return json.loads(pin(path))

def closure(directory, expected):
    manifest = json.loads(pin(directory / 'FILES.json', expected))
    for name, record in manifest.items():
        assert len(pin(directory / name, record['sha256'])) == record['bytes']
    return len(manifest)

closure(OWNER, OWNER_SHA)
policy = read(OWNER / 'POLICY.json')
assert policy['execution_enabled'] is True
assert policy['profile_preferences'] == {} and policy['feature_overrides'] is False
fixture = policy['fixture_manifest']
closure((ROOT / fixture['path']).parent, fixture['sha256'])
for record in [policy['process_helper'], *policy['references'].values(), *policy['resources'].values()]:
    pin(ROOT / record['path'], record['sha256'])
resources = {name: pin(ROOT / value['path'], value['sha256']) for name, value in policy['resources'].items()}
resources['/observe.html'] += b'\n<script src="/report.js" defer></script>\n'
resource_receipt = {name: {'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)} for name, body in resources.items()}
script = pin(OWNER / 'report.js').decode()
vm = r'''
const vm = require('vm');
let input = ''; process.stdin.on('data', d => input += d);
process.stdin.on('end', async () => {
 const x = JSON.parse(input); let callback, emitted;
 const context = {URLSearchParams, location:{search:'?run='+x.run_id+'&nonce='+x.nonce},
 navigator:{userAgent:x.report.userAgent}, window:{registrationObservations:x.report.observations.map(r=>r.record).filter(r=>r!==null)},
 add_completion_callback:f=>callback=f,
 fetch:async(url,options)=>{emitted={url,body:JSON.parse(options.body)}; return {ok:true};}};
 vm.runInNewContext(x.script, context);
 await callback(x.report.observations.filter(r=>r.wpt.status!==null).map(r=>r.wpt),x.report.harness);
 process.stdout.write(JSON.stringify(emitted));
});
'''
results = {}
for browser, (manifest, session, launch, terminal) in RUNS.items():
    directory = ROOT / policy['browsers'][browser]['output']
    payload_count = closure(directory, manifest)
    assert read(directory / 'POLICY.json') == policy
    assert read(directory / 'RESOURCES.json') == resource_receipt
    receipt = read(directory / 'ROOT-TERMINAL.json')
    assert receipt == {'session': session, 'launch_chunk': launch, 'terminal_chunk': terminal, 'exit': 0, 'active_owner_manifest_sha256': OWNER_SHA}
    binding = read(directory / 'BINDING.json')
    payload = read(directory / 'REPORT.json')
    raw = list(directory.glob('request-*.json'))
    assert len(raw) == 1 and json.loads(pin(raw[0])) == payload
    assert payload['run_id'] == binding['run_id']
    report = payload['report']
    replayed = json.loads(subprocess.check_output(['node', '-e', vm], input=json.dumps({'script':script, 'run_id':binding['run_id'], 'nonce':binding['nonce'], 'report':report}), text=True))
    assert replayed == {'url':'/report/'+binding['nonce'], 'body':payload}
    rows = report['observations']
    assert [r['mode'] for r in rows] == ['red', 'CanvasText', 'light-dark(red, blue)']
    projection = []
    for row in rows:
        rec = row['record']
        expected_acceptance = row['mode'] == 'red'
        checks = [rec is not None and rec['syntaxSupported'] is True, rec is not None and rec['controlInitial'] == rec['literalRed']]
        assert [c['passed'] for c in row['referenceChecks']] == checks
        match = rec is not None and rec['accepted'] == expected_acceptance and (rec['exception'] is None if expected_acceptance else rec['exception'] is not None and rec['exception']['name'] == 'SyntaxError')
        assert row['activeExpectation']['matches'] == match
        assert row['wpt']['name'] == 'Registered color initial independence: ' + row['mode']
        assert rec['initialValue'] == row['mode'] and rec['accepted'] == (rec['exception'] is None)
        projection.append({'initial':row['mode'], 'accepted':rec['accepted'], 'exception':rec['exception'], 'calibration':checks, 'tentative_expectation_matches':match, 'wpt_status':row['wpt']['status'], 'wpt_message':row['wpt']['message']})
    complete = all(r['record'] is not None and r['wpt']['status'] is not None for r in rows)
    assert (report['status'] == 'complete') == complete
    cleanup = read(directory / 'CLEANUP.json')
    assert cleanup['temporary_removed'] and cleanup['remaining_profile_commands'] == []
    assert cleanup['initial_group']['owned_group_absent'] and cleanup['initial_group']['remaining_members'] == []
    assert read(directory / 'SERVER-ERRORS.json') == []
    env = read(directory / 'ENVIRONMENT.json')
    assert env['user_js_created'] is False and env['feature_environment_overrides'] is False
    command = read(directory / 'COMMAND.json')
    assert command[0] == policy['browsers'][browser]['binary']
    assert command[-1] == binding['origin']+'/observe.html?run='+binding['run_id']+'&nonce='+binding['nonce']
    temp = read(directory / 'TEMPORARY.json')
    assert any(temp['profile'] in arg for arg in command)
    result = read(directory / 'RESULT.json')
    aggregate = {'observation_complete':complete, 'reference_checks_pass':all(all(r['calibration']) for r in projection), 'active_control_expectations_pass':projection[0]['tentative_expectation_matches'], 'all_callbacks_pass':all(r['wpt']['status']==0 for r in rows), 'harness_ok':report['harness']['status']==0}
    aggregate['suite_pass'] = complete and aggregate['all_callbacks_pass'] and aggregate['harness_ok']
    aggregate.update(execution_complete=result['error'] is None and cleanup['temporary_removed'], cleanup_complete=cleanup['temporary_removed'], report_received=True, native_acceptance=False, registration_initial_policy_verdict=None)
    assert all(result[k] == value for k,value in aggregate.items())
    assert report['policyVerdict'] is None and all(r['policyVerdict'] is None for r in rows)
    assert ('Firefox/158.0' if browser == 'firefox' else 'Chrome/156.') in report['userAgent']
    results[browser] = {'runtime_manifest':manifest, 'payloads_authenticated':payload_count, 'terminal':receipt, 'user_agent':report['userAgent'], 'raw_request_sha256':hashlib.sha256(raw[0].read_bytes()).hexdigest(), 'reporter_vm_exact':True, 'aggregates':aggregate, 'observations':projection, 'cleanup':cleanup}
assert results['firefox']['observations'] == results['chrome']['observations']
assert [row['wpt_status'] for row in results['firefox']['observations']] == [0, 1, 1]
for name in ['FILES.json', 'README.md']:
    pin(ROOT / 'artifacts/css-registered-color-initial-spec-trace-v1' / name)
(OUT / 'REPLAY.json').write_text(json.dumps(results, indent=2, sort_keys=True)+'\n')
(OUT / 'REFERENCES.json').write_text(json.dumps(refs, indent=2, sort_keys=True)+'\n')
print(json.dumps({'references':len(refs), 'both_reporter_replays_exact':True, 'both_raw_reports_equal':True, 'observations_equal_across_engines':True, 'each_callbacks':{'PASS':1,'FAIL':2}, 'each_harness_OK':True, 'browser_executed':False, 'live_application_read':False}))
