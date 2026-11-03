import copy
import difflib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('isolated_archive_run', HERE / 'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
policies = {'candidate': json.loads((HERE/'POLICY-candidate.json').read_text())}
for role, policy in policies.items():
    assert policy['execution_enabled'] is False
    assert policy['source_role'] == 'archived-' + role and policy['archive_role'] == role
    try: run.run(policy)
    except AssertionError as exc: assert str(exc) == 'disabled preparation'
    else: raise AssertionError('Disabled run admitted')
run.pins()
parent = ROOT / 'artifacts/css-explicit-attribute-taint-archived-original-v1'
assert (HERE / 'entry.py').read_bytes() == (parent / 'entry.py').read_bytes()
assert run.regular_files(HERE / 'support') == run.regular_files(parent / 'support')
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff((parent / 'run.py').read_text().splitlines(True), (HERE / 'run.py').read_text().splitlines(True), fromfile=str((parent / 'run.py').relative_to(ROOT)), tofile=str((HERE / 'run.py').relative_to(ROOT))))
policy = policies['candidate']
binding = policy['fixture_binding']
source = ROOT / binding['directory']
assert run.sha(source / 'FILES.json') == binding['manifest_sha256']
manifest = json.loads((source / 'FILES.json').read_text())
for name, row in manifest.get('files', manifest).items():
    assert run.sha(source / name) == row['sha256']

before_pin = policy['pre_startup_snapshot']
assert run.sha(ROOT / before_pin['path']) == before_pin['sha256']
before = json.loads((ROOT / before_pin['path']).read_text())
assert before['application'] == policy['archive_application']
assert before['native_sources'] == policy['native_sources']
assert len(before['files']) == 8327 and before['source_role'] == 'candidate'
marker = 'Contents/Resources/browser/.purgecaches'
assert before['files'][marker] == {'bytes':1,'mode':420,'sha256':'01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b'}
def validate_ready(ready):
    normalization = ready['startup_normalization']
    assert normalization['pre_startup_snapshot'] == before_pin['path']
    assert normalization['pre_startup_snapshot_sha256'] == before_pin['sha256']
    assert set(before['files']) - set(ready['files']) == {marker}
    assert set(ready['files']) <= set(before['files'])
    assert all(row == before['files'][name] for name, row in ready['files'].items())
    assert before['files'][marker] == normalization['removed_by_browser_startup_only'][marker]
    assert set(normalization['removed_by_browser_startup_only']) == {marker}
    assert normalization['connector_closed'] and not normalization['manual_archive_writes'] and normalization['retained_payloads_identical']
    assert before['bytes'] - ready['bytes'] == 1 and len(ready['files']) == 8326
    assert {k:v for k,v in ready.items() if k not in ('files','bytes','startup_normalization')} == {k:v for k,v in before.items() if k not in ('files','bytes')}
sample_ready = copy.deepcopy(before)
del sample_ready['files'][marker]
sample_ready['bytes'] -= 1
sample_ready['startup_normalization'] = {
    'pre_startup_snapshot':before_pin['path'], 'pre_startup_snapshot_sha256':before_pin['sha256'],
    'removed_by_browser_startup_only':{marker:before['files'][marker]},
    'connector_closed':True, 'manual_archive_writes':False, 'retained_payloads_identical':True}
validate_ready(sample_ready)
for change in range(5):
    bad = copy.deepcopy(sample_ready)
    if change == 0: bad['files'][marker] = before['files'][marker]
    if change == 1: bad['files'][next(iter(bad['files']))]['sha256'] = '0'*64
    if change == 2: bad['startup_normalization']['manual_archive_writes'] = True
    if change == 3: bad['startup_normalization']['removed_by_browser_startup_only']['unexpected'] = {}
    if change == 4: bad['native_sources'] = {}
    try: validate_ready(bad)
    except AssertionError: pass
    else: raise AssertionError('Invalid startup transition accepted')
receipt = json.loads((ROOT / before['build_receipt']).read_text())
assert run.sha(ROOT / before['build_receipt']) == before['build_receipt_sha256']
assert receipt['native_sources'] == policy['native_sources']
assert receipt['application_metadata']['source_role'] == 'candidate'
assert receipt['application_metadata']['revision'] == policy['build_revision']
assert receipt['browser_build_performed'] and receipt['command_success'] and receipt['preservation_verified'] and receipt['error'] is None
if policy['pending_binding']:
    assert policy['snapshot'] is policy['snapshot_sha256'] is policy['prior_owner_terminal'] is policy['prior_owner_audit'] is None
    enabled = copy.deepcopy(policy)
    enabled['execution_enabled'] = True
    try: run.run(enabled)
    except AssertionError: pass
    else: raise AssertionError('Pending archive admitted')
else:
    assert policy['prior_owner_terminal']['path'] == 'artifacts/css-explicit-taint-typed-reparse-candidate-browser-runtime-v1/ROOT-OWNER-TERMINAL.json'
    assert policy['prior_owner_audit']['path'] == 'artifacts/css-explicit-taint-typed-reparse-candidate-browser-runtime-v1/ROOT-LIVE-RESTORATION.json'
    assert run.sha(ROOT / policy['snapshot']) == policy['snapshot_sha256']
    validate_ready(json.loads((ROOT / policy['snapshot']).read_text()))
    ready = json.loads((ROOT / policy['snapshot']).read_text())
    for path, digest in ready['startup_normalization']['initialization_evidence'].items():
        assert run.sha(ROOT / path) == digest
    initial = ROOT / 'artifacts/css-explicit-taint-browser-initialization-v1'
    pre = json.loads((initial/'PRE.json').read_text())
    post = json.loads((initial/'POST.json').read_text())
    absent = json.loads((initial/'PROCESS-CHECK.json').read_text())
    assert pre['snapshot_sha256'] == before_pin['sha256'] and pre['exact_inventory_match']
    assert pre['application'] == policy['archive_application'] and pre['verified_files'] == 8327
    assert pre['bytes'] == before['bytes']
    assert post['removed'] == {marker:before['files'][marker]} and post['added'] == post['changed'] == []
    assert post['verified_files'] == 8326 and post['bytes'] == ready['bytes']
    assert post['retained_payloads_identical'] and not post['manual_archive_writes']
    assert absent['exit'] == 0 and absent['complete_output_examined'] and absent['matching_processes'] == []
    assert absent['archive_path_fragment'] == Path(policy['archive_application']).parent.name

    for key in ('prior_owner_terminal','prior_owner_audit'):
        assert run.sha(ROOT / policy[key]['path']) == policy[key]['sha256']
    terminal = json.loads((ROOT / policy['prior_owner_terminal']['path']).read_text())
    audit = json.loads((ROOT / policy['prior_owner_audit']['path']).read_text())
    assert terminal['terminal'] and terminal['exit'] in (0,1)
    assert audit['independent_live_restoration_verified']
    assert audit['owner_result_sha256'] == terminal['result_sha256']
roster = json.loads((ROOT/policy['roster']).read_text())
page, names = next(iter(roster.items()))
assert len(roster) == 1 and len(names) == 3
inputs = json.loads((source/'INPUTS.json').read_text())
assert inputs['callbacks'] == 3 and inputs['prefs'] == inputs['metadata'] == {}
assert policy['settings']['resources'] == inputs['resources']
assert policy['settings']['manifests']['portable'] == inputs['manifest']
assert policy['settings']['expected_subtests'] == policy['settings']['target_subtests'] == roster
events = [{'action': 'suite_start'}, {'action': 'test_start', 'test': page}]
events += [{'action': 'test_status', 'test': page, 'subtest': name, 'status': 'FAIL' if i == 0 else 'PASS', 'expected': 'PASS'} for i, name in enumerate(names)]
events += [{'action': 'test_end', 'test': page, 'status': 'OK'}, {'action': 'suite_end'}]
assert run.assess(events, roster, 1)['complete']
all_pass = copy.deepcopy(events)
for row in all_pass:
    if row['action'] == 'test_status':
        row['status'] = 'PASS'
assert run.assess(all_pass, roster, 0)['all_3_pass']
negatives = [events[:-1], events[:2] + events[3:], events + [events[2]], events[:1] + events[2:], events + [{'action': 'crash'}]]
for index, field, value in [(2, 'subtest', 'wrong'), (-2, 'status', 'CRASH'), (2, 'status', 'TIMEOUT'), (2, 'test', '/wrong.html')]:
    mutated = copy.deepcopy(events)
    mutated[index][field] = value
    negatives.append(mutated)
assert all(not run.assess(rows, roster, 1)['complete'] for rows in negatives)
assert not run.assess(events, roster, 0)['complete']
assert not run.assess(all_pass, roster, 1)['complete']
scratch = Path(tempfile.mkdtemp(prefix='composition-archive-check-', dir='/private/tmp'))
result = {'browser_execution': False, 'archive_read': False, 'saved_positive_streams': 2, 'startup_transition_positive': 1, 'startup_transition_negatives': 5, 'pending_binding_rejected': policy['pending_binding'], 'saved_negative_streams': len(negatives) + 2, 'scratch': str(scratch)}
try:
    output = scratch / 'stage'
    output.mkdir()
    run.prepare(output, policy)
    snapshot = before if policy['pending_binding'] else json.loads((ROOT / policy['snapshot']).read_text())
    command, env = run.command(output, scratch, policy, snapshot)
    assert './mach' not in command and not any(arg.startswith('--run-info=' + str(ROOT / 'objdir')) for arg in command)
    command.insert(3, '--check-args')
    process = subprocess.run(command, env=env, cwd=output, capture_output=True, text=True)
    result['argument_check'] = {'command': command, 'exit': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}
    assert process.returncode == 0, (process.stdout, process.stderr)
    assert json.loads((output / 'tests/config.json').read_text())['ports'] == {name: ['auto'] * count for name, count in policy['settings']['server_protocols'].items()}
    assert (output / 'run-info/mozinfo.json').read_bytes() == (HERE / 'support/mozinfo.json').read_bytes()
    result.update(success=True, staged_files=len(run.regular_files(output)), disabled_gates_rejected=True)
finally:
    shutil.rmtree(scratch)
    result['scratch_removed'] = not scratch.exists()
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
