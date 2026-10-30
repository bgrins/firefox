import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(folder, expected):
    assert sha(folder / 'FILES.json') == expected
    for name, info in read(folder / 'FILES.json').items():
        path = folder / name
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert all(not part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(folder))
        assert path.is_file() and sha(path) == (info if isinstance(info, str) else info['sha256'])


def validate(policy):
    binding = policy['admission_binding']
    assert binding['mode'] == 'restored-three-source-experiment-same-native-head'
    runtime = ROOT / policy['restored_runtime']
    owner = ROOT / policy['restored_owner']
    authenticate(runtime, binding['restored_runtime_manifest'])
    authenticate(owner, binding['restored_owner_manifest'])
    for record in policy['restoration_binding'].values():
        assert policy['references'][record['path']] == sha(ROOT / record['path']) == record['sha256']
    assert policy['restoration_binding']['terminal']['path'] == str((runtime / 'ROOT-TERMINAL.json').relative_to(ROOT))
    previous = read(owner / 'POLICY.json')
    terminal = read(runtime / 'ROOT-TERMINAL.json')
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (34257, 'ffd55f', 1)
    assert terminal['owner_sha256'] == binding['restored_owner_manifest']
    assert terminal['state_and_application_restoration_independently_verified'] and not terminal['native_acceptance']
    assert terminal['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert not result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['error'] == "AssertionError((None, True, [], ['all 32 authored callbacks across the two target fixtures must pass', 'candidate target fixture still fails']))"
    assert result['publication_errors'] == [] and result['empty_staging_preserved']
    assert terminal['build_success'] and terminal['raw_replay_verified'] and terminal['private_records_independently_validated']
    assert (terminal['callbacks_passed'], terminal['callbacks_failed'], terminal['complete_records'], terminal['ending']) == (0, 4, 4, 'OK')
    assert not result['native_fix_acceptance']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    roles = read(owner / 'SOURCE-ROLES.json')
    assert set(restored['sources']) == set(roles) == {'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h', 'servo/components/style/matching.rs'}
    before = read(runtime / 'CANDIDATE-PRE.json')
    for name, record in restored['sources'].items():
        assert record['sha256'] == roles[name]['base_sha256'] == policy['source_role_pins'][name]
        assert record['identity'] == before['sources'][name]['identity']
    manager = 'layout/style/nsAnimationManager.cpp'
    capture = read(ROOT / policy['source_capture'])
    manager_pin = capture['source_files'][manager]['sha256']
    assert policy['source_role_pins'] == dict(previous['source_context_pins'], **{manager: manager_pin})
    built = read(ROOT / policy['build_epoch'])
    assert built['pins'][manager] == manager_pin
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert not cleanup['removed'] and cleanup['verified_original_restoration'] and cleanup['retained_after_failure']
    root_cleanup = read(runtime / 'ROOT-BACKUP-CLEANUP.json')
    assert root_cleanup['removed'] and root_cleanup['verified_original_restoration']
    assert root_cleanup['inventory_verified_before_removal'] and root_cleanup['owner_failure_receipt_preserved']
    assert root_cleanup['owned_backup_bytes'] == cleanup['owned_backup_bytes']
    assert cleanup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    refresh = read(ROOT / policy['restoration_binding']['refresh']['path'])
    assert refresh['runtime_manifest_sha256'] == binding['restored_runtime_manifest']
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert refresh['observation'] == terminal['raw_index_observation'] == read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert refresh['before_epoch'] == previous['controls']['CURRENT-EPOCH.json']
    assert policy['controls'] == dict(previous['controls'], **{'CURRENT-EPOCH.json': refresh['after_epoch']})
    post = read(runtime / 'POST.json')
    expected = copy.deepcopy(before['snapshot'])
    expected['index']['raw_index'] = refresh['observation']['after']
    assert post == expected
    assert policy['head'] == previous['head'] == post['index']['head'] == policy['wpt']['harness_revision']
    assert policy['accepted_current_payloads'] == previous['accepted_current_payloads'] and len(policy['accepted_current_payloads']) == 29
    entry, target = terminal['restored_application_entry'], terminal['restored_application_target']
    app = dict(previous['prepared_application_metadata'])
    assert target['sha256'] == app['sha256'] and entry['target'] == app['symlink_target'] == app['resolved']
    assert entry['kind'] == 'symlink' and target['kind'] == 'file' and target['nlink'] == 1
    assert target['mode'] == 420 and target['size'] == 806
    app.update(entry_identity=entry['identity'], identity=target['identity'],
               build_revision=app['revision'], harness_revision=policy['head'], source_role='original')
    assert policy['prepared_application_metadata'] == app
    assert policy['wpt']['phase_revisions'] == {'original': app['revision']}
    built_app = read(ROOT / binding['original_build_application_metadata'])
    assert all(built_app[key] == app[key] for key in ('sha256', 'revision', 'browser_build_id'))
    fresh_app = read(ROOT / policy['fresh_application_receipt'])
    assert fresh_app == {key: value for key, value in app.items() if key not in ('build_revision', 'harness_revision', 'source_role')}
    signing = read(ROOT / policy['failed_signing_receipt'])
    assert (signing['session_id'], signing['terminal_chunk'], signing['owner_exit'], signing['git_exit']) == (78873, 'f67bbe', 1, 128)
    assert signing['head'] == policy['head'] and signing['epoch_sha256'] == policy['controls']['CURRENT-EPOCH.json']
    assert signing['raw_index'] == post['index']['raw_index']
    assert not signing['committed'] and signing['full_current_state_independently_verified']
    assert signing['owned_temporary_index_removed'] and signing['source_transition_lock_absent']
    failure = ROOT / policy['failed_signing_directory'] / 'result.json'
    assert sha(failure) == signing['result_sha256']
    assert read(failure) == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    fresh = read(ROOT / policy['fresh_state_receipt'])
    assert fresh['head'] == policy['head'] and fresh['epoch_sha256'] == policy['controls']['CURRENT-EPOCH.json']
    assert fresh['raw_index'] == post['index']['raw_index']
    assert fresh['full_current_state_unchanged_after_cross_engine_runs'] and fresh['source_transition_lock_absent']
    assert not fresh['signed_commit_created'] and fresh['native_acceptance_increment'] == 0
    assert not policy['candidate_execution_enabled'] and policy['original_only']
    assert policy['activation_pending'] == ([] if policy['execution_enabled'] else ['root review and activation'])
