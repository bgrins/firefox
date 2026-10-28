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


def main():
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    assert policy['install_enabled'] is True
    assert len(sys.argv) == 3
    manifest, epoch_digest = sys.argv[1:]
    assert epoch_digest == policy['epoch_sha256']
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    h = load('promotion_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    create = load('promotion_creation', ROOT / 'artifacts/css-registered-admission-wpt-install-v1/install.py')
    evidence = load('promotion_evidence', HERE / 'evidence.py')
    h.authenticate(HERE, manifest)
    for name, digest in policy['references'].items():
        assert h.digest((ROOT / name).read_bytes()) == digest
    for directory, digest in policy['packages'].items():
        h.authenticate(ROOT / directory, digest)
    s = h.load_state(RUNTIME)
    controls = {n: h.body(RUNTIME / n) for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert h.digest(controls['CURRENT-EPOCH.json']) == epoch_digest
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
    held = 'servo/components/style/custom_properties.rs'
    assert epoch['modified_native_paths'] == [held]
    evidence_binding = evidence.verify(ROOT, policy, epoch, h)
    h.quiescent(RUNTIME)
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n: s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') for n in ('.', 'artifacts/css-spec-lean')}
    control_claims = {n: h.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), h.digest(body)) for n, body in controls.items()}
    record = policy['source']
    name = record['path']
    assert name == 'servo/components/style/values/specified/font.rs'
    base, desired = [h.body(ROOT / record[k]) for k in ('base_capture', 'candidate_capture')]
    assert h.digest(base) == record['base_sha256'] and h.digest(desired) == record['candidate_sha256']
    assert h.digest(s.h.git(ROOT, ENV, 'show', policy['head'] + ':' + name)) == record['base_sha256']
    source_claim = h.claim(ROOT, name, record['base_sha256'])
    assert epoch['pins'].get(name, record['base_sha256']) == record['base_sha256']
    assert epoch['installed_identities'].get(name, source_claim['identity']) == source_claim['identity']
    owned = json.loads(controls['OWNED.json'])
    if name in owned:
        assert owned[name] == source_claim
    tests, parents = {}, {}
    assert set(policy['tests']) == {
        'testing/web-platform/tests/css/css-values/line-height-contextual-number.tentative.html',
        'testing/web-platform/tests/css/css-inline/line-height-tree-counting.html',
    }
    for test, item in policy['tests'].items():
        tests[test] = h.body(ROOT / item['capture'])
        assert h.digest(tests[test]) == item['sha256']
        assert not os.path.lexists(ROOT / test) and test not in epoch['pins'] and test not in owned
        assert not s.h.git(ROOT, ENV, 'ls-files', '--stage', '--', test)
        assert not s.h.git(ROOT, ENV, 'ls-tree', policy['head'], '--', test)
        parents[test] = create.parent_pins(ROOT, ROOT / test)
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and not os.path.lexists(output)
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert not os.path.lexists(lock)
    changed, created, lock_claim, release = False, {}, None, False

    def claims():
        for n, item in control_claims.items():
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
            assert h.body(RUNTIME / n) == controls[n]
        h.claim(ROOT, name, source_claim['owned_sha256'], source_claim['identity'])

    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            lock_claim = create.create_owned(h, ROOT, str(lock.relative_to(ROOT)), create.parent_pins(ROOT, lock))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        output.mkdir()
        for n, body in controls.items():
            (output / ('PRE-' + n)).write_bytes(body)
        h.save(output / 'PRE.json', before)
        h.save(output / 'EVIDENCE.json', evidence_binding)
        h.save(output / 'SOURCE-OWNERSHIP.json', source_claim)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        claims()
        assert evidence.verify(ROOT, policy, epoch, h) == evidence_binding
        claims()
        changed = True
        h.write_owned(ROOT, source_claim, desired)
        current = copy.deepcopy(epoch)
        current['pins'][name] = record['candidate_sha256']
        current['installed_identities'][name] = source_claim['identity']
        owned[name] = source_claim
        for test, body in tests.items():
            blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
            try:
                created[test] = create.create_owned(h, ROOT, test, parents[test])
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
            h.save(output / ('CREATED-' + str(len(created)) + '.json'), created)
            h.write_owned(ROOT, created[test], body)
            h.save(output / ('WRITTEN-' + str(len(created)) + '.json'), created)
            current = create.updated_epoch(current, test, created[test], h.digest(body))
            owned[test] = created[test]
        index = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = index['raw_index']
        current['modified_native_paths'] = sorted([held, name])
        current['counts']['native_modified_paths'] = 2
        current['counts']['roles'] = len(current['pins'])
        current['counts']['installed_identities'] = len(current['installed_identities'])
        current['line_height_transition'] = {'role':'candidate', 'compiled':False, 'accepted':False,
            'manifest_sha256':manifest, 'source_sha256':record['candidate_sha256'], 'last_phase':'install'}
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        assert after['nested_index'] == before['nested_index']
        assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == body for n, body in flags.items())
        assert all(h.body(RUNTIME / n) == body for n, body in controls.items())
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            h.write_owned(ROOT, control_claims['OWNED.json'], h.encoded(owned))
            h.write_owned(ROOT, control_claims['CURRENT-EPOCH.json'], h.encoded(current))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        assert s.a.verify_current(s.h, ROOT, ENV, current) == after
        assert h.body(RUNTIME / 'ROLE.json') == controls['ROLE.json']
        h.save(output / 'OWNERSHIP.json', {name:source_claim, **created})
        h.save(output / 'INSTALLED-EPOCH.json', current)
        h.save(output / 'POST.json', after)
        h.save(output / 'INSTALL-RESULT.json', {'installed':True, 'compiled':False, 'accepted':False,
            'preservation_verified':True, 'files':[name, *tests],
            'held_provider_preserved':True, 'epoch_sha256':h.digest(h.body(RUNTIME / 'CURRENT-EPOCH.json'))})
        release = True
    except BaseException as error:
        failures = []
        try:
            for test, item in reversed(list(created.items())):
                h.claim(ROOT, test, item['owned_sha256'], item['identity'])
                assert create.parent_pins(ROOT, ROOT / test) == parents[test]
                (ROOT / test).unlink()
            if changed:
                h.write_owned(ROOT, source_claim, base)
            restored = copy.deepcopy(epoch)
            index = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(index) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = index['raw_index']
            restored_snapshot = s.a.verify_current(s.h, ROOT, ENV, restored)
            expected_snapshot = copy.deepcopy(before)
            expected_snapshot['index']['raw_index'] = index['raw_index']
            assert restored_snapshot == expected_snapshot
            assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == body for n, body in flags.items())
            assert h.body(RUNTIME / 'ROLE.json') == controls['ROLE.json']
            h.write_owned(ROOT, control_claims['OWNED.json'], controls['OWNED.json'])
            h.write_owned(ROOT, control_claims['CURRENT-EPOCH.json'], h.encoded(restored))
            assert s.a.verify_current(s.h, ROOT, ENV, restored) == restored_snapshot
            assert h.body(RUNTIME / 'OWNED.json') == controls['OWNED.json']
            assert h.body(RUNTIME / 'ROLE.json') == controls['ROLE.json']
            release = True
        except BaseException as rollback:
            failures.append(repr(rollback))
        if output.exists():
            h.save(output / 'FAILURE.json', {'error':repr(error), 'rollback_errors':failures,
                'manual_recovery_required':bool(failures), 'source_owner':source_claim, 'created':created})
        raise
    finally:
        if release and lock_claim is not None:
            h.claim(ROOT, lock_claim['path'], lock_claim['owned_sha256'], lock_claim['identity'])
            lock.unlink()


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise RuntimeError('Interrupted ' + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
