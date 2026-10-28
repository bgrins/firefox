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
    create = load('repair_lock', 'artifacts/css-registered-admission-wpt-install-v1/install.py')

    def authenticate():
        h.authenticate(HERE, manifest)
        prior.authenticate(h, policy['prior_manifest_sha256'])
        h.authenticate(ROOT / policy['proposal'], policy['proposal_manifest_sha256'])
        for name, pin in read(HERE / 'REFERENCES.json').items():
            assert sha(ROOT / name) == pin

    authenticate()
    bodies = {n: h.body(runtime / n) for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
    epoch, role, owned = [json.loads(bodies[n]) for n in bodies]
    assert h.digest(bodies['CURRENT-EPOCH.json']) == epoch_pin == policy['epoch_sha256']
    for n in bodies:
        assert bodies[n] == (HERE / ('INITIAL-' + n)).read_bytes()
    assert role['variant'] == 'registered-provider-default-v3' and not role['built']
    assert role['last_build'] == policy['failed_build']
    assert epoch['registered_number_transition']['compiled'] is False
    assert epoch['modified_native_paths'] == sorted(prior_policy['source_roles'])
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n:s.h.git(ROOT/n, ENV, 'ls-files', '-v', '-z') for n in ['.', 'artifacts/css-spec-lean']}
    saved_untracked = prior.recovery(s, prior_policy, epoch, prior_policy['source_roles'], [])
    controls = {n:h.claim(ROOT, str((runtime/n).relative_to(ROOT)), h.digest(body)) for n,body in bodies.items()}
    name = policy['source']
    source = h.claim(ROOT, name, policy['old_sha256'], epoch['installed_identities'][name])
    assert owned[name]['owned_sha256'] == policy['old_sha256'] and owned[name]['identity'] == source['identity']
    restore = h.body(ROOT / name)
    assert h.digest(restore) == policy['old_sha256']
    desired = h.body(ROOT / policy['proposal'] / 'candidate' / name)
    assert h.digest(desired) == policy['new_sha256']

    def claims():
        authenticate()
        for item in [source, *controls.values()]:
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])

    def preserve(current):
        assert prior.recovery(s, prior_policy, current, prior_policy['source_roles'], []) == saved_untracked
        assert all(s.h.git(ROOT/n, ENV, 'ls-files', '-v', '-z') == value for n,value in flags.items())
        assert s.h.index_state(ROOT/'artifacts/css-spec-lean', ENV) == before['nested_index']

    def quiescent():
        h.quiescent(runtime)
        build = runtime / policy['failed_build']
        result = read(build/'RESULT.json')
        assert not result['command_success'] and result['preservation_verified']
        assert not result['owned_processes'] and not result['publication_errors']
        assert read(build/'OUTER.json')['exit_code'] == 1
        assert read(build/'EPOCH.json') == epoch
        for n in ['build-PROCESS.json', 'WAKE-PROCESS.json']:
            h.group_absent(read(build/n)['pgid'])
        census = subprocess.run(['ps','-axo','pid=,ppid=,pgid=,command='], check=True, capture_output=True, text=True).stdout
        guard = load('repair_census', 'artifacts/css-registered-zoom-standalone-transition-v3/install.py')
        guard.process_census_clear(census, os.getpid())

    quiescent()
    lock = runtime / 'SOURCE-TRANSITION.lock'
    run = runtime / policy['label']
    assert not os.path.lexists(lock) and not os.path.lexists(run)
    lock_item = None
    changed = False
    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            lock_item = create.create_owned(h, ROOT, str(lock.relative_to(ROOT)), create.parent_pins(ROOT, lock))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        run.mkdir()
        h.save(run/'PRE.json', before)
        for n, body in bodies.items():
            (run/('PRE-'+n)).write_bytes(body)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        preserve(epoch)
        claims()
        quiescent()
        claims()
        changed = True
        h.write_owned(ROOT, source, desired)
        current = copy.deepcopy(epoch)
        for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
            if name in current[key]:
                current[key][name] = policy['new_sha256']
        owned[name]['owned_sha256'] = policy['new_sha256']
        index = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = index['raw_index']
        current['registered_number_transition'].update(variant=policy['variant'], compiled=False, accepted=False, last_phase=policy['label'])
        current['registered_provider_default_transition']['manifest_sha256'] = policy['proposal_manifest_sha256']
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
        h.save(run/'RESULT.json', {'installed':True,'compiled':False,'accepted':False,'native_changes':1,'preservation_verified':True,'epoch_sha256':sha(runtime/'CURRENT-EPOCH.json')})
    except BaseException as error:
        failures = []
        try:
            if changed:
                h.write_owned(ROOT, source, restore)
            restored = copy.deepcopy(epoch)
            index = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(index) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = index['raw_index']
            preserve(restored)
            s.a.verify_current(s.h, ROOT, ENV, restored)
            for n in bodies:
                h.write_owned(ROOT, controls[n], h.encoded(restored) if n == 'CURRENT-EPOCH.json' else bodies[n])
            s.a.verify_current(s.h, ROOT, ENV, restored)
            if run.is_dir():
                h.save(run/'ROLLED-BACK.json', {'source_and_control_semantics_restored':True,'raw_index_before':epoch['raw_index_observation']['current'],'raw_index_after':index['raw_index'],'cause':'not inferred'})
        except BaseException as rollback:
            failures.append(repr(rollback))
        if run.is_dir():
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
