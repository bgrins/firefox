import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for path, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / path) == pin['sha256'] and (ROOT / path).stat().st_size == pin['bytes']
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
owner = ROOT / 'artifacts/css-prioritary-published-candidate-v1'
policy = read(owner / 'POLICY.json')
admission = load('saved_bridge', owner / 'admission.py')
capture = admission.validate_current(ROOT, policy, read(owner / 'SOURCE-ROLES.json'))
comparison = load('saved_comparison', owner / 'comparison.py')
assessor = load('saved_assessor', owner / 'assess.py')
checks = load('saved_streams', ROOT / policy['wpt']['checks_helper'])
original = comparison.replay_original(ROOT, policy, assessor, checks, 'ordinary')
phase = ROOT / 'artifacts/css-prioritary-published-candidate-runtime-1/candidate-wpt-ordinary'
settings = read(phase / 'ASSESSMENT-POLICY.json')
metadata = read(phase / 'APPLICATION-METADATA.json')
assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
replay = assessor.assess(events, read(phase / 'RESULT.json')['exit'], settings, checks, original=original, run_binding=metadata)
assert replay == read(phase / 'ASSESSMENT.json') and replay['complete'] and replay['errors'] == []
behavior = comparison.behavior(original, replay, policy['wpt_lanes']['ordinary'], assessor.signature)
assert behavior == read(phase / 'BEHAVIOR-COMPARISON.json')
errors = ['phase revision differs from authenticated build lineage', 'run_info changed outside the independently bound BuildID']
assert replay['comparison_errors'] == behavior['errors'] == errors and not behavior['repair_observation_gate']
def pair_metadata(before, after):
    for role, item, revision in [('original', before, policy['baseline_head']), ('candidate', after, policy['head'])]:
        binding = item['run_binding']
        assert assessor.bound_run_info(item['run_info'], binding)
        assert binding['source_role'] == role
        assert binding['revision'] == binding['build_revision'] == binding['harness_revision'] == revision
    ignore = {'revision', 'browser_build_id'}
    assert {k:v for k,v in before['run_info'].items() if k not in ignore} == {k:v for k,v in after['run_info'].items() if k not in ignore}
pair_metadata(original, replay)
assert replay['run_binding']['revision'] == capture['checkpoint']['head']
changed = {key: {'original': original['run_info'].get(key), 'candidate': replay['run_info'].get(key)}
           for key in original['run_info'].keys() | replay['run_info'].keys()
           if original['run_info'].get(key) != replay['run_info'].get(key)}
assert set(changed) == {'revision', 'browser_build_id'}
assert all(row['status'] == 'PASS' for row in replay['rows']) and len(replay['rows']) == 68
assert len(replay['ends']) == 8 and all(row['status'] == 'OK' for row in replay['ends'])
assert len(behavior['differences']) == 9
assert all(row['original']['status'] == 'FAIL' and row['candidate']['status'] == 'PASS' for row in behavior['differences'])
assert all(row['status'] == 'PASS' for row in behavior['target_rows']) and len(behavior['target_rows']) == 21
assert behavior['published_original_signatures'] == behavior['published_candidate_signatures'] and len(behavior['published_original_signatures']) == 8
negatives = []
for label in ['old_phase_revision', 'candidate_harness', 'raw_revision', 'raw_build_id', 'other_run_info', 'source_role']:
    before, after = copy.deepcopy(original), copy.deepcopy(replay)
    if label == 'old_phase_revision': before['run_binding']['revision'] = policy['head']; before['run_binding']['build_revision'] = policy['head']
    elif label == 'candidate_harness': after['run_binding']['harness_revision'] = policy['baseline_head']; after['run_info']['revision'] = policy['baseline_head']
    elif label == 'raw_revision': after['run_info']['revision'] = '0' * 40
    elif label == 'raw_build_id': after['run_info']['browser_build_id'] = 'wrong'
    elif label == 'other_run_info': after['run_info']['debug'] = not after['run_info']['debug']
    else: after['run_binding']['source_role'] = 'original'
    try: pair_metadata(before, after)
    except AssertionError: negatives.append(label)
    else: raise AssertionError('Accepted malformed pair: ' + label)
result = {'lane': 'ordinary', 'complete': True, 'callbacks': {'PASS': 68, 'FAIL': 0}, 'endings_OK': 8,
          'original_PASS_count': sum(row['status'] == 'PASS' for row in original['rows']),
          'FAIL_to_PASS': 9, 'target_PASS': 21, 'published_signatures_unchanged': 8,
          'recorded_comparison_gate': False, 'recorded_errors': errors,
          'policy_phase_revisions': settings['phase_revisions'], 'actual_original_revision': original['run_binding']['revision'],
          'actual_candidate_revision': replay['run_binding']['revision'], 'run_info_differences': changed,
          'saved_checkpoint_bridge_authenticated': True, 'proposed_pair_metadata_negatives_rejected': negatives,
          'behavioral_obligations_satisfied': True, 'corrected_live_gate_written': False,
          'restoration_claimed': False, 'full_candidate_acceptance': False}
for path, pin in read(HERE / 'REFERENCES.json').items(): assert sha(ROOT / path) == pin['sha256']
print(json.dumps(result, indent=2, sort_keys=True))
