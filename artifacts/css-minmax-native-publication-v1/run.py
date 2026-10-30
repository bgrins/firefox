import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
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
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('check', 'install', 'commit')
    action, manifest = sys.argv[1:]
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    owner = load('minmax_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    creation = load('minmax_creation', 'artifacts/css-registered-admission-wpt-install-v1/install.py')
    state = owner.load_state(RUNTIME)
    owner.authenticate(HERE, manifest)
    policy = read(HERE / 'POLICY.json')
    for path, pin in policy['references'].items():
        assert sha(ROOT / path) == pin, path
    for directory, pin in policy['packages'].items():
        owner.authenticate(ROOT / directory, pin)
    for record in policy['files'].values():
        assert sha(ROOT / record['capture']) == record['sha256']
    if action == 'check':
        compile((HERE / 'run.py').read_bytes(), 'run.py', 'exec')
        print('Static payload and helper authentication passed; no live guards executed')
        return
    assert action in policy['enabled_modes'] and policy['bindings'] is not None
    binding = policy['bindings']
    assert git('rev-parse', 'HEAD').decode().strip() == binding['head']
    assert git('symbolic-ref', 'HEAD').decode().strip() == binding['branch']
    research = read(ROOT / binding['research_receipt'])
    assert sha(ROOT / binding['research_receipt']) == binding['research_receipt_sha256']
    assert research['committed'] and research['signature_verified'] and research['head'] == binding['head']
    controls = {n: (RUNTIME / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
    assert {n: digest(b) for n, b in controls.items()} == binding['controls']
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == binding['head'] and epoch['staged_working'] == {}
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    source = policy['source_path']
    held = 'servo/components/style/custom_properties.rs'
    assert sha(ROOT / held) == policy['held_provider_sha256']
    assert len(binding['accepted_claims']) == 29
    for name, record in binding['accepted_claims'].items():
        expected = policy['files'][source]['sha256'] if action == 'commit' and name == source else record['sha256']
        assert epoch['pins'][name] == expected
        owner.claim(ROOT, name, expected, record['identity'])
        assert digest(git('show', binding['head'] + ':' + name)) == record['sha256']
    for name, value in binding['historical_markers'].items():
        assert epoch[name] == value
    for name in binding['absent_metadata']:
        assert epoch['pins'][name] is None and not os.path.lexists(ROOT / name)
        assert name not in epoch['installed_identities'] and name not in json.loads(controls['OWNED.json'])
    owner.quiescent(RUNTIME)
    owner.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
    output = ROOT / policy['runtime_output']
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert not os.path.lexists(lock)
    if action == 'install':
        assert not os.path.lexists(output)
        assert epoch['modified_native_paths'] == [held]
        assert sha(ROOT / source) == policy['base_sha256']
        assert digest(git('show', binding['head'] + ':' + source)) == policy['base_sha256']
        assert epoch['accepted_pow_special_value']['files'][source] == policy['base_sha256']
        assert epoch['pins'][source] == policy['base_sha256']
        load('minmax_pair_replay', policy['pair_replay'])
        tests = set(policy['files']) - {source}
        parents = {}
        for name in tests:
            assert not os.path.lexists(ROOT / name) and epoch['pins'].get(name) is None
            assert name not in epoch['installed_identities'] and name not in json.loads(controls['OWNED.json'])
            assert not git('ls-files', '--stage', '--', name)
            assert not git('ls-tree', binding['head'], '--', name)
            parents[name] = creation.parent_pins(ROOT, ROOT / name)
    else:
        assert output.is_dir() and not (output / 'COMMIT-RESULT.json').exists()
        installed = read(output / 'INSTALL-RESULT.json')
        assert installed['manifest_sha256'] == binding['installation_manifest']
        assert installed['epoch_sha256'] == binding['controls']['CURRENT-EPOCH.json']
        assert installed['installed'] and not installed['accepted'] and not installed['app_rebuilt']
        assert epoch['minmax_relative_infinity_transition']['installation_manifest'] == binding['installation_manifest']
        assert epoch['modified_native_paths'] == sorted([held, source])
        assert not epoch['minmax_relative_infinity_transition']['accepted']
        for name, record in policy['files'].items():
            assert epoch['pins'][name] == record['sha256']
            owner.claim(ROOT, name, record['sha256'], epoch['installed_identities'][name])
        delivery = read(ROOT / binding['delivery_receipt'])
        assert sha(ROOT / binding['delivery_receipt']) == binding['delivery_sha256']
        assert delivery['lint_exit'] == 0 and delivery['lint_errors'] == 0
        assert delivery['files'] == {n: r['sha256'] for n, r in policy['files'].items() if n != source}
        assert delivery['registered_urls'] == sorted('/' + n.removeprefix('testing/web-platform/tests/') for n in delivery['files'])
        assert delivery['manifest_entries_verified'] and not delivery['browser_executed']
        assert delivery['lint_command'] == policy['lint_command']
        assert delivery['evidence'] and delivery['manifest_command']
        for path, pin in delivery['evidence'].items():
            assert sha(ROOT / path) == pin
        assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
    claims = {n: owner.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    lock.mkdir()
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    safe = False
    created = {}
    source_claim = owner.claim(ROOT, source, epoch['pins'][source], epoch['installed_identities'][source])
    try:
        assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
        if action == 'install':
            output.mkdir()
            for name, body in controls.items():
                (output / ('LOCAL-PRE-' + name)).write_bytes(body)
            save(output / 'LOCAL-RECOVERY-REFERENCES.json', {name: digest(body) for name, body in controls.items()})
            save(output / 'PRE.json', before)
            owner.write_owned(ROOT, source_claim, (ROOT / policy['files'][source]['capture']).read_bytes())
            current = copy.deepcopy(epoch)
            owned = json.loads(controls['OWNED.json'])
            current['pins'][source] = source_claim['owned_sha256']
            owned[source] = source_claim
            for name in sorted(tests):
                blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
                try:
                    created[name] = creation.create_owned(owner, ROOT, name, parents[name])
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
                owner.write_owned(ROOT, created[name], (ROOT / policy['files'][name]['capture']).read_bytes())
                if name in current['pins']:
                    assert current['pins'].pop(name) is None
                current = creation.updated_epoch(current, name, created[name], policy['files'][name]['sha256'])
                owned[name] = created[name]
            save(output / 'OWNERSHIP.json', {source: source_claim, **created})
            actual = state.h.index_state(ROOT, ENV)
            assert {k:v for k,v in state.h.semantic_index(actual).items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
            current['semantic_index'] = state.h.semantic_index(actual)
            current['raw_index_observation']['current'] = actual['raw_index']
            current['modified_native_paths'] = sorted([held, source])
            current['counts']['native_modified_paths'] = 2
            current['minmax_relative_infinity_transition'] = {
                'source_sha256': policy['files'][source]['sha256'], 'installation_manifest': manifest,
                'compiled': False, 'current_app_contains_candidate': False, 'accepted': False,
                'historical_pair_result': policy['pair_result_sha256'], 'supersedes_source_pin': {'fix':150, 'path':source, 'sha256':policy['base_sha256']}}
            after = state.a.verify_current(state.h, ROOT, ENV, current)
            assert after['nested_index'] == before['nested_index']
            assert set(git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')) == set(untracked.split(b'\0')) | {n.encode() for n in tests}
            assert all((RUNTIME / n).read_bytes() == b for n,b in controls.items())
            owner.write_owned(ROOT, claims['OWNED.json'], owner.encoded(owned))
            owner.write_owned(ROOT, claims['CURRENT-EPOCH.json'], owner.encoded(current))
            state.a.verify_current(state.h, ROOT, ENV, current)
            save(output / 'INSTALL-RESULT.json', {'installed':True, 'accepted':False, 'app_rebuilt':False,
                 'manifest_sha256':manifest, 'epoch_sha256':digest(owner.encoded(current)), 'files':list(policy['files'])})
            safe = True
        else:
            with tempfile.TemporaryDirectory(prefix='css-minmax-native-', dir='/private/tmp') as temporary:
                temporary = Path(temporary)
                index_env = dict(ENV, GIT_INDEX_FILE=str(temporary / 'index'))
                git('read-tree', binding['head'], env=index_env)
                names = temporary / 'paths'
                names.write_bytes(b''.join(n.encode() + b'\0' for n in sorted(policy['files'])))
                add = ['add', '-f', '--pathspec-from-file=' + str(names), '--pathspec-file-nul']
                git(*add, env=index_env)
                assert set(git('diff', '--cached', '--name-only', env=index_env).decode().splitlines()) == set(policy['files'])
                for name, record in policy['files'].items():
                    assert digest(git('show', ':' + name, env=index_env)) == record['sha256']
                    assert git('ls-files', '--stage', '--', name, env=index_env).split()[0] == b'100644'
                tree = git('write-tree', env=index_env).decode().strip()
                message = temporary / 'message'
                message.write_text(policy['message'] + '\n')
                assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
                with (output / 'native-signing.log').open('x') as stream:
                    result = subprocess.run(GIT + ['commit', '--file', str(message)], cwd=ROOT, env=index_env, stdout=stream, stderr=subprocess.STDOUT)
                if result.returncode:
                    assert git('rev-parse', 'HEAD').decode().strip() == binding['head']
                    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
                    assert all((RUNTIME / n).read_bytes() == b for n,b in controls.items())
                    assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
                    assert all(sha(ROOT / n) == r['sha256'] for n,r in policy['files'].items())
                    save(output / 'SIGNING-FAILURE.json', {'exit':result.returncode, 'installed_pending_state_preserved':True})
                    safe = True
                    raise RuntimeError('Signing failed; installed pending state retained, no retry')
                commit = git('rev-parse', 'HEAD').decode().strip()
                assert git('rev-parse', commit + '^').decode().strip() == binding['head']
                assert git('rev-parse', commit + '^{tree}').decode().strip() == tree
                git(*add)
            with (output / 'native-signature.log').open('x') as stream:
                subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / policy['allowed_signers']), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
            current = copy.deepcopy(epoch)
            actual = state.h.index_state(ROOT, ENV)
            current['semantic_index'] = state.h.semantic_index(actual)
            current['raw_index_observation']['current'] = actual['raw_index']
            current['modified_native_paths'] = [held]
            current['counts']['native_modified_paths'] = 1
            current['minmax_relative_infinity_transition']['native_commit'] = commit
            expected_untracked = set(untracked.split(b'\0')) - {n.encode() for n in policy['files']}
            assert set(git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')) == expected_untracked
            after = state.a.verify_current(state.h, ROOT, ENV, current)
            assert after['nested_index'] == before['nested_index']
            assert all((RUNTIME / n).read_bytes() == b for n,b in controls.items())
            owner.write_owned(ROOT, claims['CURRENT-EPOCH.json'], owner.encoded(current))
            state.a.verify_current(state.h, ROOT, ENV, current)
            save(output / 'COMMIT-RESULT.json', {'commit':commit, 'parent':binding['head'], 'signature_verified':True,
                 'files':list(policy['files']), 'epoch_sha256':digest(owner.encoded(current)),
                 'accepted':False, 'accepted_fix_increment':0, 'app_rebuilt':False})
            safe = True
    except BaseException as error:
        if action == 'install':
            try:
                for name, item in reversed(list(created.items())):
                    owner.claim(ROOT, name, item['owned_sha256'], item['identity'])
                    assert creation.parent_pins(ROOT, ROOT / name) == parents[name]
                    (ROOT / name).unlink()
                owner.write_owned(ROOT, source_claim, (ROOT / policy['base_capture']).read_bytes())
                restored = copy.deepcopy(epoch)
                actual = state.h.index_state(ROOT, ENV)
                assert state.h.semantic_index(actual) == epoch['semantic_index']
                restored['raw_index_observation']['current'] = actual['raw_index']
                expected = copy.deepcopy(before)
                expected['index']['raw_index'] = actual['raw_index']
                assert state.a.verify_current(state.h, ROOT, ENV, restored) == expected
                assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
                owner.write_owned(ROOT, claims['OWNED.json'], controls['OWNED.json'])
                owner.write_owned(ROOT, claims['CURRENT-EPOCH.json'], owner.encoded(restored))
                assert (RUNTIME / 'ROLE.json').read_bytes() == controls['ROLE.json']
                state.a.verify_current(state.h, ROOT, ENV, restored)
                safe = True
            finally:
                if output.exists():
                    save(output / 'INSTALL-FAILURE.json', {'error':repr(error), 'rollback_verified':safe, 'manual_recovery_required':not safe})
        raise
    finally:
        if safe:
            assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
            lock.rmdir()


if __name__ == '__main__':
    main()
