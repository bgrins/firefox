import copy
import hashlib
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(directory, digest):
    assert sha(directory / 'FILES.json') == digest
    for name, pin in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = directory / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == (pin['sha256'] if isinstance(pin,dict) else pin)


def validate(root, policy):
    binding = policy['execution_handoff']
    assert binding is not None and policy['restoration_binding'] is not None
    current_pin = binding['current']
    assert current_pin['sha256'] == '5c5340680427683b4620ebb51fdcad8e6058a6da3f295bfd02695cd5da0ab27d'
    assert sha(root / current_pin['path']) == current_pin['sha256']
    current = read(root / current_pin['path'])
    directory = root / policy['restoration_binding']['directory']
    authenticate(directory, policy['restoration_binding']['manifest_sha256'])
    completed = root / binding['completed_owner']['directory']
    authenticate(completed,binding['completed_owner']['manifest_sha256'])
    old = read(completed / 'POLICY.json')
    reviewer = root / binding['reviewer']['directory']
    authenticate(reviewer,binding['reviewer']['manifest_sha256'])
    review_policy = read(reviewer / 'POLICY.json')
    review = read(directory / 'ROOT-REVIEW.json')
    terminal = read(directory / 'ROOT-TERMINAL.json')
    refresh = read(directory / 'ROOT-EPOCH-REFRESH.json')
    result = read(directory / 'CANDIDATE-RESULT.json')
    assert current['restoration_review'] == {'path': str((directory / 'ROOT-REVIEW.json').relative_to(root)), 'sha256': sha(directory / 'ROOT-REVIEW.json')}
    assert terminal == {'session':27191,'launch_chunk':'b5b1ec','terminal_chunk':'a55877','exit':0,'active_reviewer_manifest_sha256':binding['reviewer']['manifest_sha256']}
    assert review['actual_terminal'] == review_policy['actual_terminal']
    actual = review['actual_terminal']
    assert (actual['session'],actual['launch_chunk'],actual['terminal_chunk'],actual['exit']) == (97217,'0b392d','4b7236',0)
    assert actual['result_sha256'] == sha(directory / 'CANDIDATE-RESULT.json')
    assert review['owner_manifest_sha256'] == binding['completed_owner']['manifest_sha256'] == review_policy['owner_manifest_sha256']
    assert review_policy['execution_enabled'] and review_policy['owner_directory'] == binding['completed_owner']['directory']
    assert review_policy['runtime_directory'] == policy['restoration_binding']['directory']
    assert result == review['owner_result'] and result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['error'] is None and result['publication_errors'] == [] and result['empty_staging_preserved'] and not result['native_fix_acceptance']
    assert review['restoration_independently_verified'] and not review['native_acceptance'] and not review['canonical_updated']
    for name,pin in review['input_hashes'].items(): assert sha(directory / name) == pin
    pre = read(directory / 'CANDIDATE-PRE.json')
    assert pre['controls'] == old['controls']
    expected = copy.deepcopy(pre['snapshot'])
    assert refresh['previous_epoch_sha256'] == old['controls']['CURRENT-EPOCH.json']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert refresh['raw_index_before'] == expected['index']['raw_index']
    expected['index']['raw_index'] = refresh['raw_index_after']
    assert expected == read(directory / 'POST.json') == review['snapshot'] == current['snapshot']
    assert refresh['independent_review_sha256'] == sha(directory / 'ROOT-REVIEW.json') and refresh['independent_review_terminal'] == '27191/a55877/0'
    assert refresh['other_controls_unchanged'] == {k:v for k,v in old['controls'].items() if k!='CURRENT-EPOCH.json'}
    assert policy['controls'] == current['controls'] == dict(old['controls'],**{'CURRENT-EPOCH.json':refresh['new_epoch_sha256']})
    assert policy['head'] == current['head'] == old['head'] == expected['index']['head']
    assert current['native_mutation'] is False
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(directory / 'BACKUPS.json')['bytes']
    restoration = read(directory / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {} and restoration['sources'] == review['source_identities']
    source_admission = read(root / policy['source_equivalence']['path'])
    for name,role in read(completed / 'SOURCE-ROLES.json').items():
        assert restoration['sources'][name] == {'sha256':role['base_sha256'],'identity':source_admission['sources'][name]['identity']}
    assert policy['source_context_pins'] == old['source_context_pins']
    assert policy['accepted_current_payloads'] == old['accepted_current_payloads']
    assert policy['prepared_application_metadata'] == current['prepared_application_metadata'] == review['restored_application_metadata']
    omit = {'identity','entry_identity'}
    assert {k:v for k,v in policy['prepared_application_metadata'].items() if k not in omit} == {k:v for k,v in old['prepared_application_metadata'].items() if k not in omit}
    assert policy['prepared_application_metadata']['revision'] == policy['restored_application_revision']
    assert policy['prepared_flag_hashes'] == current['prepared_flag_hashes'] == old['prepared_flag_hashes']
    assert policy['prepared_flag_capture'] == current_pin
    outcomes = read(directory / 'OUTCOMES.json')
    assert outcomes == review['observation']['outcomes'] and not outcomes['native_acceptance']
    assert review['observation']['browser_executed'] and review['observation']['observation_complete']
    assert sum(row['candidate']['status']=='PASS' for row in outcomes['rows']) == outcomes['callbacks_passed']
    assert sum(row['candidate']['status']=='FAIL' for row in outcomes['rows']) == outcomes['callbacks_failed']
    return current
