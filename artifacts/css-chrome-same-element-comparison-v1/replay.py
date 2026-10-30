import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

for name, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == pin, name
runtime = ROOT / 'artifacts/css-chrome-same-element-runtime-1'
owner = ROOT / 'artifacts/css-chrome-same-element-runner-v1'
for directory in [runtime, owner]:
    for name, pin in read(directory / 'FILES.json').items():
        assert sha(directory / name) == (pin['sha256'] if isinstance(pin, dict) else pin), name
assert sha(runtime / 'FILES.json') == '2a0b0e70f5e223a21a751c757905c3be7709b3484d0fad093dca54fe3aea9a5d'
terminal = read(runtime / 'ROOT-TERMINAL.json')
assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (29017, '86e1e8', 0)
assert terminal['owner_manifest_sha256'] == sha(owner / 'FILES.json')
assert terminal['result_sha256'] == sha(runtime / 'RESULT.json')
assert terminal['complete_records'] == 2 and terminal['portable_inventory_unchanged']
assert terminal['owned_process_and_profile_cleanup_verified'] and not terminal['native_acceptance']
policy = read(runtime / 'POLICY.json')
assert policy == read(owner / 'POLICY.json')
result = read(runtime / 'RESULT.json')
assert result['execution_complete'] and result['records_complete'] and result['error'] is None
assert result['browser_exit'] == 1 and not result['all_callbacks_pass']
assessor = load('chrome_replay_assessor', owner / 'assess.py')
assessment = assessor.assess(assessor.read(runtime / 'raw.jsonl'), policy, result['browser_exit'])
assert assessment == read(runtime / 'ASSESSMENT.json') and assessment['complete']
assert [row['status'] for row in assessment['rows']] == ['FAIL', 'PASS']
assert [row['status'] for row in assessment['ends']] == ['OK']
collector = load('chrome_replay_records', owner / 'records.py')
collection = collector.collect(ROOT, runtime / 'progress-records', read(runtime / 'PROGRESS-BINDING.json'), policy, assessment)
assert collection == read(runtime / 'PROGRESS-RECORDS.json') and collection['complete']
assert not collection['errors'] and not collection['missing']
cleanup = read(runtime / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
assert cleanup['remaining_private_browser_commands'] == []
for name, pin in policy['resources'].items():
    assert sha(runtime / 'tests' / name) == pin['sha256'] == sha(ROOT / pin['path'])
assert sha(runtime / 'metadata/MANIFEST.json') == policy['manifest']['sha256']
stream = io.StringIO()
with contextlib.redirect_stdout(stream):
    runpy.run_path(str(ROOT / 'artifacts/css-contextual-duration-same-element-pair-interpretation-v1/replay.py'))
firefox = json.loads(stream.getvalue())
assert firefox == read(ROOT / 'artifacts/css-contextual-duration-same-element-pair-interpretation-v1/REPLAY.json')
for filename, pair in firefox['pairs'].items():
    pair['chrome'] = read(runtime / 'progress-records' / filename)['observations']
    for mode, observation in pair['chrome'].items():
        assert all(all(item.values()) for item in observation['membership'])
        assert observation['beforeMembership'] == observation['afterMembership']
    if filename == 'same-element-acyclic.json':
        assert pair['chrome']['literal'] == pair['original']['literal']
        assert [s['value'] for s in pair['chrome']['contextual']['samples']] == [.75] * 4
    else:
        for mode in ['literal500', 'literal1000']:
            assert pair['chrome'][mode] == pair['original'][mode]
        assert [s['value'] for s in pair['chrome']['contextual']['samples']] == [32] * 4
print(json.dumps({'chrome_outer_reported': {'session': 29017, 'terminal': '86e1e8', 'exit': 0},
    'chrome_raw_statuses': ['FAIL', 'PASS'], 'chrome_ending': 'OK', 'chrome_browser_exit': 1,
    'raw_assessment_and_records_replayed': True, 'firefox_pair_replayed_unchanged': True,
    'cleanup_saved_receipt_verified': True, 'pairs': firefox['pairs'],
    'normative_policy_or_native_acceptance': False}, indent=2))
