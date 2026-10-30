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

import tempfile

for name, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == pin, name
runtime = ROOT / 'artifacts/css-chrome-finite-depth-runtime-1'
owner = ROOT / 'artifacts/css-chrome-finite-depth-runner-v1'
assert sha(runtime / 'FILES.json') == '091d92e8721f046bab1bb8455e5bdd581e2ada0cd10ad1913b8697ae1f64601f'
for directory in [runtime, owner]:
    for name, pin in read(directory / 'FILES.json').items():
        assert sha(directory / name) == (pin['sha256'] if isinstance(pin, dict) else pin), name
terminal = read(runtime / 'ROOT-TERMINAL.json')
assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (74335, 'e72b99', 0)
assert terminal['owner_manifest_sha256'] == sha(owner / 'FILES.json')
assert terminal['result_sha256'] == sha(runtime / 'RESULT.json')
assert terminal['complete_records'] == 4 and not terminal['native_acceptance']
policy = read(runtime / 'POLICY.json')
assert policy == read(owner / 'POLICY.json')
result = read(runtime / 'RESULT.json')
assert result['execution_complete'] and result['records_complete'] and result['error'] is None
assert result['browser_exit'] == 0 and result['all_callbacks_pass']
assessor = load('chrome_depth_assessor', owner / 'assess.py')
assessment = assessor.assess(assessor.read(runtime / 'raw.jsonl'), policy, result['browser_exit'])
assert assessment == read(runtime / 'ASSESSMENT.json') and assessment['complete']
assert [row['status'] for row in assessment['rows']] == ['PASS'] * 4
assert [row['status'] for row in assessment['ends']] == ['OK']
collector = load('chrome_depth_records', owner / 'records.py')
collection = collector.collect(ROOT, runtime / 'progress-records', read(runtime / 'PROGRESS-BINDING.json'), policy, assessment)
assert collection == read(runtime / 'PROGRESS-RECORDS.json') and collection['complete']
assert not collection['errors'] and not collection['missing']
calibration = load('chrome_depth_calibration', owner / 'calibration.py')
assert calibration.report(runtime / 'progress-records', collection, policy) == read(runtime / 'CALIBRATION.json')
assert result['literal_initial_calibration_passed'] and read(runtime / 'CALIBRATION.json')['all_calibrated']
cleanup = read(runtime / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed'] and cleanup['remaining_private_browser_commands'] == []
for name, pin in policy['resources'].items():
    assert sha(runtime / 'tests' / name) == pin['sha256'] == sha(ROOT / pin['path'])
assert sha(runtime / 'metadata/MANIFEST.json') == policy['manifest']['sha256']
pair = ROOT / 'artifacts/css-contextual-duration-finite-depth-pair-interpretation-v1'
replay = load('frozen_firefox_depth_replay', pair / 'replay.py')
with tempfile.TemporaryDirectory(prefix='css-depth-saved-replay-', dir='/private/tmp') as temporary:
    replay.HERE = Path(temporary)
    with contextlib.redirect_stdout(io.StringIO()):
        replay.main()
    firefox = read(Path(temporary) / 'REPLAY.json')
assert firefox == read(pair / 'REPLAY.json')
depths = {}
for depth in (1, 2, 4, 8):
    filename = f'depth-{depth}.json'
    observations = {'chrome': read(runtime / 'progress-records' / filename)['observations']}
    for label in ('original', 'candidate'):
        directory = ROOT / f'artifacts/css-contextual-duration-finite-depth-{label}-runtime-1'
        observations[label] = read(directory / 'progress-records' / filename)['observations']
    expected = calibration.expected_snapshot(depth, True)
    for label, observation in observations.items():
        calibration.require_original_calibration(observation)
        assert observation['literal'] == observations['chrome']['literal']
        assert observation['contextual']['initial'] == observations['chrome']['contextual']['initial']
        assert observation['contextual']['literalInitial'] == observations['chrome']['contextual']['literalInitial']
        for mode in observation.values():
            assert all(all(member.values()) for member in mode['membership'])
            assert mode['beforeMembership'] == mode['afterMembership']
    chrome = observations['chrome']['contextual']
    assert chrome['beforeMembership'] == expected
    assert [sample['opacity'] for sample in chrome['samples']] == [expected['opacity']] * 4
    assert terminal['contextual_leaf_samples'][str(depth)] == [sample['opacity'] for sample in chrome['samples']]
    depths[str(depth)] = {'expected_leaf': expected['opacity'], 'literal_records_and_initial_snapshots_equal': True,
        'samples': {label: observation['contextual']['samples'] for label, observation in observations.items()},
        'observations': observations}
print(json.dumps({'chrome_actual': {'session': 74335, 'terminal': 'e72b99', 'exit': 0},
    'chrome_statuses': ['PASS'] * 4, 'firefox_original_statuses': firefox['original_statuses'],
    'firefox_candidate_statuses': firefox['candidate_statuses'], 'all_page_endings': 'OK',
    'saved_raw_records_calibration_replayed': True, 'frozen_firefox_pair_replayed_unchanged': True,
    'depths': depths, 'native_pass_count_or_arbitrary_depth_claim': False, 'native_acceptance': False}, indent=2))
