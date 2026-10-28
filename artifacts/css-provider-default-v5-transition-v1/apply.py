import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def validate_projection(original, current, roles, policy):
    expected = copy.deepcopy(original)
    for name, record in roles.items():
        for key in ['pins', 'committed_research_working_payloads']:
            if name in expected[key]:
                expected[key][name] = record['ordinary_restored_sha256']
    expected['modified_native_paths'] = ['servo/components/style/custom_properties.rs']
    expected['counts']['native_modified_paths'] = 1
    expected['semantic_index']['working_diff'] = current['semantic_index']['working_diff']
    expected['raw_index_observation']['current'] = current['raw_index_observation']['current']
    expected['registered_number_transition'].update(variant=policy['variant'], compiled=False,
                                                   accepted=False, last_phase=policy['label'])
    expected['registered_provider_default_transition'].update(
        manifest_sha256=policy['proposal_manifest_sha256'],
        changed_native=expected['modified_native_paths'], written_native=sorted(roles), accepted=False)
    assert expected == current


def main():
    policy = read(HERE / 'POLICY.json')
    assert policy['enabled']
    manifest, epoch_pin = sys.argv[1:]
    assert not any(os.environ.get(k) for k in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'RUSTFLAGS', 'CARGO_TARGET_DIR'])
    h = load('repair_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    prior = load('provider_install', policy['prior_installer'] + '/install.py')
    prior_policy = read(ROOT / policy['prior_installer'] / 'POLICY.json')
    runtime = ROOT / prior_policy['runtime']
    s = h.load_state(runtime)
    s.a = load('staged_guard', policy['staged_capsule'] + '/epoch.py')
    create = load('repair_lock', 'artifacts/css-registered-admission-wpt-install-v1/install.py')

    def authenticate():
        h.authenticate(HERE, manifest)
        prior.authenticate(h, policy['prior_manifest_sha256'])
        h.authenticate(ROOT / policy['staged_capsule'], policy['staged_manifest_sha256'])
        h.authenticate(ROOT / policy['proposal'], policy['proposal_manifest_sha256'])
        for name, pin in read(HERE / 'REFERENCES.json').items():
            assert sha(ROOT / name) == pin

    authenticate()
    bodies = {n: h.body(runtime / n) for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
    epoch, role, owned = [json.loads(bodies[n]) for n in bodies]
    assert h.digest(bodies['CURRENT-EPOCH.json']) == epoch_pin == policy['epoch_sha256']
    for n in bodies:
        assert bodies[n] == (HERE / ('INITIAL-' + n)).read_bytes()
    assert role['variant'] == 'registered-provider-default-v4' and role['built']
    assert role['last_build'] == policy['prior_build']
    assert epoch['registered_number_transition'] == policy['previous_transition']
    assert epoch['semantic_index']['head'] == policy['head']
    adoption = runtime / policy['adoption_label']
    result = read(adoption / 'RESULT.json')
    assert result['adopted'] and result['metadata_only'] and result['preservation_verified']
    assert not result['source_or_index_writes'] and result['staged_paths'] == 36
    assert (adoption / 'EPOCH.json').read_bytes() == bodies['CURRENT-EPOCH.json']
    assert epoch['modified_native_paths'] == sorted(prior_policy['source_roles'])
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n:s.h.git(ROOT/n, ENV, 'ls-files', '-v', '-z') for n in ['.', 'artifacts/css-spec-lean']}
    saved_untracked = prior.recovery(s, prior_policy, epoch, prior_policy['source_roles'], [])
    controls = {n:h.claim(ROOT, str((runtime/n).relative_to(ROOT)), h.digest(body)) for n,body in bodies.items()}
    sources, restore, desired = {}, {}, {}
    roles = read(ROOT / policy['proposal'] / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_roles']) and len(roles) == 2
    for name, record in roles.items():
        assert record == policy['source_roles'][name]
        sources[name] = h.claim(ROOT, name, record['v4_sha256'], epoch['installed_identities'][name])
        assert owned[name]['owned_sha256'] == record['v4_sha256']
        assert owned[name]['identity'] == sources[name]['identity']
        assert epoch['pins'][name] == record['v4_sha256']
        assert h.digest(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)) == record['base_sha256']
        restore[name] = h.body(ROOT / policy['proposal'] / 'v4' / name)
        desired[name] = h.body(ROOT / policy['proposal'] / 'ordinary-restored' / name)
        assert h.digest(restore[name]) == record['v4_sha256']
        assert h.digest(desired[name]) == record['ordinary_restored_sha256']
    dirty = sorted(n for n,r in roles.items() if r['ordinary_restored_sha256'] != r['base_sha256'])
    assert dirty == ['servo/components/style/custom_properties.rs']

    def claims():
        authenticate()
        for item in [*sources.values(), *controls.values()]:
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])

    def preserve(current):
        assert prior.recovery(s, prior_policy, current, prior_policy['source_roles'], []) == saved_untracked
        assert all(s.h.git(ROOT/n, ENV, 'ls-files', '-v', '-z') == value for n,value in flags.items())
        assert s.h.index_state(ROOT/'artifacts/css-spec-lean', ENV) == before['nested_index']

    def quiescent():
        h.quiescent(runtime)
        build = runtime / policy['prior_build']
        result = read(build/'RESULT.json')
        assert result['command_success'] and result['preservation_verified']
        assert not result['owned_processes'] and not result['publication_errors']
        build_epoch = read(build/'EPOCH.json')
        assert build_epoch['pins'] == epoch['pins']
        assert build_epoch['registered_number_transition'] == epoch['registered_number_transition']
        for directory in policy['completed_observers']:
            completed = ROOT / directory
            result, cleanup = read(completed/'RESULT.json'), read(completed/'CLEANUP.json')
            assert result['observation_gate_passed'] and result['execution_error'] is None and result['preservation_error'] is None
            assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
            h.group_absent(read(completed/'PROCESS.json')['pgid'])
        for n in ['build-PROCESS.json', 'WAKE-PROCESS.json']:
            h.group_absent(read(build/n)['pgid'])
        census = subprocess.run(['ps','-axo','pid=,ppid=,pgid=,command='], check=True, capture_output=True, text=True).stdout
        guard = load('repair_census', 'artifacts/css-registered-zoom-standalone-transition-v3/install.py')
        guard.process_census_clear(census, os.getpid())

    quiescent()
    lock = runtime / 'SOURCE-TRANSITION.lock'
    assert runtime.is_dir() and not runtime.is_symlink()
    assert policy['label'] == 'provider-default-partial-v5-install-1'
    run = runtime / policy['label']
    assert not os.path.lexists(lock) and not os.path.lexists(run)
    lock_item = None
    changed, run_identity = [], None
    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            lock_item = create.create_owned(h, ROOT, str(lock.relative_to(ROOT)), create.parent_pins(ROOT, lock))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        run.mkdir()
        info = run.stat()
        run_identity = (info.st_dev, info.st_ino)
        h.save(run/'PRE.json', before)
        for n, body in bodies.items():
            (run/('PRE-'+n)).write_bytes(body)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        preserve(epoch)
        claims()
        quiescent()
        claims()
        current = copy.deepcopy(epoch)
        for name in sources:
            claims()
            changed.append(name)
            h.write_owned(ROOT, sources[name], desired[name])
            pin = roles[name]['ordinary_restored_sha256']
            for key in ['pins', 'committed_research_working_payloads']:
                if name in current[key]:
                    current[key][name] = pin
            owned[name]['owned_sha256'] = pin
        assert current['staged_working'] == epoch['staged_working']
        current['modified_native_paths'] = dirty
        current['counts']['native_modified_paths'] = len(dirty)
        index = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = index['raw_index']
        current['registered_number_transition'].update(variant=policy['variant'], compiled=False, accepted=False, last_phase=policy['label'])
        current['registered_provider_default_transition'].update(manifest_sha256=policy['proposal_manifest_sha256'], changed_native=dirty, written_native=sorted(sources), accepted=False)
        validate_projection(epoch, current, roles, policy)
        role.update(variant=policy['variant'], built=False, last_transition=policy['label'])
        preserve(current)
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        for n,value in [('OWNED.json',owned),('ROLE.json',role),('CURRENT-EPOCH.json',current)]:
            h.write_owned(ROOT, controls[n], h.encoded(value))
        claims()
        assert s.a.verify_current(s.h, ROOT, ENV, current) == after
        preserve(current)
        h.save(run/'POST.json', after)
        h.save(run/'EPOCH.json', current)
        h.save(run/'RESULT.json', {'installed':True,'compiled':False,'accepted':False,'native_changes':2,'modified_native_paths':1,'staged_paths':36,'preservation_verified':True,'epoch_sha256':sha(runtime/'CURRENT-EPOCH.json')})
    except BaseException as error:
        failures = []
        try:
            for name in reversed(changed):
                h.write_owned(ROOT, sources[name], restore[name])
            restored = copy.deepcopy(epoch)
            index = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(index) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = index['raw_index']
            preserve(restored)
            restored_snapshot = s.a.verify_current(s.h, ROOT, ENV, restored)
            expected_before = copy.deepcopy(before)
            expected_before['index']['raw_index'] = index['raw_index']
            assert restored_snapshot == expected_before
            for n in bodies:
                h.write_owned(ROOT, controls[n], h.encoded(restored) if n == 'CURRENT-EPOCH.json' else bodies[n])
            restored_snapshot = s.a.verify_current(s.h, ROOT, ENV, restored)
            expected_before = copy.deepcopy(before)
            expected_before['index']['raw_index'] = index['raw_index']
            assert restored_snapshot == expected_before
            preserve(restored)
            claims()
            if run_identity is not None and not run.is_symlink() and run.is_dir() and (run.stat().st_dev, run.stat().st_ino) == run_identity:
                h.save(run/'ROLLED-BACK.json', {'source_and_control_semantics_restored':True,'raw_index_before':epoch['raw_index_observation']['current'],'raw_index_after':index['raw_index'],'cause':'not inferred'})
        except BaseException as rollback:
            failures.append(repr(rollback))
        if run_identity is not None and not run.is_symlink() and run.is_dir() and (run.stat().st_dev, run.stat().st_ino) == run_identity:
            h.save(run/'FAILURE.json', {'error':repr(error),'rollback_errors':failures,'manual_recovery_required':bool(failures)})
        raise
    finally:
        if lock_item:
            h.claim(ROOT, lock_item['path'], lock_item['owned_sha256'], lock_item['identity'])
            lock.unlink()


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise RuntimeError('Interrupted: ' + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
