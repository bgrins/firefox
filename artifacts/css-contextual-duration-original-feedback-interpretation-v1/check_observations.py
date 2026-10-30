import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RUNTIME = ROOT / 'artifacts/css-contextual-duration-broader-original-runtime-2'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(RUNTIME / 'FILES.json') == '492edf9f5cb288ecf6c2c16b8935aea5fc9a909bcfb28be04cb636165e610522'
manifest = read(RUNTIME / 'FILES.json')
selected = ['ROOT-TERMINAL.json', 'RESULT.json', 'FEEDBACK-BINDING.json', 'FEEDBACK-RECORDS.json',
            'feedback-wpt/ASSESSMENT.json', 'feedback-wpt/RESULT.json', 'feedback-wpt/raw.jsonl',
            'feedback-records/self.json', 'feedback-records/coupled.json', 'feedback-records/zero-start.json']
for name in selected:
    assert sha(RUNTIME / name) == manifest[name]
terminal = read(RUNTIME / 'ROOT-TERMINAL.json')
assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (89331, 'dcda0d', 0)
assert terminal['root_replay_complete'] and terminal['state_and_application_preserved']
phase = read(RUNTIME / 'RESULT.json')['phases']['feedback']
for key, name in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'), ('result_sha256', 'RESULT.json')]:
    assert sha(RUNTIME / 'feedback-wpt' / name) == phase[key]
assessment = read(RUNTIME / 'feedback-wpt/ASSESSMENT.json')
raw = [json.loads(line) for line in (RUNTIME / 'feedback-wpt/raw.jsonl').read_text().splitlines() if line]
assert [r for r in raw if r.get('action') == 'test_status'] == assessment['rows']
assert [r for r in raw if r.get('action') == 'test_end'] == assessment['ends']
assert len(assessment['rows']) == 3 and all(r['status'] == 'PASS' for r in assessment['rows'])
assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
assert assessment['complete'] and not assessment['errors'] and not assessment['fixture_setup_errors']
binding = read(RUNTIME / 'FEEDBACK-BINDING.json')
records = read(RUNTIME / 'FEEDBACK-RECORDS.json')
assert binding['run_id'] == records['run_id']
summaries = {}
for filename, kind, font, css, opacity, count in [
    ('self.json', 'self font', '28px', '1.75s', '1', 1),
    ('coupled.json', 'coupled font and opacity', '28px', '1.75s', '0.75', 2),
    ('zero-start.json', 'zero-start self font', '24px', '1.5s', '1', 1),
]:
    path = RUNTIME / 'feedback-records' / filename
    assert sha(path) == records['records'][filename]['sha256']
    value = read(path)
    assert value['kind'] == kind and value['run_id'] == binding['run_id']
    samples = value['samples']
    assert len(samples) == 8 and all(sample == samples[0] for sample in samples)
    sample = samples[0]
    assert sample['font'] == sample['repeatFont'] == font
    assert sample['cssDuration'] == sample['repeatDuration'] == css and sample['opacity'] == opacity
    assert len(sample['effects']) == count
    assert [e['name'] for e in sample['effects']] == (['fontCycle', 'fade'] if count == 2 else ['fontCycle'])
    assert all((e['duration'], e['time'], e['progress'], e['state']) == (1000, 750, 0.75, 'paused') for e in sample['effects'])
    summaries[kind] = {'sample_count': 8, 'all_samples_equal': True, 'representative_sample': sample}
refs = {str((RUNTIME / name).relative_to(ROOT)): sha(RUNTIME / name) for name in selected}
for path in [RUNTIME / 'FILES.json', ROOT / 'artifacts/css-contextual-duration-feedback-model-v1/FILES.json',
             ROOT / 'artifacts/css-contextual-duration-feedback-model-v1/DurationFeedback.lean',
             ROOT / 'artifacts/css-contextual-duration-scheduling-model-v1/DurationScheduling.lean']:
    refs[str(path.relative_to(ROOT))] = sha(path)
result = {'actual_root_terminal': {'session': 89331, 'terminal': 'dcda0d', 'exit': 0},
          'records': summaries, 'zero_start_projection': {'computed_ms': 1500, 'applied_ms': 1000},
          'model_pair_premise_satisfied': False, 'initial_synchronized_seed_observed': False,
          'candidate_observed': False, 'native_refinement': False,
          'loop_or_hang_observed': False, 'new_coverage': 0}
(PACKAGE / 'OBSERVATION-JOIN.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
(PACKAGE / 'REFERENCES.json').write_text(json.dumps(refs, indent=2, sort_keys=True) + '\n')
print(json.dumps({'selected_runtime_files_authenticated': 10, 'raw_rows_and_endings_match': True,
                  'records': 3, 'samples_each': 8, 'zero_start_computed_applied_ms': [1500, 1000],
                  'pair_premise': False, 'browser_executed': False}))
