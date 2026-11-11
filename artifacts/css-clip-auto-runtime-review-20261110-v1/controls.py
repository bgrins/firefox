import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAP = HERE.parent / 'css-clip-auto-runtime-20261110-v2'


def rows(result):
    return {(flavor, kind, row['test'], row.get('subtest'), row.get('occurrence', 0)): row['status']
            for flavor, group in result.items()
            for kind in ['subtests', 'harness'] for row in group[kind]}


def main():
    namespace = {'__file__': str(CAP / 'analyze.py'), '__name__': 'frozen_analyzer_review'}
    exec(compile((CAP / 'analyze.py').read_text(), str(CAP / 'analyze.py'), 'exec'), namespace)
    baseline = json.loads((CAP / 'baseline1/TEST-RESULTS.json').read_text())
    candidate = json.loads((CAP / 'candidate1/TEST-RESULTS.json').read_text())
    left, right = rows(baseline), rows(candidate)
    assert len(left) == len(right) == 5116 and left.keys() == right.keys()
    intended = {key: (left[key], right[key]) for key in left if left[key] != right[key]}
    assert len(intended) == 4 and all(pair == ('FAIL', 'PASS') for pair in intended.values())
    assert namespace['compare'](baseline, candidate)['gate_passed']
    controls = []
    first = [r for r in candidate['mochitest']['subtests'] if r['occurrence'] == 0]
    assert len(first) == 4 and all(r['subtest'] is None and r['status'] == 'PASS' for r in first)
    for original in first:
        mutated = copy.deepcopy(candidate)
        record = next(r for r in mutated['mochitest']['subtests']
                      if r['test'] == original['test'] and r['occurrence'] == 0)
        record['status'] = 'FAIL'
        assert namespace['compare'](baseline, mutated)['gate_passed'], 'collision reproducer changed'
        changed = rows(mutated)
        differences = {key: (left[key], changed[key]) for key in left if left[key] != changed[key]}
        assert len(differences) == 5 and differences != intended
        controls.append({'test': original['test'], 'first_callback_message': original['message'],
                         'actual_baseline_status': 'PASS', 'actual_candidate_status': 'PASS',
                         'synthetic_change': 'PASS to FAIL', 'frozen_compare_incorrectly_accepts': True,
                         'kind_tagged_compare_rejects': True})
    (HERE / 'CONTROLS.json').write_text(json.dumps({
        'status': 'pass', 'scope': 'Synthetic mutation of completed parsed receipts; no browser rerun',
        'controls': controls, 'actual_rows_with_kind_tags': 5116,
        'author_rows_without_kind_tags': 5112}, indent=2) + '\n')
    print('PASS: four frozen-analyzer collision reproductions; four corrected-comparison rejections')


if __name__ == '__main__':
    main()
