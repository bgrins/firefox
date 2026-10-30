import hashlib
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, policy):
    for name, pin in policy['references'].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        assert sha(root / name) == pin, name
    runtime = root / policy['evidence_runtime']
    terminal = read(runtime / 'CANDIDATE-ROOT-REPORTED-TERMINAL.json')
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (90981, '22d34a', 0)
    assert terminal['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['empty_staging_preserved'] and result['error'] is None and result['publication_errors'] == []
    assert not result['native_fix_acceptance']
    replay = read(runtime / 'CANDIDATE-ROOT-REPLAY.json')
    assert all(replay[k] for k in ('original_exact_raw_replay', 'combined_reference_exact_raw_replay', 'provider_free_exact_raw_replay', 'committed_provider_built', 'original_source_and_held_provider_restored', 'original_app_restoration_verified'))
    assert replay['callbacks'] == 578 and replay['candidate_statuses'] == {'PASS': 576, 'FAIL': 2}
    assert replay['target_repairs_against_original_with_provider'] == 33 and replay['authored_passes'] == 60
    assert replay['preserved_original_control_and_ending_signatures'] == 561
    assert replay['all_combined_row_and_end_signatures_equal'] == 594
    assert not replay['provider_free_original_causal_delta_measured'] and not replay['native_acceptance']
    build = read(runtime / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert build['native_sources'] == {policy['source_path']: policy['files'][policy['source_path']]['sha256'],
        'servo/components/style/custom_properties.rs': '8a4adc903e7d88e218ee087cbe44cc3548df70fac9353dd923d5c32de2c458f9'}
    inner = read(runtime / 'candidate-build/build-RESULT.json')
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    phase = runtime / 'candidate-wpt'
    assert result['candidate_phase'] == {key: sha(phase / name) for key, name in
        [('assessment_sha256','ASSESSMENT.json'), ('raw_sha256','raw.jsonl'), ('result_sha256','RESULT.json')]}
    phase_result = read(phase / 'RESULT.json')
    assert phase_result['success'] and phase_result['comparison_gate_passed'] and phase_result['preservation_verified']
    assert build['binaries'] == read(phase / 'BINARY-PINS.json')
    assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
    assessment = read(phase / 'ASSESSMENT.json')
    assert assessment['complete'] and assessment['comparison_gate_passed'] and assessment['errors'] == []
    assert len(assessment['rows']) == 578 and len(assessment['ends']) == 16
    metadata = (root / policy['deleted_metadata']['capture']).read_text()
    expected = '[exp-log-compute.html]\n' + '\n'.join('  [' + name + ']\n    expected: FAIL\n' for name in policy['metadata_targets'])
    assert metadata == expected
    assert (phase / 'metadata/css/css-values/exp-log-compute.html.ini').read_text() == metadata
    rows = {r['subtest']: r for r in assessment['rows'] if r['test'] == '/css/css-values/exp-log-compute.html'}
    assert len(policy['metadata_targets']) == 5 and all(rows[n]['status'] == 'PASS' and rows[n]['expected'] == 'FAIL' for n in policy['metadata_targets'])
    test = 'testing/web-platform/tests/css/css-values/log-clear-special-values.html'
    assert sha(phase / 'tests/css/css-values/log-clear-special-values.html') == policy['files'][test]['sha256']
    authored = [r for r in assessment['rows'] if r['test'] == '/css/css-values/log-clear-special-values.html']
    assert len(authored) == 24 and all(r['status'] == 'PASS' for r in authored)
    restoration = read(runtime / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert restoration['sources'][policy['source_path']]['sha256'] == 'b291d6e9a30e486fd42ff0cb3cda00cfead0ee7f7149761d8685a8cc85889576'
    assert restoration['sources']['servo/components/style/custom_properties.rs']['sha256'] == policy['held_provider_sha256']
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert cleanup['owned_backup_bytes'] == replay['owned_backup_bytes_removed'] == 1008605176
    return {'root_replay_sha256': sha(runtime / 'CANDIDATE-ROOT-REPLAY.json'),
        'actual_terminal_sha256': sha(runtime / 'CANDIDATE-ROOT-REPORTED-TERMINAL.json'),
        'candidate_source_sha256': policy['files'][policy['source_path']]['sha256'],
        'authored_log_passes': 24, 'obsolete_metadata_targets': policy['metadata_targets'],
        'new_browser_or_raw_replay': False, 'provider_free_original_causal_delta_measured': False,
        'current_app_contains_candidate': False, 'native_acceptance': False}

