import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def derive(epoch, pre, post, raw):
    assert raw['semantic_index_unchanged'] and not raw['canonical_updated']
    assert raw['before'] == pre['index']['raw_index'] == epoch['raw_index_observation']['current']
    assert raw['after'] == post['index']['raw_index']
    assert {k:v for k,v in pre['index'].items() if k != 'raw_index'} == epoch['semantic_index']
    projected = copy.deepcopy(pre)
    projected['index']['raw_index'] = raw['after']
    assert projected == post
    updated = copy.deepcopy(epoch)
    updated['raw_index_observation']['current'] = raw['after']
    return updated


def admit_current_raw(updated, post, actual_index):
    assert {k:v for k,v in actual_index.items() if k != 'raw_index'} == {k:v for k,v in post['index'].items() if k != 'raw_index'}
    current = copy.deepcopy(updated)
    current['raw_index_observation']['current'] = actual_index['raw_index']
    expected = copy.deepcopy(post)
    expected['index']['raw_index'] = actual_index['raw_index']
    return current, expected


def saved(policy):
    assert not policy['pending_runtime_binding'], 'Completed paired runtime binding is pending'
    owner = load('refresh_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    owner_dir = ROOT / policy['owner']['directory']
    owner.authenticate(owner_dir, policy['owner']['manifest_sha256'])
    runtime = ROOT / policy['runtime']
    owner.authenticate(runtime, policy['runtime_manifest_sha256'])
    for key in ('live_audit', 'audit_terminal', 'owner_terminal', 'cleanup'):
        assert policy[key] and sha(ROOT / policy[key]['path']) == policy[key]['sha256']
    terminal = read(ROOT / policy['owner_terminal']['path'])
    assert terminal == read(runtime / 'ROOT-OWNER-TERMINAL.json')
    assert (terminal['session'], terminal['launch']) == (49654, '11e22b')
    assert terminal['terminal'] and terminal['exit'] == 1
    assert terminal['result_sha256'] == sha(runtime / 'RESULT.json')
    live = read(ROOT / policy['live_audit']['path'])
    assert live == read(runtime / 'ROOT-LIVE-RESTORATION.json')
    audit_terminal = read(ROOT / policy['audit_terminal']['path'])
    assert audit_terminal == read(runtime / 'ROOT-LIVE-AUDIT-TERMINAL.json')
    assert audit_terminal['terminal'] and audit_terminal['exit'] == 0
    assert audit_terminal['audit_sha256'] == policy['live_audit']['sha256']
    for key in ('independent_live_restoration_verified', 'application_and_extras_semantically_restored', 'source_and_binary_hashes_restored', 'flags_restored', 'controls_unchanged', 'retained_backup_inventory_verified'):
        assert live[key] is True
    assert live['owner_result_sha256'] == sha(runtime / 'RESULT.json') and not live['native_acceptance']
    assert live['audit_script_sha256'] == sha(ROOT / policy['audit_script'])
    result = read(runtime / 'RESULT.json')
    assert result['success'] is False and result['error'] and result['publication_errors'] == []
    assert read(runtime / 'FAILURE-TRACEBACK.json')['error'] == result['error']
    assert live['backup_removed'] is False
    for name, pin in live['failure_pins'].items(): assert sha(runtime / name) == pin
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert not result['native_fix_acceptance'] and set(result['phase']) == {'original'}
    owner_policy = read(owner_dir / 'POLICY.json')
    assert owner_policy['head'] == policy['head'] and owner_policy['lane_order'] == ['metric', 'phase', 'typedattr'] and owner_policy['diagnostic_lane_order'] == ['sizeforms']
    comparison = load('refresh_pair_comparison', owner_dir / 'comparison.py')
    assessor = load('refresh_pair_assessor', owner_dir / 'assess.py')
    builds = {role:comparison.build_binding(ROOT, owner_dir, runtime, owner_policy, role) for role in ('original', 'candidate')}
    behaviors = {}
    counts = {role:[0,0] for role in builds}
    groups = []
    for role in builds:
        for process, cleanup_name in [('build-PROCESS.json','build-GROUP-CLEANUP.json'),('WAKE-PROCESS.json','wake-GROUP-CLEANUP.json')]:
            directory = runtime / (role + '-build')
            groups.append(read(directory / process)['pgid'])
            assert read(directory / cleanup_name)['owned_group_absent']
        if role == 'original':
            outcomes = read(runtime / 'original-OUTCOMES.json')
            assert outcomes['lanes'] == result['phase'][role] and not outcomes['native_acceptance']
            assert len(outcomes['rows']) == 21 and len(outcomes['endings']) == 3
    for lane in owner_policy['lane_order'] + owner_policy['diagnostic_lane_order']:
        settings = owner_policy['wpt_lanes'][lane]
        checks = load('refresh_lane_checks', ROOT / settings['checks_helper'])
        original = comparison.replay_original(ROOT, owner_dir, runtime, owner_policy, lane, assessor, checks)
        phase = runtime / ('candidate-wpt-' + lane)
        lane_result = read(phase / 'RESULT.json')
        assert lane_result['preservation_verified'] and lane_result['execution_error'] is None
        assert lane_result['success'] is (lane != 'sizeforms')
        expected = comparison.phase_policy(settings, builds, policy['head'])
        assert read(phase / 'ASSESSMENT-POLICY.json') == expected
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        candidate = assessor.assess(events, lane_result['exit'], expected, checks, original=original, run_binding=builds['candidate']['application_metadata'])
        assert candidate == read(phase / 'ASSESSMENT.json') and candidate['complete'] is (lane != 'sizeforms')
        if lane == 'sizeforms':
            assert candidate['rows'] == []
            assert len(candidate['ends']) == 1 and candidate['ends'][0]['status'] == 'CRASH'
        else:
            assert all(row['status'] == 'PASS' for row in candidate['rows'])
        behaviors[lane] = comparison.behavior(original, candidate, assessor.signature)
        assert behaviors[lane] == read(phase / 'BEHAVIOR-COMPARISON.json')
        for role, assessment in [('original', original), ('candidate', candidate)]:
            directory = runtime / (role + '-wpt-' + lane)
            if role == 'original':
                record = (result['phase'][role] if lane in owner_policy['lane_order'] else read(runtime / 'original-OUTCOMES.json')['diagnostics'])[lane]
                for name, key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256'),('BEHAVIOR-COMPARISON.json','behavior_sha256')]:
                    assert sha(directory / name) == record[key]
                assert record['zoom_observation_sha256'] is None
            assert read(directory / 'APPLICATION-METADATA.json') == read(directory / 'APPLICATION-METADATA-POST.json') == builds[role]['application_metadata']
            assert read(directory / 'BINARY-PINS.json') == builds[role]['binaries']
            assert read(directory / 'PRE.json') == read(directory / 'POST.json') == builds[role]['snapshot']
            staged = read(directory / 'STAGED-RESOURCES.json')
            assert all(sha(directory / name) == pin for name,pin in staged.items())
            cleanup = read(directory / 'CLEANUP.json')
            assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
            groups.append(read(directory / 'PROCESS.json')['pgid'])
            counts[role][0] += len(assessment['rows']); counts[role][1] += len(assessment['ends'])
    assert counts == {'original':[25,4], 'candidate':[21,4]}
    assert not (runtime / 'candidate-OUTCOMES.json').exists() and not (runtime / 'DIAGNOSTIC-COMPARISON.json').exists()
    core = {lane:behaviors[lane] for lane in owner_policy['lane_order']}
    assert read(runtime / 'COMPARISON.json') == {'lanes':core,'publication_observation_gate':True,'all24_signatures_equal':False,'native_acceptance':False}
    assert all(value['publication_observation_gate'] for value in core.values())
    assert behaviors['sizeforms']['publication_observation_gate'] is False
    assert outcomes['callbacks_passed'] == 6 and outcomes['callbacks_failed'] == 15
    diagnostic = read(runtime / 'original-DIAGNOSTIC-sizeforms.json')
    assert len(diagnostic['rows']) == 4 and all(row['status'] == 'FAIL' for row in diagnostic['rows'])
    assert len(groups) == len(set(groups)) == 12
    assert set(groups) == set(live['independently_absent_process_groups']) and len(live['independently_absent_process_groups']) == 12
    pre = read(runtime / 'PAIR-PRE.json')
    post, raw = read(runtime / 'POST.json'), read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert pre['controls'] == policy['controls'] and post == live['snapshot']
    assert raw['before'] == policy['raw_before'] and raw['after'] == policy['raw_after']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    roles = read(owner_dir / 'SOURCE-ROLES.json')
    assert len(roles) == 2
    assert restored['sources'] == {name:{'sha256':row['base_sha256'],'identity':pre['sources'][name]['identity']} for name,row in roles.items()}
    cleanup = read(ROOT / policy['cleanup']['path'])
    assert cleanup == read(runtime / 'ROOT-BACKUP-CLEANUP.json')
    historical = read(runtime / 'BACKUP-CLEANUP.json')
    assert historical['removed'] is False and historical['verified_original_restoration'] and historical['retained_after_failure']
    assert cleanup['removed'] and cleanup['inventory_verified_before_removal']
    assert cleanup['independent_restoration_report_sha256'] == policy['live_audit']['sha256']
    assert cleanup['historical_owner_cleanup_sha256'] == sha(runtime / 'BACKUP-CLEANUP.json')
    assert cleanup['backup_inventory_sha256'] == sha(runtime / 'BACKUPS.json') == live['backup_inventory_sha256']
    assert cleanup['cleanup_script_sha256'] == sha(ROOT / policy['cleanup_script'])
    assert cleanup['owned_backup_bytes'] == historical['owned_backup_bytes'] == read(runtime / 'BACKUPS.json')['bytes']
    receipt = read(ROOT / policy['signed_receipt']['path'])
    assert sha(ROOT / policy['signed_receipt']['path']) == policy['signed_receipt']['sha256']
    assert receipt['committed'] and receipt['signature_verified'] and receipt['head'] == policy['head']
    assert receipt['accepted_fix_increment'] == 0
    parent = policy['refresh_parent']
    assert parent and sha(ROOT / parent['directory'] / 'commit.py') == parent['driver_sha256']
    assert sha(ROOT / parent['directory'] / 'BINDINGS.json') == parent['bindings_sha256']
    lineage = load('paired_refresh_parent', ROOT / parent['directory'] / 'commit.py')
    assert lineage.BINDINGS['prior_receipt'] == policy['signed_receipt']['path'] and lineage.BINDINGS['prior_receipt_sha256'] == policy['signed_receipt']['sha256']
    assert lineage.BINDINGS['controls'] == policy['controls']
    assert lineage.validate_refresh(receipt) == pre['snapshot']
    report = {'source_identities':restored['sources'],'restored_application_metadata':live['restored_application_metadata'],'input_hashes':{name:row['sha256'] for name,row in read(runtime / 'FILES.json').items()}}
    return owner, report, pre, post, raw


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check','--run')
    ownership = load('refresh_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    ownership.authenticate(HERE, sys.argv[2])
    policy = read(HERE / 'POLICY.json')
    owner,report,pre,post,raw = saved(policy)
    if sys.argv[1] == '--check':
        print('Authenticated completed restoration; no live state or publication')
        return
    assert policy['execution_enabled'] is True
    assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    state = load('refresh_state', ROOT / 'artifacts/css-registered-number-native-runtime-v1/state.py')
    controls = {n:(CONTROL/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
    assert {n:digest(b) for n,b in controls.items()} == policy['controls']
    epoch = read(CONTROL / 'CURRENT-EPOCH.json')
    assert epoch['semantic_index']['head'] == policy['head']
    updated = derive(epoch, pre['snapshot'], post, raw)
    actual_index = state.h.index_state(ROOT, env)
    updated, expected = admit_current_raw(updated, post, actual_index)
    before = state.a.verify_current(state.h, ROOT, env, updated)
    assert before == expected
    flags = {n:state.h.git(p,env,'ls-files','-v','-z') for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
    owner_policy = read(ROOT / policy['owner']['directory'] / 'POLICY.json')
    baseline = load('refresh_baseline', ROOT / policy['owner']['directory'] / 'baseline.py')
    baseline.metadata_guard(owner_policy)
    for name in owner_policy['preserved_absent_metadata'] + owner_policy['preserved_absent_resources']:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    current = read(ROOT / owner_policy['current_binding']['path'])
    assert {n:digest(b) for n,b in flags.items()} == current['flag_hashes']
    for name,record in report['source_identities'].items(): owner.claim(ROOT,name,record['sha256'],record['identity'])
    bundle = load('refresh_bundle', ROOT / owner_policy['bundle_helper'])
    runtime = ROOT / policy['runtime']
    assert bundle.semantic(bundle.scan(ROOT / owner_policy['bundle_path'])) == bundle.semantic(read(runtime / 'APP-PRE.json'))
    assert bundle.semantic({n:bundle.entry(ROOT/n) for n in owner_policy['extra_backup_paths']}) == bundle.semantic(read(runtime / 'EXTRA-PRE.json'))
    metadata = load('refresh_metadata', ROOT / owner_policy['wpt']['metadata_helper'])
    assert metadata.application_metadata(ROOT / owner_policy['wpt']['application_ini'], owner_policy['restored_application_revision']) == report['restored_application_metadata']
    assert not (runtime/'backups').exists() and not (runtime/'backups').is_symlink()
    for path in report['input_hashes']:
        if path.endswith(('PROCESS.json','WAKE-PROCESS.json')): owner.group_absent(read(runtime/path)['pgid'])
    for role in ('original', 'candidate'):
        for lane in owner_policy['lane_order'] + owner_policy['diagnostic_lane_order']:
            phase = runtime / (role + '-wpt-' + lane)
            cleanup = read(phase / 'CLEANUP.json')
            assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
            temporary = Path(read(phase / 'COMMAND.json')['temporary_root'])
            assert not temporary.exists() and not temporary.is_symlink()
    owner.quiescent(CONTROL)
    state.h.git(ROOT,env,'-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',policy['head'])
    lock = CONTROL / 'SOURCE-TRANSITION.lock'
    assert not lock.exists() and not lock.is_symlink()
    output = ROOT / policy['output']
    assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
    claims = {n:owner.claim(ROOT,str((CONTROL/n).relative_to(ROOT)),digest(b)) for n,b in controls.items()}
    output.mkdir()
    (output/'PRE-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
    state.save(output/'PRE.json',before)
    state.save(output/'ADMISSION-RAW.json', {'canonical_before': raw['before'], 'frozen_pair_after': raw['after'], 'actual_after': actual_index['raw_index'], 'semantic_index_unchanged': True, 'full_frozen_post_equal_except_raw': True})
    with lock.open('x') as stream: stream.write(json.dumps({'pid':os.getpid(),'operation':'computed size paired browser fresh raw observation refresh'})+'\n')
    lock_identity = (lock.stat().st_dev,lock.stat().st_ino)
    def check_controls(body):
        for name,claim in claims.items():
            owner.claim(ROOT,claim['path'],claim['owned_sha256'],claim['identity'])
            assert (CONTROL/name).read_bytes() == (body if name=='CURRENT-EPOCH.json' else controls[name])
    body = (json.dumps(updated,indent=2,sort_keys=True)+'\n').encode()
    release_lock = False
    try:
        saved(policy)
        check_controls(controls['CURRENT-EPOCH.json'])
        assert state.a.verify_current(state.h,ROOT,env,updated) == before
        owner.write_owned(ROOT,claims['CURRENT-EPOCH.json'],body)
        check_controls(body)
        assert state.a.verify_current(state.h,ROOT,env,updated) == before
        assert all(state.h.git(p,env,'ls-files','-v','-z')==flags[n] for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
        state.save(output/'POST.json',before)
        (output/'EPOCH.json').write_bytes(body)
        state.save(output/'RESULT.json',{'updated':True,'updated_only':'raw_index_observation.current','old_epoch_sha256':digest(controls['CURRENT-EPOCH.json']),'epoch_sha256':digest(body),'before':raw['before'],'after':actual_index['raw_index'],'frozen_pair_after':raw['after'],'head':policy['head'],'preservation_verified':True,'restoration_independently_verified':True,'signed_commit_receipt':policy['signed_receipt'],'existing_head_signature_verified':True,'accepted_fix_increment':0,'native_fix_acceptance':False})
        release_lock=True
    except BaseException:
        owner.write_owned(ROOT,claims['CURRENT-EPOCH.json'],controls['CURRENT-EPOCH.json'])
        check_controls(controls['CURRENT-EPOCH.json'])
        assert state.a.verify_current(state.h,ROOT,env,updated)==before
        assert all(state.h.git(p,env,'ls-files','-v','-z')==flags[n] for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
        state.save(output/'ROLLBACK.json',{'canonical_preimage_restored':True,'actual_state_preserved':True})
        release_lock=True
        raise
    finally:
        if release_lock:
            assert (lock.stat().st_dev,lock.stat().st_ino)==lock_identity
            lock.unlink()


if __name__ == '__main__':main()
