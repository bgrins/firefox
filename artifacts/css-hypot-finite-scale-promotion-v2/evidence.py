import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, policy, epoch, h):
    pair = root / policy['paired_runtime']
    result = h.read(pair / 'RESULT.json')
    terminal = h.read(pair / 'CANDIDATE-ROOT-REPORTED-TERMINAL.json')
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    assert terminal['session_id'] == 70485 and terminal['terminal_tool'] == '0d77a9' and terminal['exit'] == 0
    assert terminal['root_observed_terminal'] and terminal['result_sha256'] == h.digest((pair / 'RESULT.json').read_bytes())
    restored = h.read(pair / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    cleanup = h.read(pair / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert not os.path.lexists(pair / 'backups')
    browser = h.read(root / policy['paired_browser'] / 'POLICY.json')
    assessor = load('hypot_promotion_assessor', root / policy['paired_browser'] / 'assess.py')
    checker = load('hypot_promotion_completed_checker', root / policy['completed_pair_checker'])
    checks = load('hypot_promotion_lifecycle', root / browser['wpt']['checks_helper'])
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
    old = (root / tested['candidate_capture']).read_bytes()
    clean = (root / source['candidate_capture']).read_bytes()
    before = b'use std::ops::{Add, Mul, Rem, Sub};'
    after = b'use std::ops::{Add, Rem, Sub};'
    assert old.count(before) == 1 and old.replace(before, after, 1) == clean
    for name, item in policy['tests'].items():
        relative = name.removeprefix('testing/web-platform/tests/')
        historical = (pair / 'original-wpt/tests' / relative).read_bytes()
        for before, after in [(b'hypot(0, -0)', b'hypot(0, -1 * 0)'), (b'1 / hypot(-0)', b'1 / hypot(-1 * 0)'), (b'1 / hypot(-0, -0)', b'1 / hypot(-1 * 0, -1 * 0)')]:
            assert historical.count(before) == 1
            historical = historical.replace(before, after, 1)
        assert (root / item['capture']).read_bytes() == historical
    fresh = policy['fresh_baseline']
    assert fresh['evidence'] and fresh['terminal']
    for name, pin in fresh['evidence'].items():
        assert h.digest((root / name).read_bytes()) == pin
    fresh_root = root / fresh['runtime']
    fresh_phase = fresh_root / 'original-wpt'
    fresh_result = h.read(fresh_root / 'BASELINE-RESULT.json')
    assert fresh_result['success'] and fresh_result['preservation_verified'] and not fresh_result['canonical_updated']
    assert fresh_result['phase'] == {'assessment_sha256': h.digest((fresh_phase / 'ASSESSMENT.json').read_bytes()),
        'raw_sha256': h.digest((fresh_phase / 'raw.jsonl').read_bytes()),
        'result_sha256': h.digest((fresh_phase / 'RESULT.json').read_bytes())}
    fresh_terminal = h.read(root / fresh['terminal'])
    assert fresh_terminal['root_observed_terminal'] and fresh_terminal['exit'] == 0
    assert fresh_terminal['session_id'] == fresh['terminal_session'] and fresh_terminal['terminal_tool'] == fresh['terminal_tool']
    assert fresh_terminal['result_sha256'] == h.digest((fresh_root / 'BASELINE-RESULT.json').read_bytes())
    fresh_policy = h.read(root / fresh['owner'] / 'POLICY.json')
    assert fresh_policy['head'] == policy['head']
    phase_policy = h.read(fresh_phase / 'ASSESSMENT-POLICY.json')
    assert all(phase_policy[key] == value for key, value in fresh_policy['wpt'].items())
    assert h.read(fresh_phase / 'PRE.json') == h.read(fresh_phase / 'POST.json')
    fresh_cleanup = h.read(fresh_phase / 'CLEANUP.json')
    assert fresh_cleanup['owned_group_absent'] and fresh_cleanup['temporary_root_removed']
    h.group_absent(h.read(fresh_phase / 'PROCESS.json')['pgid'])
    record = h.read(fresh_phase / 'RESULT.json')
    assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
    original = assessor.assess([json.loads(line) for line in (fresh_phase / 'raw.jsonl').read_text().splitlines()],
        record['exit'], phase_policy, checks,
        run_binding=h.read(fresh_phase / 'APPLICATION-METADATA.json'))
    assert json.loads(json.dumps(original)) == h.read(fresh_phase / 'ASSESSMENT.json')
    assert original['complete'] and original['errors'] == [] and original['fixture_setup_errors'] == []
    assert original['observed_subtest_count'] == 227 and len(original['regression_signature']) == 215
    assert len(original['ends']) == 4 and all(row['status'] == 'OK' for row in original['ends'])
    assert original['run_binding']['harness_revision'] == policy['head']
    targets = {(test, name) for test, names in fresh_policy['wpt']['target_subtests'].items() for name in names}
    assert len(targets) == 16 and all(row['status'] == 'FAIL' for row in original['rows'] if (row['test'], row['subtest']) in targets)
    for name, item in policy['tests'].items():
        relative = name.removeprefix('testing/web-platform/tests/')
        assert (root / item['capture']).read_bytes() == (fresh_phase / 'tests' / relative).read_bytes()
    checkpoint = policy['reference_checkpoint']
    receipt = h.read(root / checkpoint['final_check'])
    assert receipt['head'] == checkpoint['signed_head'] == epoch['semantic_index']['head']
    assert receipt['signature_verified'] and receipt['runtime_epoch_synchronized']
    assert receipt['accepted_fix_increment'] == receipt['canonical_coverage_increment'] == 0
    assert receipt['completed_pair_result_sha256'] == terminal['result_sha256']
    return {'pair_result_sha256': terminal['result_sha256'], 'comparison_gate_passed': True,
            'tested_source_sha256': tested['candidate_sha256'],
            'clean_source_sha256': source['candidate_sha256'], 'clean_source_validated': False,
            'reference_checkpoint': checkpoint, 'fresh_baseline_result_sha256': h.digest((fresh_root / 'BASELINE-RESULT.json').read_bytes()), 'accepted': False}
