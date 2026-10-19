#!/usr/bin/env python3
import ast
from collections import Counter
from copy import deepcopy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())


def main():
    freeze = load(P / 'FREEZE.json')
    assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
    inputs = load(P / 'INPUTS.json')
    assert len(inputs) == freeze['entries']
    for rel, expected in inputs.items():
        assert sha(P / rel) == expected, rel
    for name, pins in load(P / 'DEPENDENCIES.json').items():
        dep = P.parent / name
        assert sha(dep / 'FREEZE.json') == pins['freeze_sha256']
        assert sha(dep / 'INPUTS.json') == pins['inputs_sha256']
        for rel, expected in load(dep / 'INPUTS.json').items():
            assert sha(dep / rel) == expected, (name, rel)
    base = P.parent / 'css-fontface-provider-integration-v2'
    wpt = P.parent / 'css-fontface-provider-wpt-v3'
    adaptation = load(P / 'HARNESS-ADAPTATION.json')
    assert sha(base / 'harness.py') == adaptation['v2_harness_sha256']
    expected = (base / 'harness.py').read_text()
    for row in adaptation['replacements']:
        assert expected.count(row['old']) == 1
        expected = expected.replace(row['old'], row['new'])
    assert expected == (P / 'harness.py').read_text()
    for name in ['NATIVE-PINS.json', 'CONTEXT-PINS.json', 'RESOURCE-PINS.json',
                 'REGRESSION-PINS.json', 'CONFIG-PINS.json',
                 'CASES.json', 'RUN.json']:
        assert (P / name).read_bytes() == (base / name).read_bytes(), name
    for name in ['check.py', 'harness.py', 'admission.py']:
        ast.parse((P / name).read_text())
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('verified_admission', P / 'admission.py')
    admission = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(admission)
    delta = admission.verify_test_delta()
    metadata = admission.verify_metadata_delta()
    old_metadata = P / 'metadata-original' / metadata['path']
    patch = ''.join(difflib.unified_diff(old_metadata.read_text().splitlines(True), [],
                                       fromfile='a/' + metadata['path'], tofile='/dev/null'))
    assert patch == (P / 'metadata-removal.patch').read_text()
    with tempfile.TemporaryDirectory(prefix='metadata-check-', dir=P) as temp:
        tree = Path(temp)
        target = tree / metadata['path']
        target.parent.mkdir(parents=True)
        target.write_bytes(old_metadata.read_bytes())
        argv = ['patch', '--batch', '--fuzz=0', '-E', '-p1', '-i', str(P / 'metadata-removal.patch')]
        result = subprocess.run(argv, cwd=tree, capture_output=True, text=True)
        assert result.returncode == 0, (result.stdout, result.stderr)
        assert not target.exists()
    evidence = P / 'evidence/v2-build-before.json'
    assert sha(evidence) == load(P / 'EVIDENCE.json')['sha256']
    before = load(evidence)
    fixed = {name: row['candidate'] for name, row in load(P / 'NATIVE-PINS.json').items()}
    for group in ['CONTEXT', 'RESOURCE', 'REGRESSION', 'METADATA', 'CONFIG']:
        fixed.update(load(base / (group + '-PINS.json')))
    fixed.update({name: row['proposed'] for name, row in load(base / 'TEST-PINS.json').items()})
    assert before['fixed'] == fixed
    proposed_run = deepcopy(before)
    proposed_run['package_manifest_sha256'] = sha(P / 'INPUTS.json')
    for rel, row in delta.items():
        proposed_run['fixed'][rel] = row['v3']
    proposed_run['fixed'][metadata['path']] = None
    positive = admission.admit_build_snapshot(before, proposed_run)
    assert positive['new_prebuild_snapshot_inferred'] is False
    rejected = []
    def must_reject(name, left, right):
        try:
            admission.admit_build_snapshot(left, right)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(('unexpected admission', name))
    bad = deepcopy(proposed_run)
    bad['fixed'][next(iter(load(P / 'NATIVE-PINS.json')))] = 'changed'
    must_reject('native drift', before, bad)
    bad = deepcopy(proposed_run)
    bad['fixed'][next(iter(load(P / 'CONFIG-PINS.json')))] = 'changed'
    must_reject('configuration drift', before, bad)
    bad = deepcopy(proposed_run)
    first_test = next(iter(delta))
    bad['fixed'][first_test] = delta[first_test]['v2']
    must_reject('uninstalled v3 test', before, bad)
    bad = deepcopy(before)
    bad['fixed'][first_test] = delta[first_test]['v3']
    must_reject('post-edit snapshot mislabeled pre-build', bad, proposed_run)
    bad = deepcopy(before)
    bad['package_manifest_sha256'] = sha(P / 'INPUTS.json')
    must_reject('v3 snapshot substituted for actual v2 build snapshot', bad, proposed_run)
    bad = deepcopy(proposed_run)
    bad['mach_sha256'] = 'changed'
    must_reject('Mach drift', before, bad)
    bad = deepcopy(proposed_run)
    bad['fixed'][metadata['path']] = metadata['v2_sha256']
    must_reject('stale FAIL expectation retained', before, bad)
    observed = {}
    for phase in ['baseline', 'candidate']:
        directory = P / 'evidence' / ('v2-' + phase + '-regressions')
        receipt = load(directory / 'receipt.json')
        for name in ['before.json', 'after.json', 'raw.jsonl']:
            assert sha(directory / name) == receipt['files'][name]
        assert load(directory / 'before.json') == load(directory / 'after.json')
        assert receipt['valid_observation'] and receipt['stable_pins']
        raw = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines() if line.strip()]
        rows = [e for e in raw if e.get('action') == 'test_status']
        assert [{k: e.get(k) for k in ['test', 'subtest', 'status', 'expected', 'message']} for e in rows] == receipt['statuses']
        observed[phase] = receipt
    identities = lambda rows: {(r['test'], r['subtest']): (r['status'], r['expected']) for r in rows}
    old_rows = identities(observed['baseline']['statuses'])
    new_rows = identities(observed['candidate']['statuses'])
    assert old_rows.keys() == new_rows.keys()
    target_key = (metadata['test'], metadata['subtest'])
    assert old_rows[target_key] == ('FAIL', None) and new_rows[target_key] == ('PASS', 'FAIL')
    assert [k for k in old_rows if old_rows[k] != new_rows[k]] == [target_key]
    ending_tuples = lambda rows: Counter((r['test'], r['status'], r['expected']) for r in rows)
    assert ending_tuples(observed['baseline']['test_end']) == ending_tuples(observed['candidate']['test_end'])
    expected_final_rows = deepcopy(observed['candidate']['statuses'])
    for row in expected_final_rows:
        if (row['test'], row['subtest']) == target_key:
            row['expected'] = None
    assert admission.final_regressions_match(expected_final_rows, observed['candidate']['test_end'], 0)
    assert not admission.final_regressions_match(expected_final_rows, observed['candidate']['test_end'], 1)
    assert not admission.final_regressions_match(observed['candidate']['statuses'], observed['candidate']['test_end'], 0)
    replays = {}
    for dep in [base, wpt]:
        run = subprocess.run([sys.executable, str(dep / 'check.py')], capture_output=True, text=True)
        assert run.returncode == 0, (dep.name, run.stdout, run.stderr)
        replays[dep.name] = json.loads(run.stdout)
    print(json.dumps({'status': 'PASS_SOURCE_ONLY', 'inputs': len(inputs),
                      'actual_v2_prebuild_sha256': sha(evidence),
                      'test_and_metadata_admission_checked': True, 'rejected_drift_controls': rejected,
                      'derived_run_for_check_only': True, 'new_prebuild_snapshot_created': False,
                      'metadata_removal_applied': True, 'original_metadata_bytes_retained': True,
                      'observed_v2_regression_improvement': list(target_key),
                      'final_regression_contract': '19 PASS + 4 PASS / 1 expected FAIL / 3 OK; exit zero; all other tuples identical',
                      'exact_cases': [12, 28, 28], 'dependency_replays': replays,
                      'build_or_browser_run': False}, indent=2))


if __name__ == '__main__':
    main()
