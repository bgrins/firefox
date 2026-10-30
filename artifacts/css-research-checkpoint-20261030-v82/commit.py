import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
BINDINGS = json.loads((HERE / 'BINDINGS.json').read_bytes())
HEAD = BINDINGS['head']
EPOCH = BINDINGS['epoch_sha256']
EXECUTION_ENABLED = True
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda data: hashlib.sha256(data).hexdigest()


def git(*args, env=ENV):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saved_admission():
    read = lambda path: json.loads((ROOT / path).read_bytes())
    binding = BINDINGS['restoration_binding']
    runtime = ROOT / binding['runtime']
    terminal = read(str((runtime / 'ROOT-TERMINAL.json').relative_to(ROOT)))
    result = read(str((runtime / 'CANDIDATE-RESULT.json').relative_to(ROOT)))
    assert sha((runtime / 'FILES.json').read_bytes()) == binding['runtime_manifest_sha256']
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (51189, '2e4e74', 0)
    assert (binding['session_id'], binding['terminal_chunk'], binding['exit']) == (51189, '2e4e74', 0)
    assert terminal['owner_sha256'] == binding['owner_manifest_sha256']
    assert terminal['result_sha256'] == binding['result_sha256'] == sha((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert terminal['build_success'] and terminal['raw_replay_verified'] and terminal['state_and_application_restoration_independently_verified']
    assert (terminal['callbacks_passed'], terminal['callbacks_failed'], terminal['page_endings_ok'], terminal['browser_exit']) == (9, 0, 4, 0)
    assert terminal['all_callbacks_passed'] and terminal['observation_complete'] and terminal['ending'] == 'OK'
    assert terminal['comparison_gate_passed'] is False and terminal['native_acceptance'] is False
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['error'] is None and result['publication_errors'] == [] and result['native_fix_acceptance'] is False
    assert result['success_scope'] == terminal['success_scope'] == 'build, complete observation and restoration; callback PASS is separate'
    phase = runtime / 'candidate-wpt'
    phase_result = read(str((phase / 'RESULT.json').relative_to(ROOT)))
    assessment = read(str((phase / 'ASSESSMENT.json').relative_to(ROOT)))
    replay = read(str((runtime / 'ROOT-REPLAY.json').relative_to(ROOT)))
    hashes = {key: sha((phase / name).read_bytes()) for key, name in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'), ('result_sha256', 'RESULT.json')]}
    assert result['candidate_phase'] == replay['phase'] == hashes
    assert assessment['complete'] and assessment['errors'] == [] and assessment['infrastructure_faults'] == []
    assert replay['candidate_rows'] == assessment['rows'] and replay['candidate_endings'] == assessment['ends']
    assert len(assessment['rows']) == 9 and all(row['status'] == 'PASS' for row in assessment['rows'])
    assert len(assessment['ends']) == 4 and all(row['status'] == 'OK' for row in assessment['ends'])
    assert assessment['comparison_gate_passed'] is replay['comparison_gate_passed'] is phase_result['comparison_gate_passed'] is False
    assert assessment['comparison_errors'] == replay['comparison_errors'] == ['regression identities/status/expectations/intermittents changed']
    assert phase_result['execution_error'] is None and phase_result['preservation_verified'] and phase_result['success'] and phase_result['exit'] == 0
    assert phase_result['native_fix_acceptance'] is False and replay['native_acceptance'] is False
    assert phase_result['success_scope'] == 'complete observation and preservation; comparison verdict retained separately'
    assert replay['outcomes_sha256'] == sha((runtime / 'OUTCOMES.json').read_bytes())
    outcomes = read(str((runtime / 'OUTCOMES.json').relative_to(ROOT)))
    assert outcomes['callbacks_passed'] == 9 and outcomes['callbacks_failed'] == 0 and outcomes['all_callbacks_passed']
    assert outcomes['comparison_gate_passed'] is False and outcomes['comparison_errors'] == assessment['comparison_errors'] and outcomes['native_acceptance'] is False
    backup = read(str((runtime / 'BACKUP-CLEANUP.json').relative_to(ROOT)))
    assert backup['verified_original_restoration'] and backup['removed'] and not backup['retained_after_failure']
    assert backup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    restoration = read(str((runtime / 'RESTORATION.json').relative_to(ROOT)))
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    owner = ROOT / binding['owner_directory']
    assert sha((owner / 'FILES.json').read_bytes()) == terminal['owner_sha256']
    roles = read(str((owner / 'SOURCE-ROLES.json').relative_to(ROOT)))
    expected_roles = {'layout/style/AnimationCollection.h', 'layout/style/GeckoBindings.cpp', 'layout/style/GeckoBindings.h', 'layout/style/ServoTypes.h', 'layout/style/nsAnimationManager.cpp', 'layout/style/nsAnimationManager.h', 'servo/components/style/context.rs', 'servo/components/style/matching.rs'}
    assert set(roles) == set(restoration['sources']) == expected_roles
    pre = read(str((runtime / 'CANDIDATE-PRE.json').relative_to(ROOT)))
    compiled = read(str((runtime / 'candidate-build/RESULT.json').relative_to(ROOT)))
    assert compiled['command_success'] and compiled['browser_build_performed'] and compiled['preservation_verified'] and compiled['error'] is None
    assert compiled['native_sources'] == {name: role['candidate_sha256'] for name, role in roles.items()}
    for name, role in roles.items():
        assert restoration['sources'][name] == {'sha256': role['base_sha256'], 'identity': pre['sources'][name]['identity']}
    assert read(str((runtime / 'PHASES-PRE.json').relative_to(ROOT))) == read(str((runtime / 'PHASES-POST.json').relative_to(ROOT))) == compiled['snapshot']
    refresh = read(binding['root_refresh'])
    assert refresh['after_epoch'] == EPOCH and refresh['full_restored_state_verified']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['accepted_fix_increment'] == 0
    assert refresh['runtime_manifest_sha256'] == binding['runtime_manifest_sha256'] and refresh['observation'] == terminal['raw_index_observation']
    current = read(BINDINGS['root_current_capture']['path'])
    assert current['head'] == HEAD and current['controls'] == BINDINGS['controls'] and current['controls']['CURRENT-EPOCH.json'] == EPOCH
    assert current['raw_index'] == refresh['observation']['after'] and current['runtime_manifest_sha256'] == binding['runtime_manifest_sha256']
    assert current['source_transition_lock_absent'] and current['native_acceptance_increment'] == 0
    supplement = read(BINDINGS['signing_supplement']['path'])
    assert supplement['head'] == HEAD and supplement['raw_index'] == current['raw_index']
    assert supplement['audit_path'] == BINDINGS['completed_untracked_audit']['path'] and supplement['audit_sha256'] == BINDINGS['completed_untracked_audit']['sha256']
    assert supplement['root_current_receipt'] == BINDINGS['root_current_capture']['path'] and supplement['root_current_receipt_sha256'] == BINDINGS['root_current_capture']['sha256']
    assert supplement['status_capture_sha256'] == BINDINGS['audit_status_capture']['sha256'] and supplement['project_working_hashes_rechecked'] == 68
    assert supplement['nested_status'] == ['?? .DS_Store'] and supplement['nested_status_sha256'] == '51ae3af8b9e4fa2c686fff2fcd83b5394fdf9b4d19e13b52323f320f21e8dc68'
    verified = current['full_state_verification']
    assert (verified['session_id'], verified['terminal_chunk'], verified['exit']) == (15435, '25bac7', 0)
    assert sha((ROOT / verified['log']).read_bytes()) == verified['log_sha256']
    for field, target in [('final_state_audit', 'final_state_audit'), ('fresh_application_capture', 'fresh_application_capture'), ('untracked_audit', 'completed_untracked_audit')]:
        assert current[field] == BINDINGS[target]['path'] and current[field + '_sha256'] == BINDINGS[target]['sha256']
    assert current['refresh'] == binding['root_refresh'] and current['refresh_sha256'] == sha((ROOT / binding['root_refresh']).read_bytes())
    audit = read(BINDINGS['final_state_audit']['path'])
    assert audit == read(str((runtime / 'POST.json').relative_to(ROOT)))
    normalized = copy.deepcopy(pre['snapshot'])
    normalized['index']['raw_index'] = refresh['observation']['after']
    assert normalized == audit and audit['index']['head'] == HEAD
    assert supplement['nested_head'] == audit['nested_index']['head']
    assert BINDINGS['root_verification_reported'] == verified
    assert BINDINGS['prepared_application_metadata'] == {name: terminal[name] for name in ['restored_application_entry', 'restored_application_target']}
    fresh_app = read(BINDINGS['fresh_application_capture']['path'])
    assert fresh_app['entry_identity'] == terminal['restored_application_entry']['identity'] and fresh_app['identity'] == terminal['restored_application_target']['identity']
    assert fresh_app['sha256'] == terminal['restored_application_target']['sha256'] and fresh_app['entry_type'] == 40960
    assert fresh_app['resolved'] == fresh_app['symlink_target'] == terminal['restored_application_entry']['target']
    owner_policy = read(str((owner / 'POLICY.json').relative_to(ROOT)))
    original_app = read(owner_policy['original_build']['application_metadata'])
    assert sha((ROOT / owner_policy['original_build']['application_metadata']).read_bytes()) == owner_policy['references'][owner_policy['original_build']['application_metadata']]
    assert original_app['revision'] == fresh_app['revision'] == '20ab7e723b663c0f78c8490e60a6fccc5e65cc99'
    assert original_app['browser_build_id'] == fresh_app['browser_build_id'] == '20261029165244'
    assert original_app['sha256'] == fresh_app['sha256'] == '936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a'
    original_binding = BINDINGS['baseline_binding']
    original = ROOT / original_binding['runtime']
    assert sha((original / 'FILES.json').read_bytes()) == original_binding['runtime_manifest_sha256']
    original_terminal = read(str((original / 'ROOT-TERMINAL.json').relative_to(ROOT)))
    assert (original_terminal['session_id'], original_terminal['terminal_chunk'], original_terminal['exit']) == (65891, '8be757', 0)
    assert original_terminal['callbacks_passed'] == 6 and original_terminal['callbacks_failed'] == 3 and original_terminal['page_endings_ok'] == 4 and original_terminal['browser_exit'] == 1
    assert original_terminal['raw_replay_verified'] and original_terminal['pre_post_equality_verified'] and original_terminal['current_source_binary_control_pins_verified']
    assert original_terminal['native_acceptance'] is False
    assert original_terminal['result_sha256'] == sha((original / 'RESULT.json').read_bytes())
    original_assessment = read(str((original / 'original-wpt/ASSESSMENT.json').relative_to(ROOT)))
    assert replay['original_rows'] == original_assessment['rows']
    assert outcomes['rows'] == [{'original': old, 'candidate': new} for old, new in zip(original_assessment['rows'], assessment['rows'])]
    assert outcomes['original_endings'] == original_assessment['ends'] and outcomes['candidate_endings'] == assessment['ends']
    previous = BINDINGS['previous_attempt']
    prior = ROOT / previous['path']
    failed = read(str((prior / 'result.json').relative_to(ROOT)))
    failed_terminal = read(previous['root_terminal_path'])
    assert sha((prior / 'result.json').read_bytes()) == previous['result_sha256'] == failed_terminal['result_sha256']
    assert sha((ROOT / previous['root_terminal_path']).read_bytes()) == previous['root_terminal_sha256']
    assert failed == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    assert (failed_terminal['session_id'], failed_terminal['terminal_chunk'], failed_terminal['owner_exit']) == (83194, '2e1312', 1)
    assert failed_terminal['head'] == HEAD and failed_terminal['full_current_state_independently_verified']
    assert failed_terminal['owned_temporary_index_removed'] and failed_terminal['source_transition_lock_absent']
    assert sha((prior / 'signing.log').read_bytes()) == failed_terminal['signing_log_sha256']
    reviewer = read(BINDINGS['reviewer_binding']['path'])
    assert reviewer['exit'] == 0 and reviewer['commit_reviewer'] == 'r?#firefox-style-system-reviewers'
    assert sha((ROOT / reviewer['log_path']).read_bytes()) == reviewer['log_sha256']
    return audit


def main():
    assert sys.argv[1:] in [['--check'], ['--run']]
    if sys.argv[1:] == ['--run']:
        assert EXECUTION_ENABLED, 'Draft signing execution is disabled'
    required = ('head', 'epoch_sha256', 'selection_sha256', 'base_selection_sha256', 'restoration_binding', 'reviewer_binding', 'final_state_audit', 'final_roadmap', 'prepared_application_metadata', 'completed_untracked_audit', 'baseline_binding', 'root_verification_reported', 'fresh_application_capture', 'audit_status_capture', 'root_current_capture', 'signing_supplement', 'controls')
    assert all(BINDINGS.get(name) is not None for name in required), 'Final restoration, selection and reviewer bindings are pending'
    assert not BINDINGS['pending_inclusion'], 'Final completed-work selection remains pending'
    assert not (HERE / 'result.json').exists(), 'A completed attempt must not be retried'
    for name, digest in BINDINGS['references'].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == digest, name
    for name in ('reviewer_binding', 'final_state_audit', 'final_roadmap', 'completed_untracked_audit', 'fresh_application_capture', 'audit_status_capture', 'root_current_capture', 'signing_supplement'):
        binding = BINDINGS[name]
        assert BINDINGS['references'][binding['path']] == binding['sha256']
    audit = saved_admission()
    user_audit = json.loads((ROOT / BINDINGS['completed_untracked_audit']['path']).read_bytes())
    assert user_audit['head'] == HEAD and user_audit['untracked_count'] == 563
    assert not user_audit['unexpected_paths'] and not user_audit['missing_paths'] and not user_audit['staged_paths']
    assert user_audit['project_hashes_match_committed_recovery'] and len(user_audit['project_files']) == 68
    assert all(row['matches'] and row['sha256'] == row['committed_sha256'] for row in user_audit['project_files'])
    assert user_audit['unrelated_count'] == 495 and not user_audit['unrelated_metadata_mismatches']
    assert user_audit['tracked_modified_paths'] == ['servo/components/style/custom_properties.rs']
    assert user_audit['provider_sha256'] == '2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
    assert user_audit['project_wpt'] == 53 and user_audit['project_native_and_support'] == 15
    assert user_audit['unrelated_contents_read'] is False and user_audit['ignored_research_artifacts_included'] is False
    assert user_audit['status_capture_sha256'] == BINDINGS['audit_status_capture']['sha256']
    assert sha((ROOT / BINDINGS['audit_status_capture']['path']).read_bytes()) == user_audit['status_capture_sha256']
    assert BINDINGS['references'][user_audit['reference_audit']] == user_audit['reference_sha256']
    assert (HERE / 'WORK-TABLE.md').read_bytes() == (ROOT / Path(BINDINGS['final_roadmap']['path']).parent / 'WORK-TABLE.md').read_bytes()
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert git('symbolic-ref', '--short', 'HEAD').decode().strip() == 'stylo-bloom-verification-2'
    assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
    assert sha((HERE / 'SELECTION.json').read_bytes()) == BINDINGS['selection_sha256']
    selected = json.loads((HERE / 'SELECTION.json').read_bytes())
    assert sha((HERE / 'BASE-SELECTION.json').read_bytes()) == BINDINGS['base_selection_sha256']
    base_selected = json.loads((HERE / 'BASE-SELECTION.json').read_bytes())
    assert len(base_selected) == BINDINGS['base_selected_paths'] and all(selected.get(path) == row for path, row in base_selected.items())
    assert len(selected) == BINDINGS['selected_paths_before_self']
    for manifest_path, digest in BINDINGS['completed_packages'].items():
        manifest = ROOT / manifest_path
        assert manifest_path.startswith('artifacts/') and '..' not in Path(manifest_path).parts
        assert sha(manifest.read_bytes()) == digest
        assert selected[manifest_path]['sha256'] == digest
        for name, record in json.loads(manifest.read_bytes()).items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            path = str((manifest.parent / name).relative_to(ROOT))
            expected = record['sha256'] if isinstance(record, dict) else record
            assert selected[path]['sha256'] == expected
    extras = [HERE / name for name in ['commit.py', 'README.md', 'WORK-TABLE.md', 'RUN-DELTA.patch', 'BINDINGS.json', 'CHECK.json', 'FILES.json', 'SELECTION.json', 'BASE-SELECTION.json']]
    for path in extras:
        selected[str(path.relative_to(ROOT))] = {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
    for path, record in selected.items():
        assert path.startswith('artifacts/') and '..' not in Path(path).parts
        file = ROOT / path
        assert file.is_file() and not file.is_symlink()
        assert file.stat().st_size == record['bytes'] and sha(file.read_bytes()) == record['sha256'], path
    tracked = set(git('ls-files', '-z').decode().split('\0'))
    skipped = []
    for path in list(selected):
        if path in tracked:
            assert sha(git('show', HEAD + ':' + path)) == selected[path]['sha256'], path
            skipped.append(path)
            del selected[path]
    controls = {name: (RUNTIME / name).read_bytes() for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    assert sha(controls['CURRENT-EPOCH.json']) == EPOCH
    assert {name: sha(body) for name, body in controls.items()} == BINDINGS['controls']
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    state = load('state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
    owned = load('owned', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    assert before == audit
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    print(json.dumps({'selected_paths': len(selected), 'identical_committed_paths_skipped': len(skipped), 'full_current_state_verified': True}), flush=True)
    if sys.argv[1] == '--check':
        return
    output = HERE / 'result.json'
    assert not output.exists()
    owned.quiescent(RUNTIME)
    owned.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    lock.mkdir()
    lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
    safe_to_unlock = False
    try:
        with tempfile.TemporaryDirectory(prefix='css-research-v82-', dir='/private/tmp') as directory:
            directory = Path(directory)
            index_env = dict(ENV, GIT_INDEX_FILE=str(directory / 'index'))
            git('read-tree', HEAD, env=index_env)
            paths = directory / 'paths'
            paths.write_bytes(b''.join(path.encode() + b'\0' for path in sorted(selected)))
            add = ['add', '-f', '--pathspec-from-file=' + str(paths), '--pathspec-file-nul']
            git(*add, env=index_env)
            assert set(git('diff', '--cached', '--name-only', env=index_env).decode().splitlines()) == set(selected)
            for path, record in selected.items():
                assert sha(git('show', ':' + path, env=index_env)) == record['sha256']
            tree = git('write-tree', env=index_env).decode().strip()
            assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
            message = directory / 'message'
            message.write_text('No bug - Record masked duration controls and installed Firefox observations. r?#firefox-style-system-reviewers\n')
            with (HERE / 'signing.log').open('x') as stream:
                result = subprocess.run(GIT + ['commit', '--file', str(message)], cwd=ROOT, env=index_env, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                assert git('rev-parse', 'HEAD').decode().strip() == HEAD
                assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
                assert all((RUNTIME / name).read_bytes() == data for name, data in controls.items())
                assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
                assert all(sha((ROOT / path).read_bytes()) == record['sha256'] for path, record in selected.items())
                output.write_text(json.dumps({'committed': False, 'exit': result.returncode, 'real_index_and_canonical_state_unchanged': True}, indent=2) + '\n')
                safe_to_unlock = True
                raise RuntimeError('Signing failed; real index and worktree unchanged')
            commit = git('rev-parse', 'HEAD').decode().strip()
            assert git('rev-parse', commit + '^').decode().strip() == HEAD
            assert git('rev-parse', commit + '^{tree}').decode().strip() == tree
            git(*add)
        with (HERE / 'signature.log').open('x') as stream:
            subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
        actual = state.h.index_state(ROOT, ENV)
        assert actual['working_diff'] == before['index']['working_diff']
        assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
        updated = copy.deepcopy(epoch)
        updated['semantic_index'] = state.h.semantic_index(actual)
        updated['raw_index_observation']['current'] = actual['raw_index']
        updated['committed_research_working_payloads'].update({path: record['sha256'] for path, record in selected.items()})
        updated['counts']['committed_research_payloads'] = len(updated['committed_research_working_payloads'])
        state.a.verify_current(state.h, ROOT, ENV, updated)
        assert all((RUNTIME / name).read_bytes() == data for name, data in controls.items())
        claim = owned.claim(ROOT, str((RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), EPOCH)
        owned.write_owned(ROOT, claim, owned.encoded(updated))
        state.a.verify_current(state.h, ROOT, ENV, updated)
        output.write_text(json.dumps({'committed': True, 'head': commit, 'parent': HEAD, 'signature_verified': True, 'selected_paths': len(selected), 'epoch_sha256': sha(owned.encoded(updated)), 'accepted_fix_increment': 0, 'native_working_diff_preserved': True}, indent=2) + '\n')
        safe_to_unlock = True
    finally:
        if safe_to_unlock:
            assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
            lock.rmdir()


if __name__ == '__main__':
    main()
