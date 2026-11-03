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
    assert terminal == read(runtime / 'ROOT-OWNER-TERMINAL.json') == policy['actual_owner_terminal']
    assert terminal['terminal'] and terminal['result_sha256'] == sha(runtime / 'RESULT.json')
    result = read(runtime / 'RESULT.json')
    assert result['success'] is True and terminal['exit'] == 0
    assert set(result['phase']) == {'candidate'} and set(result['phase']['candidate']) == {'cancellation'}
    assert result['publication_errors'] == []
    assert result['error'] is None and result['restoration_verified']
    assert result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert not result['native_fix_acceptance']
    live = read(ROOT / policy['live_audit']['path'])
    assert live == read(runtime / 'ROOT-LIVE-RESTORATION.json')
    audit_terminal = read(ROOT / policy['audit_terminal']['path'])
    assert audit_terminal == policy['actual_audit_terminal']
    assert type(audit_terminal['terminal_chunk']) is str and audit_terminal['terminal_chunk'] and audit_terminal['exit'] == 0
    assert audit_terminal['active_audit_manifest'] == sha((ROOT / policy['audit_script']).parent / 'FILES.json')
    assert audit_terminal['report_sha256'] == policy['live_audit']['sha256']
    for key in ('independent_live_restoration_verified','application_and_extras_semantically_restored','source_and_binary_hashes_restored','flags_restored','controls_unchanged'):
        assert live[key] is True
    assert live['owner_terminal'] == terminal
    assert live['owner_result_sha256'] == sha(runtime / 'RESULT.json') and not live['native_acceptance']
    assert live['audit_script_sha256'] == sha(ROOT / policy['audit_script'])
    assert live['native_authority_freshly_verified'] is True
    owner_policy = read(owner_dir / 'POLICY.json')
    assert owner_policy['head'] == policy['head']
    assert owner_policy['direct_equivalence'] == policy['direct_equivalence'] == {'directory': 'artifacts/css-native-epoch-direct-equivalence-v1', 'manifest_sha256': '0c42724061acefb0f49b654d8a22f8aff2507f6138b72109e1906c4e7e49c488'}
    assert owner_policy['lane_order'] == ['cancellation'] and owner_policy['diagnostic_lane_order'] == []
    roles = read(owner_dir / 'SOURCE-ROLES.json')
    assert set(roles) == {'dom/animation/KeyframeEffect.cpp', 'layout/style/GeckoBindings.cpp', 'servo/components/style/data.rs', 'servo/components/style/gecko/traversal.rs', 'servo/components/style/matching.rs', 'servo/components/style/traversal.rs', 'servo/components/style/values/specified/length.rs', 'servo/ports/geckolib/glue.rs'}
    comparison = load('refresh_pair_comparison', owner_dir / 'comparison.py')
    assessor = load('refresh_pair_assessor', owner_dir / 'assess.py')
    build = comparison.build_binding(ROOT, owner_dir, runtime, owner_policy, 'candidate')
    archive = live['archive_observation']
    assert archive['status'] == 'verified-retained-candidate' and archive['archive_retained_verified'] is True
    assert archive['owner_terminal_and_restoration_verified'] is True
    assert archive['browser_execution_authorized'] is False and archive['native_acceptance'] is False
    assert archive['native_sources'] == {name: row['candidate_sha256'] for name, row in roles.items()}
    assert archive['build_receipt_sha256'] == sha(runtime / 'candidate-build/RESULT.json')
    assert archive['receipt_hashes'] == policy['archive_receipts']
    assert set(archive['receipt_hashes']) == {'ARCHIVE-OWNERSHIP.json', 'ARCHIVE-SNAPSHOT.json', 'ARCHIVE-VALIDATION.json', 'ARCHIVE-HANDOFF.json'}
    assert all(sha(runtime / name) == pin for name, pin in archive['receipt_hashes'].items())
    handoff = read(runtime / 'ARCHIVE-HANDOFF.json')
    assert handoff['snapshot_sha256'] == archive['receipt_hashes']['ARCHIVE-SNAPSHOT.json']
    assert read(runtime / 'ARCHIVE-SNAPSHOT.json')['unchanged_source_preimages'] == {name: pin for name, pin in owner_policy['source_context_pins'].items() if name not in roles}
    assert handoff['restoration_sha256'] == sha(runtime / 'RESTORATION.json')
    assert handoff['post_sha256'] == sha(runtime / 'POST.json')
    assert handoff['application'] == archive['application'] == read(runtime / 'ARCHIVE-SNAPSHOT.json')['application']
    assert handoff['browser_execution_authorized'] is False and handoff['owner_terminal_and_independent_audit_required'] is True
    assert sum(owner_policy['wpt_lanes'][lane]['expected_subtest_count'] for lane in owner_policy['lane_order']) == 8
    assert sum(owner_policy['wpt_lanes'][lane]['expected_page_count'] for lane in owner_policy['lane_order']) == 1
    for lane in owner_policy['lane_order']:
        settings = owner_policy['wpt_lanes'][lane]
        checks = load('refresh_lane_checks', ROOT / settings['checks_helper'])
        phase = runtime / ('candidate-wpt-' + lane)
        lane_result = read(phase / 'RESULT.json')
        assert lane_result['preservation_verified'] and lane_result['execution_error'] is None
        expected = comparison.phase_policy(settings, {'candidate': build}, policy['head'])
        assert read(phase / 'ASSESSMENT-POLICY.json') == expected
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        assessment = assessor.assess(events, lane_result['exit'], expected, checks, run_binding=build['application_metadata'])
        assert assessment == read(phase / 'ASSESSMENT.json')
        assert read(phase / 'BEHAVIOR-COMPARISON.json') is None
        assert lane_result['success'] and lane_result['exit'] in (0, 1)
        assert assessment['complete'] and len(assessment['rows']) == settings['expected_subtest_count']
        assert len(assessment['ends']) == settings['expected_page_count']
        assert all(row['status'] == 'OK' for row in assessment['ends'])
        assert all(row['status'] in ('PASS', 'FAIL') for row in assessment['rows'])
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == build['binaries']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json') == build['snapshot']
        assert all(sha(phase / name) == pin for name, pin in read(phase / 'STAGED-RESOURCES.json').items())
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    runtime_manifest = read(runtime/'FILES.json')
    assert runtime_manifest and all(type(row) is dict and set(row) == {'sha256', 'bytes'} for row in runtime_manifest.values())
    runtime_files = runtime_manifest
    links = sorted(str(path.relative_to(runtime)) for path in runtime.rglob('*') if path.is_symlink())
    assert links == ['candidate-wpt-cancellation/tests/tools']
    assert (runtime/links[0]).readlink() == ROOT/'testing/web-platform/tests/tools'
    process_paths = [path for path in runtime_files if path.endswith(('PROCESS.json','WAKE-PROCESS.json'))]
    groups = [read(runtime/path)['pgid'] for path in process_paths]
    assert len(groups) == len(set(groups))
    assert set(groups) | {terminal['outer_group']} == set(live['independently_absent_process_groups'])
    assert {row['path']: row['pgid'] for row in live['process_records']} == {path: read(runtime/path)['pgid'] for path in process_paths}
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
        assert cleanup['removed'] and cleanup['inventory_verified_before_removal']
        assert cleanup['independent_restoration_verified'] and cleanup['historical_runtime_records_unchanged']
        assert cleanup['restoration_sha256'] == policy['live_audit']['sha256']
        assert cleanup['owner_result_sha256'] == sha(runtime / 'RESULT.json')
        assert cleanup['terminal_runtime_manifest_sha256'] == policy['runtime_manifest_sha256']
        assert cleanup['backup_inventory_sha256'] == sha(runtime/'BACKUPS.json')
        assert cleanup['removed_path'] == policy['runtime'] + '/backups'
        assert not cleanup['native_fix_acceptance']
        assert cleanup['owned_backup_bytes'] == historical['owned_backup_bytes']
    assert historical['owned_backup_bytes'] == read(runtime/'BACKUPS.json')['bytes']
    receipt = read(ROOT/policy['signed_receipt']['path'])
    assert sha(ROOT/policy['signed_receipt']['path']) == policy['signed_receipt']['sha256']
    assert receipt['signature_verified'] and receipt['commit'] == policy['head']
    assert receipt['stage'] == 'capacity' and receipt['app_rebuilt'] is False
    assert policy['authority_kind'] == 'signed-native-publication'
    assert receipt['accepted_fix_increment'] == 0
    admission = load('diagnostic_saved_native_admission',owner_dir/'admission.py')
    capture = admission.validate_current(ROOT,owner_policy,roles)
    assert capture['checkpoint'] == receipt and capture['checkpoint_receipt'] == policy['signed_receipt']
    assert capture['snapshot'] == pre['snapshot'] and capture['controls'] == policy['controls']
    assert capture['refresh_binding'] == policy['refresh_parent']
    assert capture['refresh_lineage_verified'] and capture['additional_sources_match_head']
    assert set(capture['additional_sources']) == {'servo/components/style/data.rs', 'servo/components/style/gecko/traversal.rs', 'servo/components/style/traversal.rs'}
    source_claims = capture['payload_claims'] | capture['additional_sources']
    assert live['restored_source_claims'] == {name: source_claims[name] for name in roles}
    assert all(restored['sources'][name]['identity'] == source_claims[name]['identity'] for name in roles)
    report = {'source_identities':restored['sources'],'restored_application_metadata':live['restored_application_metadata'],'input_hashes':runtime_files}
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
    if actual_index['raw_index'] == epoch['raw_index_observation']['current']:
        print(json.dumps({'updated': False, 'reason': 'raw observation already current', 'head': policy['head'], 'epoch_sha256': digest(controls['CURRENT-EPOCH.json']), 'raw_index': actual_index['raw_index'], 'preservation_verified': True}))
        return
    output = ROOT / policy['output']
    assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
    claims = {n:owner.claim(ROOT,str((CONTROL/n).relative_to(ROOT)),digest(b)) for n,b in controls.items()}
    output.mkdir()
    (output/'PRE-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
    state.save(output/'PRE.json',before)
    state.save(output/'ADMISSION-RAW.json', {'canonical_before': raw['before'], 'frozen_pair_after': raw['after'], 'actual_after': actual_index['raw_index'], 'semantic_index_unchanged': True, 'full_frozen_post_equal_except_raw': True})
    with lock.open('x') as stream: stream.write(json.dumps({'pid':os.getpid(),'operation':'native-authority eight-source startup trace restored raw observation refresh'})+'\n')
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
