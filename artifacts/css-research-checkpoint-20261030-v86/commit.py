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



def verify_blob(stream, record):
    header = stream.readline(4097)
    assert header.endswith(b"\n") and len(header) <= 4096
    fields = header[:-1].split(b" ")
    assert len(fields) == 3 and fields[1] == b"blob"
    assert len(fields[0]) in (40, 64) and all(c in b"0123456789abcdef" for c in fields[0])
    assert fields[2].isdigit() and int(fields[2]) == record['bytes']
    remaining = record['bytes']
    digest = hashlib.sha256()
    while remaining:
        part = stream.read(min(remaining, 1024 * 1024))
        assert part
        digest.update(part)
        remaining -= len(part)
    assert stream.read(1) == b"\n" and digest.hexdigest() == record['sha256']


def verify_blobs(requests, env=ENV):
    if not requests:
        return
    for spec, record in requests:
        assert spec and not any(c in spec for c in "\n\r\0")
        assert type(record['bytes']) is int and record['bytes'] >= 0
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(GIT + ['cat-file', '--batch'], cwd=ROOT, env=env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors)
        try:
            for spec, record in requests:
                process.stdin.write(spec.encode() + b"\n")
                process.stdin.flush()
                verify_blob(process.stdout, record)
            process.stdin.close()
            assert process.stdout.read(1) == b""
            assert process.wait() == 0
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait()
            process.stdout.close()
            if not process.stdin.closed:
                process.stdin.close()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saved_admission():
    assert not BINDINGS['pending_current_admission']
    assert HEAD is not None and EPOCH is not None and BINDINGS['controls'] is not None
    current = json.loads((ROOT / BINDINGS['current_capture']).read_bytes())
    runtime = ROOT / BINDINGS['restoration_runtime']
    review = json.loads((runtime / 'ROOT-REVIEW.json').read_bytes())
    refresh = json.loads((runtime / 'ROOT-EPOCH-REFRESH.json').read_bytes())
    cleanup = json.loads((runtime / 'ROOT-BACKUP-CLEANUP.json').read_bytes())
    result = json.loads((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    pre = json.loads((runtime / 'CANDIDATE-PRE.json').read_bytes())
    owner = ROOT / BINDINGS['restored_owner']
    owner_policy = json.loads((owner / 'POLICY.json').read_bytes())
    assert sha((owner / 'FILES.json').read_bytes()) == review['owner_manifest_sha256']
    assert current['full_current_state_verified'] and current['source_transition_lock_absent']
    assert current['controls'] == BINDINGS['controls']
    assert current['audit'] == review['snapshot'] == json.loads((runtime / 'POST.json').read_bytes())
    assert current['restoration_runtime'] == BINDINGS['restoration_runtime']
    assert current['runtime_manifest_sha256'] == sha((runtime / 'FILES.json').read_bytes())
    assert current['restoration_review_sha256'] == sha((runtime / 'ROOT-REVIEW.json').read_bytes())
    assert review['restoration_independently_verified'] and not review['native_acceptance']
    assert not review['canonical_updated'] and result == review['owner_result']
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert not result['success'] and result['error'] == 'AssertionError()'
    assert result['candidate_phase'] is None and result['publication_errors'] == [] and not result['native_fix_acceptance']
    assert not review['observation_complete']
    actual = review['actual_terminal']
    assert (actual['session'], actual['launch_chunk'], actual['terminal_chunk'], actual['exit']) == (8402, 'b88cb6', '06fb14', 1)
    assert actual['result_sha256'] == sha((runtime / 'CANDIDATE-RESULT.json').read_bytes())
    assert json.loads((runtime / 'ROOT-OWNER-TERMINAL.json').read_bytes()) == actual
    terminal = json.loads((runtime / 'ROOT-REVIEW-TERMINAL.json').read_bytes())
    assert (terminal['session'], terminal['launch_chunk'], terminal['terminal_chunk'], terminal['exit']) == (8389, '508559', '8aaeb3', 0)
    assert terminal['review_sha256'] == sha((runtime / 'ROOT-REVIEW.json').read_bytes())
    for name, digest in review['input_hashes'].items():
        assert sha((runtime / name).read_bytes()) == digest
    restoration = json.loads((runtime / 'RESTORATION.json').read_bytes())
    assert not restoration['errors'] and restoration['sources'] == review['source_identities']
    roles = json.loads((owner / 'SOURCE-ROLES.json').read_bytes())
    assert len(roles) == 3 and set(roles) == set(pre['sources']) == set(restoration['sources'])
    for name, role in roles.items():
        assert pre['sources'][name] == dict(role, identity=restoration['sources'][name]['identity'])
        assert restoration['sources'][name]['sha256'] == role['base_sha256'] == sha((ROOT / role['base_capture']).read_bytes())
    backup = review['backup']
    assert not backup['removed'] and backup['retained_after_failure'] and backup['verified_original_restoration']
    assert backup['owned_backup_bytes'] == cleanup['owned_backup_bytes'] == 1008605176
    assert cleanup['removed'] and cleanup['original_owner_backup_receipt_preserved']
    assert cleanup['restoration_review_sha256'] == sha((runtime / 'ROOT-REVIEW.json').read_bytes())
    assert refresh['changed_field'] == 'raw_index_observation.current' and refresh['semantic_index_unchanged']
    assert refresh['restoration_independently_verified']
    assert refresh['before'] == owner_policy['controls']['CURRENT-EPOCH.json']
    assert refresh['after'] == EPOCH == current['controls']['CURRENT-EPOCH.json']
    assert {k:v for k,v in current['controls'].items() if k != 'CURRENT-EPOCH.json'} == {k:v for k,v in owner_policy['controls'].items() if k != 'CURRENT-EPOCH.json'}
    assert pre['controls'] == owner_policy['controls']
    expected = copy.deepcopy(pre['snapshot'])
    assert expected['index']['raw_index'] == refresh['raw_before'] == review['raw_index_observation']['before']
    expected['index']['raw_index'] = refresh['raw_after']
    assert refresh['raw_after'] == review['raw_index_observation']['after']
    assert expected == current['audit'] and expected['index']['head'] == HEAD
    audit_path = ROOT / BINDINGS['completed_untracked_audit']['path']
    audit = json.loads(audit_path.read_bytes())
    assert current['untracked_audit'] == BINDINGS['completed_untracked_audit']['path']
    assert current['untracked_audit_sha256'] == sha(audit_path.read_bytes())
    assert audit['head'] == HEAD and audit['untracked_count'] == 563
    assert not audit['unexpected_paths'] and not audit['missing_paths'] and not audit['staged_paths']
    assert audit['project_hashes_match_committed_recovery'] and len(audit['project_files']) == 68
    assert not audit['unrelated_metadata_mismatches'] and audit['unrelated_count'] == 495
    assert audit['tracked_modified_paths'] == ['servo/components/style/custom_properties.rs']
    prior_dir = ROOT / 'artifacts/css-research-checkpoint-20261030-v85'
    prior = json.loads((ROOT / 'artifacts/css-research-checkpoint-20261030-v85-root-outcome.json').read_bytes())
    assert not prior['committed'] and prior['head'] == HEAD and prior['git_exit'] == 128
    assert prior['head_unchanged'] and prior['controls_unchanged'] and prior['staging_empty']
    assert prior['result_sha256'] == sha((prior_dir / 'result.json').read_bytes())
    assert prior['signing_log_sha256'] == sha((prior_dir / 'signing.log').read_bytes())
    assert json.loads((prior_dir / 'result.json').read_bytes()) == {'committed':False,'exit':128,'real_index_and_canonical_state_unchanged':True}
    readiness = json.loads((ROOT / 'artifacts/css-signing-readiness-20261030-v2/RESULT.json').read_bytes())
    assert readiness['verified'] and readiness['signature_created'] and not readiness['commit_created'] and readiness['exit'] == 0
    reviewer = json.loads((ROOT / 'artifacts/css-commit-reviewers-20261030-v1.json').read_bytes())
    assert reviewer['exit'] == 0 and reviewer['commit_reviewer'] == 'r?#firefox-style-system-reviewers'
    assert sha((ROOT / reviewer['log_path']).read_bytes()) == reviewer['log_sha256']
    return current['audit']

def main():
    assert sys.argv[1:] in [['--check'], ['--run']]
    if sys.argv[1:] == ['--run']:
        assert EXECUTION_ENABLED, 'Draft signing execution is disabled'
    assert not (HERE / 'result.json').exists(), 'A completed attempt must not be retried'
    for name, digest in BINDINGS['references'].items():
        assert name.startswith('artifacts/') and '..' not in Path(name).parts
        path = ROOT / name
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == digest, name
    audit = saved_admission()
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
    extras = [HERE / name for name in ['commit.py', 'README.md', 'WORK-TABLE.md', 'RUN-DELTA.patch', 'BINDINGS.json', 'CHECK.json', 'FILES.json', 'SELECTION.json', 'BASE-SELECTION.json', 'check.py', 'capture_current.py']]
    for path in extras:
        selected[str(path.relative_to(ROOT))] = {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
    for path, record in selected.items():
        assert path.startswith('artifacts/') and '..' not in Path(path).parts
        file = ROOT / path
        assert file.is_file() and not file.is_symlink()
        assert file.stat().st_size == record['bytes'] and sha(file.read_bytes()) == record['sha256'], path
    tracked = set(git('ls-files', '-z').decode().split('\0'))
    skipped = [path for path in selected if path in tracked]
    verify_blobs([(HEAD + ':' + path, selected[path]) for path in skipped])
    for path in skipped:
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
        with tempfile.TemporaryDirectory(prefix='css-research-v86-', dir='/private/tmp') as directory:
            directory = Path(directory)
            index_env = dict(ENV, GIT_INDEX_FILE=str(directory / 'index'))
            git('read-tree', HEAD, env=index_env)
            paths = directory / 'paths'
            paths.write_bytes(b''.join(path.encode() + b'\0' for path in sorted(selected)))
            add = ['add', '-f', '--pathspec-from-file=' + str(paths), '--pathspec-file-nul']
            git(*add, env=index_env)
            assert set(git('diff', '--cached', '--name-only', env=index_env).decode().splitlines()) == set(selected)
            verify_blobs([(':' + path, record) for path, record in selected.items()], env=index_env)
            tree = git('write-tree', env=index_env).decode().strip()
            assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
            message = directory / 'message'
            message.write_text('No bug - Record CSS dependency verification research. r?#firefox-style-system-reviewers\n')
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
