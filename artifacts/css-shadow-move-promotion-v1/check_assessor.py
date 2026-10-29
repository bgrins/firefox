import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sample = load('shadow_final_samples', ROOT / 'artifacts/css-shadow-move-paired-browser-v1/check_assessor.py')
final = load('shadow_final_projection', HERE / 'assess.py')
settings = json.loads((HERE / 'POLICY.json').read_bytes())
events, binding = sample.sample('candidate')
known = sample.known
row = next(e for e in events if (e.get('test'), e.get('subtest')) == known)
assert row['expected'] == 'FAIL' and row['known_intermittent'] == []
del row['expected']
rejected = 0
with tempfile.TemporaryDirectory(prefix='css-shadow-final-assessor-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    prior = scratch / 'historical.json'
    prior.write_text(json.dumps(sample.result))
    settings['historical_candidate_assessment'] = {'path': str(prior), 'sha256': hashlib.sha256(prior.read_bytes()).hexdigest()}
    (scratch / 'POLICY.json').write_text(json.dumps(settings))
    final.HERE = scratch

    def evaluate(rows, code=0, current_binding=binding):
        return final.assess(rows, code, sample.phase, sample.checks, run_binding=current_binding)

    result = evaluate(events)
    assert result['comparison_gate_passed'] and result['complete']
    assert len(result['rows']) == 98 and len(result['ends']) == 16
    for field, value in [('status', 'FAIL'), ('expected', 'FAIL'), ('message', 'changed'), ('known_intermittent', ['FAIL'])]:
        bad = copy.deepcopy(events)
        row = next(e for e in bad if (e.get('test'), e.get('subtest')) == known)
        row[field] = value
        assert not evaluate(bad)['comparison_gate_passed']
        rejected += 1
    bad = copy.deepcopy(events)
    row = next(e for e in bad if (e.get('test'), e.get('subtest')) == known)
    del row['known_intermittent']
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
    bad = copy.deepcopy(events)
    row = next(e for e in bad if e.get('action') == 'test_status' and (e['test'], e['subtest']) != known)
    row['expected'] = 'FAIL'
    assert not evaluate(bad)['comparison_gate_passed']
    rejected += 1
    for action in ['test_status', 'test_end']:
        bad = copy.deepcopy(events)
        del bad[next(i for i, e in enumerate(bad) if e.get('action') == action)]
        assert not evaluate(bad)['comparison_gate_passed']
        rejected += 1
    assert not evaluate(events, 1)['comparison_gate_passed']
    assert not evaluate(events, current_binding=dict(binding, browser_build_id='wrong'))['comparison_gate_passed']
    rejected += 2
    for mutation in ['status', 'duplicate', 'identity', 'intermittent']:
        historical = copy.deepcopy(sample.result)
        row = next(e for e in historical['rows'] if (e['test'], e['subtest']) == known)
        if mutation == 'status':
            row['status'] = 'FAIL'
        elif mutation == 'duplicate':
            historical['rows'].append(copy.deepcopy(row))
        elif mutation == 'identity':
            row['subtest'] += ' changed'
        else:
            del row['known_intermittent']
        prior.write_text(json.dumps(historical))
        altered = copy.deepcopy(settings)
        altered['historical_candidate_assessment']['sha256'] = hashlib.sha256(prior.read_bytes()).hexdigest()
        try:
            final.projected_candidate(altered)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError('Historical mutation accepted: ' + mutation)
print(json.dumps({'synthetic_final_accepts': 1, 'rejected_final_mutations': rejected,
                  'exact_signatures': 114, 'empty_intermittent_presence_retained': True,
                  'scratch_removed': True, 'actual_candidate_or_browser_result': False}))
