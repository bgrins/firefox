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
        assert (root / item['capture']).read_bytes() == (pair / 'original-wpt/tests' / relative).read_bytes()
    checkpoint = policy['reference_checkpoint']
    receipt = h.read(root / checkpoint['final_check'])
    assert receipt['head'] == checkpoint['signed_head'] == epoch['semantic_index']['head']
    assert receipt['signature_verified'] and receipt['runtime_epoch_synchronized']
    assert receipt['accepted_fix_increment'] == receipt['canonical_coverage_increment'] == 0
    assert receipt['completed_pair_result_sha256'] == terminal['result_sha256']
    return {'pair_result_sha256': terminal['result_sha256'], 'comparison_gate_passed': True,
            'tested_source_sha256': tested['candidate_sha256'],
            'clean_source_sha256': source['candidate_sha256'], 'clean_source_validated': False,
            'reference_checkpoint': checkpoint, 'accepted': False}
