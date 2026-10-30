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
    matching = BINDINGS['restoration_binding']
    runtime = ROOT / matching['runtime']
    terminal = json.loads((runtime / 'ROOT-TERMINAL.json').read_bytes())
    result = json.loads((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert sha((runtime / 'FILES.json').read_bytes()) == matching['runtime_manifest_sha256']
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (matching['session_id'], matching['terminal_chunk'], matching['exit'])
    assert terminal['owner_sha256'] == matching['owner_manifest_sha256']
    assert terminal['result_sha256'] == matching['result_sha256'] == sha((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert terminal['exit'] in (0, 1) and terminal['build_success']
    assert terminal['callbacks_passed'] + terminal['callbacks_failed'] == 4 and terminal['ending'] == 'OK'
    assert terminal['complete_records'] == 4 and terminal['private_records_independently_validated']
    assert terminal['raw_replay_verified'] and terminal['state_and_application_restoration_independently_verified']
    assert terminal['native_acceptance'] is False
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['publication_errors'] == [] and result['native_fix_acceptance'] is False
    phase = runtime / 'candidate-wpt'
    phase_result = json.loads((phase / 'RESULT.json').read_bytes())
    assessment = json.loads((phase / 'ASSESSMENT.json').read_bytes())
    replay = json.loads((runtime / 'ROOT-REPLAY.json').read_bytes())
    assert assessment['complete'] and assessment['errors'] == []
    assert replay['candidate_rows'] == assessment['rows'] and replay['candidate_endings'] == assessment['ends']
    assert len(assessment['rows']) == 4 and all(row['status'] in ('PASS', 'FAIL') for row in assessment['rows'])
    assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
    assert terminal['callbacks_passed'] == sum(row['status'] == 'PASS' for row in assessment['rows'])
    assert terminal['callbacks_failed'] == sum(row['status'] == 'FAIL' for row in assessment['rows'])
    hashes = {key: sha((phase / name).read_bytes()) for key, name in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'), ('result_sha256', 'RESULT.json')]}
    assert replay['phase'] == hashes and replay['comparison_errors'] == assessment['comparison_errors']
    passed = assessment['comparison_gate_passed']
    assert passed == terminal['comparison_gate_passed'] == replay['comparison_gate_passed'] == phase_result['comparison_gate_passed'] == phase_result['success'] == result['success']
    assert phase_result['execution_error'] is None and phase_result['preservation_verified'] and phase_result['native_fix_acceptance'] is False
    assert terminal['exit'] == phase_result['exit'] == (0 if passed else 1)
    backup = json.loads((runtime / 'BACKUP-CLEANUP.json').read_bytes())
    assert backup['verified_original_restoration'] and backup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    if passed:
        assert terminal['callbacks_failed'] == 0 and not assessment['comparison_errors']
        assert result['error'] is None and result['candidate_phase'] == hashes
        assert backup['removed'] and not backup['retained_after_failure']
    else:
        assert terminal['callbacks_failed'] > 0 and assessment['comparison_errors']
        assert result['candidate_phase'] is None
        assert result['error'] == repr(AssertionError((None, True, assessment['errors'], assessment['comparison_errors'])))
        assert not backup['removed'] and backup['retained_after_failure']
        removed = json.loads((runtime / 'ROOT-BACKUP-CLEANUP.json').read_bytes())
        assert removed['removed'] and removed['verified_original_restoration'] and removed['inventory_verified_before_removal']
        assert removed['owner_failure_receipt_preserved'] and removed['owned_backup_bytes'] == backup['owned_backup_bytes']
    collection = json.loads((runtime / 'PROGRESS-RECORDS.json').read_bytes())
    assert collection['complete'] and len(collection['records']) == 4 and not collection['missing'] and not collection['errors']
    assert replay['record_comparison_sha256'] == sha((runtime / 'RECORD-COMPARISON.json').read_bytes())
    restoration = json.loads((runtime / 'RESTORATION.json').read_bytes())
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert set(restoration['sources']) == {'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h'}
    refresh = json.loads((ROOT / matching['root_refresh']).read_bytes())
    assert refresh['after_epoch'] == EPOCH and refresh['full_restored_state_verified']
    assert refresh['only_changed_field'] == 'raw_index_observation.current' and refresh['accepted_fix_increment'] == 0
    assert refresh['runtime_manifest_sha256'] == matching['runtime_manifest_sha256']
    assert refresh['observation'] == terminal['raw_index_observation']
    assert BINDINGS['prepared_application_metadata'] == {name: terminal[name] for name in ('restored_application_entry', 'restored_application_target')}
    fresh_app = json.loads((ROOT / BINDINGS['fresh_application_capture']['path']).read_bytes())
    assert fresh_app['entry_identity'] == terminal['restored_application_entry']['identity']
    assert fresh_app['identity'] == terminal['restored_application_target']['identity']
    assert fresh_app['sha256'] == terminal['restored_application_target']['sha256']
    assert fresh_app['entry_type'] == 40960 and fresh_app['symlink_target'] == terminal['restored_application_entry']['target']
    assert fresh_app['resolved'] == terminal['restored_application_entry']['target']
    assert fresh_app['revision'] == '20ab7e723b663c0f78c8490e60a6fccc5e65cc99' and fresh_app['browser_build_id'] == '20261029165244'
    audit = json.loads((ROOT / BINDINGS['final_state_audit']['path']).read_bytes())
    assert audit['index']['head'] == HEAD and audit['index']['raw_index'] == refresh['observation']['after']
    assert audit == json.loads((runtime / 'POST.json').read_bytes())
    pre = json.loads((runtime / 'CANDIDATE-PRE.json').read_bytes())
    normalized = copy.deepcopy(pre['snapshot'])
    normalized['index']['raw_index'] = refresh['observation']['after']
    assert normalized == audit
    original_binding = BINDINGS['baseline_binding']
    original = ROOT / original_binding['runtime']
    assert sha((original / 'FILES.json').read_bytes()) == original_binding['runtime_manifest_sha256']
    original_terminal = json.loads((original / 'ROOT-TERMINAL.json').read_bytes())
    assert (original_terminal['session_id'], original_terminal['terminal_chunk'], original_terminal['exit']) == (81249, '88aff8', 0)
    assert original_terminal['callbacks_passed'] == 0 and original_terminal['callbacks_failed'] == 4 and original_terminal['page_endings_ok'] == 1
    assert original_terminal['raw_replay_verified'] and original_terminal['pre_post_equality_verified'] and original_terminal['current_source_binary_control_pins_verified']
    assert original_terminal['private_records_independently_validated'] and original_terminal['literal_and_initial_calibrations_verified']
    assert original_terminal['complete_records'] == 4 and original_terminal['native_acceptance'] is False
    original_assessment = json.loads((original / 'original-wpt/ASSESSMENT.json').read_bytes())
    assert replay['original_rows'] == original_assessment['rows']
    previous = BINDINGS['previous_attempt']
    prior = ROOT / previous['path']
    failed = json.loads((prior / 'result.json').read_bytes())
    failed_terminal = json.loads((ROOT / previous['root_terminal_path']).read_bytes())
    assert sha((prior / 'result.json').read_bytes()) == previous['result_sha256'] == failed_terminal['result_sha256']
    assert sha((ROOT / previous['root_terminal_path']).read_bytes()) == previous['root_terminal_sha256']
    assert failed == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    assert (failed_terminal['session_id'], failed_terminal['terminal_chunk'], failed_terminal['owner_exit']) == (98813, '41c786', 1)
    assert failed_terminal['head'] == HEAD and failed_terminal['full_current_state_independently_verified']
    assert failed_terminal['owned_temporary_index_removed'] and failed_terminal['source_transition_lock_absent']
    assert sha((prior / 'signing.log').read_bytes()) == failed_terminal['signing_log_sha256']
    reviewer = json.loads((ROOT / BINDINGS['reviewer_binding']['path']).read_bytes())
    assert reviewer['exit'] == 0 and reviewer['commit_reviewer'] == 'r?#firefox-style-system-reviewers'
    assert sha((ROOT / reviewer['log_path']).read_bytes()) == reviewer['log_sha256']
    return audit


def main():
    assert sys.argv[1:] in [['--check'], ['--run']]
    if sys.argv[1:] == ['--run']:
        assert EXECUTION_ENABLED, 'Draft signing execution is disabled'
    required = ('head', 'epoch_sha256', 'selection_sha256', 'base_selection_sha256', 'restoration_binding', 'reviewer_binding', 'final_state_audit', 'final_roadmap', 'prepared_application_metadata', 'completed_untracked_audit', 'baseline_binding', 'root_verification_reported', 'fresh_application_capture', 'audit_status_capture')
    assert all(BINDINGS.get(name) is not None for name in required), 'Final restoration, selection and reviewer bindings are pending'
    assert not BINDINGS['pending_inclusion'], 'Final completed-work selection remains pending'
    assert not (HERE / 'result.json').exists(), 'A completed attempt must not be retried'
    for name, digest in BINDINGS['references'].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == digest, name
    for name in ('reviewer_binding', 'final_state_audit', 'final_roadmap', 'completed_untracked_audit', 'fresh_application_capture', 'audit_status_capture'):
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
    assert user_audit['raw_index'] == audit['index']['raw_index']
    assert user_audit['provider_sha256'] == '2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
    assert user_audit['nested_status'] == ['?? .DS_Store']
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
    assert len(base_selected) == 4456 and all(selected.get(path) == row for path, row in base_selected.items())
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
        with tempfile.TemporaryDirectory(prefix='css-research-v80-', dir='/private/tmp') as directory:
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
            message.write_text('No bug - Record CSS duration dependency experiments and publication preparation. r?#firefox-style-system-reviewers\n')
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
