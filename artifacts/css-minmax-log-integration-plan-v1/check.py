import copy
import difflib
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def apply_context(source, patch):
    chunks = re.split(r'^@@[^\n]*\n', patch, flags=re.M)[1:]
    assert chunks
    for chunk in chunks:
        lines = chunk.splitlines(True)
        old = ''.join(line[1:] for line in lines if line.startswith((' ', '-')))
        new = ''.join(line[1:] for line in lines if line.startswith((' ', '+')))
        assert old and source.count(old) == 1
        source = source.replace(old, new, 1)
    return source


def derive():
    base_path = ROOT / 'artifacts/css-pow-special-value-proposal-v1/candidate/servo/components/style/values/generics/calc.rs'
    minmax_path = ROOT / 'artifacts/css-minmax-relative-infinity-proposal-v2/candidate-calc.rs'
    log_path = ROOT / 'artifacts/css-log-clear-candidate-v1/candidate-calc.rs'
    minmax_patch = (ROOT / 'artifacts/css-minmax-relative-infinity-proposal-v2/native.patch').read_text()
    log_patch = (ROOT / 'artifacts/css-log-clear-special-values-proposal-v1/native.patch').read_text()
    base = base_path.read_text()
    assert sha(base_path) == 'b291d6e9a30e486fd42ff0cb3cda00cfead0ee7f7149761d8685a8cc85889576'
    assert sha(minmax_path) == '065c05d8c9fee140c07a7ef68841c95a6339ca66021c72122fc8832b136e0103'
    assert sha(log_path) == '7fbbd668ac096686b2ef77a7226cf44decd4295a8435b266519491ec978c5388'
    minmax = apply_context(base, minmax_patch)
    log = apply_context(base, log_patch)
    assert minmax == minmax_path.read_text() and log == log_path.read_text()
    combined = apply_context(minmax, log_patch)
    assert combined == apply_context(log, minmax_patch)
    return base, minmax, combined


def check():
    plan = read(HERE / 'PLAN.json')
    for name, record in plan['references'].items():
        assert sha(ROOT / name) == record['sha256'], name
    base, minmax, combined = derive()
    assert (HERE / 'candidate-calc.rs').read_text() == combined
    assert sha(HERE / 'candidate-calc.rs') == plan['combined_source_sha256']
    assert apply_context(base, (HERE / 'native.patch').read_text()) == combined
    assert apply_context(minmax, (HERE / 'log-after-minmax.patch').read_text()) == combined
    policies = [read(ROOT / n)['wpt'] for n in plan['input_policies']]
    pages = [set(p['expected_subtests']) for p in policies]
    assert not pages[0] & pages[1]
    roster = read(HERE / 'ROSTER.json')
    assert roster['expected_subtests'] == {page:names for p in policies for page,names in p['expected_subtests'].items()}
    assert roster['target_subtests'] == {page:names for p in policies for page,names in p['target_subtests'].items()}
    assert len(roster['expected_subtests']) == 15
    assert sum(map(len, roster['expected_subtests'].values())) == 574
    assert sum(map(len, roster['target_subtests'].values())) == 29
    assert sum(map(len, roster['control_subtests'].values())) == 545
    for page,names in roster['expected_subtests'].items():
        targets = set(roster['target_subtests'].get(page, []))
        controls = set(roster['control_subtests'][page])
        assert len(set(names)) == len(names)
        assert targets.isdisjoint(controls) and targets | controls == set(names)
    inputs = read(HERE / 'INPUTS.json')
    for group in ('resources', 'metadata'):
        for name, record in inputs[group].items():
            if record['sha256'] is not None:
                assert sha(ROOT / record['path']) == record['sha256']
            originals = [p[group][name] for p in policies if name in p[group]]
            assert all(item['sha256'] == record['sha256'] for item in originals)
    manifest = read(HERE / 'SUBSET-MANIFEST.json')
    assert set(manifest['items']['testharness']['css']['css-values']) == {Path(page).name for page in roster['expected_subtests']}
    assert sum(len(roster['expected_subtests'][page]) for page in roster['candidate_required_pass_pages']) == 56
    return {'patches_commute_exactly':True, 'combined_source_sha256':plan['combined_source_sha256'],
            'disjoint_pages':15, 'predicted_callbacks':574, 'targets':29, 'controls':545,
            'predicted_control_ending_signatures':560, 'authored_callbacks':56,
            'fresh_combined_run_required':True, 'combined_browser_or_build_executed':False}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2, sort_keys=True))
