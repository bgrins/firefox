"""Called only after the entry-point package/dependency authentication."""
import hashlib
import json
from pathlib import Path
from collections import Counter

P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())


def verify_test_delta():
    wpt = P.parent / 'css-fontface-provider-wpt-v3'
    old = P.parent / 'css-fontface-provider-integration-v2'
    changes = load(wpt / 'TRANSFORMATION.json')
    old_pins = load(old / 'TEST-PINS.json')
    final_pins = load(P / 'TEST-PINS.json')
    delta = load(wpt / 'TEST-PINS.json')
    assert old_pins.keys() == final_pins.keys() == delta.keys()
    for rel, row in delta.items():
        assert old_pins[rel]['proposed'] == row['v2']
        assert final_pins[rel] == {**old_pins[rel], 'proposed': row['v3']}
        name = Path(rel).name
        original = (wpt / 'original' / name).read_text()
        assert sha(wpt / 'original' / name) == row['v2']
        assert sha(wpt / 'proposal' / name) == row['v3']
        assert original.count(changes['old_ternary']) == 1
        expected = original.replace(changes['old_ternary'], changes['new_ternary'])
        if name.endswith('.any.js'):
            marker = '// META: global=window,dedicatedworker\n'
            assert expected.count(marker) == 1
            expected = expected.replace(marker, marker + changes['added_js_metadata'])
        assert expected == (wpt / 'proposal' / name).read_text()
    return delta


def admit_build_snapshot(build_before, run_before):
    delta = verify_test_delta()
    metadata = verify_metadata_delta()
    previous = P.parent / 'css-fontface-provider-integration-v2'
    assert build_before['package_manifest_sha256'] == sha(previous / 'INPUTS.json'), 'requires actual v2 build snapshot'
    assert run_before['package_manifest_sha256'] == sha(P / 'INPUTS.json'), 'requires v3 final-run snapshot'
    for field in ['phase', 'mach_sha256', 'python_sha256']:
        assert build_before[field] == run_before[field], ('build-to-run drift', field)
    assert build_before['phase'] == 'candidate', 'final v3 admission is candidate-only'
    native = load(P / 'NATIVE-PINS.json')
    assert all(build_before['fixed'][name] == row['candidate'] for name, row in native.items())
    expected_final = dict(build_before['fixed'])
    for rel, row in delta.items():
        assert expected_final[rel] == row['v2'], ('wrong pre-build test bytes', rel)
        expected_final[rel] = row['v3']
    assert expected_final[metadata['path']] == metadata['v2_sha256']
    expected_final[metadata['path']] = None
    assert expected_final == run_before['fixed'], 'unexpected build-to-run input change'
    assert build_before['binaries'].keys() == run_before['binaries'].keys()
    return {
        'kind': 'ACTUAL_V2_PREBUILD_PLUS_VERIFIED_TEST_AND_EXPECTATION_DELTA',
        'build_snapshot_package': build_before['package_manifest_sha256'],
        'run_snapshot_package': run_before['package_manifest_sha256'],
        'test_changes': delta,
        'metadata_change': metadata,
        'native_and_all_other_fixed_pins_unchanged': True,
        'new_prebuild_snapshot_inferred': False,
        'binary_boundary': 'Build outputs may differ from pre-build binaries; final run pins are checked before and after WPT.',
        'build_success': 'Root must provide successful actual terminal status and full build log; no success inferred from snapshots.'
    }


def verify_metadata_delta():
    metadata = load(P / 'METADATA-DELTA.json')
    old = load(P.parent / 'css-fontface-provider-integration-v2/METADATA-PINS.json')
    assert old[metadata['path']] == metadata['v2_sha256']
    assert sha(P / 'metadata-original' / metadata['path']) == metadata['v2_sha256']
    expected = dict(old)
    expected[metadata['path']] = None
    assert expected == load(P / 'METADATA-PINS.json')
    assert metadata['v3_expected'] is None
    assert (P / 'metadata-original' / metadata['path']).read_text() == (
        '[fontface-descriptor-updates-2.html]\n'
        '  [Font matching uses updated style and family name]\n'
        '    expected: FAIL\n')
    return metadata


def final_regressions_match(statuses, endings, exit_code):
    metadata = verify_metadata_delta()
    reference = load(P / 'evidence/v2-candidate-regressions/receipt.json')
    expected_statuses = reference['statuses']
    changed = 0
    for row in expected_statuses:
        if (row['test'], row['subtest']) == (metadata['test'], metadata['subtest']):
            assert row['status'] == 'PASS' and row['expected'] == 'FAIL'
            row['expected'] = None
            changed += 1
    assert changed == 1
    project = lambda rows, fields: Counter(tuple(row.get(k) for k in fields) for row in rows)
    return (exit_code == 0
            and project(statuses, ['test', 'subtest', 'status', 'expected'])
            == project(expected_statuses, ['test', 'subtest', 'status', 'expected'])
            and project(endings, ['test', 'status', 'expected'])
            == project(reference['test_end'], ['test', 'status', 'expected'])
            and Counter(row['status'] for row in statuses) == {'PASS': 19}
            and Counter(row['status'] for row in endings) == {'PASS': 4, 'FAIL': 1, 'OK': 3})
