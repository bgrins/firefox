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
policies = {role: json.loads((HERE / ('POLICY-' + role + '.json')).read_text()) for role in ['original', 'candidate']}
for role, policy in policies.items():
    assert policy['execution_enabled'] is False
    assert policy['source_role'] == 'archived-' + role and policy['archive_role'] == role
    try:
        run.run(policy)
    except AssertionError as exc:
        assert str(exc) == 'disabled preparation'
    else:
        raise AssertionError('Disabled run admitted')
run.pins()
parent = ROOT / 'artifacts/css-attr-fallback-archived-original-runner-v1'
assert (HERE / 'entry.py').read_bytes() == (parent / 'entry.py').read_bytes()
assert run.regular_files(HERE / 'support') == run.regular_files(parent / 'support')
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff((parent / 'run.py').read_text().splitlines(True), (HERE / 'run.py').read_text().splitlines(True), fromfile=str((parent / 'run.py').relative_to(ROOT)), tofile=str((HERE / 'run.py').relative_to(ROOT))))
policy = policies['original']
assert policy['fixture_binding'] == policies['candidate']['fixture_binding']
assert policy['settings'] == policies['candidate']['settings']
assert policy['roster'] == policies['candidate']['roster']
binding = policy['fixture_binding']
source = ROOT / binding['directory']
assert run.sha(source / 'FILES.json') == binding['manifest_sha256']
manifest = json.loads((source / 'FILES.json').read_text())
for name, row in manifest.get('files', manifest).items():
    assert run.sha(source / name) == row['sha256']
source_roles = json.loads((source / 'SOURCE.json').read_text())['roles']
for role, current in policies.items():
    assert current['pending_binding'] is False
    snapshot = json.loads((ROOT / current['snapshot']).read_text())
    assert run.sha(ROOT / current['snapshot']) == current['snapshot_sha256']
    assert snapshot['source_role'] == role
    assert snapshot['application'] == current['archive_application']
    assert len(snapshot['files']) == current['archive_files'] == 8326
    assert snapshot['native_sources'] == current['native_sources']
    for name, record in source_roles.items():
        assert current['native_sources'][name] == record['base' if role == 'original' else 'candidate']['sha256']
    receipt = json.loads((ROOT / snapshot['build_receipt']).read_text())
    assert run.sha(ROOT / snapshot['build_receipt']) == snapshot['build_receipt_sha256']
    assert receipt['native_sources'] == current['native_sources']
    assert receipt['application_metadata']['source_role'] == role
    assert receipt['application_metadata']['revision'] == current['build_revision']
    assert receipt['browser_build_performed'] and receipt['command_success'] and receipt['preservation_verified'] and receipt['error'] is None
    terminal = json.loads((ROOT / current['prior_owner_terminal']['path']).read_text())
    audit = json.loads((ROOT / current['prior_owner_audit']['path']).read_text())
    assert run.sha(ROOT / current['prior_owner_terminal']['path']) == current['prior_owner_terminal']['sha256']
    assert run.sha(ROOT / current['prior_owner_audit']['path']) == current['prior_owner_audit']['sha256']
    assert terminal['terminal'] and terminal['exit'] == 0
    assert audit['independent_live_restoration_verified'] and audit['backup_removed']
    assert audit['owner_result_sha256'] == terminal['result_sha256']
    assert audit['raw_wpt_observation']['all_24_pass']
ready = json.loads((ROOT / policies['candidate']['snapshot']).read_text())
normalization = ready['startup_normalization']
before = json.loads((ROOT / normalization['pre_startup_snapshot']).read_text())
assert run.sha(ROOT / normalization['pre_startup_snapshot']) == normalization['pre_startup_snapshot_sha256']
marker = 'Contents/Resources/browser/.purgecaches'
assert set(before['files']) - set(ready['files']) == {marker}
assert set(ready['files']) <= set(before['files'])
assert all(row == before['files'][name] for name, row in ready['files'].items())
assert before['files'][marker] == normalization['removed_by_browser_startup_only'][marker]
assert normalization['connector_closed'] and not normalization['manual_archive_writes'] and normalization['retained_payloads_identical']
assert before['bytes'] - ready['bytes'] == 1
assert len(before['files']) == 8327
assert {k: v for k, v in ready.items() if k not in ('files', 'bytes', 'startup_normalization')} == {k: v for k, v in before.items() if k not in ('files', 'bytes')}
roster = json.loads((ROOT / policy['roster']).read_text())
old = json.loads((ROOT / 'artifacts/css-attr-own-fallback-fix-v1/ROSTER.json').read_text())
page, names = next(iter(roster.items()))
assert len(roster) == 1 and len(names) == 28 and names[:24] == old[page]
assert (source / 'tests/css/css-values/attr-fallback-taint.html').read_bytes().startswith((ROOT / 'artifacts/css-attr-own-fallback-fix-v1/tests/css/css-values/attr-fallback-taint.html').read_bytes())
events = [{'action': 'suite_start'}, {'action': 'test_start', 'test': page}]
events += [{'action': 'test_status', 'test': page, 'subtest': name, 'status': 'FAIL' if i < 9 else 'PASS', 'expected': 'PASS'} for i, name in enumerate(names)]
events += [{'action': 'test_end', 'test': page, 'status': 'OK'}, {'action': 'suite_end'}]
assert run.assess(events, roster, 1)['complete']
all_pass = copy.deepcopy(events)
for row in all_pass:
    if row['action'] == 'test_status':
        row['status'] = 'PASS'
assert run.assess(all_pass, roster, 0)['all_28_pass']
negatives = [events[:-1], events[:2] + events[3:], events + [events[2]], events[:1] + events[2:], events + [{'action': 'crash'}]]
for index, field, value in [(2, 'subtest', 'wrong'), (-2, 'status', 'CRASH'), (2, 'status', 'TIMEOUT'), (2, 'test', '/wrong.html')]:
    mutated = copy.deepcopy(events)
    mutated[index][field] = value
    negatives.append(mutated)
assert all(not run.assess(rows, roster, 1)['complete'] for rows in negatives)
assert not run.assess(events, roster, 0)['complete']
assert not run.assess(all_pass, roster, 1)['complete']
scratch = Path(tempfile.mkdtemp(prefix='attr-archive28-check-'))
result = {'browser_execution': False, 'archive_read': False, 'saved_positive_streams': 2, 'saved_negative_streams': len(negatives) + 2, 'scratch': str(scratch)}
try:
    output = scratch / 'stage'
    output.mkdir()
    run.prepare(output, policy)
    snapshot = json.loads((ROOT / policy['snapshot']).read_text())
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
