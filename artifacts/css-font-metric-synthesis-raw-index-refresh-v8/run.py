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
    assert terminal == read(runtime / 'ROOT-TERMINAL.json')
    assert terminal == policy['actual_owner_terminal']
    assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(runtime / 'RESULT.json')
    live = read(ROOT / policy['live_audit']['path'])
    assert live == read(runtime / 'ROOT-LIVE-RESTORATION.json')
    audit_terminal = read(ROOT / policy['audit_terminal']['path'])
    assert audit_terminal == policy['actual_audit_terminal'] and audit_terminal['exit'] == 0
    assert audit_terminal['audit_sha256'] == policy['live_audit']['sha256']
    for key in ('independent_live_restoration_verified', 'application_and_extras_semantically_restored', 'source_and_binary_hashes_restored', 'flags_restored', 'controls_unchanged', 'backup_removed'):
        assert live[key] is True
    assert live['owner_result_sha256'] == sha(runtime / 'RESULT.json') and not live['native_acceptance']
    assert live['audit_script_sha256'] == sha(ROOT / policy['audit_script'])
    result = read(runtime / 'RESULT.json')
    assert result['success'] is True and result['error'] is None
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['publication_errors'] == [] and not result['native_fix_acceptance']
    typecheck = read(owner_dir / 'TYPECHECK.json')
    command = read(runtime / 'candidate-check/COMMAND.json')
    assert command['owner_manifest'] == policy['owner']['manifest_sha256'] and command['source_role'] == 'candidate'
    assert command['command'] == typecheck['command'] and command['required_input_hashes'] == typecheck['required_input_hashes']
    assert read(runtime / 'candidate-check/INPUTS-AFTER.json') == typecheck['required_input_hashes']
    inner = read(runtime / 'candidate-check/build-RESULT.json')
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
    assessor = load('refresh_cargo_assessor', owner_dir / 'assess.py')
    assessment = assessor.assess((runtime / 'candidate-check/build.log').read_bytes(), inner['exit'], ROOT, ROOT / 'objdir-full.noindex')
    assert assessment == read(runtime / 'candidate-check/ASSESSMENT.json') == result['phase']['cargo']
    assert assessment['success'] is True and assessment['build_finished'] == [{'reason':'build-finished','success':True}]
    assert assessment['errors'] == [] and set(assessment['requested_library_artifacts']) == {'style','geckoservo'}
    warning_codes = [row['message']['code']['code'] for row in assessment['warnings']]
    assert sorted(warning_codes) == policy['actual_warning_codes']
    pre = read(runtime / 'PAIR-PRE.json')
    post, raw = read(runtime / 'POST.json'), read(runtime / 'RAW-INDEX-OBSERVATION.json')
    assert pre['controls'] == policy['controls'] and post == live['snapshot']
    assert raw['before'] == policy['raw_before'] and raw['after'] == policy['raw_after']
    restored = read(runtime / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    roles = read(owner_dir / 'SOURCE-ROLES.json')
    assert len(roles) == 2 and command['source_sha256'] == {name:row['candidate_sha256'] for name,row in roles.items()}
    assert restored['sources'] == {name:{'sha256':row['base_sha256'],'identity':pre['sources'][name]['identity']} for name,row in roles.items()}
    groups = [read(runtime / name)['pgid'] for name in ('candidate-check/build-PROCESS.json','candidate-check/WAKE-PROCESS.json')]
    assert len(set(groups)) == 2 and live['independently_absent_process_groups'] == groups
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert sha(ROOT / policy['cleanup']['path']) == policy['cleanup']['sha256']
    assert cleanup == read(ROOT / policy['cleanup']['path'])
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert cleanup['owned_backup_bytes'] == read(runtime / 'BACKUPS.json')['bytes'] == pre['owned_backup_bytes']
    owner_policy = read(owner_dir / 'POLICY.json')
    capture = read(ROOT / owner_policy['current_binding']['path'])
    assert sha(ROOT / owner_policy['current_binding']['path']) == owner_policy['current_binding']['sha256']
    receipt = read(ROOT / policy['signed_receipt']['path'])
    assert sha(ROOT / policy['signed_receipt']['path']) == policy['signed_receipt']['sha256']
    assert receipt['committed'] and receipt['signature_verified'] and receipt['head'] == policy['head']
    assert receipt['accepted_fix_increment'] == 0
    parent = policy['refresh_parent']
    assert parent and sha(ROOT / parent['directory'] / 'commit.py') == parent['driver_sha256']
    assert sha(ROOT / parent['directory'] / 'BINDINGS.json') == parent['bindings_sha256']
    lineage = load('diagnostic_refresh_parent', ROOT / parent['directory'] / 'commit.py')
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
    for role in ('candidate',):
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
    with lock.open('x') as stream: stream.write(json.dumps({'pid':os.getpid(),'operation':'computed size Cargo check fresh raw observation refresh'})+'\n')
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
