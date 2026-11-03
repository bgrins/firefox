import ast
import copy
import difflib
import hashlib
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
spec = importlib.util.spec_from_file_location('supplement_runner', HERE / 'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
run.pins()
parent = ROOT / 'artifacts/css-root-self-smil-archived-original-v1'
old = (parent / 'run.py').read_text()
new = (HERE / 'run.py').read_text()
expected = old
for before, after in [
    ('len(roster) == 1 and all(len(names) == len(set(names)) == 7 for names in roster.values())',
     'len(roster) == 2 and sorted(map(len, roster.values())) == [3, 4] and all(len(names) == len(set(names)) for names in roster.values())'),
    ('len(starts) == 1', 'len(starts) == 2'),
    ('len(endings) == 1', 'len(endings) == 2'),
    ("prefix='css-root-self-smil-'", "prefix='css-route-supplement-'"),
    ("choices=['original']", "choices=['original', 'candidate']"),
]:
    assert before in expected
    expected = expected.replace(before, after)
assert new == expected
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff(
    old.splitlines(True), new.splitlines(True),
    fromfile=str((parent / 'run.py').relative_to(ROOT)),
    tofile=str((HERE / 'run.py').relative_to(ROOT))))
assert (HERE / 'entry.py').read_bytes() == (parent / 'entry.py').read_bytes()
assert run.regular_files(HERE / 'support') == run.regular_files(parent / 'support')
roster = json.loads((HERE / 'ROSTER.json').read_text())
assert sorted(map(len, roster.values())) == [3, 4]
events = [{'action': 'suite_start'}]
for page, names in roster.items():
    events.append({'action': 'test_start', 'test': page})
    events.extend({'action': 'test_status', 'test': page, 'subtest': name,
                   'status': 'PASS', 'expected': 'PASS'} for name in names)
    events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
events.append({'action': 'suite_end'})
assert run.assess(events, roster, 0)['all_7_pass']
mixed = copy.deepcopy(events)
mixed[2]['status'] = 'FAIL'
assert run.assess(mixed, roster, 1)['complete']
assert not run.assess(mixed, roster, 1)['all_7_pass']
bad = [events[:-1], events[:2] + events[3:], events + [events[2]],
       events[:1] + events[2:], events + [{'action': 'crash'}]]
for field, value in [('test', '/wrong.html'), ('subtest', 'wrong'), ('status', 'TIMEOUT')]:
    rows = copy.deepcopy(events)
    rows[2][field] = value
    bad.append(rows)
rows = copy.deepcopy(events)
rows[-2]['status'] = 'ERROR'
bad.append(rows)
rows = copy.deepcopy(events)
rows.insert(-1, copy.deepcopy(rows[-2]))
bad.append(rows)
assert all(not run.assess(rows, roster, 0)['complete'] for rows in bad)
assert not run.assess(events, roster, 1)['complete']
assert not run.assess(mixed, roster, 0)['complete']
scratch = Path(tempfile.mkdtemp(prefix='route-supplement-check-', dir='/private/tmp'))
result = {'browser_execution': False, 'archive_inventory_read': False,
          'positive_streams': 2, 'rejecting_streams': len(bad) + 2,
          'pages': 2, 'callbacks': 7, 'scratch': str(scratch), 'roles': {}}
try:
    for role in ('original', 'candidate'):
        policy = json.loads((HERE / ('POLICY-' + role + '.json')).read_text())
        assert policy['execution_enabled'] is False and policy['pending_binding'] is False
        try:
            run.run(policy)
        except AssertionError as exc:
            assert str(exc) == 'disabled preparation'
        else:
            raise AssertionError('disabled runner admitted')
        snapshot = json.loads((ROOT / policy['snapshot']).read_text())
        assert run.sha(ROOT / policy['snapshot']) == policy['snapshot_sha256']
        assert snapshot['source_role'] == role
        assert snapshot['application'] == policy['archive_application']
        assert snapshot['native_sources'] == policy['native_sources']
        assert len(snapshot['files']) == policy['archive_files'] == 8326
        assert not any(name.endswith('/.purgecaches') for name in snapshot['files'])
        build = json.loads((ROOT / snapshot['build_receipt']).read_text())
        assert run.sha(ROOT / snapshot['build_receipt']) == snapshot['build_receipt_sha256']
        assert build['native_sources'] == snapshot['native_sources']
        assert build['browser_build_performed'] and build['command_success'] and build['preservation_verified']
        assert build['error'] is None and build['application_metadata']['source_role'] == role
        terminal = json.loads((ROOT / policy['prior_owner_terminal']['path']).read_text())
        audit = json.loads((ROOT / policy['prior_owner_audit']['path']).read_text())
        at = json.loads((ROOT / policy['prior_audit_terminal']['path']).read_text())
        assert terminal['exit'] == 0 and terminal['terminal']
        assert audit['independent_live_restoration_verified'] and audit['owner_terminal'] == terminal
        assert audit['owner_result_sha256'] == terminal['result_sha256']
        assert at['exit'] == 0 and at['terminal']
        assert at['report_sha256'] == policy['prior_owner_audit']['sha256']
        if role == 'candidate':
            archive = audit['archive_observation']
            assert archive['archive_retained_verified'] and archive['owner_terminal_and_restoration_verified']
            assert archive['receipt_hashes']['ARCHIVE-SNAPSHOT.json'] == policy['snapshot_sha256']
            assert archive['application'] == snapshot['application']
            assert archive['native_sources'] == snapshot['native_sources']
            assert archive['build_receipt_sha256'] == snapshot['build_receipt_sha256']
        output = scratch / role
        output.mkdir()
        run.prepare(output, policy)
        for url, record in policy['settings']['resources'].items():
            assert run.sha(output / 'tests' / url.lstrip('/')) == record['sha256']
        command, env = run.command(output, scratch, policy, snapshot)
        assert {arg.removeprefix('--include=') for arg in command if arg.startswith('--include=')} == set(roster)
        assert '--run-info=' + str(output / 'run-info') in command
        command.insert(3, '--check-args')
        completed = subprocess.run(command, env=env, cwd=output, capture_output=True, text=True)
        assert completed.returncode == 0, (completed.stdout, completed.stderr)
        assert json.loads((output / 'tests/config.json').read_text())['ports'] == {
            name: ['auto'] * count for name, count in policy['settings']['server_protocols'].items()}
        assert (output / 'run-info/mozinfo.json').read_bytes() == (HERE / 'support/mozinfo.json').read_bytes()
        result['roles'][role] = {'argument_check_exit': completed.returncode,
                                 'staged_files': len(run.regular_files(output)),
                                 'snapshot_sha256': policy['snapshot_sha256']}
    result['success'] = True
finally:
    shutil.rmtree(scratch)
    result['scratch_removed'] = not scratch.exists()
    result['tested_inputs'] = {name: run.sha(HERE / name) for name in (
        'run.py', 'check.py', 'prepare_wpt.py', 'REFERENCES.json', 'POLICY-original.json',
        'POLICY-candidate.json', 'MANIFEST.json', 'ROSTER.json', 'RESOURCES.json')}
    print(json.dumps(result))
