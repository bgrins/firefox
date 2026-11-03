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


def validate_refresh(receipt):
    binding = BINDINGS['refresh_binding']
    assert binding is not None
    parent_binding = BINDINGS['refresh_parent']
    parent_dir = ROOT / parent_binding['directory']
    assert sha((parent_dir / 'commit.py').read_bytes()) == parent_binding['driver_sha256']
    assert sha((parent_dir / 'BINDINGS.json').read_bytes()) == parent_binding['bindings_sha256']
    parent = load('previous_verified_raw_refresh', str((parent_dir / 'commit.py').relative_to(ROOT)))
    assert parent.BINDINGS['prior_receipt'] == BINDINGS['prior_receipt']
    assert parent.BINDINGS['prior_receipt_sha256'] == BINDINGS['prior_receipt_sha256']
    previous = parent.saved_admission()
    assert parent.BINDINGS['head'] == HEAD
    old_epoch = parent.BINDINGS['epoch_sha256']
    for binding in BINDINGS['refresh_prefix'] + [binding]:
        directory = ROOT / binding['directory']
        body = (directory / 'RESULT.json').read_bytes()
        assert sha(body) == binding['result_sha256']
        result = json.loads(body)
        assert result['updated'] and result['updated_only'] == 'raw_index_observation.current'
        assert result['preservation_verified'] and result['restoration_independently_verified']
        assert result['existing_head_signature_verified'] and result['accepted_fix_increment'] == 0
        assert not result['native_fix_acceptance']
        assert result['head'] == receipt['commit'] == HEAD
        assert result['signed_commit_receipt'] == {'path': BINDINGS['prior_receipt'], 'sha256': BINDINGS['prior_receipt_sha256']}
        old_body, new_body = (directory / 'PRE-CURRENT-EPOCH.json').read_bytes(), (directory / 'EPOCH.json').read_bytes()
        assert sha(old_body) == result['old_epoch_sha256'] == old_epoch
        new_epoch = result['epoch_sha256']
        assert sha(new_body) == new_epoch
        old, new = json.loads(old_body), json.loads(new_body)
        assert old['raw_index_observation']['current'] == result['before']
        expected = copy.deepcopy(old)
        expected['raw_index_observation']['current'] = result['after']
        assert expected == new
        assert new['semantic_index']['head'] == HEAD
        pre, post = json.loads((directory / 'PRE.json').read_bytes()), json.loads((directory / 'POST.json').read_bytes())
        assert pre == post and post['index']['raw_index'] == result['after']
        assert {k:v for k,v in post['index'].items() if k != 'raw_index'} == new['semantic_index']
        projected_previous = copy.deepcopy(previous)
        projected_previous['index']['raw_index'] = result['after']
        assert projected_previous == post
        previous = post
        old_epoch = new_epoch
    assert old_epoch == EPOCH
    return previous


def saved_admission():
    assert not BINDINGS['pending_current_admission']
    body = (ROOT / BINDINGS['prior_receipt']).read_bytes()
    assert sha(body) == BINDINGS['prior_receipt_sha256']
    receipt = json.loads(body)
    assert set(receipt) == {'stage', 'commit', 'parent', 'signature_verified', 'files', 'epoch_sha256', 'accepted', 'accepted_fix_increment', 'app_rebuilt'}
    assert receipt['stage'] == 'capacity' and receipt['signature_verified'] is True
    assert receipt['commit'] == HEAD
    refreshed = validate_refresh(receipt)
    assert receipt['accepted'] is False and receipt['accepted_fix_increment'] == 0
    assert receipt['app_rebuilt'] is False
    assert receipt['files'] == ['servo/components/style/properties/cascade.rs', 'testing/web-platform/tests/css/css-cascade/prioritary-after-many-unrelated-declarations.html']
    research_body = (ROOT / BINDINGS['prior_research_receipt']).read_bytes()
    assert sha(research_body) == BINDINGS['prior_research_receipt_sha256']
    research = json.loads(research_body)
    assert research['committed'] and research['signature_verified']
    assert receipt['parent'] == research['head'] == BINDINGS['native_parent']
    assert receipt['commit'] != receipt['parent']
    body = (ROOT / BINDINGS['current_capture']).read_bytes()
    assert sha(body) == BINDINGS['current_capture_sha256']
    current = json.loads(body)
    assert current['prior_receipt_sha256'] == BINDINGS['prior_receipt_sha256']
    assert current['controls'] == BINDINGS['controls']
    assert current['controls']['CURRENT-EPOCH.json'] == EPOCH
    assert current['full_current_state_verified'] and current['source_transition_lock_absent']
    assert current['tracked_modified_paths'] == [] and current['staged_paths'] == []
    audit = current['audit']
    assert audit == refreshed
    assert audit['index']['head'] == HEAD
    assert audit['index']['working_diff'] == audit['index']['cached_diff'] == sha(b'')
    assert audit['current_raw_stable_during_check'] and audit['working_sources_binaries_research_preserved']
    return audit


def manifest_items(manifest):
    payloads = manifest.get('files', manifest)
    if isinstance(payloads, list):
        assert all(isinstance(row, dict) and isinstance(row.get('path'), str) for row in payloads)
        assert len({row['path'] for row in payloads}) == len(payloads)
        return [(row['path'], row) for row in payloads]
    assert isinstance(payloads, dict)
    return payloads.items()


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
    git('-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', HEAD)
    assert sha((HERE / 'SELECTION.json').read_bytes()) == BINDINGS['selection_sha256']
    selected = json.loads((HERE / 'SELECTION.json').read_bytes())
    assert len(selected) == BINDINGS['selected_paths_before_self']
    for manifest_path, digest in BINDINGS['completed_packages'].items():
        manifest = ROOT / manifest_path
        assert manifest_path.startswith('artifacts/') and '..' not in Path(manifest_path).parts
        assert sha(manifest.read_bytes()) == digest
        assert selected[manifest_path]['sha256'] == digest
        for name, record in manifest_items(json.loads(manifest.read_bytes())):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            path = str((manifest.parent / name).relative_to(ROOT))
            expected = record['sha256'] if isinstance(record, dict) else record
            assert selected[path]['sha256'] == expected
    self_manifest = json.loads((HERE / 'FILES.json').read_bytes())
    self_names = [name for name, _ in manifest_items(self_manifest)]
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in self_names)
    assert {str(path.relative_to(HERE)) for path in HERE.rglob('*') if path.is_file()} == set(self_names) | {'FILES.json'}
    for name, record in manifest_items(self_manifest):
        expected = record['sha256'] if isinstance(record, dict) else record
        assert sha((HERE / name).read_bytes()) == expected
    extras = [HERE / name for name in self_names] + [HERE / 'FILES.json']
    for path in extras:
        selected[str(path.relative_to(ROOT))] = {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
    for path, record in selected.items():
        assert path.startswith('artifacts/') and '..' not in Path(path).parts
        file = ROOT / path
        assert file.is_file() and not file.is_symlink()
        assert file.stat().st_size == record['bytes'] and sha(file.read_bytes()) == record['sha256'], path
    tracked = set(git('ls-files', '-z').decode().split('\0'))
    skipped = [path for path in selected if path in tracked]
    assert not skipped, 'V125 must not reselect already committed payloads'
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
        with tempfile.TemporaryDirectory(prefix='css-research-v125-', dir='/private/tmp') as directory:
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
            message.write_text('No bug - Record validated attribute-taint and root-font animation repair research. r?#firefox-style-system-reviewers\n')
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
