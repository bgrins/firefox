import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
runner = load('actual_publication_function', HERE / 'run.py')
assessor = load('actual_assessor', HERE / 'assess.py')
policy = read(HERE / 'POLICY.json')
checks = load('lifecycle_checks', ROOT / policy['helpers']['checks'])
old = ROOT / 'artifacts/css-line-height-reversible-pair-runtime-1/original-wpt'
inputs = {str((old / name).relative_to(ROOT)): sha(old / name)
          for name in ('raw.jsonl', 'RESULT.json', 'APPLICATION-METADATA.json', 'ASSESSMENT.json')}
events = [json.loads(line) for line in (old / 'raw.jsonl').read_text().splitlines()]
original_result = read(old / 'RESULT.json')
metadata = read(old / 'APPLICATION-METADATA.json')
assessment = assessor.assess(events, original_result['exit'], policy, checks, run_binding=metadata)
assert assessment['complete'] and assessment['observed_subtest_count'] == 34
local_policy = dict(policy, original_binding=None)
published = runner.augment_assessment(assessment, phase='original-1', capsule_sha='a'*64,
    epoch_sha='b'*64, policy=local_policy, capsule_directory='artifacts/control-only',
    experiment_sha='c'*64, execution_preserved=True)
published = json.loads(json.dumps(published))
replayed = json.loads(json.dumps(assessor.assess(events, original_result['exit'], policy, checks, run_binding=metadata)))
assert all(published[k] == value for k, value in replayed.items())
old_saved = read(old / 'ASSESSMENT.json')
differing = [k for k, value in replayed.items() if old_saved.get(k) != value]
assert differing == ['oracle_caveat'], differing
broken = dict(published, oracle_caveat=old_saved['oracle_caveat'])
assert [k for k, value in replayed.items() if broken.get(k) != value] == ['oracle_caveat']
assert {n: sha(ROOT / n) for n in inputs} == inputs
(HERE / 'PUBLICATION-CONTROLS.json').write_text(json.dumps({
    'actual_historical_inputs': inputs, 'original_raw_assertions': 34,
    'actual_v2_augmentation_serialization_replay': True,
    'historical_v1_exact_difference': differing,
    'old_publication_override_rejected': True,
    'historical_raw_and_assessment_modified': False,
    'historical_observation_adopted_as_new_baseline': False,
    'browser_executed': False}, indent=2)+'\n')
print(json.dumps({'actual_original_assertions':34,'v2_publication_replay':True,'old_override_rejected':True}))
