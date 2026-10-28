import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S -B without optimization')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
read = lambda path: json.loads(path.read_text())
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(h, manifest):
    h.authenticate(HERE, manifest)
    for name, pin in read(HERE / 'REFERENCES.json').items():
        assert h.sha(ROOT / name) == pin, name


def check_evidence(h, previous, policy, epoch):
    assert not policy['baseline_pending']
    capsule = ROOT / policy['baseline_capsule']
    h.authenticate(capsule, policy['baseline_capsule_sha256'])
    runner = load('provider_baseline_runner', str((capsule / 'run.py').relative_to(ROOT)))
    bindings = load('provider_baseline_bindings', str((capsule / 'bindings.py').relative_to(ROOT)))
    baseline_policy = read(capsule / 'POLICY.json')
    bindings.validate_phase(ROOT, capsule, baseline_policy, epoch, runner)
    run = ROOT / policy['required_run']
    assert sha(run / 'FILES.json') == policy['baseline_inventory_sha256']
    inventory = read(run / 'FILES.json')
    assert inventory['complete'] and not inventory['native_fix_accepted']
    assert len(inventory['files']) == 73
    for name, item in inventory['files'].items():
        assert sha(run / name) == item['sha256']
        assert (run / name).stat().st_size == item['bytes']
    for name, target in inventory['excluded_derived_links'].items():
        assert os.readlink(run / name) == target
    result, assessment = read(run / 'RESULT.json'), read(run / 'ASSESSMENT.json')
    outer = read(run / 'OUTER.json')
    assert outer['wrapper_exit'] == 0 and outer['wpt_exit'] == result['exit']
    assert result['observation_gate_passed'] and result['clean_staging_preserved']
    assert result['execution_error'] is None and result['preservation_error'] is None
    assert result['observation_only'] and not result['native_fix_acceptance']
    assert assessment['complete'] and assessment['execution_preserved']
    assert not assessment['errors'] and not assessment['infrastructure_faults']
    assert assessment['observed_subtest_count'] == len(assessment['rows']) == 775
    assert len(assessment['ends']) == 36
    assert assessment['capsule_manifest_sha256'] == policy['baseline_capsule_sha256']
    assert assessment['epoch_sha256'] == policy['epoch_sha256']
    assert read(run / 'EPOCH.json') == epoch
    assert assessment['native_sources'] == baseline_policy['source_roles']['candidate']
    assert read(run / 'PRE.json') == read(run / 'POST.json')
    assert assessment['run_binding'] == read(run / 'APPLICATION-METADATA.json')
    assert read(run / 'APPLICATION-METADATA.json') == read(run / 'APPLICATION-METADATA-POST.json')
    assert runner.application_metadata(ROOT / baseline_policy['application_ini'], policy['head']) == read(run / 'APPLICATION-METADATA.json')
    cleanup = read(run / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    h.group_absent(read(run / 'PROCESS.json')['pgid'])
    h.quiescent(ROOT / policy['runtime'])
    build = ROOT / policy['runtime'] / previous['last_build']
    result = read(build / 'RESULT.json')
    assert result['command_success'] and result['preservation_verified']
    assert not result['owned_processes'] and not result['publication_errors']
    for name in ['build-PROCESS.json', 'WAKE-PROCESS.json']:
        h.group_absent(read(build / name)['pgid'])
    census = subprocess.run(['ps', '-axo', 'pid=,ppid=,pgid=,command='],
                            check=True, capture_output=True, text=True).stdout
    prior = load('prior_source_census', 'artifacts/css-registered-zoom-standalone-transition-v3/install.py')
    prior.process_census_clear(census, os.getpid())


def recovery(s, policy, epoch, roles, added):
    runtime = ROOT / policy['runtime']
    restoration = read(runtime / 'RESTORATION-PLAN.json')['paths']
    assert len(restoration) == policy['parked_count']
    for name, item in restoration.items():
        assert sha(runtime / 'prototype-original' / name) == item['prototype_original']
        assert digest(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)) == item['head_original']
        assert sha(ROOT / name) == epoch['pins'].get(name, item['head_original'])
    captured = read(ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
    assert len(captured) == policy['recovery_count']
    for name, pin in captured.items():
        if name in ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json',
                    'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md']:
            assert sha(ROOT / name) == epoch['pins'][name]
        elif name in policy['ledger_preimages']:
            assert sha(ROOT / policy['ledger_preimages'][name]) == pin
            assert sha(ROOT / name) == epoch['pins'][name]
            assert digest(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)) == epoch['pins'][name]
        else:
            source = (runtime / 'prototype-original' / name if name in restoration else
                      ROOT / roles[name]['base'] if name in roles else ROOT / name)
            assert sha(source) == pin, name
    names = set(s.h.git(ROOT, ENV, 'ls-files', '--others', '--exclude-standard',
                       'dom/animation', 'layout/style/test/gtest', 'servo/components/style',
                       'testing/web-platform/tests/css').decode().splitlines())
    assert set(added) <= names and len(names - set(added)) == policy['prior_untracked_project_count']
    assert names - set(added) <= set(captured)
    return names


def main():
    policy = read(HERE / 'POLICY.json')
    assert policy['execution_enabled'] is True, 'Disabled pending baseline binding and review'
    assert len(sys.argv) == 3, 'Usage: install.py MANIFEST_SHA EPOCH_SHA'
    manifest, epoch_pin = sys.argv[1:]
    assert not any(os.environ.get(k) for k in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                                             'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                                             'RUSTFLAGS', 'CARGO_TARGET_DIR'])
    h = load('payload_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    authenticate(h, manifest)
    payload = ROOT / policy['payload']
    h.authenticate(payload, policy['payload_manifest_sha256'])
    for name, pin in read(payload / 'REFERENCES.json').items():
        assert h.sha(ROOT / name) == pin
    roles = policy['source_roles']
    assert set(roles) == set(read(payload / 'SOURCE-ROLES.json'))
    for name, pins in read(payload / 'SOURCE-ROLES.json').items():
        assert roles[name]['base_sha256'] == roles[name]['current_sha256'] == pins['base_sha256']
        assert roles[name]['candidate_sha256'] == pins['candidate_sha256']
    native = {n:r for n,r in roles.items() if r['kind'] == 'native'}
    edits = native
    tests = {n:r for n,r in roles.items() if r['kind'] == 'wpt'}
    assert (len(native), len(edits), len(tests)) == (2, 2, 0)
    runtime = ROOT / policy['runtime']
    s = h.load_state(runtime)
    create = load('existing_file_creation', 'artifacts/css-registered-admission-wpt-install-v1/install.py')
    controls_before = {n:h.body(runtime / n) for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
    epoch, role, owned = [json.loads(controls_before[n]) for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']]
    assert digest(controls_before['CURRENT-EPOCH.json']) == epoch_pin == policy['epoch_sha256']
    assert epoch == read(HERE / 'INITIAL-EPOCH.json')
    assert role == read(HERE / 'INITIAL-ROLE.json') and owned == read(HERE / 'INITIAL-OWNED.json')
    assert epoch['semantic_index']['head'] == policy['head']
    assert epoch['registered_number_transition'] == policy['previous_transition']
    assert role['role'] == 'candidate' and role['variant'] == 'zoom-standalone-v1' and role['built']
    assert epoch['accepted_registered_zoom']['native_commit'] == '0f40801f1418318e51f81b4e273c758a9a24b3e4'
    assert len(owned) == policy['owned_count'] and len(epoch['installed_identities']) == policy['installed_identity_count']
    assert epoch['modified_native_paths'] == []
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n:s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') for n in ['.', 'artifacts/css-spec-lean']}
    check_evidence(h, role, policy, epoch)
    prior_untracked = recovery(s, policy, epoch, roles, [])
    control_claims = {n:h.claim(ROOT, str((runtime/n).relative_to(ROOT)), digest(data)) for n,data in controls_before.items()}
    source_claims, desired, restore, parents = {}, {}, {}, {}
    for name, record in native.items():
        assert epoch['pins'][name] == owned[name]['owned_sha256'] == record['current_sha256']
        source_claims[name] = h.claim(ROOT, name, record['current_sha256'], epoch['installed_identities'][name])
        assert owned[name]['identity'] == source_claims[name]['identity']
        assert digest(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)) == record['base_sha256']
        restore[name] = h.body(ROOT / record['current'])
        assert digest(restore[name]) == record['current_sha256']
    for name, record in roles.items():
        desired[name] = h.body(payload / record['payload'])
        assert digest(desired[name]) == record['candidate_sha256']
    for name in tests:
        assert name not in owned and name not in epoch['pins'] and name not in epoch['installed_identities']
        assert not os.path.lexists(ROOT / name)
        assert not s.h.git(ROOT, ENV, 'ls-files', '--', name)
        assert not s.h.git(ROOT, ENV, 'ls-tree', 'HEAD', '--', name)
        parents[name] = create.parent_pins(ROOT, ROOT / name)

    def claims():
        authenticate(h, manifest)
        for item in list(control_claims.values()) + list(source_claims.values()):
            h.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
        for name in tests:
            assert create.parent_pins(ROOT, ROOT / name) == parents[name]

    def preserve(current, added):
        assert current['accepted_registered_zoom'] == epoch['accepted_registered_zoom']
        assert all(s.h.git(ROOT/n, ENV, 'ls-files', '-v', '-z') == value for n,value in flags.items())
        assert recovery(s, policy, current, roles, added) == prior_untracked | set(added)
        assert s.h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']

    lock = runtime / 'SOURCE-TRANSITION.lock'
    assert not os.path.lexists(lock)
    lock_item = None
    changed, created, current = [], {}, copy.deepcopy(epoch)
    run = runtime / policy['install_label']
    assert not os.path.lexists(run)
    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            lock_item = create.create_owned(h, ROOT, str(lock.relative_to(ROOT)), create.parent_pins(ROOT, lock))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        run.mkdir()
        for name, data in controls_before.items():
            (run / ('PRE-' + name)).write_bytes(data)
        h.save(run / 'PRE.json', before)
        h.save(run / 'FLAGS.json', {n:digest(v) for n,v in flags.items()})
        h.save(run / 'PAYLOAD-BINDING.json', {'path':policy['payload'],'manifest_sha256':policy['payload_manifest_sha256']})
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        preserve(epoch, [])
        claims()
        check_evidence(h, role, policy, epoch)
        claims()
        for name in edits:
            changed.append(name)
            h.write_owned(ROOT, source_claims[name], desired[name])
            owned[name]['owned_sha256'] = roles[name]['candidate_sha256']
            for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
                if name in current[key]:
                    current[key][name] = roles[name]['candidate_sha256']
        for name in tests:
            blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
            try:
                created[name] = create.create_owned(h, ROOT, name, parents[name])
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
            h.write_owned(ROOT, created[name], desired[name])
            owned[name] = copy.deepcopy(created[name])
            current['pins'][name] = roles[name]['candidate_sha256']
            current['installed_identities'][name] = created[name]['identity']
        state = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(state)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = state['raw_index']
        current['modified_native_paths'] = sorted(edits)
        current['counts']['native_modified_paths'] = len(edits)
        current['counts']['roles'] = len(current['pins'])
        current['counts']['installed_identities'] = len(current['installed_identities'])
        current['registered_number_transition'] = {'role':'candidate','variant':policy['variant'],
            'compiled':False,'accepted':False,'last_phase':policy['install_label']}
        current['registered_provider_default_transition'] = {'manifest_sha256':policy['payload_manifest_sha256'],
            'changed_native':sorted(edits),'new_wpt':sorted(tests),'accepted':False}
        role.update(role='candidate', variant=policy['variant'], built=False, last_install=policy['install_label'], last_transition=policy['install_label'], paired_head=policy['head'])
        preserve(current, tests)
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        h.save(run / 'INDEX-OBSERVATION.json', {'before':before['index']['raw_index'],
            'after':state['raw_index'],'cause':'not inferred','semantic_index_except_working_diff_preserved':True})
        for name, value in [('OWNED.json',owned),('ROLE.json',role),('CURRENT-EPOCH.json',current)]:
            h.write_owned(ROOT, control_claims[name], h.encoded(value))
        assert s.a.verify_current(s.h, ROOT, ENV, read(runtime/'CURRENT-EPOCH.json')) == after
        preserve(current, tests)
        claims()
        h.save(run / 'POST.json', after)
        h.save(run / 'EPOCH.json', current)
        h.save(run / 'POST-ROLE.json', role)
        h.save(run / 'POST-OWNED.json', owned)
        h.save(run / 'CREATED.json', created)
        h.save(run / 'RESULT.json', {'installed':True,'compiled':False,'accepted':False,
            'native_changes':2,'modified_native_paths':2,'new_wpt':0,'preservation_verified':True,
            'epoch_sha256':sha(runtime/'CURRENT-EPOCH.json')})
    except BaseException as error:
        failures = []
        try:
            for name, item in reversed(list(created.items())):
                h.claim(ROOT, name, item['owned_sha256'], item['identity'])
                (ROOT/name).unlink()
            for name in reversed(changed):
                h.write_owned(ROOT, source_claims[name], restore[name])
            restored = copy.deepcopy(epoch)
            state = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(state) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = state['raw_index']
            preserve(restored, [])
            s.a.verify_current(s.h, ROOT, ENV, restored)
            for name in ['OWNED.json','ROLE.json','CURRENT-EPOCH.json']:
                data = h.encoded(restored) if name == 'CURRENT-EPOCH.json' else controls_before[name]
                h.write_owned(ROOT, control_claims[name], data)
            s.a.verify_current(s.h, ROOT, ENV, restored)
            if run.is_dir():
                h.save(run/'ROLLED-BACK.json', {'source_and_control_semantics_restored':True,
                    'raw_index_before':epoch['raw_index_observation']['current'],
                    'raw_index_after':restored['raw_index_observation']['current'],
                    'raw_drift_cause':'not inferred','epoch_sha256':sha(runtime/'CURRENT-EPOCH.json')})
        except BaseException as rollback:
            failures.append(repr(rollback))
        if run.is_dir():
            h.save(run/'FAILURE.json', {'error':repr(error),'rollback_errors':failures,
                'manual_recovery_required':bool(failures),'created':created,'changed_native':changed})
        raise
    finally:
        if lock_item is not None:
            h.claim(ROOT, lock_item['path'], lock_item['owned_sha256'], lock_item['identity'])
            lock.unlink()


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise RuntimeError('Interrupted: ' + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
