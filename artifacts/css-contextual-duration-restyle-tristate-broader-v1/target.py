import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def verify(root,policy,here):
    binding = policy['target_binding']
    assert binding is not None
    owner, runtime = root / binding['owner'], root / binding['directory']
    assert sha(owner / 'FILES.json') == binding['owner_sha256']
    assert sha(runtime / 'FILES.json') == binding['manifest_sha256']
    source = read(owner / 'POLICY.json')
    roles = read(here / 'SOURCE-ROLES.json')
    assert roles == read(owner / 'SOURCE-ROLES.json')
    assert source['head'] == policy['head']
    for key in ('accepted_current_payloads','accepted_epoch_records','source_context_pins','prepared_flag_hashes','original_build','source_equivalence'):
        assert policy[key] == source[key],key
    terminal = read(runtime / binding['terminal_path'])
    assert sha(runtime / binding['terminal_path']) == binding['terminal_sha256']
    assert terminal['session_id'] == 7257 and terminal['terminal_chunk'] == '7a7e91' and terminal['exit'] == 0
    assert terminal['owner_sha256'] == binding['owner_sha256']
    assert terminal['result_sha256'] == binding['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    assert terminal['state_and_application_restoration_independently_verified'] and terminal['raw_replay_verified']
    assert terminal['build_success'] and terminal['calibrated_acquisition'] and terminal['callbacks_passed'] == terminal['records'] == 2
    assert terminal['ending'] == 'OK' and terminal['native_acceptance'] is False and terminal['self_feedback_numeric_or_convergence_oracle'] is False
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    restoration = read(runtime / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert set(restoration['sources']) == set(roles)
    for name,record in roles.items():
        assert restoration['sources'][name]['sha256'] == record['base_sha256']
    backup = read(runtime / 'BACKUP-CLEANUP.json')
    assert backup['removed'] and backup['verified_original_restoration'] and backup['retained_after_failure'] is False
    assert backup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    phase = runtime / 'feedback-wpt'
    comparison = load('completed_target_comparison',owner / 'comparison.py')
    assessor = load('completed_target_assessor',owner / 'assess.py')
    checks = load('completed_target_checks',root / source['wpt']['checks_helper'])
    comparison.replay_all(root,source)
    original = comparison.replay_original(root,source,assessor,checks)
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    phase_result = read(phase / 'RESULT.json')
    app = read(phase / 'APPLICATION-METADATA.json')
    settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert settings == comparison.phase_policy(source['wpt'])
    observed = assessor.assess(events,phase_result['exit'],settings,checks,original=original,run_binding=app)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and observed['comparison_gate_passed'] and len(observed['rows']) == 2
    assert all(row['status'] == 'PASS' for row in observed['rows']) and phase_result['exit'] == 0
    assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == read(runtime / 'PHASES-PRE.json') == read(runtime / 'PHASES-POST.json')
    assert app == read(phase / 'APPLICATION-METADATA-POST.json')
    assert app['revision'] == app['build_revision'] == app['harness_revision'] == source['head'] and app['source_role'] == 'candidate'
    build = read(runtime / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert build['native_sources'] == {name:record['candidate_sha256'] for name,record in roles.items()}
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    inner = read(runtime / 'candidate-build/build-RESULT.json')
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
    assert read(phase / 'CLEANUP.json')['owned_group_absent'] and read(phase / 'CLEANUP.json')['temporary_root_removed']
    records = load('completed_target_records',owner / 'phases.py').feedback_records(root,runtime,source)
    assert records == read(runtime / 'FEEDBACK-RECORDS.json') and records['calibrated_acquisition']
    assert result['candidate_phase'] == {'feedback':{key:sha(phase / filename) for key,filename in [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json')]},'calibrated_acquisition':True,'record_index_sha256':sha(runtime / 'FEEDBACK-RECORDS.json')}
    observation = read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert observation == terminal['raw_index_observation'] and observation['semantic_index_unchanged'] and observation['canonical_updated'] is False
    before = read(runtime / 'CANDIDATE-PRE.json')['snapshot']
    after = read(runtime / 'POST.json')
    expected = copy.deepcopy(before);expected['index']['raw_index'] = observation['after']
    assert after == expected and before['index']['raw_index'] == observation['before']
    refresh = read(root / policy['prepared_state_evidence']['refresh'])
    assert policy['prepared_state_evidence']['restoration'] == str((runtime / binding['terminal_path']).relative_to(root))
    assert refresh['runtime_manifest_sha256'] == binding['manifest_sha256']
    assert refresh['before_epoch'] == source['controls']['CURRENT-EPOCH.json']
    assert refresh['after_epoch'] == policy['controls']['CURRENT-EPOCH.json']
    assert refresh['observation'] == observation and refresh['only_changed_field'] == 'raw_index_observation.current'
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    expected_app = copy.deepcopy(source['prepared_application_metadata'])
    expected_app['entry_identity'] = terminal['restored_application_entry']['identity']
    expected_app['identity'] = terminal['restored_application_target']['identity']
    assert expected_app == policy['prepared_application_metadata']
    assert expected_app['sha256'] == terminal['restored_application_target']['sha256']
    fresh = load('broader_admission_comparison',here / 'comparison.py')
    fresh.admit_snapshot(read(root / policy['baseline_binding']['directory'] / 'POST.json'),after)
    return {'target_raw_replayed':True,'calibrated_acquisition':True,'source_and_application_restoration_bound':True,'new_browser_execution':False}
