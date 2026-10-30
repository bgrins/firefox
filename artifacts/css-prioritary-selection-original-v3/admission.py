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
    assert policy['activation_pending'] == []
    assert policy['baseline_binding'] is None and policy['baseline_capsule'] is None
    assert policy['original_admission_policy_sha256'] is None
    binding = policy['execution_handoff']
    assert binding is not None and policy['restoration_binding'] is not None
    current_pin = binding['current']
    assert current_pin['sha256'] == '66716e834dc4bedba746bc7efa48fccb1a909896488aa04dd8792ae98545d86c'
    assert sha(root / current_pin['path']) == current_pin['sha256']
    directory = root / policy['restoration_binding']['directory']
    assert policy['restoration_binding'] == {'directory':'artifacts/css-prioritary-selection-candidate-runtime-1','manifest_sha256':'0f84e91a3ceb15e14570c80a92851a7aab686eb521018c942af97f758c134452'}
    authenticate(directory, policy['restoration_binding']['manifest_sha256'])
    completed = root / binding['completed_owner']['directory']
    authenticate(completed,binding['completed_owner']['manifest_sha256'])
    old = read(completed / 'POLICY.json')
    reviewer = root / binding['reviewer']['directory']
    authenticate(reviewer,binding['reviewer']['manifest_sha256'])
    review_policy = read(reviewer / 'POLICY.json')
    review = read(directory / 'ROOT-REVIEW.json')
    terminal = read(directory / 'ROOT-REVIEWER-TERMINAL.json')
    refresh = read(directory / 'ROOT-EPOCH-REFRESH.json')
    result = read(directory / 'CANDIDATE-RESULT.json')
    current = {'restoration_review':current_pin,'snapshot':review['snapshot'],'controls':dict(old['controls'],**{'CURRENT-EPOCH.json':refresh['new_epoch_sha256']}),'head':old['head'],'prepared_application_metadata':review['restored_application_metadata'],'prepared_flag_hashes':old['prepared_flag_hashes']}
    assert current['restoration_review'] == {'path': str((directory / 'ROOT-REVIEW.json').relative_to(root)), 'sha256': sha(directory / 'ROOT-REVIEW.json')}
    assert terminal == {'session':99202,'launch_chunk':'b5d534','terminal_chunk':'1822df','exit':0,'report_sha256':current_pin['sha256'],'active_reviewer_manifest_sha256':binding['reviewer']['manifest_sha256']}
    assert review['actual_terminal'] == review_policy['actual_terminal']
    actual = review['actual_terminal']
    assert (actual['session'],actual['launch_chunk'],actual['terminal_chunk'],actual['exit']) == (72027,'67e6f7','a877de',0)
    owner_terminal = read(directory / 'ROOT-OWNER-TERMINAL.json')
    assert owner_terminal == dict(actual,active_owner_manifest_sha256=binding['completed_owner']['manifest_sha256'])
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
    assert refresh['independent_review_sha256'] == sha(directory / 'ROOT-REVIEW.json') and refresh['independent_review_terminal'] == '99202/1822df/0'
    assert refresh['other_controls_unchanged'] == {k:v for k,v in old['controls'].items() if k!='CURRENT-EPOCH.json'}
    assert policy['controls'] == current['controls'] == dict(old['controls'],**{'CURRENT-EPOCH.json':refresh['new_epoch_sha256']})
    assert policy['head'] == current['head'] == old['head'] == expected['index']['head']
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(directory / 'BACKUPS.json')['bytes']
    restoration = read(directory / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {} and restoration['sources'] == review['source_identities']
    source_admission = read(root / policy['source_equivalence']['path'])
    for name,role in read(completed / 'SOURCE-ROLES.json').items():
        assert restoration['sources'][name] == {'sha256':role['base_sha256'],'identity':source_admission['sources'][name]['identity']}
    own_roles = read(root / policy['owner_directory'] / 'SOURCE-ROLES.json')
    completed_roles = read(completed / 'SOURCE-ROLES.json')
    assert set(own_roles) == {'servo/components/style/custom_properties.rs'}
    assert set(completed_roles) == set(own_roles) | {'servo/components/style/properties/cascade.rs'}
    assert own_roles == {name: completed_roles[name] for name in own_roles}
    moved = set(completed_roles) - set(own_roles)
    assert policy['restored_context_claims'] == {name: restoration['sources'][name] for name in moved}
    for name in moved:
        record = completed_roles[name]
        assert record['base_sha256'] == policy['source_context_pins'][name] == source_admission['sources'][name]['working_sha256']
        assert policy['restored_context_claims'][name] == {'sha256':record['base_sha256'],'identity':source_admission['sources'][name]['identity']}
        assert source_admission['sources'][name]['head_sha256'] == record['base_sha256']
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
    assert sum(row['status']=='PASS' for row in outcomes['rows']) == outcomes['callbacks_passed'] == 56
    assert sum(row['status']=='FAIL' for row in outcomes['rows']) == outcomes['callbacks_failed'] == 18
    assert len(outcomes['rows']) == 74 and len(outcomes['endings']) == 11
    observed = review['observation']
    assert observed['original_counts'] == {'PASS':46,'FAIL':28} and observed['original_endings'] == 11
    assert observed['target_callbacks'] == 15 and observed['repair_observation_gate'] is False
    assert observed['all85_signatures_equal'] is False and observed['zoom_target_correctness'] is None
    targets = [row for lane in observed['behaviors'].values() for row in lane['target_rows']]
    assert len(targets) == 15 and all(row['status']=='PASS' for row in targets)
    assert observed['behaviors']['ordinary']['repair_observation_gate'] is False
    assert all(observed['behaviors'][lane]['repair_observation_gate'] for lane in ['forced_colors','mozilla_appearance'])
    assert read(directory/'COMPARISON.json')['repair_observation_gate'] is False
    history = read(directory/'ROOT-FAILED-REVIEW.json')
    assert history['actual_terminal'] == {'session':94768,'launch_chunk':'6dd736','terminal_chunk':'295f06','exit':1}
    assert history['restoration_verified'] and not history['observation_complete']
    assert policy['disabled_preimage'] == {'directory':'artifacts/css-prioritary-selection-original77-disabled-v1','manifest_sha256':'c1fcb240a000db0d79064e75eed033860d93f73ea7fe377f67c75f85a53ab7c6'}
    authenticate(root/policy['disabled_preimage']['directory'],policy['disabled_preimage']['manifest_sha256'])
    return current
