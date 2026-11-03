import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-root-self-animation-candidate-browser-v1'
RUNTIME = ROOT / 'artifacts/css-root-self-animation-candidate-browser-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, expected):
    assert sha(directory / 'FILES.json') == expected
    manifest = read(directory / 'FILES.json')
    for name, record in manifest.get('files', manifest).items():
        assert (directory / name).is_file() and not (directory / name).is_symlink()
        assert sha(directory / name) == (record if isinstance(record, str) else record['sha256'])
        if isinstance(record, dict):
            assert (directory / name).stat().st_size == record['bytes']


def compare_signatures(baseline, rows, ends):
    key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
    old = {key(row): row for row in baseline['rows'] + baseline['ends']}
    new = {key(row): row for row in rows + ends}
    assert len(rows) == len(baseline['rows']) == 61
    assert len(ends) == len(baseline['ends']) == 5
    assert len(old) == len(new) == 66 and set(old) == set(new)
    assert all(row['status'] == 'PASS' for row in rows)
    assert all(row['status'] == 'OK' for row in ends)
    preserved = [identity for identity, row in old.items() if row['status'] == 'PASS' or row['kind'] == 'test_end']
    assert len(preserved) == 59 and all(old[identity] == new[identity] for identity in preserved)
    differences = [{'identity': identity, 'original': old[identity], 'candidate': new[identity]} for identity in sorted(old) if old[identity] != new[identity]]
    assert len(differences) == 7
    assert all(row['original']['status'] == 'FAIL' and row['candidate']['status'] == 'PASS' for row in differences)
    assert Counter(row['candidate']['test'] for row in differences) == Counter({
        '/web-animations/animation-model/keyframe-effects/root-font-self-reference.html': 7,
    })
    return {'comparison_passed': True, 'candidate_pass': 61, 'preserved_pass_signatures': 54,
            'preserved_ending_signatures': 5, 'fail_to_pass': 7, 'differences': differences}


def main():
    bindings = read(HERE / 'BINDINGS.json')
    assert bindings['execution_enabled'], 'comparison disabled pending actual terminal evidence'
    assert bindings['owner_directory'] == str(OWNER.relative_to(ROOT))
    assert bindings['runtime_directory'] == str(RUNTIME.relative_to(ROOT))
    assert bindings['owner_manifest'] and bindings['runtime_manifest']
    assert all(bindings[key] for key in ('owner_terminal', 'owner_result', 'build_result', 'restoration'))
    authenticate(OWNER, bindings['owner_manifest'])
    authenticate(RUNTIME, bindings['runtime_manifest'])
    authenticate(ROOT / bindings['baseline']['directory'], bindings['baseline']['manifest_sha256'])
    assert sha(ROOT / bindings['baseline']['path']) == bindings['baseline']['sha256']
    for key in ('owner_terminal', 'owner_result', 'build_result', 'restoration'):
        record = bindings[key]
        assert sha(ROOT / record['path']) == record['sha256']
    terminal = read(ROOT / bindings['owner_terminal']['path'])
    assert terminal['terminal'] and terminal['exit'] == 0
    assert (ROOT / bindings['owner_terminal']['path']).parent == RUNTIME
    assert bindings['owner_result']['path'] == str((RUNTIME / 'RESULT.json').relative_to(ROOT))
    assert bindings['build_result']['path'] == str((RUNTIME / 'candidate-build/RESULT.json').relative_to(ROOT))
    assert bindings['restoration']['path'] == str((RUNTIME / 'RESTORATION.json').relative_to(ROOT))
    result = read(RUNTIME / 'RESULT.json')
    restored = read(RUNTIME / 'RESTORATION.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['error'] is None and result['publication_errors'] == []
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    policy = read(OWNER / 'POLICY.json')
    assert policy['lane_order'] == ['root_identity', 'controls']
    assert read(OWNER / 'SOURCE-ROLES.json') == read(ROOT / bindings['baseline']['directory'] / 'SOURCE-ROLES.json')
    assessor = load('combined_assessor', OWNER / 'assess.py')
    checks = load('combined_checks', ROOT / policy['wpt']['checks_helper'])
    original = read(ROOT / bindings['baseline']['path'])
    assert original['counts'] == {'PASS': 54, 'FAIL': 7} and original['projection_only']
    for path, pin in original['input_runtime_manifests'].items():
        authenticate((ROOT / path).parent, pin)
    baseline = {'rows': [assessor.signature(row) for row in original['rows']],
                'ends': [assessor.signature(row) for row in original['endings']]}
    build = read(RUNTIME / 'candidate-build/RESULT.json')
    command = read(RUNTIME / 'candidate-build/COMMAND.json')
    assert build['browser_build_performed'] and build['command_success'] and build['preservation_verified']
    assert build['error'] is None
    assert command['owner_manifest'] == sha(OWNER / 'FILES.json')
    expected_sources = {name: role['candidate_sha256'] for name, role in read(OWNER / 'SOURCE-ROLES.json').items()}
    assert command['source_sha256'] == build['native_sources'] == expected_sources
    assert build['application_metadata']['source_role'] == 'candidate'
    rows, ends, lanes = [], [], {}
    for lane in policy['lane_order']:
        phase = RUNTIME / ('candidate-wpt-' + lane)
        result = read(phase / 'RESULT.json')
        assert result['success'] and result['preservation_verified'] and result['execution_error'] is None
        metadata = read(phase / 'APPLICATION-METADATA.json')
        assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == build['binaries']
        for name, pin in read(phase / 'STAGED-RESOURCES.json').items():
            assert sha(phase / name) == pin
        for url, record in policy['wpt_lanes'][lane]['resources'].items():
            resource = phase / 'mozilla-tests' / url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase / 'tests' / url[1:]
            assert sha(resource) == record['sha256']
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        actual = assessor.assess(events, result['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=metadata)
        assert actual == read(phase / 'ASSESSMENT.json') and actual['complete']
        rows.extend(assessor.signature(row) for row in actual['rows'])
        ends.extend(assessor.signature(row) for row in actual['ends'])
        lanes[lane] = {'raw_sha256': sha(phase / 'raw.jsonl'), 'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'statuses': dict(Counter(row['status'] for row in actual['rows']))}
    report = compare_signatures(baseline, rows, ends)
    report.update(baseline_projection=True, candidate_sources=expected_sources,
                  build_sha256=sha(RUNTIME / 'candidate-build/RESULT.json'),
                  baseline_sha256=sha(ROOT / bindings['baseline']['path']), lanes=lanes,
                  native_acceptance=False, independent_restoration_audit_required=True)
    with (HERE / 'RESULT.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print('61 PASS; 54 prior PASS and five endings unchanged; exactly 7 FAIL-to-PASS improvements')


if __name__ == '__main__':
    main()
