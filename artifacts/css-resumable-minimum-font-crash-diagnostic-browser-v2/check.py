import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path=None):
    spec = importlib.util.spec_from_file_location('pair_check_' + name, path or HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-resumable-minimum-font-crash-diagnostic-browser-runtime-2'
    assert policy['execution_enabled'] == policy['candidate_execution_enabled']
    assert policy['authority_kind'] == 'signed-native-publication'
    conditions = read(HERE/'PRECONDITIONS.json')
    for key in ('head','capture_owner','refresh_lineage','main_pair_restoration','source_baseline_binding'):
        assert policy[key] == conditions[key]
    if policy['current_binding'] is None:
        assert not policy['execution_enabled']
        assert policy['controls'] == policy['accepted_current_payloads'] == {}
        assert policy['activation_pending'] == ['fresh_post_v120_restoration_capture']
        assert policy['capture_binding'] is None
    else:
        assert policy['activation_pending'] == []
        capture = load('admission').validate_current(ROOT, policy, read(HERE/'SOURCE-ROLES.json'))
        assert capture['controls']['CURRENT-EPOCH.json'] == conditions['epoch_sha256']
        terminal_binding = policy['capture_binding']
        assert terminal_binding and policy['references'][terminal_binding['path']] == terminal_binding['sha256']
        assert sha(ROOT/terminal_binding['path']) == terminal_binding['sha256']
        terminal = read(ROOT/terminal_binding['path'])
        assert terminal['terminal'] is True and terminal['exit'] == 0
        assert terminal['capture'] == policy['current_binding']['path'] and terminal['capture_sha256'] == policy['current_binding']['sha256']
    restoration = policy['main_pair_restoration']
    failed = read(ROOT/restoration['failed_research_result']['path'])
    terminal = read(ROOT/restoration['terminal']['path'])
    assert failed['committed'] is False and failed['exit'] == 128 and failed['real_index_and_canonical_state_unchanged'] is True
    assert terminal['terminal'] is True and terminal['exit'] == 1
    assert terminal['result_sha256'] == restoration['failed_research_result']['sha256']
    assert terminal['head'] == policy['head']
    assert all(terminal[key] is True for key in ('root_verified_clean_tracked_and_staged','root_verified_epoch_unchanged','root_verified_lock_absent'))
    assert policy['compile_prerequisite'] is policy['native_owner_binding'] is policy['typecheck_binding'] is policy['predecessor_binding'] is None
    assert policy['required_typecheck_inputs'] == {}
    admission = load('admission')
    source = admission.authenticate(ROOT,policy['source_binding'])
    assert source == ROOT/'artifacts/css-resumable-minimum-font-crash-diagnostic-v1'
    assert policy['source_binding']['manifest_sha256'] == '4f773d82b7e768fe5df898cfce4a9d6c172cffd21761812c01d0bf0b68444968'
    source_roles = read(source/'SOURCE-ROLES.json')
    roles = read(HERE/'SOURCE-ROLES.json')
    expected = {name:{kind+'_capture':row[kind]['path'] for kind in ('base','candidate')} | {kind+'_sha256':row[kind]['sha256'] for kind in ('base','candidate')} for name,row in source_roles.items()}
    assert roles == expected and len(roles) == 3
    assert policy['committed_source_preimages'] == {name:row['base_sha256'] for name,row in roles.items()}
    for row in roles.values():
        for kind in ('base','candidate'):
            assert sha(ROOT/row[kind+'_capture']) == row[kind+'_sha256']
    main = read(ROOT/'artifacts/css-resumable-font-selection-integrated-pair-v1/POLICY.json')
    expected_lane = copy.deepcopy(main['wpt_lanes']['minimum_off'])
    expected_lane.update(harness_revision=policy['head'],phase_revisions={'original':policy['head'],'candidate':policy['head']})
    assert policy['wpt'] == policy['wpt_lanes']['minimum_off'] == expected_lane
    assert policy['suite_bindings'] == {'minimum_off':main['suite_bindings']['minimum_off']}
    assert policy['lane_order'] == ['minimum_off'] and policy['diagnostic_lane_order'] == []
    assert policy['archived_original'] is None
    free = read(ROOT/policy['current_binding']['path'])['free_bytes'] if policy['current_binding'] else None
    assert policy['resource_policy'] == dict(main['resource_policy'],captured_free_bytes=free)
    for name in ('image_commit','nowrap_commit','language_commit','ownership_commit','ownership_helper','phase_helper','process_helper','state_helper','bundle_helper','bundle_path','extra_backup_paths','rebuilt_binaries','source_context_pins','restored_application_revision','timeout_seconds','metadata_current_pins','preserved_absent_metadata','preserved_absent_resources','capture_source_owner','additional_source_paths'):
        assert policy[name] == main[name], name
    for path,pin in policy['references'].items():
        assert sha(ROOT/path) == pin,path
    external = load('closure').external_inputs(ROOT,policy,roles)
    assert external == policy['intermediate_consumed_inputs']
    for path,pin in external.items():
        if path.startswith('artifacts/'):
            assert pin is not None and sha(ROOT/path) == pin,path
    import difflib
    for name,path in read(HERE/'ORIGINS.json').items():
        difference = ''.join(difflib.unified_diff((ROOT/path).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile=path,tofile=str((HERE/name).relative_to(ROOT))))
        patch = HERE/(name+'.diff')
        assert (patch.read_text() if patch.exists() else '') == difference,name
    parent = ROOT/'artifacts/css-attr-fallback-candidate-browser-v1'
    assert (HERE/'run.py').read_text().replace('resumable-minimum-font-crash-diagnostic-v2','attr-own-fallback-candidate-v1') == (parent/'run.py').read_text()
    assert (HERE/'phases.py').read_text().replace('==7','==24') == (parent/'phases.py').read_text()
    return len(external)


def rejected(action):
    try: action()
    except (AssertionError,KeyError,TypeError,ValueError): return
    raise AssertionError('negative control unexpectedly admitted')


def synthetic(policy, lane, status, role):
    metadata = {'browser_build_id': 'synthetic-' + role, 'revision': policy['head'], 'build_revision': policy['head'], 'harness_revision': policy['head'], 'source_role': role, 'sha256': ('a' if role == 'original' else 'b') * 64, 'path': 'synthetic/application.ini', 'resolved': 'synthetic/application.ini'}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': metadata['browser_build_id'], 'revision': policy['head']}}]
    for page, names in policy['wpt_lanes'][lane]['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': page})
        for name in names:
            row = {'action': 'test_status', 'test': page, 'subtest': name, 'status': status}
            if status == 'FAIL':
                row.update(expected='PASS', message='ordinary assertion failure')
            events.append(row)
        events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, int(status == 'FAIL'), metadata


def stream_checks(policy):
    assessor, comparison = load('assess'), load('comparison')
    checks = load('stream_helpers', ROOT / policy['wpt']['checks_helper'])
    cases = []
    for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
        original_events, code, original_metadata = synthetic(policy, lane, 'FAIL', 'original')
        candidate_events, _, candidate_metadata = synthetic(policy, lane, 'PASS', 'candidate')
        builds = {role: {'application_metadata': meta} for role, meta in [('original', original_metadata), ('candidate', candidate_metadata)]}
        settings = comparison.phase_policy(policy['wpt_lanes'][lane], builds, policy['head'])
        original = assessor.assess(original_events, code, settings, checks, run_binding=original_metadata)
        assert original['complete'] and all(row['status'] == 'FAIL' for row in original['rows'])
        candidate = assessor.assess(candidate_events, 0, settings, checks, original=original, run_binding=candidate_metadata)
        behavior = comparison.behavior(original, candidate, assessor.signature)
        assert candidate['complete'] and behavior['publication_observation_gate'] and behavior['differences']
        assert json.loads(json.dumps(behavior)) == behavior
        failed_events, failed_code, _ = synthetic(policy, lane, 'FAIL', 'candidate')
        failed = assessor.assess(failed_events, failed_code, settings, checks, original=original, run_binding=candidate_metadata)
        assert failed['complete'] and not comparison.behavior(original, failed, assessor.signature)['publication_observation_gate']
        for mutation in ('metadata', 'role', 'revision', 'platform', 'setup', 'missing-ending'):
            events, binding = copy.deepcopy(candidate_events), copy.deepcopy(candidate_metadata)
            if mutation == 'metadata': binding['sha256'] = 'c' * 64
            elif mutation == 'role': binding['source_role'] = 'original'
            elif mutation == 'revision': events[0]['run_info']['revision'] = '0' * 40
            elif mutation == 'platform': events[0]['run_info']['debug'] = True
            elif mutation == 'setup': events[2].update(status='FAIL', expected='PASS', message='ReferenceError: setup')
            else: events = [row for row in events if not (row.get('action') == 'test_end' and row['test'] == next(iter(settings['expected_subtests'])))]
            actual = assessor.assess(events, int(mutation == 'setup'), settings, checks, original=original, run_binding=binding)
            assert not comparison.behavior(original, actual, assessor.signature)['publication_observation_gate'], mutation
        passing_events, _, _ = synthetic(policy, lane, 'PASS', 'original')
        passing = assessor.assess(passing_events, 0, settings, checks, run_binding=original_metadata)
        changed = copy.deepcopy(candidate_events); changed[2]['message'] = 'changed full signature'
        actual = assessor.assess(changed, 0, settings, checks, original=passing, run_binding=candidate_metadata)
        assert actual['complete'] and not comparison.behavior(passing, actual, assessor.signature)['publication_observation_gate']
        cases.append({'lane': lane, 'ordinary_FAIL_retained': len(original['rows']), 'candidate_PASS': len(candidate['rows']), 'endings': len(candidate['ends']), 'negative_cases': 7})
    return cases


def stage_checks(policy):
    wpt = load('wpt')
    directory = Path(tempfile.mkdtemp(prefix='css-publication-pair-saved-', dir=ROOT / 'artifacts'))
    try:
        for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
            output = directory / lane; output.mkdir()
            settings = policy['wpt_lanes'][lane]
            config, capture = wpt.prepare_inputs(ROOT, output, settings, 'original')
            assert capture is None and config.is_file()
            for kind, folder in [('portable', 'metadata'), ('mozilla', 'mozilla-metadata')]:
                for relative, row in settings['metadata'][kind].items():
                    target = output / folder / relative
                    assert (not target.exists()) if row['sha256'] is None else sha(target) == row['sha256']
    finally:
        shutil.rmtree(directory)
    assert not directory.exists()
    return len(policy['lane_order'] + policy['diagnostic_lane_order'])


if __name__ == '__main__':
    policy = read(HERE/'POLICY.json')
    count = validate_policy(policy)
    mutations = [('head','0'*40),('current_binding',{}),('execution_enabled',True),('candidate_execution_enabled',True),('activation_pending',[] if policy['current_binding'] is None else ['unexpected']),('committed_source_preimages',{}),('intermediate_consumed_inputs',{}),('source_binding',dict(policy['source_binding'],manifest_sha256='0'*64)),('source_baseline_binding',{})]
    for key,value in mutations:
        bad=copy.deepcopy(policy);bad[key]=value;rejected(lambda:validate_policy(bad))
    both = copy.deepcopy(policy); both['execution_enabled'] = both['candidate_execution_enabled'] = True
    if policy['current_binding'] is None:
        rejected(lambda:validate_policy(both))
    else:
        validate_policy(both)
    synthetic_policy=copy.deepcopy(policy);synthetic_policy['head']='1'*40
    for settings in list(synthetic_policy['wpt_lanes'].values())+[synthetic_policy['wpt']]:
        settings['harness_revision']='1'*40;settings['phase_revisions']={'original':'1'*40,'candidate':'1'*40}
    streams=stream_checks(synthetic_policy)
    stages=stage_checks(policy)
    comparison,assessor=load('comparison'),load('assess')
    checks=load('stream_helpers',ROOT/policy['wpt']['checks_helper'])
    events,code,metadata=synthetic(synthetic_policy,'minimum_off','FAIL','candidate')
    settings=comparison.phase_policy(synthetic_policy['wpt_lanes']['minimum_off'],{'candidate':{'application_metadata':metadata}},synthetic_policy['head'])
    failed=assessor.assess(events,code,settings,checks,run_binding=metadata)
    assert failed['complete'] and len(failed['rows'])==7
    crashed=[row for row in events if row.get('action')!='test_status']
    for row in crashed:
        if row.get('action')=='test_end':row.update(status='CRASH',expected='OK')
    failed=assessor.assess(crashed,1,settings,checks,run_binding=metadata)
    assert not failed['complete'] and not failed['rows']
    import subprocess
    identity = subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE/'check_identity.py')], capture_output=True, text=True)
    assert identity.returncode == 0, identity.stderr
    print(identity.stdout)
    print(json.dumps({'consumed_inputs':count,'binding_negatives':len(mutations)+(policy['current_binding'] is None),'both_gate_activation_positive':policy['current_binding'] is not None,'streams':streams,'staged_lanes':stages,'candidate_only_FAIL_complete_CRASH_incomplete':True,'current_admission_pending':policy['current_binding'] is None,'native_or_browser_run':False},sort_keys=True))
