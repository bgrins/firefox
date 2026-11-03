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
    for key in ('live_audit', 'audit_terminal', 'owner_terminal'):
        assert policy[key] and sha(ROOT / policy[key]['path']) == policy[key]['sha256']
    terminal = read(ROOT / policy['owner_terminal']['path'])
    assert terminal == read(runtime / 'ROOT-OWNER-TERMINAL.json')
    assert (terminal['session'], terminal['launch']) == (68207, 'b1490c')
    assert terminal['terminal'] and terminal['result_sha256'] == sha(runtime / 'RESULT.json')
    result = read(runtime / 'RESULT.json')
    assert type(result['success']) is bool and terminal['exit'] == (0 if result['success'] else 1)
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert not result['native_fix_acceptance']
    if result['success']:
        assert result['error'] is None and result['publication_errors'] == []
        assert set(result['phase']) == {'original','candidate'}
    else:
        assert result['error'] or result['publication_errors']
        if result['error']:
            assert read(runtime / 'FAILURE-TRACEBACK.json')['error'] == result['error']
    live = read(ROOT / policy['live_audit']['path'])
    assert live == read(runtime / 'ROOT-LIVE-RESTORATION.json')
    audit_terminal = read(ROOT / policy['audit_terminal']['path'])
    assert audit_terminal == read(runtime / 'ROOT-LIVE-AUDIT-TERMINAL.json')
    assert audit_terminal['terminal'] and audit_terminal['exit'] == 0
    assert audit_terminal['audit_sha256'] == policy['live_audit']['sha256']
    for key in ('independent_live_restoration_verified','application_and_extras_semantically_restored','source_and_binary_hashes_restored','flags_restored','controls_unchanged'):
        assert live[key] is True
    assert live['owner_terminal'] == terminal
    assert live['owner_result_sha256'] == sha(runtime / 'RESULT.json') and not live['native_acceptance']
    assert live['audit_script_sha256'] == sha(ROOT / policy['audit_script'])
    for name, pin in live['outcome_pins'].items(): assert sha(runtime / name) == pin
    owner_policy = read(owner_dir / 'POLICY.json')
    assert owner_policy['head'] == policy['head'] and owner_policy['lane_order'] == ['capacity'] and owner_policy['diagnostic_lane_order'] == []
    roles = read(owner_dir / 'SOURCE-ROLES.json')
    assert set(roles) == {'servo/components/style/properties/cascade.rs'}
    comparison = load('refresh_pair_comparison', owner_dir / 'comparison.py')
    assessor = load('refresh_pair_assessor', owner_dir / 'assess.py')
    settings = owner_policy['wpt_lanes']['capacity']
    checks = load('refresh_lane_checks', ROOT / settings['checks_helper'])
    builds, assessments = {}, {}
    for role in ('original','candidate'):
        build_result = runtime / (role + '-build/RESULT.json')
        if build_result.exists() and read(build_result)['command_success']:
            builds[role] = comparison.build_binding(ROOT,owner_dir,runtime,owner_policy,role)
        phase = runtime / (role + '-wpt-capacity')
        if not phase.exists():
            continue
        assert role in builds
        lane_result = read(phase / 'RESULT.json')
        assert lane_result['preservation_verified']
        expected = comparison.phase_policy(settings, builds, policy['head'])
        assert read(phase / 'ASSESSMENT-POLICY.json') == expected
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        original = assessments.get('original') if role == 'candidate' else None
        if role == 'candidate': assert original and original['complete']
        assessment = assessor.assess(events,lane_result['exit'],expected,checks,original=original,run_binding=builds[role]['application_metadata'])
        assert assessment == read(phase / 'ASSESSMENT.json')
        if lane_result['success']: assert assessment['complete']
        if assessment['complete']:
            assert len(assessment['rows']) == len(assessment['ends']) == 1
            assert assessment['rows'][0]['status'] in ('PASS','FAIL')
        if role == 'candidate':
            behavior = comparison.behavior(original,assessment,assessor.signature)
            assert behavior == read(phase / 'BEHAVIOR-COMPARISON.json')
        assessments[role] = assessment
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == builds[role]['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == builds[role]['binaries']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json') == builds[role]['snapshot']
        assert all(sha(phase / name) == pin for name,pin in read(phase / 'STAGED-RESOURCES.json').items())
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        if role in (result['phase'] or {}):
            record = result['phase'][role]['capacity']
            for name,key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256')]:
                assert sha(phase / name) == record[key]
    if result['success']:
        assert set(builds) == set(assessments) == {'original','candidate'}
        assert all(row['complete'] for row in assessments.values())
    process_paths = [path for path in read(runtime/'FILES.json') if path.endswith(('PROCESS.json','WAKE-PROCESS.json'))]
    groups = [read(runtime/path)['pgid'] for path in process_paths]
    assert len(groups) == len(set(groups))
    assert set(groups) == set(live['independently_absent_process_groups'])
    assert all(path in live['outcome_pins'] for path in process_paths)
    pre = read(runtime / 'PAIR-PRE.json')
    post, raw = read(runtime / 'POST.json'), read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert pre['controls'] == policy['controls'] and post == live['snapshot']
    assert raw['before'] == policy['raw_before'] and raw['after'] == policy['raw_after']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    assert restored['sources'] == {name:{'sha256':row['base_sha256'],'identity':pre['sources'][name]['identity']} for name,row in roles.items()}
    historical = read(runtime / 'BACKUP-CLEANUP.json')
    assert historical['verified_original_restoration']
    assert historical['removed'] is result['success'] and historical['retained_after_failure'] is (not result['success'])
    assert live['backup_removed'] is historical['removed']
    assert live['backup_inventory_sha256'] == sha(runtime/'BACKUPS.json')
    if historical['removed']:
        assert policy['cleanup'] is None and not live['retained_backup_inventory_verified']
    else:
        assert live['retained_backup_inventory_verified'] and policy['cleanup']
        assert sha(ROOT/policy['cleanup']['path']) == policy['cleanup']['sha256']
        cleanup = read(ROOT/policy['cleanup']['path'])
        assert cleanup == read(runtime/'ROOT-BACKUP-CLEANUP.json')
        assert cleanup['removed'] and cleanup['inventory_verified_before_removal']
        assert cleanup['independent_restoration_report_sha256'] == policy['live_audit']['sha256']
        assert cleanup['historical_owner_cleanup_sha256'] == sha(runtime/'BACKUP-CLEANUP.json')
        assert cleanup['backup_inventory_sha256'] == sha(runtime/'BACKUPS.json')
        assert cleanup['cleanup_script_sha256'] == sha(ROOT/policy['cleanup_script'])
        assert cleanup['owned_backup_bytes'] == historical['owned_backup_bytes']
    assert historical['owned_backup_bytes'] == read(runtime/'BACKUPS.json')['bytes']
    receipt = read(ROOT/policy['signed_receipt']['path'])
    assert sha(ROOT/policy['signed_receipt']['path']) == policy['signed_receipt']['sha256']
    assert receipt['committed'] and receipt['signature_verified'] and receipt['head'] == policy['head']
    assert receipt['accepted_fix_increment'] == 0 and receipt['epoch_sha256'] == policy['controls']['CURRENT-EPOCH.json']
    assert policy['refresh_parent'] is None
    admission = load('capacity_saved_admission',owner_dir/'admission.py')
    capture = admission.validate_current(ROOT,owner_policy,roles)
    assert capture['checkpoint'] == receipt and capture['checkpoint_receipt'] == policy['signed_receipt']
    assert capture['snapshot'] == pre['snapshot'] and capture['controls'] == policy['controls']
    report = {'source_identities':restored['sources'],'restored_application_metadata':live['restored_application_metadata'],'input_hashes':{name:row['sha256'] for name,row in read(runtime/'FILES.json').items()}}
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
            if not phase.exists():
                continue
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
    with lock.open('x') as stream: stream.write(json.dumps({'pid':os.getpid(),'operation':'capacity browser restored raw observation refresh'})+'\n')
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
