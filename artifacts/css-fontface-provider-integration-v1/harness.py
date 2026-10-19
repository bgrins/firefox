#!/usr/bin/env python3
"""Root-only run proposal: never installs sources or invokes a native build."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def load(path):
    return json.loads(path.read_text())

def authenticate():
    freeze = load(PACKAGE / 'FREEZE.json')
    assert digest(PACKAGE / 'INPUTS.json') == freeze['inputs_sha256']
    for rel, sha in load(PACKAGE / 'INPUTS.json').items():
        assert digest(PACKAGE / rel) == sha, rel

def snapshot(repo, phase):
    fixed = {rel: row['original' if phase == 'baseline' else 'candidate']
             for rel, row in load(PACKAGE / 'NATIVE-PINS.json').items()}
    for name in ['CONTEXT', 'RESOURCE', 'REGRESSION', 'METADATA', 'CONFIG']:
        fixed.update(load(PACKAGE / (name + '-PINS.json')))
    fixed.update({rel: row['proposed'] for rel, row in load(PACKAGE / 'TEST-PINS.json').items()})
    for rel, expected in fixed.items():
        actual = digest(repo / rel) if (repo / rel).exists() else None
        assert actual == expected, ('input mismatch', rel, expected, actual)
    run = load(PACKAGE / 'RUN.json')
    return {'phase': phase, 'fixed': fixed,
            'binaries': {rel: digest(repo / rel) for rel in run['binary_pins']},
            'mach_sha256': digest(repo / 'mach'),
            'python_sha256': digest(Path(run['python']).resolve()),
            'package_manifest_sha256': digest(PACKAGE / 'INPUTS.json')}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--phase', choices=['baseline', 'candidate'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--suite', choices=['matrix', 'regressions'], default='matrix')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--build-before', type=Path)
    parser.add_argument('--build-log', type=Path)
    parser.add_argument('--build-exit-code', type=int)
    args = parser.parse_args()
    authenticate()
    repo = args.repo.resolve()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    before = snapshot(repo, args.phase)
    (args.out / 'before.json').write_text(json.dumps(before, indent=2) + '\n')
    if not args.execute:
        print('Captured pins only; no browser or build command executed.')
        return
    assert args.build_before and args.build_log and args.build_exit_code == 0, 'successful root build receipt required'
    build_before = load(args.build_before)
    for key in ['phase', 'fixed', 'mach_sha256', 'python_sha256', 'package_manifest_sha256']:
        assert build_before[key] == before[key], ('build-to-run drift', key)
    run = load(PACKAGE / 'RUN.json')
    command = [run['python'], './mach', 'wpt', '--binary', run['binary'],
               '--headless', '--processes=1', '--log-raw', str(args.out / 'raw.jsonl')] + run[args.suite]
    start = time.time()
    with (args.out / 'console.log').open('wb') as log:
        result = subprocess.run(command, cwd=repo, stdout=log, stderr=subprocess.STDOUT)
    after = snapshot(repo, args.phase)
    (args.out / 'after.json').write_text(json.dumps(after, indent=2) + '\n')
    stable = before == after
    events = [json.loads(line) for line in (args.out / 'raw.jsonl').read_text().splitlines() if line.strip()]
    statuses = [e for e in events if e.get('action') == 'test_status']
    endings = [e for e in events if e.get('action') == 'test_end']
    complete = any(e.get('action') == 'suite_end' for e in events)
    exact_cases = None
    if args.suite == 'matrix':
        expected = load(PACKAGE / 'CASES.json')
        expected_pairs = Counter((run['case_key_to_id'][key], name) for key, names in expected.items() for name in names)
        actual_pairs = Counter((e['test'], e['subtest']) for e in statuses)
        exact_cases = actual_pairs == expected_pairs
        complete = complete and Counter(e['test'] for e in endings) == Counter(run['expected_test_ids'])
        complete = complete and all(e['status'] == 'OK' for e in endings) and exact_cases
    else:
        expected_ids = run['regression_expected_test_ids']
        complete = complete and Counter(e['test'] for e in endings) == Counter(expected_ids)
    valid = stable and complete and result.returncode in [0, 1]
    candidate_success = None
    if args.phase == 'candidate' and args.suite == 'matrix':
        candidate_success = valid and result.returncode == 0 and all(e['status'] == 'PASS' for e in statuses)
    receipt = {'phase': args.phase, 'suite': args.suite, 'command': command,
               'exit_code': result.returncode, 'elapsed_seconds': time.time() - start,
               'stable_pins': stable, 'complete': complete, 'exact_case_names': exact_cases,
               'valid_observation': valid, 'candidate_matrix_success': candidate_success,
               'counts': dict(Counter(e['status'] for e in statuses)),
               'harness_counts': dict(Counter(e['status'] for e in endings)),
               'statuses': [{k: e.get(k) for k in ['test', 'subtest', 'status', 'expected', 'message']} for e in statuses],
               'test_end': [{k: e.get(k) for k in ['test', 'status', 'expected', 'message']} for e in endings],
               'build': {'before_sha256': digest(args.build_before), 'log_sha256': digest(args.build_log),
                         'exit_code_attested_by_root': args.build_exit_code,
                         'note': 'Root must retain full build command/log; this harness does not run or infer build success.'},
               'files': {name: digest(args.out / name) for name in ['before.json', 'after.json', 'raw.jsonl', 'console.log']}}
    (args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['valid_observation', 'candidate_matrix_success', 'counts', 'harness_counts']}, indent=2))
    assert valid and candidate_success is not False, 'invalid or failing candidate run; inspect retained receipt'

if __name__ == '__main__':
    main()
