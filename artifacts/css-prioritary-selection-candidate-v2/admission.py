import copy
import hashlib
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(directory, expected):
    assert sha(directory / 'FILES.json') == expected
    for name, pin in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = directory / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == (pin['sha256'] if isinstance(pin, dict) else pin)
        if isinstance(pin, dict):
            assert path.stat().st_size == pin['bytes']


def validate_original(root, policy):
    capsule, binding, handoff = policy['baseline_capsule'], policy['baseline_binding'], policy['execution_handoff']
    assert capsule is not None and binding is not None and handoff is not None
    owner, directory = root / capsule['directory'], root / binding['directory']
    authenticate(owner, capsule['sha256'])
    authenticate(directory, binding['manifest_sha256'])
    source = read(owner / 'POLICY.json')
    assert sha(owner / 'POLICY.json') == policy['original_admission_policy_sha256']
    assert source['provider_source_role'] == 'clean-original'
    assert policy['head'] == source['head']
    assert source['suite_binding'] == policy['suite_binding']
    assert source['source_context_pins'] == policy['source_context_pins']
    assert source['accepted_current_payloads'] == policy['accepted_current_payloads']
    assert source['restored_application_revision'] == policy['restored_application_revision']
    assert source['preserved_absent_metadata'] == policy['preserved_absent_metadata']
    assert source['preserved_absent_resources'] == policy['preserved_absent_resources']
    terminal = read(directory / binding['terminal_path'])
    assert terminal.pop('active_owner_manifest_sha256') == capsule['sha256']
    assert terminal == binding['terminal']
    assert (terminal['session'], terminal['launch_chunk'], terminal['terminal_chunk'], terminal['exit']) == (99665, '31e9ed', '08b9e2', 0)
    result = read(directory / 'RESULT.json')
    assert sha(directory / 'RESULT.json') == binding['result_sha256'] == terminal['result_sha256']
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['provider_source_role'] == 'clean-original' and result['build_revision'] == policy['head'] and result['native_fix_acceptance'] is False
    root_terminal = read(directory / 'ROOT-REVIEWER-TERMINAL.json')
    review = read(directory / 'ROOT-REVIEW.json')
    refresh = read(directory / 'ROOT-EPOCH-REFRESH.json')
    assert sha(directory / 'ROOT-REVIEWER-TERMINAL.json') == handoff['root_terminal_sha256']
    assert sha(directory / 'ROOT-REVIEW.json') == handoff['review_sha256']
    assert sha(directory / 'ROOT-EPOCH-REFRESH.json') == handoff['epoch_refresh_sha256']
    assert (root_terminal['session'], root_terminal['launch_chunk'], root_terminal['terminal_chunk'], root_terminal['exit']) == (4433, '018000', '6cf122', 0)
    assert capsule['sha256'] == review['owner_manifest_sha256']
    assert review['actual_terminal'] == terminal and review['owner_result'] == result
    assert review['restoration_independently_verified'] and review['native_acceptance'] is False
    assert not review['canonical_updated'] and not review['backup_deleted_by_reviewer']
    for name, digest in review['input_hashes'].items():
        assert sha(directory / name) == digest
    reviewer = root / handoff['reviewer_directory']
    authenticate(reviewer, handoff['reviewer_manifest_sha256'])
    assert root_terminal == {'session':4433,'launch_chunk':'018000','terminal_chunk':'6cf122','exit':0,'report_sha256':handoff['review_sha256'],'active_reviewer_manifest_sha256':handoff['reviewer_manifest_sha256']}
    reviewer_policy = read(reviewer / 'POLICY.json')
    assert reviewer_policy['actual_terminal'] == terminal and reviewer_policy['execution_enabled']
    assert reviewer_policy['owner_manifest_sha256'] == capsule['sha256']
    assert reviewer_policy['owner_directory'] == capsule['directory'] and reviewer_policy['runtime_directory'] == binding['directory']
    pre, post = read(directory / 'BUILD-PRE.json'), read(directory / 'POST.json')
    assert pre['controls'] == source['controls']
    raw = read(directory / 'RAW-INDEX-OBSERVATION.json')
    assert review['raw_index_observation'] == raw and raw['semantic_index_unchanged'] and not raw['canonical_updated']
    expected = copy.deepcopy(pre['snapshot'])
    assert expected['index']['raw_index'] == raw['before']
    expected['index']['raw_index'] = raw['after']
    assert expected == post == review['snapshot']
    assert post['index']['head'] == policy['head'] and post['working_sources_binaries_research_preserved']
    assert refresh['previous_epoch_sha256'] == source['controls']['CURRENT-EPOCH.json']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert (refresh['raw_index_before'], refresh['raw_index_after']) == (raw['before'], raw['after'])
    assert refresh['independent_review_sha256'] == handoff['review_sha256'] and refresh['independent_review_terminal'] == '4433/6cf122/0'
    assert refresh['other_controls_unchanged'] == {k:v for k,v in source['controls'].items() if k != 'CURRENT-EPOCH.json'}
    assert policy['controls'] == dict(source['controls'], **{'CURRENT-EPOCH.json': refresh['new_epoch_sha256']})
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['verified_original_restoration'] and backup['removed'] and not backup['retained_after_failure']
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(directory / 'BACKUPS.json')['bytes']
    restoration = read(directory / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    provider = 'servo/components/style/custom_properties.rs'
    role = read(owner / 'SOURCE-ROLES.json')[provider]
    assert role['candidate_sha256'] == policy['semantic_original_sources'][provider]
    assert role['base_sha256'] == policy['source_context_pins'][provider]
    assert restoration['sources'] == review['source_identities'] == {provider: {'sha256': role['base_sha256'], 'identity': pre['sources'][provider]['identity']}}
    assert policy['prepared_application_metadata'] == review['restored_application_metadata']
    omit = {'identity', 'entry_identity'}
    assert {k:v for k,v in policy['prepared_application_metadata'].items() if k not in omit} == {k:v for k,v in source['prepared_application_metadata'].items() if k not in omit}
    assert policy['prepared_application_metadata']['revision'] == policy['restored_application_revision']
    assert policy['prepared_flag_hashes'] == source['prepared_flag_hashes']
    assert policy['prepared_flag_capture'] == {'path': str((directory / 'ROOT-REVIEW.json').relative_to(root)), 'sha256': handoff['review_sha256']}
    assert review['observation']['browser_executed'] and review['observation']['observation_complete'] and review['observation']['build_exit'] == 0
    assert review['observation']['outcomes'] == read(directory / 'OUTCOMES.json')
    assert review['observation']['lanes']['ordinary']['zoom_capture_complete']
    assert review['observation_complete']
    assert all(lane['observation_complete'] and lane['resources_and_metadata_verified'] for lane in review['observation']['lanes'].values())
    return review


def validate(root, policy):
    assert policy['activation_pending']==[]
    review=validate_original(root,policy)
    assert policy['restoration_binding']=={'directory':policy['baseline_binding']['directory'],'manifest_sha256':policy['baseline_binding']['manifest_sha256']}
    import importlib.util
    path=root/policy['owner_directory']/'comparison.py'
    spec=importlib.util.spec_from_file_location('actual_original74_replay',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    lanes=module.replay_all(root,policy)
    assert set(lanes)==set(policy['lane_order'])
    return review
