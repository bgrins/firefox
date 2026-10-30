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


def verify_publication_receipt(stage, receipt, parent):
    assert receipt['signature_verified'] and receipt['parent'] == parent
    assert not receipt['accepted'] and not receipt['app_rebuilt'] and receipt['accepted_fix_increment'] == 0
    assert set(receipt['files']) == set(stage['statuses'])
    if stage['stage'] in ('union', 'image'):
        assert receipt['stage'] == stage['stage']
    return receipt['commit']


def saved_admission():
    assert not BINDINGS['pending_current_admission']
    assert HEAD and EPOCH and BINDINGS['controls']
    current = json.loads((ROOT / BINDINGS['current_capture']).read_bytes())
    research = json.loads((ROOT / BINDINGS['research_receipt']).read_bytes())
    assert sha((ROOT / BINDINGS['research_receipt']).read_bytes()) == BINDINGS['research_receipt_sha256']
    assert research['committed'] and research['signature_verified'] and research['accepted_fix_increment'] == 0
    assert research['head'] == '8f0f2859676d19f41848f376724e1281c12f1f00'
    parent = research['head']
    stages = json.loads((HERE / 'NATIVE-COMMITS.json').read_bytes())
    assert [stage['stage'] for stage in stages] == ['minmax', 'log', 'union', 'image']
    assert len(BINDINGS['native_receipts']) == 4
    commits = {}
    for stage, binding in zip(stages, BINDINGS['native_receipts']):
        assert binding['stage'] == stage['stage'] and binding['path'] and binding['sha256']
        body = (ROOT / binding['path']).read_bytes()
        assert sha(body) == binding['sha256']
        receipt = json.loads(body)
        parent = verify_publication_receipt(stage, receipt, parent)
        commits[stage['stage']] = parent
    batch = json.loads((ROOT / BINDINGS['batch_receipt']).read_bytes())
    terminal = json.loads((ROOT / BINDINGS['batch_terminal']).read_bytes())
    assert batch['all_four_signed_publications_complete'] and batch['commits'] == commits
    assert not batch['pushed'] and not terminal['pushed'] and terminal['commits'] == commits
    assert (terminal['session'], terminal['launch_chunk'], terminal['terminal_chunk'], terminal['exit']) == (46597, 'bb3321', 'ee9e4e', 0)
    assert terminal['result_sha256'] == sha((ROOT / BINDINGS['batch_receipt']).read_bytes())
    assert parent == HEAD == current['audit']['index']['head']
    assert current['controls'] == BINDINGS['controls'] and current['controls']['CURRENT-EPOCH.json'] == EPOCH == receipt['epoch_sha256']
    assert current['full_current_state_verified'] and current['source_transition_lock_absent']
    assert current['publication_receipts'] == BINDINGS['native_receipts']
    role = current['role']
    assert role['role'] == 'published-native' and role['variant'] == 'registered-image'
    assert role['built'] is False and role['paired_head'] == HEAD and 'last_build' not in role
    assert 'last_install' not in role and role['pending_gtest_overlay_installed'] is False
    retirement = current['prototype_overlay_state']
    assert retirement['installed'] is False and retirement['held_provider_parked'] is True
    assert retirement['old_restoration_recipes_require_rebase'] is True
    union_runtime = (ROOT / BINDINGS['native_receipts'][2]['path']).parent
    claim = current['retirement_claim']
    assert retirement['original_role_preserved_in'] == claim['path'] == str((union_runtime / 'PRE-ROLE.json').relative_to(ROOT))
    assert sha((ROOT / claim['path']).read_bytes()) == claim['sha256']
    assert claim['initial_claims_path'] == str((union_runtime / 'INITIAL-CLAIMS.json').relative_to(ROOT))
    assert sha((ROOT / claim['initial_claims_path']).read_bytes()) == claim['initial_claims_sha256']
    assert json.loads((ROOT / claim['initial_claims_path']).read_bytes())['controls']['ROLE.json']['owned_sha256'] == claim['sha256']
    audit_path = ROOT / BINDINGS['completed_untracked_audit']['path']
    assert current['untracked_audit_sha256'] == sha(audit_path.read_bytes())
    assert current['untracked_audit'] == BINDINGS['completed_untracked_audit']['path']
    audit = json.loads(audit_path.read_bytes())
    assert audit['head'] == HEAD and not audit['staged_paths'] and not audit['tracked_modified_paths']
    assert audit['untracked_count'] == 563 and not audit['unexpected_paths'] and not audit['missing_paths']
    assert audit['project_hashes_match_committed_recovery'] and len(audit['project_files']) == 68
    assert audit['unrelated_count'] == 495 and not audit['unrelated_metadata_mismatches']
    return current['audit']


def verify_native_commits():
    stages = json.loads((HERE / 'NATIVE-COMMITS.json').read_bytes())
    for stage, binding in zip(stages, BINDINGS['native_receipts']):
        receipt = json.loads((ROOT / binding['path']).read_bytes())
        commit = receipt['commit']
        assert git('rev-list', '--parents', '-n', '1', commit).decode().split() == [commit, receipt['parent']]
        expected = {stage['statuses'][name] + '\t' + name for name in stage['statuses']}
        assert set(git('diff-tree', '--no-commit-id', '--name-status', '--no-renames', '-r', commit).decode().splitlines()) == expected
        for name, pin in stage['files'].items():
            assert sha(git('show', commit + ':' + name)) == pin
        for name, pin in stage['deleted'].items():
            assert sha(git('show', receipt['parent'] + ':' + name)) == pin
        git('-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', commit)

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
    verify_native_commits()
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
    extras = [HERE / name for name in ['commit.py', 'README.md', 'WORK-TABLE.md', 'RUN-DELTA.patch', 'BINDINGS.json', 'CHECK.json', 'FILES.json', 'SELECTION.json', 'BASE-SELECTION.json', 'check.py', 'NATIVE-COMMITS.json', 'capture_current.py']]
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
        with tempfile.TemporaryDirectory(prefix='css-research-v87-', dir='/private/tmp') as directory:
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
            message.write_text('No bug - Record signed CSS native publication evidence. r?#firefox-style-system-reviewers\n')
            with (HERE / 'signing.log').open('x') as stream:
                result = subprocess.run(GIT + ['commit', '--quiet', '--file', str(message)], cwd=ROOT, env=index_env, stdout=stream, stderr=subprocess.STDOUT)
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
