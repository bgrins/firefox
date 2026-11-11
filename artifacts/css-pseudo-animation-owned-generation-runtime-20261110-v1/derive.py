import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def derive():
    origins = json.loads((HERE / 'ORIGINS.json').read_text())
    for name, digest in origins['authenticated_files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    parsed = []
    receipts = []
    for key in ['range_evidence', 'snapshot_evidence']:
        directory = ROOT / origins[key]
        spec = importlib.util.spec_from_file_location(key, directory / 'analyze.py')
        analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyzer)
        actual = analyzer.parse(directory / 'candidate1/wpt-raw.jsonl')
        assert actual == json.loads((directory / 'candidate1/TEST-RESULTS.json').read_text())
        receipt = json.loads((directory / 'candidate1/RESULT.json').read_text())
        restored = json.loads((directory / 'candidate1/RESTORED.json').read_text())
        assert receipt['error'] is None and receipt['restoration_verified']
        assert receipt['commands']['build']['exit_code'] == 0
        assert receipt['commands']['wpt']['exit_code'] in [0, 1]
        if key == 'range_evidence':
            assert receipt['comparison']['accepted_changes_only']
        else:
            assert receipt['comparison']['identical_callback_statuses_and_inventory']
            assert receipt['comparison']['changes'] == []
        assert restored['source_and_application_restored'] and restored['backup_removed']
        parsed.append(actual)
        receipts.append({'directory': origins[key], 'raw_sha256': origins['authenticated_files'][origins[key] + '/candidate1/wpt-raw.jsonl'], 'rows': len(actual['subtests']) + len(actual['harness'])})
    fixtures = json.loads((HERE / 'RUN-PLAN.json').read_text())['fixtures']
    urls = {'/' + name.removeprefix('testing/web-platform/tests/') for name in fixtures}
    result = {field: sorted(parsed[0][field] + [r for r in parsed[1][field] if r['test'] in urls], key=repr) for field in ['subtests', 'harness']}
    result.update(subtest_count=len(result['subtests']), test_count=len(result['harness']))
    assert len({(r['test'], r['subtest']) for r in result['subtests']}) == result['subtest_count']
    assert len({r['test'] for r in result['harness']}) == result['test_count']
    return result, receipts


if __name__ == '__main__':
    baseline, receipts = derive()
    for name, value in [('EXPECTED-BASELINE.json', baseline), ('EXPECTED-CALLBACKS.json', sorted([[r['test'], r['subtest']] for r in baseline['subtests']], key=repr)), ('EXPECTED-DERIVATION.json', receipts)]:
        assert not (HERE / name).exists()
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
