import copy
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project(epoch, owned, policy):
    old, new = policy['old_path'], policy['new_path']
    current, owners = copy.deepcopy(epoch), copy.deepcopy(owned)
    assert old != new and Path(old).parent == Path(new).parent
    assert owners[old] == policy['claim'] and new not in owners
    for key, value in (('pins', policy['claim']['owned_sha256']), ('installed_identities', policy['claim']['identity'])):
        assert current[key][old] == value and new not in current[key]
        current[key][new] = current[key].pop(old)
    owners[new] = owners.pop(old)
    owners[new]['path'] = new
    return current, owners


def main():
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    assert policy['execution_enabled'] is True and len(sys.argv) == 3
    manifest, epoch_sha = sys.argv[1:]
    assert epoch_sha == policy['epoch_sha256']
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    h = load('rename_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    c = load('rename_creation', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
    h.authenticate(HERE, manifest)
    for n, pin in policy['references'].items(): assert h.digest(h.body(ROOT / n)) == pin
    s = h.load_state(RUNTIME)
    controls = {n:h.body(RUNTIME / n) for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert h.digest(controls['CURRENT-EPOCH.json']) == epoch_sha
    assert h.digest(controls['ROLE.json']) == policy['role_sha256']
    assert h.digest(controls['OWNED.json']) == policy['owned_sha256']
    epoch, owned = json.loads(controls['CURRENT-EPOCH.json']), json.loads(controls['OWNED.json'])
    assert epoch['semantic_index']['head'] == policy['head'] and not epoch['staged_working']
    assert epoch['linear_guard_transition']['compiled'] and not epoch['linear_guard_transition']['accepted']
    assert epoch == json.loads(h.body(ROOT / policy['build_epoch']))
    build = json.loads(h.body(ROOT / policy['build_result']))
    assert build['command_success'] and build['preservation_verified']
    inner = json.loads(h.body(ROOT / policy['inner_build_result']))
    assert inner['exit'] == 0 and inner['owned_group_absent'] and not inner['cleanup_errors'] and inner['stop_reason'] is None and inner['error'] is None
    old, new = policy['old_path'], policy['new_path']
    assert old == 'testing/web-platform/tests/css/css-easing/linear-contextual-second-position-crash.html'
    assert new == 'testing/web-platform/tests/css/css-easing/linear-contextual-second-position.html'
    claim = h.claim(ROOT, old, policy['claim']['owned_sha256'], policy['claim']['identity'])
    assert claim == policy['claim'] and not os.path.lexists(ROOT / new)
    assert not s.h.git(ROOT, ENV, 'ls-files', '--stage', '--', old, new)
    assert not s.h.git(ROOT, ENV, 'ls-tree', policy['head'], '--', old, new)
    parents = c.parent_pins(ROOT, ROOT / old)
    current, owners = project(epoch, owned, policy)
    h.quiescent(RUNTIME)
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n:s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') for n in ('.', 'artifacts/css-spec-lean')}
    claims = {n:h.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), h.digest(b)) for n,b in controls.items()}
    output = ROOT / policy['runtime_output']
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert output.parent == ROOT / 'artifacts' and not os.path.lexists(output) and not os.path.lexists(lock)
    lock_claim, linked, removed, release = None, False, False, False
    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try: lock_claim = c.create_owned(h, ROOT, str(lock.relative_to(ROOT)), c.parent_pins(ROOT, lock))
        finally: signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        output.mkdir()
        for n,b in controls.items(): (output / ('PRE-' + n)).write_bytes(b)
        h.save(output / 'PRE.json', before)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        assert c.parent_pins(ROOT, ROOT / old) == parents
        h.claim(ROOT, old, claim['owned_sha256'], claim['identity'])
        for n,item in claims.items():
            h.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
            assert h.body(RUNTIME / n) == controls[n]
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            os.link(ROOT / old, ROOT / new, follow_symlinks=False)
            linked = True
            h.claim(ROOT, new, claim['owned_sha256'], claim['identity'])
            h.claim(ROOT, old, claim['owned_sha256'], claim['identity'])
            (ROOT / old).unlink()
            removed = True
        finally: signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        assert not os.path.lexists(ROOT / old)
        index = s.h.index_state(ROOT, ENV)
        assert s.h.semantic_index(index) == epoch['semantic_index']
        current['raw_index_observation']['current'] = index['raw_index']
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        assert after['nested_index'] == before['nested_index']
        assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == b for n,b in flags.items())
        assert all(h.body(RUNTIME / n) == b for n,b in controls.items())
        h.write_owned(ROOT, claims['OWNED.json'], h.encoded(owners))
        h.write_owned(ROOT, claims['CURRENT-EPOCH.json'], h.encoded(current))
        assert s.a.verify_current(s.h, ROOT, ENV, current) == after
        assert h.body(RUNTIME / 'ROLE.json') == controls['ROLE.json']
        h.save(output / 'EPOCH.json', current)
        h.save(output / 'OWNERSHIP.json', {new:owners[new]})
        h.save(output / 'POST.json', after)
        h.save(output / 'RESULT.json', {'renamed':True, 'old_path':old, 'new_path':new, 'body_and_inode_preserved':True, 'native_and_binaries_unchanged':True, 'preservation_verified':True, 'accepted':False, 'build_epoch_sha256':epoch_sha, 'epoch_sha256':h.digest(h.body(RUNTIME / 'CURRENT-EPOCH.json')), 'raw_observation_changed':index['raw_index'] != epoch['raw_index_observation']['current']})
        release = True
    except BaseException as error:
        failures = []
        try:
            if linked:
                assert c.parent_pins(ROOT, ROOT / old) == parents
                h.claim(ROOT, new, claim['owned_sha256'], claim['identity'])
                if removed:
                    assert not os.path.lexists(ROOT / old)
                    os.link(ROOT / new, ROOT / old, follow_symlinks=False)
                h.claim(ROOT, old, claim['owned_sha256'], claim['identity'])
                (ROOT / new).unlink()
            restored = copy.deepcopy(epoch)
            index = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(index) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = index['raw_index']
            snapshot = s.a.verify_current(s.h, ROOT, ENV, restored)
            expected = copy.deepcopy(before); expected['index']['raw_index'] = index['raw_index']
            assert snapshot == expected
            assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == b for n,b in flags.items())
            h.write_owned(ROOT, claims['OWNED.json'], controls['OWNED.json'])
            h.write_owned(ROOT, claims['CURRENT-EPOCH.json'], h.encoded(restored))
            assert s.a.verify_current(s.h, ROOT, ENV, restored) == snapshot
            assert h.body(RUNTIME / 'ROLE.json') == controls['ROLE.json']
            assert h.body(RUNTIME / 'OWNED.json') == controls['OWNED.json']
            release = True
        except BaseException as rollback: failures.append(repr(rollback))
        if output.exists(): h.save(output / 'FAILURE.json', {'error':repr(error), 'rollback_errors':failures, 'manual_recovery_required':bool(failures)})
        raise
    finally:
        if release and lock_claim is not None:
            h.claim(ROOT, lock_claim['path'], lock_claim['owned_sha256'], lock_claim['identity'])
            lock.unlink()


if __name__ == '__main__':
    def interrupted(signum, frame): raise RuntimeError('Interrupted ' + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
