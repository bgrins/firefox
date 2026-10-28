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
    owned = json.loads(controls['OWNED.json'])
    assert h.digest(controls['OWNED.json']) == policy['owned_sha256']
    assert h.digest(controls['ROLE.json']) == policy['role_sha256']
    for name, digest in policy['accepted_line_height'].items():
        assert epoch['pins'][name] == digest
        h.claim(ROOT, name, digest, epoch['installed_identities'][name])
    source_claims, bases, desired = {}, {}, {}
    for name, record in policy['sources'].items():
        bases[name], desired[name] = [h.body(ROOT / record[k]) for k in ('base_capture', 'candidate_capture')]
        assert h.digest(bases[name]) == record['base_sha256'] and h.digest(desired[name]) == record['candidate_sha256']
        assert h.digest(s.h.git(ROOT, ENV, 'show', policy['head'] + ':' + name)) == record['base_sha256']
        item = h.claim(ROOT, name, record['base_sha256'])
        assert epoch['pins'].get(name, record['base_sha256']) == record['base_sha256']
        assert epoch['installed_identities'].get(name, item['identity']) == item['identity']
        if name in owned:
            assert owned[name] == item
        source_claims[name] = item
    overwritten, created_test, retired = [policy[k] for k in ('overwritten_test','created_test','retired_test')]
    assert set(policy['tests']) == {overwritten, created_test}
    assert set(policy['existing_tests']) == {overwritten, retired}
    assert policy['existing_tests'] == h.read(ROOT/'artifacts/css-random-counter-wpt-install-v1/INSTALLED.json')
    existing, original_tests, tests, parents = {}, {}, {}, {}
    for name in (overwritten, created_test, retired):
        assert name not in epoch['pins'] and name not in epoch['installed_identities'] and name not in owned
        assert name not in epoch['untracked_native'] and name not in epoch['committed_research_working_payloads']
        assert not s.h.git(ROOT, ENV, 'ls-files', '--stage', '--', name)
        assert not s.h.git(ROOT, ENV, 'ls-tree', policy['head'], '--', name)
        parents[name] = create.parent_pins(ROOT, ROOT / name)
    for name, item in policy['existing_tests'].items():
        existing[name] = h.claim(ROOT, name, item['sha256'], item['identity'])
        original_tests[name] = h.body(ROOT / name)
        assert h.digest(original_tests[name]) == item['sha256']
        assert h.body(ROOT / item['source']) == original_tests[name]
    assert not os.path.lexists(ROOT / created_test)
    for name, item in policy['tests'].items():
        tests[name] = h.body(ROOT / item['capture'])
        assert h.digest(tests[name]) == item['sha256']
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and not os.path.lexists(output)
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert not os.path.lexists(lock)
    changed, created, lock_claim, release = [], {}, None, False
    test_changed, retirement = False, None

    def claims():
        for n, item in control_claims.items():
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
            assert h.body(RUNTIME / n) == controls[n]
        for item in source_claims.values():
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
        for item in existing.values():
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])

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
        h.save(output / 'SOURCE-OWNERSHIP.json', source_claims)
        h.save(output / 'EXISTING-TEST-OWNERSHIP.json', existing)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        claims()
        assert evidence.verify(ROOT, policy, epoch, h) == evidence_binding
        claims()
        current = copy.deepcopy(epoch)
        for name, item in source_claims.items():
            changed.append(name)
            h.write_owned(ROOT, item, desired[name])
            current['pins'][name] = policy['sources'][name]['candidate_sha256']
            current['installed_identities'][name] = item['identity']
            owned[name] = item
        test_changed = True
        h.write_owned(ROOT, existing[overwritten], tests[overwritten])
        current = create.updated_epoch(current, overwritten, existing[overwritten], h.digest(tests[overwritten]))
        owned[overwritten] = existing[overwritten]
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            created[created_test] = create.create_owned(h, ROOT, created_test, parents[created_test])
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        h.save(output / 'CREATED.json', created)
        h.write_owned(ROOT, created[created_test], tests[created_test])
        current = create.updated_epoch(current, created_test, created[created_test], h.digest(tests[created_test]))
        owned[created_test] = created[created_test]
        archived = output / 'RETIRED-WPT.html'
        assert not os.path.lexists(archived)
        item = existing[retired]
        h.claim(ROOT, retired, item['owned_sha256'], item['identity'])
        assert create.parent_pins(ROOT, ROOT / retired) == parents[retired]
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            os.rename(ROOT / retired, archived)
            retirement = {'original_path':retired,'archived_path':str(archived.relative_to(ROOT)),
                          'claim':dict(item,path=str(archived.relative_to(ROOT)))}
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        h.claim(ROOT, retirement['archived_path'], item['owned_sha256'], item['identity'])
        h.save(output / 'RETIREMENT.json', retirement)
        index = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = index['raw_index']
        current['modified_native_paths'] = sorted([held, *source_claims])
        current['counts']['native_modified_paths'] = len(current['modified_native_paths'])
        current['counts']['roles'] = len(current['pins'])
        current['counts']['installed_identities'] = len(current['installed_identities'])
        current['random_counter_transition'] = {'role':'candidate', 'variant':'random-parser-counter-rollback', 'compiled':False, 'accepted':False,
            'manifest_sha256':manifest, 'source_sha256':{n:r['candidate_sha256'] for n,r in policy['sources'].items()}, 'last_phase':'install'}
        assert not os.path.lexists(ROOT / retired)
        h.claim(ROOT, retirement['archived_path'], item['owned_sha256'], item['identity'])
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
        h.save(output / 'OWNERSHIP.json', {**source_claims, overwritten:existing[overwritten], **created})
        h.save(output / 'INSTALLED-EPOCH.json', current)
        h.save(output / 'POST.json', after)
        h.save(output / 'INSTALL-RESULT.json', {'installed':True, 'compiled':False, 'accepted':False,
            'preservation_verified':True, 'files':[*source_claims, *tests], 'retired_path':retired,
            'held_provider_preserved':True, 'epoch_sha256':h.digest(h.body(RUNTIME / 'CURRENT-EPOCH.json'))})
        release = True
    except BaseException as error:
        failures = []
        try:
            for test, item in reversed(list(created.items())):
                h.claim(ROOT, test, item['owned_sha256'], item['identity'])
                assert create.parent_pins(ROOT, ROOT / test) == parents[test]
                (ROOT / test).unlink()
            if retirement is not None:
                item = retirement['claim']
                h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
                assert not os.path.lexists(ROOT / retired)
                assert create.parent_pins(ROOT, ROOT / retired) == parents[retired]
                os.rename(ROOT / item['path'], ROOT / retired)
            if test_changed:
                h.write_owned(ROOT, existing[overwritten], original_tests[overwritten])
            for name in reversed(changed):
                h.write_owned(ROOT, source_claims[name], bases[name])
            for name, item in existing.items():
                h.claim(ROOT, name, h.digest(original_tests[name]), item['identity'])
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
                'manual_recovery_required':bool(failures), 'source_owners':source_claims, 'created':created, 'retirement':retirement})
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
