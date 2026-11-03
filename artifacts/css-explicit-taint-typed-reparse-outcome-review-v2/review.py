import importlib.util
import json
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticated(record):
    assert record is not None, 'pending actual binding'
    directory = ROOT / record['directory']
    assert directory.is_dir() and not directory.is_symlink()
    assert sha(directory / 'FILES.json') == record['manifest_sha256']
    manifest = read(directory / 'FILES.json')
    for name, row in manifest.get('files', manifest).items():
        path = directory / name
        assert path.is_relative_to(directory) and '..' not in Path(name).parts
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == (row if isinstance(row, str) else row['sha256']), name
    return directory


def signature(event):
    return {"kind": event["action"], "test": event["test"],
            "subtest": event.get("subtest"), "status": event["status"],
            "expected": event.get("expected", event["status"]),
            "expected_field_present": "expected" in event,
            "known_intermittent": event.get("known_intermittent", []),
            "intermittent_field_present": "known_intermittent" in event,
            "message": event.get("message"), "message_field_present": "message" in event}


def signatures(events, roster, exit_code, checks):
    expected = {(page, name) for page, names in roster.items() for name in names}
    rows = [e for e in events if e.get('action') == 'test_status']
    ends = [e for e in events if e.get('action') == 'test_end']
    assert len(rows) == len(expected) and {(e['test'], e['subtest']) for e in rows} == expected
    assert all(e['status'] in ('PASS', 'FAIL') for e in rows)
    assert len(ends) == len(roster) and {e['test'] for e in ends} == set(roster)
    assert all(e['status'] == 'OK' for e in ends)
    assert checks.lifecycle(events, {'expected_subtests': {p: [] for p in roster}, 'reftests': []})
    assert not checks.infrastructure_faults(events)
    assert not any(e.get('action') == 'crash' for e in events)
    assert checks.exit_matches_results(exit_code, rows + ends)
    return {(e['action'], e['test'], e.get('subtest')): signature(e) for e in rows + ends}


def compare(original, candidate, target=False):
    assert original.keys() == candidate.keys()
    changes = [{'identity': list(key), 'original': original[key], 'candidate': candidate[key]}
               for key in original if original[key] != candidate[key]]
    preserved = all(candidate[k] == v for k, v in original.items()
                    if v['status'] in ('PASS', 'OK'))
    if target:
        assert sum(v['kind'] == 'test_status' and v['status'] == 'FAIL' for v in original.values()) == 1
        failed = next(v for v in original.values() if v['status'] == 'FAIL')
        assert failed['subtest'] == 'Primary attribute taint survives universal-to-string registration during a transition'
        assert 'Image policy at 0.25 progress expected "none"' in failed['message']
        assert 'image-set(' in failed['message'] and 'data:image/svg+xml' in failed['message']
        assert failed['expected'] == 'PASS' and not failed['known_intermittent']
        passed = all(v['status'] == 'PASS' and v['expected'] == 'PASS'
                     and not v['known_intermittent'] and v['message'] is None
                     for v in candidate.values() if v['kind'] == 'test_status')
        return {'preserved_prior_pass_and_endings': preserved, 'target_all_pass': passed,
                'comparison_passed': preserved and passed, 'changes': changes}
    return {'preserved_prior_pass_and_endings': preserved, 'full_signatures_equal': not changes,
            'comparison_passed': not changes, 'changes': changes}


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def staged(directory, inputs):
    pins = read(directory / 'STAGED-RESOURCES.json')
    for url, record in inputs['resources'].items():
        relative = 'tests/' + url.lstrip('/')
        assert pins[relative] == record['sha256'] == sha(directory / relative)
    assert pins['metadata/MANIFEST.json'] == inputs['manifest']['sha256']
    assert sha(directory / 'metadata/MANIFEST.json') == inputs['manifest']['sha256']
    assert inputs['metadata'] == inputs['prefs'] == {}
    assert not list((directory / 'metadata').rglob('*.ini'))
    cleanup = read(directory / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']


def original(directory, inputs, roster, snapshot, checks):
    result = read(directory / 'RESULT.json')
    assert result['success'] and result['archive_preserved'] and result['staged_preserved']
    assert result['execution_error'] is None and result['source_role'] == 'archived-original'
    terminal = read(directory / 'ROOT-OWNER-TERMINAL.json')
    assert terminal['terminal'] and terminal['exit'] == 0
    assert terminal['result_sha256'] == sha(directory / 'RESULT.json')
    assert terminal['wpt_exit'] == result['exit']
    assert read(directory / 'ARCHIVE-PRE.json') == read(directory / 'ARCHIVE-POST.json')
    assert read(directory / 'ARCHIVE-PRE.json')['files'] == len(snapshot['files']) == 8326
    assert read(directory / 'ARCHIVE-PRE.json')['application'] == snapshot['application']
    expected_digest = hashlib.sha256(json.dumps(snapshot['files'], sort_keys=True).encode()).hexdigest()
    assert read(directory / 'ARCHIVE-PRE.json')['manifest_sha256'] == expected_digest
    staged(directory, inputs)
    raw = events(directory / 'raw.jsonl')
    build = read(ROOT / snapshot['build_receipt'])
    suites = [e for e in raw if e.get('action') == 'suite_start']
    assert len(suites) == 1
    assert suites[0]['run_info']['browser_build_id'] == build['application_metadata']['browser_build_id']
    assert suites[0]['run_info']['revision'] == build['application_metadata']['revision']
    saved = read(directory / 'ASSESSMENT.json')
    assert saved['complete'] and saved['subtests'] == [e for e in raw if e.get('action') == 'test_status']
    assert saved['endings'] == [e for e in raw if e.get('action') == 'test_end']
    return signatures(raw, roster, result['exit'], checks)


def review(binding):
    assert binding['execution_enabled'], 'disabled pending review'
    assert all(binding.get(k) is not None for k in ('candidate', 'owner', 'audit', 'controls_original')), 'pending actual evidence'
    for path, digest in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / path) == digest, path
    checks = load('saved_checks', ROOT / binding['checks'])
    owner = authenticated(binding['owner'])
    candidate = authenticated(binding['candidate'])
    audit_dir = authenticated(binding['audit'])
    policy = read(owner / 'POLICY.json')
    assert policy['source_binding'] == binding['source']
    source = authenticated(binding['source'])
    role = read(source / 'SOURCE.json')['roles']['servo/components/style/custom_properties.rs']
    assert role['base']['sha256'].startswith('bb13b61a') and role['candidate']['sha256'].startswith('2bcc5d15')
    result = read(candidate / 'RESULT.json')
    terminal = read(candidate / 'ROOT-OWNER-TERMINAL.json')
    assert terminal['terminal'] and terminal['exit'] == 0
    assert terminal['result_sha256'] == sha(candidate / 'RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['error'] is None
    assert not result['publication_errors'] and result['runtime_controls_unchanged']
    audit = read(audit_dir / binding['audit_report'])
    assert audit['owner_result_sha256'] == sha(candidate / 'RESULT.json')
    for field in ('independent_live_restoration_verified', 'application_and_extras_semantically_restored',
                  'source_and_binary_hashes_restored', 'flags_restored', 'controls_unchanged'):
        assert audit[field]
    assert audit['restored_source_claims']['servo/components/style/custom_properties.rs']['owned_sha256'] == role['base']['sha256']
    build = read(candidate / 'candidate-build/RESULT.json')
    assert build['browser_build_performed'] and build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert build['native_sources'] == {'servo/components/style/custom_properties.rs': role['candidate']['sha256']}
    assert build['application_metadata']['source_role'] == 'candidate'
    assert build['application_metadata']['revision'] == build['application_metadata']['build_revision'] == policy['head']
    snapshot = read(ROOT / binding['original_snapshot'])
    old_build = read(ROOT / snapshot['build_receipt'])
    assert sha(ROOT / snapshot['build_receipt']) == snapshot['build_receipt_sha256']
    assert old_build['browser_build_performed'] and old_build['command_success'] and old_build['preservation_verified']
    assert old_build['native_sources'] == snapshot['native_sources']
    assert snapshot['native_sources']['servo/components/style/custom_properties.rs'] == role['base']['sha256']
    assessor = load('candidate_assess', owner / 'assess.py')
    out = {}
    for lane in ('reparse', 'fallback', 'controls'):
        suite = authenticated(binding['suites'][lane])
        assert policy['suite_bindings'][lane] == binding['suites'][lane]
        inputs, roster = read(suite / 'INPUTS.json'), read(suite / 'ROSTER.json')
        old = authenticated(binding[lane + '_original'])
        before = original(old, inputs, roster, snapshot, checks)
        phase = candidate / ('candidate-wpt-' + lane)
        record = read(phase / 'RESULT.json')
        assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
        staged(phase, inputs)
        metadata = read(phase / 'APPLICATION-METADATA.json')
        assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == build['binaries']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json')
        raw = events(phase / 'raw.jsonl')
        saved = read(phase / 'ASSESSMENT.json')
        replay = assessor.assess(raw, record['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=metadata)
        assert replay == saved and replay['complete']
        for name, key in [('raw.jsonl','raw_sha256'), ('ASSESSMENT.json','assessment_sha256'), ('RESULT.json','result_sha256')]:
            assert result['phase']['candidate'][lane][key] == sha(phase / name)
        after = signatures(raw, roster, record['exit'], checks)
        out[lane] = compare(before, after, target=lane == 'reparse')
        out[lane]['original_signatures'] = list(before.values())
        out[lane]['candidate_signatures'] = list(after.values())
    return {'complete_authenticated_observations': True, 'lanes': out,
            'comparison_passed': all(x['comparison_passed'] for x in out.values()),
            'native_fix_acceptance': False, 'scope': 'Saved-artifact comparison; no fresh live archive/process checks'}


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    print(json.dumps(review(read(HERE / 'BINDINGS.json')), indent=2))
