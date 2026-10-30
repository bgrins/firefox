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
    assert binding['mode'] == 'unchanged-native-head-after-failed-research-signing'
    for name, digest in binding['references'].items():
        assert policy['references'][name] == sha(ROOT / name) == digest
    runtime = ROOT / policy['restored_runtime']
    authenticate(runtime, binding['restored_runtime_manifest'])
    owner = ROOT / policy['restored_owner']
    authenticate(owner, binding['restored_owner_manifest'])
    assert policy['restoration_binding']['terminal'] == {
        'path': str((runtime / 'ROOT-TERMINAL.json').relative_to(ROOT)),
        'sha256': sha(runtime / 'ROOT-TERMINAL.json')}
    assert policy['restoration_binding']['refresh']['sha256'] == sha(ROOT / policy['restoration_binding']['refresh']['path'])
    before = read(owner / 'POLICY.json')
    terminal = read(runtime / 'ROOT-TERMINAL.json')
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (61350, '6fb92f', 0)
    assert terminal['owner_sha256'] == binding['restored_owner_manifest']
    assert terminal['state_and_application_restoration_independently_verified']
    assert terminal['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    result = read(runtime / 'CANDIDATE-RESULT.json')
    assert result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['publication_errors'] == [] and result['empty_staging_preserved']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    roles = read(owner / 'SOURCE-ROLES.json')
    assert set(restored['sources']) == set(roles) and len(roles) == 5
    for name, record in restored['sources'].items():
        assert record['sha256'] == roles[name]['base_sha256']
        assert record['identity'] == read(runtime / 'CANDIDATE-PRE.json')['sources'][name]['identity']
        if name in policy['source_role_pins']:
            assert policy['source_role_pins'][name] == record['sha256']
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration']
    assert cleanup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    refresh = read(ROOT / policy['restoration_binding']['refresh']['path'])
    assert refresh['runtime_manifest_sha256'] == binding['restored_runtime_manifest']
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert refresh['observation'] == terminal['raw_index_observation'] == read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert refresh['before_epoch'] == before['controls']['CURRENT-EPOCH.json']
    assert policy['controls'] == dict(before['controls'], **{'CURRENT-EPOCH.json': refresh['after_epoch']})
    post = read(runtime / 'POST.json')
    expected = copy.deepcopy(read(runtime / 'CANDIDATE-PRE.json')['snapshot'])
    expected['index']['raw_index'] = refresh['observation']['after']
    assert post == expected
    assert policy['head'] == before['head'] == post['index']['head'] == policy['wpt']['harness_revision']
    assert policy['accepted_current_payloads'] == before['accepted_current_payloads'] and len(policy['accepted_current_payloads']) == 29

    fresh_app = read(ROOT / binding['post_signing_application'])
    assert fresh_app == {key: terminal[key] for key in ('restored_application_entry', 'restored_application_target')}
    app = dict(before['prepared_application_metadata'])
    app.update(entry_identity=fresh_app['restored_application_entry']['identity'],
               identity=fresh_app['restored_application_target']['identity'],
               sha256=fresh_app['restored_application_target']['sha256'])
    app.update(build_revision=app['revision'], harness_revision=policy['head'], source_role='original')
    assert policy['prepared_application_metadata'] == app
    assert policy['wpt']['phase_revisions'] == {'original': app['revision']}
    assert fresh_app['restored_application_entry']['target'] == app['symlink_target'] == app['resolved']

    failed = read(ROOT / binding['failed_signing_terminal'])
    assert (failed['session_id'], failed['terminal_chunk'], failed['owner_exit'], failed['git_exit']) == (98813, '41c786', 1, 128)
    assert not failed['committed'] and failed['accepted_fix_increment'] == 0
    assert failed['full_current_state_independently_verified']
    assert failed['owned_temporary_index_removed'] and failed['source_transition_lock_absent']
    assert failed['controls'] == policy['controls'] and failed['epoch_sha256'] == refresh['after_epoch']
    assert failed['head'] == policy['head'] and failed['raw_index'] == post['index']['raw_index']
    assert failed['result_sha256'] == sha(ROOT / policy['failed_signing_result'])
    assert read(ROOT / policy['failed_signing_result']) == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    assert failed['signing_log_sha256'] == sha(ROOT / binding['failed_signing_log'])

    compact = ROOT / policy['historical_compact_original']['directory']
    authenticate(compact, policy['historical_compact_original']['manifest_sha256'])
    compact_state = read(compact / 'POST.json')
    assert compact_state == read(compact / 'PRE.json')
    assert compact_state['controls'] == policy['controls'] and compact_state['head'] == policy['head']
    assert compact_state['index_sha256'] == post['index']['raw_index']
    assert compact_state['diff_sha256'] == post['index']['working_diff'] and compact_state['staged'] == ''
    assert compact_state['pins'][policy['wpt']['application_ini']] == app['sha256']
    built = read(ROOT / policy['build_epoch'])
    assert all(compact_state['pins'][name] == built['pins'][name] for name in compact_state['pins'] if name != policy['wpt']['application_ini'])
    built_app = read(ROOT / binding['original_build_application_metadata'])
    assert built_app['sha256'] == app['sha256'] and built_app['revision'] == app['revision']
    assert built_app['browser_build_id'] == app['browser_build_id']
    compact_terminal = read(compact / 'ROOT-TERMINAL.json')
    assert (compact_terminal['session_id'], compact_terminal['terminal_chunk'], compact_terminal['owner_exit']) == (55405, '658b02', 0)
    assert compact_terminal['complete_browser_evidence'] and compact_terminal['state_preserved']
    schema_path = ROOT / next(iter(policy['record_kinds'].values()))['schema']
    spec = importlib.util.spec_from_file_location('same_element_admission_schema', schema_path)
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    for filename, record in policy['record_kinds'].items():
        envelope = read(compact / 'records' / filename)
        assert envelope['run_id'] == 'css-duration-feedback-original-v2'
        assert schema.validate({key: envelope[key] for key in ('kind', 'observations')}) == record['kind']
    assert not policy['candidate_execution_enabled'] and policy['original_only']
    if policy['execution_enabled']:
        assert policy['activation_pending'] == []
    else:
        assert policy['activation_pending'] == ['root review and activation']
