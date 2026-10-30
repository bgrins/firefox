import copy
import hashlib
import json

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def validate(root, policy, previous, authenticate):
    binding = policy['restoration_handoff']
    runtime, owner = root / binding['runtime'], root / binding['owner']['directory']
    authenticate(runtime, binding['manifest_sha256'])
    authenticate(owner, binding['owner']['manifest_sha256'])
    assert read(owner / 'POLICY.json') == previous
    for key in ('head','execution_handoff','baseline_binding','baseline_capsule','original_admission_policy_sha256','suite_binding','wpt','source_paths','source_context_pins','semantic_original_sources','committed_source_preimages','source_equivalence','accepted_current_payloads','preserved_absent_metadata','preserved_absent_resources','restored_application_revision'):
        assert policy[key] == previous[key], key
    terminal = read(runtime / 'ROOT-OWNER-TERMINAL.json')
    assert terminal.pop('active_owner_manifest_sha256') == binding['owner']['manifest_sha256']
    assert (terminal['session'],terminal['launch_chunk'],terminal['terminal_chunk'],terminal['exit']) == (50372,'cbc269','d0eb31',1)
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert sha(runtime / 'CANDIDATE-RESULT.json') == terminal['result_sha256']
    assert not result['success'] and result['candidate_phase'] is None and result['error'] == 'AssertionError()'
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['publication_errors'] == [] and result['native_fix_acceptance'] is False
    assert not (runtime / 'candidate-wpt').exists()
    build = read(runtime / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 2 and build['owned_group_absent'] and build['cleanup_errors'] == []
    assert build['error'] is None and build['stop_reason'] is None
    review = read(runtime / 'ROOT-REVIEW.json')
    assert sha(runtime / 'ROOT-REVIEW.json') == binding['review_sha256']
    rt = read(runtime / 'ROOT-REVIEWER-TERMINAL.json')
    assert (rt['session'],rt['launch_chunk'],rt['terminal_chunk'],rt['exit']) == (46693,'056f06','973d76',0)
    reviewer = root / binding['reviewer']['directory']
    authenticate(reviewer, binding['reviewer']['manifest_sha256'])
    assert rt['active_reviewer_manifest_sha256'] == binding['reviewer']['manifest_sha256']
    config = read(reviewer / 'POLICY.json')
    assert config['execution_enabled'] and config['actual_terminal'] == terminal
    assert config['owner_directory'] == binding['owner']['directory'] and config['owner_manifest_sha256'] == binding['owner']['manifest_sha256']
    assert config['runtime_directory'] == binding['runtime']
    assert review['actual_terminal'] == terminal and review['owner_result'] == result and review['owner_manifest_sha256'] == binding['owner']['manifest_sha256']
    assert review['restoration_independently_verified'] and not review['canonical_updated'] and not review['native_acceptance'] and not review['backup_deleted_by_reviewer']
    assert review['observation'] == {'browser_executed':False,'observation_complete':False,'build_exit':2}
    for name,digest in review['input_hashes'].items(): assert sha(runtime / name) == digest
    pre = read(runtime / 'CANDIDATE-PRE.json')
    assert pre['snapshot'] == read(root / previous['restoration_handoff']['runtime'] / 'POST.json')
    original_snapshot = read(root / policy['baseline_binding']['directory'] / 'POST.json')
    original_snapshot['index']['raw_index'] = pre['snapshot']['index']['raw_index']
    assert original_snapshot == pre['snapshot'] and pre['controls'] == previous['controls']
    raw = read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert raw == review['raw_index_observation'] and raw['semantic_index_unchanged'] and not raw['canonical_updated']
    expected = copy.deepcopy(pre['snapshot'])
    assert expected['index']['raw_index'] == raw['before']
    expected['index']['raw_index'] = raw['after']
    assert expected == read(runtime / 'POST.json') == review['snapshot'] and expected['index']['head'] == policy['head']
    refresh = read(runtime / 'ROOT-EPOCH-REFRESH.json')
    assert refresh['previous_epoch_sha256'] == previous['controls']['CURRENT-EPOCH.json']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert (refresh['raw_index_before'],refresh['raw_index_after']) == (raw['before'],raw['after'])
    assert refresh['independent_review_sha256'] == binding['review_sha256'] and refresh['independent_review_terminal'] == '46693/973d76/0'
    assert refresh['other_controls_unchanged'] == {k:v for k,v in previous['controls'].items() if k != 'CURRENT-EPOCH.json'}
    assert policy['controls'] == dict(previous['controls'], **{'CURRENT-EPOCH.json':refresh['new_epoch_sha256']})
    backup, cleanup = read(runtime / 'BACKUP-CLEANUP.json'), read(runtime / 'ROOT-BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['verified_original_restoration'] and backup['retained_after_failure'] and not backup['removed']
    assert cleanup['removed'] and cleanup['source_and_app_reverified'] and cleanup['owner_failure_retained']
    assert cleanup['independent_review_sha256'] == binding['review_sha256']
    assert cleanup['reviewer_terminal'] == {k:v for k,v in rt.items() if k != 'active_reviewer_manifest_sha256'}
    assert cleanup['bytes'] == backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(runtime / 'BACKUPS.json')['bytes'] == 1008605176
    restoration = read(runtime / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    roles, old_roles = read(root / policy['owner_directory'] / 'SOURCE-ROLES.json'), read(owner / 'SOURCE-ROLES.json')
    admission = read(root / policy['source_equivalence']['path'])
    assert set(roles) == set(old_roles) == set(pre['sources']) == set(restoration['sources']) == set(review['source_identities'])
    for name,role in roles.items():
        identity = admission['sources'][name]['identity']
        assert pre['sources'][name] == dict(old_roles[name], identity=identity)
        assert role['base_sha256'] == old_roles[name]['base_sha256']
        assert restoration['sources'][name] == review['source_identities'][name] == {'sha256':role['base_sha256'],'identity':identity}
    assert policy['prepared_application_metadata'] == review['restored_application_metadata']
    omit = {'identity','entry_identity'}
    assert {k:v for k,v in policy['prepared_application_metadata'].items() if k not in omit} == {k:v for k,v in previous['prepared_application_metadata'].items() if k not in omit}
    assert policy['prepared_flag_hashes'] == previous['prepared_flag_hashes']
    assert policy['prepared_flag_capture'] == {'path':str((runtime / 'ROOT-REVIEW.json').relative_to(root)),'sha256':binding['review_sha256']}
    return review
