import copy
import hashlib
import importlib.util
import json
from pathlib import Path

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(directory, digest):
    assert sha(directory / 'FILES.json') == digest
    for name, record in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = directory / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_original(root, policy, roles):
    capsule, binding, handoff = policy['baseline_capsule'], policy['baseline_binding'], policy['execution_handoff']
    assert binding is not None and handoff is not None
    owner, directory = root / capsule['directory'], root / binding['directory']
    authenticate(owner, capsule['sha256'])
    authenticate(directory, binding['manifest_sha256'])
    source = read(owner / 'POLICY.json')
    assert source['owner_directory'] == capsule['directory']
    assert source['head'] == policy['baseline_head']
    assert source['suite_binding'] == policy['suite_binding'] and source['capture_binding'] == policy['capture_binding']
    original_roles = read(owner / 'SOURCE-ROLES.json')
    assert set(original_roles) == set(roles)
    for name, row in roles.items():
        assert original_roles[name]['base_sha256'] == original_roles[name]['candidate_sha256'] == row['base_sha256']
    terminal = read(directory / binding['terminal_path'])
    assert sha(directory / binding['terminal_path']) == binding['terminal_sha256']
    assert terminal == binding['terminal'] and terminal['exit'] == 0
    assert terminal['session'] == policy['expected_original_run']['session']
    assert terminal['launch_chunk'] == policy['expected_original_run']['launch_chunk'] and terminal['terminal_chunk']
    result = read(directory / 'RESULT.json')
    assert sha(directory / 'RESULT.json') == binding['result_sha256'] == terminal['result_sha256']
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['empty_staging_preserved'] and result['publication_errors'] == [] and result['error'] is None
    assert result['native_fix_acceptance'] is False and result['build_revision'] == policy['baseline_head']
    assert result['provider_source_role'] == 'published-color-image-original'
    review = read(directory / handoff['review_path'])
    assert sha(directory / handoff['review_path']) == handoff['review_sha256']
    assert review['owner_manifest_sha256'] == capsule['sha256']
    assert review['actual_terminal'] == terminal and review['owner_result'] == result
    assert review['restoration_independently_verified'] and review['observation_complete']
    assert review['native_acceptance'] is False and not review['canonical_updated'] and not review['backup_deleted_by_reviewer']
    for name, digest in review['input_hashes'].items():
        assert sha(directory / name) == digest
    reviewer = root / handoff['reviewer']['directory']
    authenticate(reviewer, handoff['reviewer']['manifest_sha256'])
    config = read(reviewer / 'POLICY.json')
    assert config['execution_enabled'] and not config['mutations_allowed'] and not config['epoch_publication_allowed']
    assert config['owner_directory'] == capsule['directory'] and config['owner_manifest_sha256'] == capsule['sha256']
    assert config['runtime_directory'] == binding['directory']
    assert config['expected_session'] == terminal['session'] and config['expected_launch'] == terminal['launch_chunk']
    review_terminal = read(directory / handoff['terminal_path'])
    assert sha(directory / handoff['terminal_path']) == handoff['terminal_sha256']
    assert review_terminal == handoff['terminal'] and review_terminal['exit'] == 0
    assert review_terminal['review_sha256'] == handoff['review_sha256']
    pre, post = read(directory / 'BUILD-PRE.json'), read(directory / 'POST.json')
    raw = read(directory / 'RAW-INDEX-OBSERVATION.json')
    assert raw == review['raw_index_observation'] and raw['semantic_index_unchanged'] and not raw['canonical_updated']
    assert raw['before'] == raw['after'] == pre['snapshot']['index']['raw_index']
    assert pre['snapshot'] == post == review['snapshot']
    assert pre['controls'] == source['controls']
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup == review['backup'] and backup['removed'] and not backup['retained_after_failure']
    assert backup['verified_original_restoration']
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(directory / 'BACKUPS.json')['bytes']
    restoration = read(directory / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    expected_sources = {name: {'sha256': row['base_sha256'], 'identity': pre['sources'][name]['identity']} for name, row in roles.items()}
    assert restoration['sources'] == review['source_identities'] == expected_sources
    original_capture = read(root / source['current_binding']['path'])
    assert sha(root / source['current_binding']['path']) == source['current_binding']['sha256']
    assert original_capture['snapshot'] == pre['snapshot']
    return source, review, original_capture


def validate_bridge(root, policy, source, review):
    bridge = policy['checkpoint_bridge']
    directory = root / bridge['directory']
    authenticate(directory, bridge['manifest_sha256'])
    receipt = bridge['receipt']
    assert sha(root / receipt['path']) == receipt['sha256']
    result = read(root / receipt['path'])
    assert result['committed'] and result['signature_verified'] and result['native_working_diff_preserved']
    assert result['accepted_fix_increment'] == 0
    assert result['parent'] == source['head'] and result['head'] == policy['head']
    binding = read(directory / 'BINDINGS.json')
    assert policy['references']['artifacts/css-local-signing-20261027-v1/allowed-signers'] == binding['references']['artifacts/css-local-signing-20261027-v1/allowed-signers']
    assert not binding['pending_current_admission']
    assert binding['head'] == source['head'] and binding['controls'] == source['controls']
    assert sha(root / binding['current_capture']) == binding['current_capture_sha256']
    before = read(root / binding['current_capture'])
    assert before['audit'] == review['snapshot'] and before['controls'] == source['controls']
    assert before['full_current_state_verified'] and before['source_transition_lock_absent']
    assert before['tracked_modified_paths'] == before['staged_paths'] == []
    selected = read(directory / 'SELECTION.json')
    assert sha(directory / 'SELECTION.json') == binding['selection_sha256']
    selected.update({str((directory / name).relative_to(root)): record for name, record in read(directory / 'FILES.json').items()})
    selected[str((directory / 'FILES.json').relative_to(root))] = {'sha256': sha(directory / 'FILES.json')}
    assert sorted(selected) == bridge['committed_paths'] and len(selected) == result['selected_paths']
    assert all(name.startswith('artifacts/') for name in selected)
    for name, record in selected.items():
        assert sha(root / name) == record['sha256']
    return result


def validate_current(root, policy, roles):
    source, review, original = validate_original(root, policy, roles)
    checkpoint = validate_bridge(root, policy, source, review)
    binding = policy['current_binding']
    assert binding is not None and sha(root / binding['path']) == binding['sha256']
    capture = read(root / binding['path'])
    assert capture['full_current_state_verified'] and capture['source_transition_lock_absent']
    assert capture['published_image_ancestor_verified'] and capture['sources_match_head']
    assert capture['prepared_manifest_sha256'] == policy['baseline_capsule']['sha256']
    assert capture['capture_helper_sha256'] == sha(root / policy['baseline_capsule']['directory'] / 'capture_current.py')
    assert capture['checkpoint_receipt'] == policy['checkpoint_bridge']['receipt'] and capture['checkpoint'] == checkpoint
    for name in ('role', 'prototype_overlay_state', 'sources', 'payload_claims', 'epoch_payload_pins', 'installed_identities', 'binaries'):
        assert capture[name] == original[name], name
    expected = copy.deepcopy(review['snapshot'])
    for key in ('head', 'entries', 'raw_index'):
        expected['index'][key] = capture['snapshot']['index'][key]
    assert expected == capture['snapshot'] and capture['snapshot']['index']['head'] == checkpoint['head']
    assert capture['controls'] == policy['controls'] and capture['controls']['CURRENT-EPOCH.json'] == checkpoint['epoch_sha256']
    for name in ('OWNED.json', 'ROLE.json'):
        assert capture['controls'][name] == source['controls'][name]
    assert capture['flag_hashes']['nested'] == original['flag_hashes']['nested']
    assert capture['application_metadata'] == review['restored_application_metadata']
    assert set(capture['extras']) == set(policy['extra_backup_paths']) and len(capture['app_inventory_sha256']) == 64
    assert policy['accepted_current_payloads'] == {
        name: {'sha256': row['owned_sha256'], 'identity': row['identity']}
        for name, row in capture['payload_claims'].items()}
    return capture
