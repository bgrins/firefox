import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNER = ROOT / 'artifacts/css-selective-handoff-font-unit-archived-wpt-v1'
RUNTIME = ROOT / 'artifacts/css-selective-handoff-font-unit-archived-runtime-v1'
OLD = ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-runtime-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
assert sha(OWNER / 'FILES.json') == 'efcbb30d8a480c30c96f0138437cf979864a4b2638b0bce0ad180a73f4bb17a4'
for name, record in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == record['sha256'], name
for name, digest in read(HERE / 'INPUTS.json').items():
    assert sha(ROOT / name) == digest, name
terminal = read(RUNTIME / 'ROOT-TERMINAL.json')
assert terminal['terminal'] is True and terminal['launch'] == '3c7cc0'
assert terminal['session'] == 66109 and terminal['terminal_chunk'] == '700520'
assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(RUNTIME / 'RESULT.json')
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['exit'] == 0 and result['execution_error'] is None
assert result['archive_preserved'] and result['staged_preserved']
spec = importlib.util.spec_from_file_location('selective_font14_archive_audit_runner', OWNER / 'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
run.pins()
policy = read(OWNER / 'POLICY-candidate.json')
snapshot = read(ROOT / policy['snapshot'])
assert sha(ROOT / policy['snapshot']) == policy['snapshot_sha256']
actual_archive = run.archive(snapshot, policy)
assert actual_archive == read(RUNTIME / 'ARCHIVE-PRE.json') == read(RUNTIME / 'ARCHIVE-POST.json')
staged = read(RUNTIME / 'STAGED.json')
assert all(sha(RUNTIME / name) == digest for name, digest in staged.items())
trees = read(RUNTIME / 'STAGED-TREES.json')
assert set(trees) == {'tests', 'metadata', 'mozilla-tests', 'mozilla-metadata', 'support', 'run-info'}
assert all(run.regular_files(RUNTIME / name) == files for name, files in trees.items())
link = RUNTIME / 'tests/tools'
assert link.is_symlink() and link.resolve() == ROOT / 'testing/web-platform/tests/tools'
command = read(RUNTIME / 'COMMAND.json')
temporary = Path(command['temporary'])
assert temporary.parent == Path('/private/tmp')
assert temporary.name.startswith('css-selective-font-units-candidate-')
assert not temporary.exists() and not temporary.is_symlink()
expected_command, _ = run.command(RUNTIME, temporary, policy, snapshot)
assert command['command'] == expected_command
process = read(RUNTIME / 'PROCESS.json')
assert process['pid'] == process['pgid'] and process['pgid'] > 1
try:
    os.killpg(process['pgid'], 0)
except ProcessLookupError:
    pass
else:
    raise AssertionError('Owned WPT group still exists')
processes = subprocess.check_output(['ps', '-axo', 'pid=,pgid=,command='], text=True)
assert not any(policy['archive_application'] in line or str(temporary) in line
               for line in processes.splitlines())
cleanup = read(RUNTIME / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
assert sha(OLD / 'FILES.json') == '4e5fdea12bdaefcf9aa4b887b6ac0a783ac5f93e4a04bf2b424bf8cd5d23bbc4'
old_files = read(OLD / 'FILES.json')['files']
old_raw = OLD / 'candidate-wpt-font_units/raw.jsonl'
assert sha(old_raw) == old_files['candidate-wpt-font_units/raw.jsonl']['sha256'] == '20749ba95bcbf291e9eddd740bc805618e9c70feb907cea02b100279e83de3e1'
roster = read(ROOT / policy['roster'])
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
old_events = [json.loads(line) for line in old_raw.read_text().splitlines()]
assessment = run.assess(events, roster, 0)
assert assessment == read(RUNTIME / 'ASSESSMENT.json')
assert assessment['all_14_pass'] and run.assess(old_events, roster, 0)['all_14_pass']
keys = ('test', 'subtest', 'status', 'expected', 'known_intermittent', 'message')
def signatures(rows, action):
    return [{key: row[key] for key in keys if key in row}
            for row in rows if row.get('action') == action]
assert signatures(events, 'test_status') == signatures(old_events, 'test_status')
assert signatures(events, 'test_end') == signatures(old_events, 'test_end')
for url, record in policy['settings']['resources'].items():
    assert sha(RUNTIME / 'tests' / url.lstrip('/')) == record['sha256']
page = next(iter(roster)).lstrip('/')
assert sha(RUNTIME / 'tests' / page) == sha(OLD / 'candidate-wpt-font_units/tests' / page)
assert sha(OLD / 'candidate-wpt-font_units/tests' / page) == old_files['candidate-wpt-font_units/tests/' + page]['sha256']
run.pins()
for name, digest in read(HERE / 'INPUTS.json').items():
    assert sha(ROOT / name) == digest, name
print(json.dumps({
    'success': True, 'archive_inventory_verified': actual_archive,
    'staged_trees_verified': sorted(trees), 'owned_group_absent': process['pgid'],
    'temporary_absent': str(temporary), 'archive_processes_absent': True,
    'preserved_pass_signatures': 14, 'preserved_ending_signatures': 1,
    'original_raw_sha256': sha(old_raw), 'current_raw_sha256': sha(RUNTIME / 'raw.jsonl'),
    'owner_result_sha256': sha(RUNTIME / 'RESULT.json'),
    'owner_terminal_sha256': sha(RUNTIME / 'ROOT-TERMINAL.json'),
    'audit_script_sha256': sha(HERE / 'audit.py'),
    'native_source_or_index_operations': False,
}, indent=2))
