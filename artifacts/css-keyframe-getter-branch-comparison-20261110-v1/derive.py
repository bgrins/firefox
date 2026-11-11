import hashlib
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def derive():
    origins = json.loads((HERE / 'ORIGINS.json').read_text())
    for category in ['authenticated_files', 'frozen_files']:
        for name, digest in origins[category].items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    parsed, evidence = [], []
    for kind, key in [('ordinary', 'ordinary_evidence'), ('branch', 'branch_evidence')]:
        directory = ROOT / origins[key]
        spec = importlib.util.spec_from_file_location(kind + '_analyzer', directory / 'analyze.py')
        analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyzer)
        actual = analyzer.parse(directory / 'baseline1/wpt-raw.jsonl')
        assert actual == json.loads((directory / 'baseline1/TEST-RESULTS.json').read_text())
        receipt = json.loads((directory / 'baseline1/RESULT.json').read_text())
        restored = json.loads((directory / 'baseline1/RESTORED.json').read_text())
        assert receipt['mode'] == 'baseline' and receipt['error'] is None and receipt['restoration_verified']
        assert receipt['commands']['lint']['exit_code'] == 0
        assert receipt['commands']['wpt']['exit_code'] in (0, 1)
        assert receipt['commands']['lint']['group_absent'] and receipt['commands']['wpt']['group_absent']
        assert restored['source_and_application_restored'] and restored['index_preserved'] and restored['backup_removed']
        assert receipt['runner_inputs_sha256'] == hashlib.sha256((directory / 'RUN-INPUTS.json').read_bytes()).hexdigest()
        if kind == 'ordinary':
            candidate = analyzer.parse(directory / 'candidate1/wpt-raw.jsonl')
            assert candidate == json.loads((directory / 'candidate1/TEST-RESULTS.json').read_text())
            done = json.loads((directory / 'candidate1/RESULT.json').read_text())
            assert done['error'] is None and done['restoration_verified']
            assert done['commands']['build']['exit_code'] == 0 and done['commands']['build']['group_absent']
            assert done['commands']['wpt']['exit_code'] in (0, 1) and done['commands']['wpt']['group_absent']
            assert done['comparison']['accepted_changes_only'] and analyzer.compare(actual, candidate)['accepted_changes_only']
            assert json.loads((directory / 'candidate1/RESTORED.json').read_text())['source_and_application_restored']
        parsed.append(actual)
        evidence.append(dict(kind=kind, directory=origins[key], raw_sha256=hashlib.sha256((directory / 'baseline1/wpt-raw.jsonl').read_bytes()).hexdigest(),
            records=len(actual['subtests']) + len(actual['harness']), use='preserved historical evidence; not a new run'))
    result = {field: sorted(parsed[0][field] + parsed[1][field], key=repr) for field in ['subtests', 'harness']}
    result.update(subtest_count=len(result['subtests']), test_count=len(result['harness']))
    assert len({(r['test'], r['subtest']) for r in result['subtests']}) == result['subtest_count']
    assert len({r['test'] for r in result['harness']}) == result['test_count']
    return result, evidence


def prediction(base):
    url = '/css/css-animations/getkeyframes-specified-branch.html'
    target = [row for row in base['subtests'] if row['test'] == url and row['status'] == 'FAIL']
    assert len(target) == 3
    control = next(row for row in base['subtests'] if row['test'] == url
                   and row['subtest'] == 'WAAPI keyframes preserve specified variable expressions')
    assert control['status'] == 'PASS'
    keys = {(row['test'], row['subtest']) for row in target}
    result = copy.deepcopy(base)
    for index, row in enumerate(result['subtests']):
        if (row['test'], row['subtest']) in keys:
            result['subtests'][index] = {**control, 'subtest': row['subtest']}
    changes = sorted([{'kind': 'assertion', 'test': row['test'], 'subtest': row['subtest'],
                       'baseline': 'FAIL', 'candidate': 'PASS'} for row in target],
                     key=lambda row: repr((row['kind'], row['test'], row['subtest'])))
    return result, changes


if __name__ == '__main__':
    baseline, evidence = derive()
    for name, value in [('EXPECTED-BASELINE.json', baseline), ('EXPECTED-CALLBACKS.json', sorted([[r['test'], r['subtest']] for r in baseline['subtests']], key=repr)), ('EXPECTED-DERIVATION.json', evidence)]:
        assert not (HERE / name).exists()
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
