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
    assert terminal == binding['terminal']
    assert (terminal['session'], terminal['launch_chunk'], terminal['terminal_chunk'], terminal['exit']) == (48866, '734dd7', 'c3df52', 0)
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
    assert (root_terminal['session'], root_terminal['launch_chunk'], root_terminal['terminal_chunk'], root_terminal['exit']) == (86819, '8afde2', '7e586b', 0)
    assert capsule['sha256'] == review['owner_manifest_sha256']
    assert review['actual_terminal'] == terminal and review['owner_result'] == result
    assert review['restoration_independently_verified'] and review['native_acceptance'] is False
    assert not review['canonical_updated'] and not review['backup_deleted_by_reviewer']
    for name, digest in review['input_hashes'].items():
        assert sha(directory / name) == digest
    reviewer = root / handoff['reviewer_directory']
    authenticate(reviewer, handoff['reviewer_manifest_sha256'])
    assert root_terminal == {'session':86819,'launch_chunk':'8afde2','terminal_chunk':'7e586b','exit':0,'review_sha256':handoff['review_sha256']}
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
    assert refresh['independent_review_sha256'] == handoff['review_sha256'] and refresh['independent_review_terminal'] == '86819/7e586b/0'
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
    assert review['observation']['comparison_to_held_baseline_performed'] is False
    return review


def validate(root, policy):
    binding = policy['restoration_handoff']
    directory = root / binding['directory']
    authenticate(directory,binding['manifest_sha256'])
    owner = root / binding['owner']['directory']
    authenticate(owner,binding['owner']['manifest_sha256'])
    previous = read(owner / 'POLICY.json')
    for key in ('head','baseline_binding','baseline_capsule','original_admission_policy_sha256','execution_handoff','suite_binding','wpt','source_context_pins','accepted_current_payloads','semantic_original_sources','preserved_absent_metadata','preserved_absent_resources','restored_application_revision','prepared_flag_hashes'):
        assert policy[key] == previous[key], key
    historical = copy.deepcopy(policy)
    for key in ('controls','prepared_application_metadata','prepared_flag_capture'):
        historical[key] = previous[key]
    original_review = validate_original(root,historical)
    review = read(directory / 'ROOT-REVIEW.json')
    assert sha(directory / 'ROOT-REVIEW.json') == binding['review_sha256']
    reviewer = root / binding['reviewer']['directory']
    authenticate(reviewer,binding['reviewer']['manifest_sha256'])
    reviewer_policy = read(reviewer / 'POLICY.json')
    actual = review['actual_terminal']
    assert (actual['session'],actual['launch_chunk'],actual['terminal_chunk'],actual['exit']) == (80603,'b130f7','bbb1f1',0)
    assert review['owner_manifest_sha256'] == binding['owner']['manifest_sha256']
    assert read(directory / 'ROOT-OWNER-TERMINAL.json') == dict(actual,active_owner_manifest_sha256=binding['owner']['manifest_sha256'])
    assert read(directory / 'ROOT-REVIEWER-TERMINAL.json') == {'session':92363,'launch_chunk':'1c2cb4','terminal_chunk':'939c49','exit':0,'review_sha256':binding['review_sha256'],'active_reviewer_manifest_sha256':binding['reviewer']['manifest_sha256']}
    assert reviewer_policy['execution_enabled'] and reviewer_policy['actual_terminal'] == actual
    assert reviewer_policy['owner_manifest_sha256'] == binding['owner']['manifest_sha256']
    assert reviewer_policy['owner_directory'] == binding['owner']['directory'] and reviewer_policy['runtime_directory'] == binding['directory']
    result = read(directory / 'CANDIDATE-RESULT.json')
    assert result == review['owner_result'] and sha(directory / 'CANDIDATE-RESULT.json') == actual['result_sha256']
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['error'] is None and result['publication_errors'] == [] and not result['native_fix_acceptance']
    assert review['restoration_independently_verified'] and not review['native_acceptance'] and not review['canonical_updated']
    for name,digest in review['input_hashes'].items():assert sha(directory / name) == digest
    pre,post = read(directory / 'CANDIDATE-PRE.json'),read(directory / 'POST.json')
    assert pre['controls'] == previous['controls'] and pre['snapshot'] == original_review['snapshot']
    assert previous['prepared_application_metadata'] == original_review['restored_application_metadata']
    refresh = read(directory / 'ROOT-EPOCH-REFRESH.json')
    assert refresh['previous_epoch_sha256'] == previous['controls']['CURRENT-EPOCH.json']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert refresh['independent_review_sha256'] == binding['review_sha256'] and refresh['independent_review_terminal'] == '92363/939c49/0'
    assert refresh['other_controls_unchanged'] == {k:v for k,v in previous['controls'].items() if k!='CURRENT-EPOCH.json'}
    expected = copy.deepcopy(pre['snapshot'])
    assert expected['index']['raw_index'] == refresh['raw_index_before']
    expected['index']['raw_index'] = refresh['raw_index_after']
    assert expected == post == review['snapshot']
    assert policy['controls'] == dict(previous['controls'],**{'CURRENT-EPOCH.json':refresh['new_epoch_sha256']})
    raw = read(directory / 'RAW-INDEX-OBSERVATION.json')
    assert raw == review['raw_index_observation'] and raw['semantic_index_unchanged'] and not raw['canonical_updated']
    assert (raw['before'],raw['after']) == (refresh['raw_index_before'],refresh['raw_index_after'])
    restored = read(directory / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    old_roles = read(owner / 'SOURCE-ROLES.json')
    assert restored['sources'] == review['source_identities'] == {name:{'sha256':role['base_sha256'],'identity':pre['sources'][name]['identity']} for name,role in old_roles.items()}
    assert {name:role['base_sha256'] for name,role in old_roles.items()} == {name:policy['source_context_pins'][name] for name in old_roles}
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(directory / 'BACKUPS.json')['bytes']
    assert policy['prepared_application_metadata'] == review['restored_application_metadata']
    omit = {'identity','entry_identity'}
    assert {k:v for k,v in policy['prepared_application_metadata'].items() if k not in omit} == {k:v for k,v in previous['prepared_application_metadata'].items() if k not in omit}
    assert policy['prepared_flag_capture'] == {'path':str((directory/'ROOT-REVIEW.json').relative_to(root)),'sha256':binding['review_sha256']}
    observation = review['observation']
    assert observation['browser_executed'] and observation['observation_complete'] and observation['build_exit'] == 0
    assert observation['outcomes'] == read(directory / 'OUTCOMES.json') and not observation['outcomes']['native_acceptance']
    return review
