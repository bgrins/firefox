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
BASE_INVENTORY = ROOT / 'artifacts/css-continuation-completed-inventory-20261029-v77'
INVENTORY = ROOT / 'artifacts/css-continuation-completed-inventory-20261029-v78'
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


def main():
    assert sys.argv[1:] in [['--check'], ['--run']]
    if sys.argv[1:] == ['--run']:
        assert EXECUTION_ENABLED, 'Draft signing execution is disabled'
    required = ('head', 'epoch_sha256', 'selection_sha256', 'inventory_manifest_sha256', 'restoration_binding', 'reviewer_binding', 'final_state_audit', 'final_roadmap', 'prepared_application_metadata', 'completed_untracked_audit', 'application_capture')
    assert all(BINDINGS.get(name) is not None for name in required), 'Final restoration, selection and reviewer bindings are pending'
    assert not (HERE / 'result.json').exists(), 'A completed attempt must not be retried'
    for name, digest in BINDINGS['references'].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == digest, name
    for name in ('reviewer_binding', 'final_state_audit', 'final_roadmap', 'completed_untracked_audit', 'application_capture'):
        binding = BINDINGS[name]
        assert BINDINGS['references'][binding['path']] == binding['sha256']
    matching = BINDINGS['restoration_binding']
    runtime = ROOT / matching['runtime']
    terminal = json.loads((runtime / 'ROOT-TERMINAL.json').read_bytes())
    result = json.loads((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert sha((runtime / 'FILES.json').read_bytes()) == matching['runtime_manifest_sha256']
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (matching['session_id'], matching['terminal_chunk'], matching['exit']) == (8127, 'bef82f', 0)
    assert terminal['result_sha256'] == sha((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert terminal['callbacks_failed'] == 0 and terminal['callbacks_passed'] == 9 and terminal['page_endings_ok'] == 3
    assert terminal['comparison_gate_passed'] is True and terminal['native_acceptance'] is False
    assert terminal['raw_replay_verified'] and terminal['state_and_application_restoration_independently_verified']
    assert result['success'] is True and result['restoration_verified'] and not result['publication_errors']
    analysis_path = runtime / 'RECORD-ANALYSIS.json'
    assert terminal['record_analysis_sha256'] == sha(analysis_path.read_bytes())
    analysis = json.loads(analysis_path.read_bytes())
    assert analysis['collection_complete'] and len(analysis['records']) == 9
    assert {name for name, item in analysis['records'].items() if not item['observation']['first_sample_matches_fixed_oracle']} == {'two-hop-ordinary', 'two-hop-animated', 'lh-chain-ordinary', 'lh-chain-animated'}
    cleanup = json.loads((runtime / 'BACKUP-CLEANUP.json').read_bytes())
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and cleanup['retained_after_failure'] is False
    assert cleanup['owned_backup_bytes'] == terminal['backup_removed_bytes'] == 1008605176
    refresh = json.loads((ROOT / matching['root_refresh']).read_bytes())
    assert refresh['after_epoch'] == EPOCH and refresh['full_restored_state_verified']
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert refresh['runtime_manifest_sha256'] == matching['runtime_manifest_sha256']
    assert refresh['observation'] == terminal['raw_index_observation']
    assert BINDINGS['prepared_application_metadata'] == {name: terminal[name] for name in ('restored_application_entry', 'restored_application_target')}
    reviewer = json.loads((ROOT / BINDINGS['reviewer_binding']['path']).read_bytes())
    assert reviewer['exit'] == 0 and reviewer['commit_reviewer'] == 'r?#firefox-style-system-reviewers'
    assert sha((ROOT / reviewer['log_path']).read_bytes()) == reviewer['log_sha256']
    audit = json.loads((ROOT / BINDINGS['final_state_audit']['path']).read_bytes())
    assert audit['epoch_sha256'] == EPOCH and audit['snapshot']['index']['head'] == HEAD
    assert audit['snapshot']['index']['raw_index'] == refresh['observation']['after']
    assert audit['snapshot'] == json.loads((runtime / 'POST.json').read_bytes())
    assert json.loads((ROOT / BINDINGS['application_capture']['path']).read_bytes()) == BINDINGS['prepared_application_metadata']
    user_audit = json.loads((ROOT / BINDINGS['completed_untracked_audit']['path']).read_bytes())
    assert user_audit['head'] == HEAD and user_audit['untracked_count'] == 563
    assert not user_audit['unexpected_paths'] and not user_audit['missing_paths'] and not user_audit['staged_paths']
    assert user_audit['project_hashes_match_committed_recovery'] and len(user_audit['project_files']) == 68
    assert all(row['matches'] and row['sha256'] == row['committed_sha256'] for row in user_audit['project_files'])
    assert user_audit['unrelated_count'] == 495 and not user_audit['unrelated_metadata_mismatches']
    assert user_audit['status_stable_on_repeat'] and user_audit['tracked_modified_paths'] == ['servo/components/style/custom_properties.rs']
    assert (HERE / 'WORK-TABLE.md').read_bytes() == (ROOT / Path(BINDINGS['final_roadmap']['path']).parent / 'WORK-TABLE.md').read_bytes() + BINDINGS['work_table_addendum'].encode()
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert git('symbolic-ref', '--short', 'HEAD').decode().strip() == 'stylo-bloom-verification-2'
    assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
    assert sha((BASE_INVENTORY / 'SELECTION.json').read_bytes()) == BINDINGS['selection_sha256']
    selected = json.loads((BASE_INVENTORY / 'SELECTION.json').read_bytes())
    assert sha((BASE_INVENTORY / 'FILES.json').read_bytes()) == BINDINGS['base_inventory_manifest_sha256']
    assert sha((INVENTORY / 'DELTA-SELECTION.json').read_bytes()) == BINDINGS['delta_selection_sha256']
    delta = json.loads((INVENTORY / 'DELTA-SELECTION.json').read_bytes())
    assert len(selected) == 3676 and len(delta) == 250 and not set(selected).intersection(delta)
    selected.update(delta)
    audit_path = ROOT / BINDINGS['completed_untracked_audit']['path']
    selected[str(audit_path.relative_to(ROOT))] = {'sha256': sha(audit_path.read_bytes()), 'bytes': audit_path.stat().st_size}
    assert sha((INVENTORY / 'FILES.json').read_bytes()) == BINDINGS['inventory_manifest_sha256']
    inventory_files = json.loads((INVENTORY / 'FILES.json').read_bytes())
    for name, record in inventory_files.items():
        assert sha((INVENTORY / name).read_bytes()) == record['sha256']
        assert (INVENTORY / name).stat().st_size == record['bytes']
    extras = [INVENTORY / name for name in [*inventory_files, 'FILES.json']]
    extras += [ROOT / BINDINGS[name]['path'] for name in ('final_state_audit', 'application_capture')]
    for manifest_path, digest in BINDINGS['completed_packages'].items():
        assert manifest_path.startswith('artifacts/') and '..' not in Path(manifest_path).parts
        manifest = ROOT / manifest_path
        assert sha(manifest.read_bytes()) == digest
        extras.append(manifest)
        for name, record in json.loads(manifest.read_bytes()).items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            path = manifest.parent / name
            expected = record['sha256'] if isinstance(record, dict) else record
            assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected
            extras.append(path)
    extras += [HERE / name for name in ['commit.py', 'README.md', 'WORK-TABLE.md', 'RUN-DELTA.patch', 'BINDINGS.json', 'CHECK.json', 'FILES.json']]
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
    assert before == audit['snapshot']
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
        with tempfile.TemporaryDirectory(prefix='css-research-v78-', dir='/private/tmp') as directory:
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
            message.write_text('No bug - Record CSS duration progress and first-read research. r?#firefox-style-system-reviewers\n')
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
