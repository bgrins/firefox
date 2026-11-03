import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-root-font-cancellation-candidate-browser-v2'
RUNTIME = ROOT / 'artifacts/css-root-font-cancellation-candidate-browser-runtime-v1'
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


def compare_signatures(baseline, rows, ends, complete):
    key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
    old = {key(row): row for row in baseline['rows'] + baseline['ends']}
    assert len(baseline['rows']) == 8 and len(baseline['ends']) == 1 and len(old) == 9
    assert Counter(row['status'] for row in baseline['rows']) == {'PASS': 6, 'FAIL': 2}
    assert baseline['ends'][0]['status'] == 'OK'
    report = {'observation_complete': bool(complete), 'witness_closed_under_known_fix': False,
              'candidate_statuses': dict(Counter(row['status'] for row in rows)),
              'rows': rows, 'endings': ends, 'native_acceptance': False}
    if not complete:
        return report
    new = {key(row): row for row in rows + ends}
    assert len(rows) == 8 and len(ends) == 1 and len(new) == 9 and set(old) == set(new)
    assert all(row['status'] in ('PASS', 'FAIL') for row in rows) and ends[0]['status'] == 'OK'
    controls = [identity for identity, row in old.items() if row['kind'] == 'test_status' and row['status'] == 'PASS']
    preserved = [identity for identity in controls if old[identity] == new[identity]]
    changed_controls = [{'identity': identity, 'original': old[identity], 'candidate': new[identity]}
                        for identity in controls if old[identity] != new[identity]]
    improvements = [{'identity': identity, 'original': old[identity], 'candidate': new[identity]}
                    for identity in old if old[identity]['status'] == 'FAIL' and new[identity]['status'] == 'PASS']
    preserved_end = old[key(ends[0])] == ends[0]
    report.update(preserved_pass_signatures=len(preserved), changed_prior_pass_signatures=changed_controls,
                  fail_to_pass=len(improvements), improvements=improvements,
                  remaining_failures=[row for row in rows if row['status'] == 'FAIL'],
                  ending_signature_preserved=preserved_end,
                  differences=[{'identity': identity, 'original': old[identity], 'candidate': new[identity]}
                               for identity in old if old[identity] != new[identity]],
                  witness_closed_under_known_fix=all(row['status'] == 'PASS' for row in rows)
                      and len(preserved) == 6 and preserved_end)
    return report


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
    assert terminal['terminal']
    assert terminal['result_sha256'] == bindings['owner_result']['sha256']
    assert (ROOT / bindings['owner_terminal']['path']).parent == RUNTIME
    assert bindings['owner_result']['path'] == str((RUNTIME / 'RESULT.json').relative_to(ROOT))
    assert bindings['build_result']['path'] == str((RUNTIME / 'candidate-build/RESULT.json').relative_to(ROOT))
    assert bindings['restoration']['path'] == str((RUNTIME / 'RESTORATION.json').relative_to(ROOT))
    result = read(RUNTIME / 'RESULT.json')
    restored = read(RUNTIME / 'RESTORATION.json')
    assert terminal['exit'] == (0 if result['success'] else 1)
    assert result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['publication_errors'] == []
    owner_error = result['error']
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    policy = read(OWNER / 'POLICY.json')
    assert policy['lane_order'] == ['cancellation']
    assert policy['head'] == 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
    assert read(OWNER / 'SOURCE-ROLES.json') == read(ROOT / bindings['baseline']['directory'] / 'SOURCE-ROLES.json')
    assessor = load('combined_assessor', OWNER / 'assess.py')
    checks = load('combined_checks', ROOT / policy['wpt']['checks_helper'])
    original = read(ROOT / bindings['baseline']['path'])
    assert original['projection_only']
    authenticate(ROOT / original['full22_runtime'], original['full22_manifest_sha256'])
    full_events = [json.loads(line) for line in (ROOT / original['full22_runtime'] / 'raw.jsonl').read_text().splitlines()]
    page = '/web-animations/animation-model/keyframe-effects/root-font-cancel-child-animation.html'
    assert [row for row in full_events if row.get('action') == 'test_status' and row.get('test') == page] == original['rows']
    assert [row for row in full_events if row.get('action') == 'test_end' and row.get('test') == page] == original['endings']
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
    complete = True
    for lane in policy['lane_order']:
        phase = RUNTIME / ('candidate-wpt-' + lane)
        result = read(phase / 'RESULT.json')
        assert result['preservation_verified']
        metadata = read(phase / 'APPLICATION-METADATA.json')
        assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == build['binaries']
        for name, pin in read(phase / 'STAGED-RESOURCES.json').items():
            assert sha(phase / name) == pin
        for url, record in policy['wpt_lanes'][lane]['resources'].items():
            resource = phase / 'mozilla-tests' / url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase / 'tests' / url[1:]
            assert sha(resource) == record['sha256']
            original_root = ROOT / original['full22_runtime']
            original_resource = original_root / 'mozilla-tests' / url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else original_root / 'tests' / url[1:]
            assert sha(original_resource) == record['sha256']
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        actual = assessor.assess(events, result['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=metadata)
        assert actual == read(phase / 'ASSESSMENT.json')
        complete = complete and actual['complete']
        rows.extend(assessor.signature(row) for row in actual['rows'])
        ends.extend(assessor.signature(row) for row in actual['ends'])
        lanes[lane] = {'raw_sha256': sha(phase / 'raw.jsonl'), 'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'statuses': dict(Counter(row['status'] for row in actual['rows'])), 'complete': actual['complete'], 'errors': actual['errors'], 'execution_error': result['execution_error'], 'crash_events': [row for row in events if row.get('action') == 'crash' or row.get('status') == 'CRASH']}
    report = compare_signatures(baseline, rows, ends, complete)
    report.update(baseline_projection=True, owner_error=owner_error, candidate_sources=expected_sources,
                  build_sha256=sha(RUNTIME / 'candidate-build/RESULT.json'),
                  baseline_sha256=sha(ROOT / bindings['baseline']['path']), lanes=lanes,
                  native_acceptance=False, independent_restoration_audit_required=True)
    with (HERE / 'RESULT.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'observation_complete':report['observation_complete'], 'witness_closed_under_known_fix':report['witness_closed_under_known_fix'], 'candidate_statuses':report['candidate_statuses']}))


if __name__ == '__main__':
    main()
