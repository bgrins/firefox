import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy, epoch, h):
    refresh = root / policy['raw_refresh']['runtime']
    terminal = h.read(refresh / 'ROOT-REPORTED-TERMINAL.json')
    assert terminal == policy['raw_refresh']['terminal'] and terminal['exit'] == 0
    assert terminal['result_sha256'] == h.digest((refresh / 'RESULT.json').read_bytes())
    result = h.read(refresh / 'RESULT.json')
    assert result['success'] and result['preservation_verified']
    assert result['updated_only'] == 'raw_index_observation.current' and not result['paired_result_reclassified']
    assert result['epoch_sha256'] == terminal['epoch_sha256'] == policy['epoch_sha256']
    assert result['head'] == policy['head']
    pair = root / policy['paired_runtime']
    result = h.read(pair / 'RESULT.json')
    binding = policy['pair_terminal']
    assert binding and binding['record']
    terminal = h.read(root / binding['path'])
    assert terminal == binding['record'] and terminal[binding['exit_field']] == 0
    assert terminal['session_id'] == 87473
    assert terminal[binding['result_field']] == h.digest((pair / 'RESULT.json').read_bytes())
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    restored = h.read(pair / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    cleanup = h.read(pair / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert not os.path.lexists(pair / 'backups')
    browser = h.read(root / policy['paired_browser'] / 'POLICY.json')
    assessor = load('pow_promotion_assessor', root / policy['paired_browser'] / 'assess.py')
    checker = load('pow_promotion_completed_checker', root / policy['completed_pair_checker'])
    checks = load('pow_promotion_lifecycle', root / browser['wpt']['checks_helper'])
    original = None
    for role in ('original', 'candidate'):
        phase = pair / (role + '-wpt')
        record = h.read(phase / 'RESULT.json')
        assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
        assert h.read(phase / 'PRE.json') == h.read(phase / 'POST.json')
        cleanup = h.read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        h.group_absent(h.read(phase / 'PROCESS.json')['pgid'])
        replay = assessor.assess([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()],
            record['exit'], h.read(phase / 'ASSESSMENT-POLICY.json'), checks,
            original=original, run_binding=h.read(phase / 'APPLICATION-METADATA.json'))
        assert json.loads(json.dumps(replay)) == h.read(phase / 'ASSESSMENT.json')
        if role == 'original':
            original = replay
        else:
            checker.validate_completed_assessments(original, replay, browser['wpt'], assessor.signature)
    for name in ('candidate-build/build-PROCESS.json', 'candidate-build/WAKE-PROCESS.json'):
        h.group_absent(h.read(pair / name)['pgid'])
    build = h.read(pair / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
    assert build['error'] is None and build['stop_reason'] is None
    source = policy['source']
    tested = h.read(root / policy['paired_browser'] / 'SOURCE-ROLES.json')[source['path']]
    assert tested['base_sha256'] == source['base_sha256']
    assert tested['candidate_sha256'] == source['candidate_sha256']
    assert (root / tested['candidate_capture']).read_bytes() == (root / source['candidate_capture']).read_bytes()
    for name, item in policy['tests'].items():
        relative = name.removeprefix('testing/web-platform/tests/')
        body = (root / item['capture']).read_bytes()
        assert h.digest(body) == item['sha256']
        assert body == (pair / 'original-wpt/tests' / relative).read_bytes() == (pair / 'candidate-wpt/tests' / relative).read_bytes()
    phase = pair / 'candidate-wpt'
    assert result['candidate_phase'] == {'assessment_sha256':h.digest((phase / 'ASSESSMENT.json').read_bytes()),
        'raw_sha256':h.digest((phase / 'raw.jsonl').read_bytes()),'result_sha256':h.digest((phase / 'RESULT.json').read_bytes())}
    deletion = policy['deleted_metadata']
    metadata = (root / deletion['capture']).read_text()
    assert h.digest(metadata.encode()) == deletion['sha256']
    lines = [line.strip() for line in metadata.splitlines() if line.strip()]
    assert lines[0] == '[hypot-pow-sqrt-computed.html]'
    assert len(lines) == 25
    assert [line[1:-1] for line in lines[1::2]] == deletion['target_subtests']
    assert all(line == 'expected: FAIL' for line in lines[2::2])
    target_page = '/css/css-values/hypot-pow-sqrt-computed.html'
    assert set(deletion['target_subtests']) == set(browser['wpt']['target_subtests'][target_page])
    for role in ('original', 'candidate'):
        assert (pair / (role + '-wpt/metadata/css/css-values/hypot-pow-sqrt-computed.html.ini')).read_bytes() == metadata.encode()
    checkpoint = policy['reference_checkpoint']
    receipt = h.read(root / checkpoint['final_check'])
    assert receipt['head'] == checkpoint['signed_head'] == epoch['semantic_index']['head']
    assert receipt['signature_chain_verified'] and receipt['runtime_epoch_synchronized']
    assert receipt['accepted_fix'] == 149 and receipt['accepted_fixes'] == 148 and receipt['tracked'] == 149
    assert receipt['provider_candidate_accepted'] is False
    return {'pair_result_sha256':terminal[binding['result_field']], 'comparison_gate_passed':True,
            'tested_source_sha256':tested['candidate_sha256'], 'installed_source_sha256':source['candidate_sha256'],
            'source_and_fixture_exact_tested_bytes':True, 'reference_checkpoint':checkpoint, 'accepted':False}
