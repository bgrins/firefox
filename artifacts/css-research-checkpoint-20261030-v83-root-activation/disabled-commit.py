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
EXECUTION_ENABLED = False
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
    historical = load('v82_saved_signer', BINDINGS['historical_signer']['path'])
    audit = historical.saved_admission()
    assert historical.HEAD == HEAD and historical.EPOCH == EPOCH
    assert historical.BINDINGS['controls'] == BINDINGS['controls']
    assert read(BINDINGS['final_state_audit']['path']) == audit
    current = read(BINDINGS['root_current_capture']['path'])
    assert current['audit'] == audit and current['controls'] == BINDINGS['controls']
    assert current['source_transition_lock_absent'] and current['full_current_state_verified'] and current['matched_prior_restoration_audit']
    assert current['untracked_audit'] == BINDINGS['completed_untracked_audit']['path']
    assert current['untracked_audit_sha256'] == BINDINGS['completed_untracked_audit']['sha256']
    previous = BINDINGS['previous_attempt']
    prior = ROOT / previous['path']
    result = read(str((prior / 'result.json').relative_to(ROOT)))
    outcome = read(previous['root_outcome']['path'])
    review = read(previous['independent_review']['path'])
    assert result == {'committed': False, 'exit': 128, 'real_index_and_canonical_state_unchanged': True}
    assert sha((prior / 'result.json').read_bytes()) == previous['result_sha256'] == outcome['result_sha256'] == review['result_sha256']
    assert sha((prior / 'signing.log').read_bytes()) == outcome['signing_log_sha256'] == review['signing_log_sha256']
    assert outcome['head'] == review['head'] == HEAD and outcome['git_exit'] == review['signing_exit'] == 128
    assert not outcome['committed'] and not review['committed']
    assert outcome['outer_owner_terminal_unknown'] is previous['outer_owner_terminal_unknown'] is True
    for field in ['head_unchanged', 'controls_unchanged', 'raw_index_unchanged', 'native_working_diff_preserved', 'untracked_paths_unchanged', 'source_transition_lock_absent', 'owned_temporary_index_removed']:
        assert outcome[field] is True
    assert review['control_hashes'] == BINDINGS['controls'] and review['raw_index'] == audit['index']['raw_index']
    assert review['full_current_state_equals_pre_sign_audit'] and review['full_porcelain_status_equals_pre_sign']
    assert review['source_transition_lock_absent'] and review['staging_empty'] and not review['retry_or_signing_executed']
    assert review['selected_bodies_unchanged'] == historical.BINDINGS['selected_paths_before_self']
    assert review['active_owner_manifest_sha256'] == sha((prior / 'FILES.json').read_bytes())
    assert review['owned_temporary_index_directory_absent'] == '/private/tmp/css-research-v82-bgvjs0hs'
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
        for name, record in json.loads(manifest.read_bytes()).get('files', json.loads(manifest.read_bytes())).items():
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
        with tempfile.TemporaryDirectory(prefix='css-research-v83-', dir='/private/tmp') as directory:
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
            message.write_text('No bug - Record animation-taint interoperability and focused controls. r?#firefox-style-system-reviewers\n')
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
