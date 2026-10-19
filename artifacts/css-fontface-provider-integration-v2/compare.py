#!/usr/bin/env python3
"""Compare authenticated v1 baseline and v2 candidate WPT records offline."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def authenticate():
    freeze = load(P / 'FREEZE.json')
    assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
    for name, expected in load(P / 'INPUTS.json').items():
        assert sha(P / name) == expected, name
    for name, pins in load(P / 'DEPENDENCIES.json').items():
        dep = P.parent / name
        assert sha(dep / 'FREEZE.json') == pins['freeze_sha256']
        assert sha(dep / 'INPUTS.json') == pins['inputs_sha256']
        for rel, expected in load(dep / 'INPUTS.json').items():
            assert sha(dep / rel) == expected, (name, rel)


def expected_fixed(phase):
    fixed = {rel: row['original' if phase == 'baseline' else 'candidate']
             for rel, row in load(P / 'NATIVE-PINS.json').items()}
    for group in ['CONTEXT', 'RESOURCE', 'REGRESSION', 'METADATA', 'CONFIG']:
        fixed.update(load(P / (group + '-PINS.json')))
    fixed.update({rel: row['proposed'] for rel, row in load(P / 'TEST-PINS.json').items()})
    return fixed


def read_run(directory, phase):
    receipt = load(directory / 'receipt.json')
    assert receipt['phase'] == phase and receipt['valid_observation'] is True
    assert receipt['exit_code'] in [0, 1] and receipt['build']['exit_code_attested_by_root'] == 0
    for name in ['before.json', 'after.json', 'raw.jsonl', 'console.log']:
        assert sha(directory / name) == receipt['files'][name], (directory, name)
    before, after = load(directory / 'before.json'), load(directory / 'after.json')
    assert before == after and before['phase'] == phase
    assert before['fixed'] == expected_fixed(phase), (directory, 'fixed pins')
    package = P.parent / 'css-fontface-provider-integration-v1' if phase == 'baseline' else P
    assert before['package_manifest_sha256'] == sha(package / 'INPUTS.json')
    run = load(P / 'RUN.json')
    assert set(before['binaries']) == set(run['binary_pins'])
    suite = receipt['suite']
    assert suite in ['matrix', 'regressions']
    command = receipt['command']
    expected = [run['python'], './mach', 'wpt', '--binary', run['binary'],
                '--headless', '--processes=1', '--log-raw', command[8]] + run[suite]
    assert command == expected
    assert Path(command[8]).name == 'raw.jsonl'
    events = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines() if line.strip()]
    assert any(e.get('action') == 'suite_end' for e in events)
    statuses = [e for e in events if e.get('action') == 'test_status']
    endings = [e for e in events if e.get('action') == 'test_end']
    fields = ['test', 'subtest', 'status', 'expected', 'message']
    assert [{k: e.get(k) for k in fields} for e in statuses] == receipt['statuses']
    assert [{k: e.get(k) for k in fields if k != 'subtest'} for e in endings] == receipt['test_end']
    expected_ids = run['expected_test_ids' if suite == 'matrix' else 'regression_expected_test_ids']
    assert Counter(e['test'] for e in endings) == Counter(expected_ids)
    assert dict(Counter(e['status'] for e in statuses)) == receipt['counts']
    assert dict(Counter(e['status'] for e in endings)) == receipt['harness_counts']
    if suite == 'matrix':
        cases = load(P / 'CASES.json')
        expected_pairs = Counter((run['case_key_to_id'][key], name) for key, names in cases.items() for name in names)
        assert Counter((e['test'], e['subtest']) for e in statuses) == expected_pairs
        assert all(e['status'] == 'OK' for e in endings)
    rows = {}
    for kind, values in [('subtest', statuses), ('harness', endings)]:
        for e in values:
            key = (kind, e['test'], e.get('subtest'))
            assert key not in rows, ('duplicate result', key)
            rows[key] = {k: e.get(k) for k in fields}
    return receipt, before, rows


def compare(baseline, candidate):
    left, lb, lr = read_run(baseline, 'baseline')
    right, rb, rr = read_run(candidate, 'candidate')
    assert left['suite'] == right['suite'] and lr.keys() == rr.keys()
    for field in ['mach_sha256', 'python_sha256']:
        assert lb[field] == rb[field], field
    native = set(load(P / 'NATIVE-PINS.json'))
    changed = sorted(k for k in lb['fixed'] if lb['fixed'][k] != rb['fixed'][k])
    assert set(changed) <= native
    transitions, unchanged = [], 0
    for key in lr:
        a, b = lr[key], rr[key]
        if (a['status'], a['expected']) == (b['status'], b['expected']):
            unchanged += 1
            continue
        passed = {'PASS', 'OK'}
        classification = ('improvement' if a['status'] not in passed and b['status'] in passed
                          else 'regression' if a['status'] in passed and b['status'] not in passed
                          else 'changed_result_review_required')
        transitions.append({'identity': list(key), 'classification': classification,
                            'baseline': a, 'candidate': b})
    matrix_pass = None
    if left['suite'] == 'matrix':
        matrix_pass = right['exit_code'] == 0 and all(e['status'] in ['PASS', 'OK'] for e in rr.values())
    return {'status': 'VALID_PAIRED_OBSERVATIONS', 'suite': left['suite'],
            'baseline_receipt_sha256': sha(baseline / 'receipt.json'),
            'candidate_receipt_sha256': sha(candidate / 'receipt.json'),
            'rows': len(lr), 'unchanged_status_expected_tuples': unchanged,
            'transitions': transitions, 'changed_native_files': changed,
            'changed_binaries': [k for k in lb['binaries'] if lb['binaries'][k] != rb['binaries'][k]],
            'candidate_matrix_all_pass': matrix_pass,
            'regression_or_unclassified_change': any(t['classification'] != 'improvement' for t in transitions),
            'build_boundary': 'Recorded successful root build attestation and hashes; full build logs/terminal provenance require root review.',
            'runtime_acceptance': 'Not implied; inspect transitions and outstanding platform/lifetime gates.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    authenticate()
    if args.candidate:
        result = compare(args.baseline, args.candidate)
    else:
        receipt, snapshot, rows = read_run(args.baseline, 'baseline')
        result = {'status': 'VALID_BASELINE_ONLY', 'suite': receipt['suite'], 'rows': len(rows),
                  'counts': receipt['counts'], 'harness_counts': receipt['harness_counts'],
                  'receipt_sha256': sha(args.baseline / 'receipt.json'), 'candidate_executed': False}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'transitions'}, indent=2))


if __name__ == '__main__':
    main()
