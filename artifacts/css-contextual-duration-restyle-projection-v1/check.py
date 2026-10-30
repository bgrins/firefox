import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


read = lambda p: json.loads(p.read_bytes())
module = load('restyle_projection', HERE / 'project.py')
base = load('restyle_assessor', ROOT / 'artifacts/css-contextual-duration-broader-candidate-v4/restyles.py')
policy = read(ROOT / 'artifacts/css-contextual-duration-broader-candidate-v4/POLICY.json')
checks = load('restyle_checks', ROOT / policy['wpt']['checks_helper'])
original_dir = ROOT / policy['restyle_baseline']['directory']
candidate_dir = ROOT / 'artifacts/css-contextual-duration-broader-candidate-runtime-1/restyles'
observed = []
for path in (original_dir, candidate_dir):
    events = [json.loads(line) for line in (path / 'raw.jsonl').read_text().splitlines()]
    observed.append(base.assess(events, read(path / 'RESULT.json')['exit'], checks))
original, candidate = observed
assert candidate == read(candidate_dir / 'ASSESSMENT.json')
assert [i for i, (a, b) in enumerate(zip(original['assertions'], candidate['assertions'])) if a != b] == list(module.TEMPLATES)
before = copy.deepcopy(observed)
assert module.compare(original, candidate)
assert observed == before
negative = []


def reject(label, mutate):
    changed = copy.deepcopy(candidate)
    mutate(changed)
    try:
        accepted = module.compare(original, changed)
    except (AssertionError, ValueError, TypeError, KeyError):
        accepted = False
    assert not accepted, label
    negative.append(label)


for index in module.TEMPLATES:
    def message(a, before, after):
        a['assertions'][index]['message'] = a['assertions'][index]['message'].replace(before, after)
    reject(f'{index}: status', lambda a: a['assertions'][index].update(status='FAIL'))
    reject(f'{index}: threshold', lambda a: message(a, '200ms', '100ms'))
    reject(f'{index}: expected presence', lambda a: a['assertions'][index].update(expected='PASS', expected_field_present=True))
    reject(f'{index}: intermittent field', lambda a: a['assertions'][index].update(known_intermittent=[]))
    reject(f'{index}: NaN', lambda a: message(a, 'now: ', 'now: NaN'))
    reject(f'{index}: negative time', lambda a: message(a, 'now: ', 'now: -'))
    reject(f'{index}: extra diagnostic', lambda a: a['assertions'][index].update(message=a['assertions'][index]['message'] + ' ERROR'))
    gap = '' if index in (24, 27) else ' '
    reject(f'{index}: arithmetic mismatch', lambda a: a['assertions'][index].update(message=module.TEMPLATES[index] + ' now: 1000 start time: 500 elapsed:' + gap + '200'))
reject('unrelated assertion message', lambda a: a['assertions'][10].update(message='changed'))
reject('ending status', lambda a: a['ending'].update(status='FAIL'))
reject('assertion order', lambda a: a['assertions'].__setitem__(slice(24,26), list(reversed(a['assertions'][24:26]))))
print(json.dumps({'saved_raw_assessments_replayed': True, 'raw_assessments_unchanged': observed == before, 'exact_differing_indices': list(module.TEMPLATES), 'projected_comparison_passed': True, 'negative_controls': negative, 'browser_or_native_execution': False}, indent=2))
