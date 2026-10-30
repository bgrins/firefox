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
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (45913, 'd24784', 0)
    assert terminal['owner_sha256'] == binding['restored_owner_manifest']
    assert terminal['state_and_application_restoration_independently_verified'] and not terminal['native_acceptance']
    assert terminal['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['error'] is None and result['publication_errors'] == [] and result['empty_staging_preserved']
    assert not result['native_fix_acceptance']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    roles = read(owner / 'SOURCE-ROLES.json')
    assert set(restored['sources']) == set(roles) == {'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h', 'servo/components/style/matching.rs'}
    before = read(runtime / 'CANDIDATE-PRE.json')
    for name, record in restored['sources'].items():
        assert record['sha256'] == roles[name]['base_sha256'] == policy['source_role_pins'][name]
        assert record['identity'] == before['sources'][name]['identity']
    assert policy['source_role_pins'] == previous['source_context_pins']
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
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
    audit = read(ROOT / policy['postrun_audit'])
    assert policy['references'][policy['postrun_audit']] == sha(ROOT / policy['postrun_audit'])
    assert audit['candidate_runtime_manifest'] == binding['restored_runtime_manifest']
    assert audit['head'] == policy['head'] and audit['controls'] == policy['controls']
    assert audit['staged_paths'] == [] and audit['tracked_modified_paths'] == ['servo/components/style/custom_properties.rs']
    assert audit['provider_sha256'] == policy['source_role_pins']['servo/components/style/custom_properties.rs']
    assert audit['transition_lock_absent'] and audit['experiment_backup_absent']
    assert audit['untracked_count'] == 563 and audit['unexpected_paths'] == audit['missing_paths'] == []
    assert audit['project_hashes_match_previous_committed_recovery_audit'] and audit['unrelated_metadata_unchanged']
    assert not policy['candidate_execution_enabled'] and policy['original_only']
    assert policy['activation_pending'] == ([] if policy['execution_enabled'] else ['root review and activation'])
