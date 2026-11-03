import copy
import hashlib
import importlib.util
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
read = lambda p: json.loads(p.read_bytes())
digest = lambda b: hashlib.sha256(b).hexdigest()
sha = lambda p: digest(p.read_bytes())


def git(*args, env=ENV):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def authenticated_receipt(binding, name):
    record = binding[name]
    path = ROOT / record['path']
    assert sha(path) == record['sha256']
    return read(path)


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('check', 'install', 'commit')
    action, manifest = sys.argv[1:]
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    owner = load('publication_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    owner.authenticate(HERE, manifest)
    policy = read(HERE / 'POLICY.json')
    for path, pin in policy['references'].items():
        assert sha(ROOT / path) == pin, path
    stages = read(HERE / 'STAGES.json')['stages']
    for stage in stages:
        for record in stage['files'].values():
            assert sha(ROOT / record['path']) == record['sha256']
    if action == 'check':
        print('Saved payload authentication passed; no live guard')
        return
    assert action in policy['enabled_modes'] and policy['bindings'] is not None
    stage = next(s for s in stages if s['stage'] == policy['stage'])
    binding = policy['bindings']
    creation = load('publication_creation', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
    transform = load('publication_transform', HERE / 'transform.py')
    state = owner.load_state(RUNTIME)
    assert git('rev-parse', 'HEAD').decode().strip() == binding['head']
    assert git('symbolic-ref', 'HEAD').decode().strip() == binding['branch']
    prior = authenticated_receipt(binding, 'predecessor_receipt')
    assert prior['head'] == binding['head'] and prior['signature_verified']
    assert prior['committed'] and prior['accepted_fix_increment'] == 0 and prior['native_working_diff_preserved']
    assert binding['predecessor_kind'] == 'signed-research' and stage['stage'] == 'reparse'
    evidence = load('nowrap_pair_evidence', HERE / 'evidence.py')
    observed = evidence.verify(ROOT, policy['pair_binding'], stage)
    pair_head = observed['pair_head']
    assert not git('merge-base', '--is-ancestor', pair_head, binding['head'])
    assert all(path.startswith('artifacts/') for path in git('diff', '--name-only', pair_head, binding['head']).decode().splitlines())
    git('-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / policy['allowed_signers']), 'verify-commit', binding['head'])
    controls = {n: (RUNTIME / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    assert {n: digest(b) for n, b in controls.items()} == binding['controls']
    epoch, ownership, role = (json.loads(controls[n]) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'))
    assert epoch['semantic_index']['head'] == binding['head'] and epoch['staged_working'] == {}
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    assert before == binding['snapshot']
    for path, pin in stage['head_preimages'].items():
        assert digest(git('show', binding['head'] + ':' + path)) == pin
    for path, record in binding['preserved_claims'].items():
        assert path not in stage['files']
        assert epoch['pins'][path] == record['sha256']
        owner.claim(ROOT, path, record['sha256'], record['identity'])
    assert binding['historical_markers'] == {n: epoch[n] for n in binding['historical_markers']}
    for path in binding['absent_metadata']:
        assert epoch['pins'].get(path) is None and not os.path.lexists(ROOT / path)
    owner.quiescent(RUNTIME)
    owner.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and output.name.startswith('css-explicit-taint-typed-reparse-publication-')
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert not os.path.lexists(lock)
    sources = set(stage['head_preimages'])
    tests = set(stage['files']) - sources
    assert {p.replace('testing/web-platform/tests/', 'testing/web-platform/meta/') + '.ini' for p in tests} <= set(binding['absent_metadata'])
    adopted_paths, created_paths = set(stage['adopt_existing_tests']), set(stage['create_tests'])
    assert adopted_paths.isdisjoint(created_paths) and adopted_paths | created_paths == tests
    source_claims, parents, adopted, created = {}, {}, {}, {}
    if action == 'install':
        assert not os.path.lexists(output)
        assert epoch['modified_native_paths'] == []
        assert prior['epoch_sha256'] == binding['controls']['CURRENT-EPOCH.json']
        assert set(binding['adopted_tests']) == adopted_paths
        assert set(binding['created_test_parents']) == created_paths
        for path in sources:
            pin = stage.get('working_preimages', stage['head_preimages'])[path]
            assert epoch['pins'][path] == pin
            source_claims[path] = owner.claim(ROOT, path, pin, epoch['installed_identities'][path])
        for path in tests:
            assert epoch['pins'].get(path) is None
            assert path not in epoch['installed_identities'] and path not in ownership
            assert not git('ls-files', '--stage', '--', path) and not git('ls-tree', binding['head'], '--', path)
            parents[path] = creation.parent_pins(ROOT, ROOT / path)
            if path in adopted_paths:
                expected = binding['adopted_tests'][path]
                adopted[path] = owner.claim(ROOT, path, stage['files'][path]['sha256'], expected['claim']['identity'])
                assert adopted[path] == expected['claim'] and parents[path] == expected['parents']
            else:
                assert not os.path.lexists(ROOT / path)
                assert parents[path] == binding['created_test_parents'][path]
            assert digest(git('show', binding['head'] + ':' + stage['files'][path]['path'])) == stage['files'][path]['sha256']
    else:
        installed = read(output / 'INSTALL-RESULT.json')
        assert installed['stage'] == stage['stage'] and installed['installed'] and not installed['app_rebuilt']
        assert installed['manifest_sha256'] == binding['installation_manifest']
        assert installed['epoch_sha256'] == binding['controls']['CURRENT-EPOCH.json']
        assert epoch['explicit_taint_reparse_publication'][stage['stage']]['installation_manifest'] == binding['installation_manifest']
        assert epoch['modified_native_paths'] == sorted(sources)
        for path, record in stage['files'].items():
            assert epoch['pins'][path] == record['sha256']
            owner.claim(ROOT, path, record['sha256'], epoch['installed_identities'][path])
        assert not role['built'] and role['variant'] == stage['stage']
        if tests:
            delivery = authenticated_receipt(binding, 'delivery_receipt')
            assert delivery['lint_exit'] == 0 and delivery['lint_errors'] == 0
            assert delivery['files'] == {p: stage['files'][p]['sha256'] for p in tests}
            assert delivery['registered_urls'] == sorted('/' + p.removeprefix('testing/web-platform/tests/') for p in tests)
            assert delivery['manifest_entries_verified'] and not delivery['browser_executed']
            assert delivery['installation_manifest'] == binding['installation_manifest']
            assert delivery['lint_command'] == policy['lint_prefix'] + sorted(tests)
            assert delivery['manifest_command']
            assert delivery['evidence']
            for path, pin in delivery['evidence'].items():
                assert sha(ROOT / path) == pin
        assert not (output / 'COMMIT-RESULT.json').exists()
        assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
    control_claims = {n: owner.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    assert {path.encode() for path in (adopted_paths if action=='install' else tests)} <= set(untracked.split(b'\0'))
    if action=='install':
        assert not {path.encode() for path in created_paths} & set(untracked.split(b'\0'))
    lock.mkdir()
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    safe, originals = False, {}
    try:
        assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
        if action == 'install':
            output.mkdir()
            for name, body in controls.items():
                with (output / ('PRE-' + name)).open('xb') as stream:
                    stream.write(body)
            save(output / 'PRE.json', before)
            save(output / 'INITIAL-CLAIMS.json', {'sources': source_claims, 'controls': control_claims, 'parents': parents, 'adopted_tests': adopted})
            for number, path in enumerate(sorted(sources)):
                originals[path] = (ROOT / path).read_bytes()
                with (output / ('SOURCE-PRE-' + str(number))).open('xb') as stream:
                    stream.write(originals[path])
                owner.write_owned(ROOT, source_claims[path], (ROOT / stage['files'][path]['path']).read_bytes())
            for path, claim in adopted.items():
                assert owner.claim(ROOT, path, claim['owned_sha256'], claim['identity']) == claim
                assert creation.parent_pins(ROOT, ROOT / path) == parents[path]
            save(output / 'ADOPTED-TESTS.json', adopted)
            for path in sorted(created_paths):
                blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
                try:
                    created[path] = creation.create_owned(owner, ROOT, path, parents[path])
                    save(output / 'CREATED.json', created)
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
                owner.write_owned(ROOT, created[path], (ROOT / stage['files'][path]['path']).read_bytes())
            claims = {**source_claims, **adopted, **created}
            save(output / 'OWNERSHIP.json', claims)
            index = state.h.index_state(ROOT, ENV)
            semantic = state.h.semantic_index(index)
            assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
            current, new_owned, new_role = transform.installed(epoch, ownership, role, stage, claims, index, semantic, manifest, str(output.relative_to(ROOT)))
            after = state.a.verify_current(state.h, ROOT, ENV, current)
            assert after['nested_index'] == before['nested_index']
            assert set(git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')) == set(untracked.split(b'\0')) | {p.encode() for p in tests}
            assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
            for name, value in [('OWNED.json', new_owned), ('ROLE.json', new_role), ('CURRENT-EPOCH.json', current)]:
                owner.write_owned(ROOT, control_claims[name], owner.encoded(value))
            state.a.verify_current(state.h, ROOT, ENV, current)
            save(output / 'INSTALL-RESULT.json', {'stage': stage['stage'], 'installed': True, 'accepted': False,
                 'manifest_sha256': manifest, 'epoch_sha256': digest(owner.encoded(current)),
                 'files': sorted(stage['files']), 'app_rebuilt': False, 'existing_tests_adopted_without_write': sorted(adopted_paths), 'new_tests_created': sorted(created_paths)})
            safe = True
        else:
            with tempfile.TemporaryDirectory(prefix='css-explicit-taint-typed-reparse-native-', dir='/private/tmp') as temporary:
                temporary = Path(temporary)
                index_env = dict(ENV, GIT_INDEX_FILE=str(temporary / 'index'))
                git('read-tree', binding['head'], env=index_env)
                names = temporary / 'paths'
                names.write_bytes(b''.join(p.encode() + b'\0' for p in sorted(stage['files'])))
                add = ['add', '-f', '--pathspec-from-file=' + str(names), '--pathspec-file-nul']
                git(*add, env=index_env)
                assert set(git('diff', '--cached', '--name-only', env=index_env).decode().splitlines()) == set(stage['files'])
                for path, record in stage['files'].items():
                    assert digest(git('show', ':' + path, env=index_env)) == record['sha256']
                    assert git('ls-files', '--stage', '--', path, env=index_env).split()[0] == b'100644'
                tree = git('write-tree', env=index_env).decode().strip()
                message = temporary / 'message'
                message.write_text(policy['messages'][stage['stage']] + '\n')
                assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
                with (output / 'native-signing.log').open('x') as stream:
                    result = subprocess.run(GIT + ['commit', '--quiet', '--file', str(message)], cwd=ROOT, env=index_env, stdout=stream, stderr=subprocess.STDOUT)
                if result.returncode:
                    assert git('rev-parse', 'HEAD').decode().strip() == binding['head']
                    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
                    assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
                    assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
                    save(output / 'SIGNING-FAILURE.json', {'exit': result.returncode, 'installed_pending_state_preserved': True})
                    safe = True
                    raise RuntimeError('Signing failed; pending installation retained, no retry')
                commit = git('rev-parse', 'HEAD').decode().strip()
                assert git('rev-parse', commit + '^').decode().strip() == binding['head']
                assert git('rev-parse', commit + '^{tree}').decode().strip() == tree
                git(*add)
            with (output / 'native-signature.log').open('x') as stream:
                subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / policy['allowed_signers']), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
            index = state.h.index_state(ROOT, ENV)
            current = transform.committed(epoch, stage['stage'], index, state.h.semantic_index(index), commit)
            new_role = copy.deepcopy(role)
            new_role['paired_head'] = commit
            assert set(git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')) == set(untracked.split(b'\0')) - {p.encode() for p in stage['files']}
            after = state.a.verify_current(state.h, ROOT, ENV, current)
            assert after['nested_index'] == before['nested_index']
            assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
            owner.write_owned(ROOT, control_claims['ROLE.json'], owner.encoded(new_role))
            owner.write_owned(ROOT, control_claims['CURRENT-EPOCH.json'], owner.encoded(current))
            state.a.verify_current(state.h, ROOT, ENV, current)
            save(output / 'COMMIT-RESULT.json', {'stage': stage['stage'], 'commit': commit, 'parent': binding['head'],
                 'signature_verified': True, 'files': sorted(stage['files']), 'epoch_sha256': digest(owner.encoded(current)),
                 'accepted': False, 'accepted_fix_increment': 0, 'app_rebuilt': False})
            safe = True
    except BaseException as error:
        if action == 'install':
            try:
                for path, claim in adopted.items():
                    assert owner.claim(ROOT, path, claim['owned_sha256'], claim['identity']) == claim
                    assert creation.parent_pins(ROOT, ROOT / path) == parents[path]
                for path, claim in reversed(list(created.items())):
                    owner.claim(ROOT, path, claim['owned_sha256'], claim['identity'])
                    assert creation.parent_pins(ROOT, ROOT / path) == parents[path]
                    (ROOT / path).unlink()
                for path, body in originals.items():
                    owner.write_owned(ROOT, source_claims[path], body)
                restored = copy.deepcopy(epoch)
                index = state.h.index_state(ROOT, ENV)
                assert state.h.semantic_index(index) == epoch['semantic_index']
                restored['raw_index_observation']['current'] = index['raw_index']
                expected = copy.deepcopy(before)
                expected['index']['raw_index'] = index['raw_index']
                assert state.a.verify_current(state.h, ROOT, ENV, restored) == expected
                assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
                for name, body in controls.items():
                    owner.write_owned(ROOT, control_claims[name], owner.encoded(restored) if name == 'CURRENT-EPOCH.json' else body)
                state.a.verify_current(state.h, ROOT, ENV, restored)
                safe = True
            finally:
                if output.exists():
                    save(output / 'INSTALL-FAILURE.json', {'error': repr(error), 'rollback_verified': safe,
                         'manual_recovery_required': not safe, 'sources': source_claims, 'adopted_tests_preserved': adopted})
        raise
    finally:
        if safe:
            assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
            lock.rmdir()


if __name__ == '__main__':
    main()
