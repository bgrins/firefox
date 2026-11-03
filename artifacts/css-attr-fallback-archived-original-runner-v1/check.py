import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('isolated_original_run', HERE / 'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
policy = json.loads((HERE / 'POLICY.json').read_text())
assert policy['execution_enabled'] is False
try:
    run.run(policy)
    raise AssertionError('disabled gate accepted')
except AssertionError as exc:
    assert str(exc) == 'disabled preparation'
run.pins()
roster = json.loads((run.ROOT / policy['roster']).read_text())
page, names = next(iter(roster.items()))
events = [{'action': 'suite_start'}] + [
    {'action': 'test_status', 'test': page, 'subtest': name, 'status': 'FAIL' if i < 9 else 'PASS'}
    for i, name in enumerate(names)
] + [{'action': 'test_end', 'test': page, 'status': 'OK'}, {'action': 'suite_end'}]
assert run.assess(events, roster)['complete']
all_pass = copy.deepcopy(events)
for event in all_pass:
    if event['action'] == 'test_status':
        event['status'] = 'PASS'
assert run.assess(all_pass, roster)['complete']
negatives = []
negatives.append(events[:-1])
negatives.append(events[:1] + events[2:])
negatives.append(events + [events[1]])
wrong = copy.deepcopy(events)
wrong[1]['subtest'] = 'wrong callback'
negatives.append(wrong)
wrong = copy.deepcopy(events)
wrong[-2]['status'] = 'CRASH'
negatives.append(wrong)
wrong = copy.deepcopy(events)
wrong[1]['status'] = 'TIMEOUT'
negatives.append(wrong)
wrong = copy.deepcopy(events)
wrong[1]['test'] = '/wrong.html'
negatives.append(wrong)
assert all(not run.assess(value, roster)['complete'] for value in negatives)
scratch = Path(tempfile.mkdtemp(prefix='attr-original-runner-check-'))
result = {'browser_execution': False, 'archive_read': False, 'saved_positive_streams': 2,
          'saved_negative_streams': len(negatives), 'scratch': str(scratch)}
try:
    output = scratch / 'stage'
    output.mkdir()
    run.prepare(output, policy)
    snapshot = json.loads((run.ROOT / policy['snapshot']).read_text())
    command, env = run.command(output, scratch, policy, snapshot)
    assert all('mach' != arg for arg in command)
    command.insert(3, '--check-args')
    proc = subprocess.run(command, env=env, cwd=output, capture_output=True, text=True)
    result['argument_check'] = {'command': command, 'exit': proc.returncode,
                                'stdout': proc.stdout, 'stderr': proc.stderr}
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    staged = run.regular_files(output)
    assert json.loads((output / 'tests/config.json').read_text())['ports'] == {
        name: ['auto'] * count for name, count in policy['settings']['server_protocols'].items()}
    assert (output / 'run-info/mozinfo.json').read_bytes() == (HERE / 'support/mozinfo.json').read_bytes()
    result.update(success=True, staged_files=len(staged), disabled_gate_rejected=True)
finally:
    shutil.rmtree(scratch)
    result['scratch_removed'] = not scratch.exists()
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
