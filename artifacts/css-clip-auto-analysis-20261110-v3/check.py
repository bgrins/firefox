import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    source = json.loads((HERE / 'SOURCE-ONLY.json').read_text())
    raw = json.loads((HERE / 'RAW-INPUTS.json').read_text())
    for name, expected in source.items():
        assert digest(HERE / name) == expected, name
    for name, expected in raw.items():
        assert digest(args.evidence / name) == expected, name
    args.out.mkdir(parents=True, exist_ok=False)
    current = module('current_analysis', HERE / 'analyze.py')
    prior = module('prior_analysis', HERE / 'origin/analyze.py')
    synthetic = module('parser_controls', HERE / 'parser-controls.py').main()
    assert len(synthetic['rejected_controls']) == 25
    results = {}
    for variant in ['baseline1', 'candidate1']:
        results[variant] = {
            flavor: current.parse(args.evidence / variant / (flavor + '-raw.jsonl'), flavor)
            for flavor in ['wpt', 'mochitest']
        }
        saved = json.loads((args.evidence / variant / 'TEST-RESULTS.json').read_text())
        assert results[variant] == saved, variant
    baseline, candidate = results['baseline1'], results['candidate1']
    current.baseline_check(baseline)
    comparison = current.compare(baseline, candidate)
    assert comparison['gate_passed']
    assert comparison['baseline_rows'] == comparison['candidate_rows'] == 5116
    assert comparison['svg_observation_count'] == 12
    assert comparison['mochitest_messages_unchanged']
    assert len(comparison['changes']) == 4
    first = [row for row in candidate['mochitest']['subtests'] if row['occurrence'] == 0]
    assert len(first) == 4 and all(row['subtest'] is None for row in first)
    controls = []
    for original in first:
        changed = copy.deepcopy(candidate)
        row = next(r for r in changed['mochitest']['subtests']
                   if r['test'] == original['test'] and r['occurrence'] == 0)
        assert row['status'] == 'PASS'
        row['status'] = 'FAIL'
        assert prior.compare(baseline, changed)['gate_passed']
        assert not current.compare(baseline, changed)['gate_passed']
        controls.append(['first-callback-status', original['test']])
        changed['mochitest']['subtests'].remove(row)
        assert prior.compare(baseline, changed)['gate_passed']
        assert not current.compare(baseline, changed)['gate_passed']
        controls.append(['first-callback-missing', original['test']])
        changed = copy.deepcopy(candidate)
        row = next(r for r in changed['mochitest']['subtests']
                   if r['test'] == original['test'] and r['occurrence'] == 0)
        row['message'] += ' changed assertion'
        assert prior.compare(baseline, changed)['gate_passed']
        assert not current.compare(baseline, changed)['gate_passed']
        controls.append(['first-callback-label', original['test']])
    for field in ['subtests', 'harness']:
        changed = copy.deepcopy(candidate)
        changed['mochitest'][field].append(copy.deepcopy(changed['mochitest'][field][0]))
        assert prior.compare(baseline, changed)['gate_passed']
        try:
            current.compare(baseline, changed)
        except AssertionError as error:
            assert error.args[0][0] == 'duplicate result identity'
        else:
            raise AssertionError('Duplicate parsed record accepted')
        controls.append(['duplicate-parsed-record', field])
    for name, expected in source.items():
        assert digest(HERE / name) == expected, name
    for name, expected in raw.items():
        assert digest(args.evidence / name) == expected, name
    report = {
        'status': 'pass', 'source_sha256': source, 'raw_sha256': raw,
        'comparison': comparison, 'parser_controls': synthetic,
        'regression_controls': controls, 'browser_tests_executed': False,
        'original_parsed_results_unchanged': True,
        'assertion_and_harness_keys_distinct': True,
    }
    (args.out / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: 5116 rows, 25 parser controls, {len(controls)} collision/label controls')


if __name__ == '__main__':
    main()
