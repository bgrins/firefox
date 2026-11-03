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
    assert policy['runtime_output'] == 'artifacts/css-explicit-taint-typed-reparse-candidate-browser-runtime-v1'
    assert policy['execution_enabled'] == policy['candidate_execution_enabled']
    assert policy['authority_kind'] == 'signed-native-publication'
    assert policy['capacity_commit'] == 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
    conditions = read(HERE/'PRECONDITIONS.json')
    for key in ('head','capture_owner','refresh_lineage','main_pair_restoration'):
        assert policy[key] == conditions[key]
    if policy['current_binding'] is None:
        assert not policy['execution_enabled']
        assert policy['controls'] == policy['accepted_current_payloads'] == {}
        assert policy['activation_pending'] == ['fresh_post_pair_capture']
    else:
        assert policy['activation_pending'] == []
        capture = load('admission').validate_current(ROOT, policy, read(HERE/'SOURCE-ROLES.json'))
        assert capture['controls']['CURRENT-EPOCH.json'] == conditions['epoch_sha256']
        assert policy['capture_binding'] and policy['references'][policy['capture_binding']['path']] == policy['capture_binding']['sha256']
        assert sha(ROOT/policy['capture_binding']['path']) == policy['capture_binding']['sha256']
        terminal = read(ROOT/policy['capture_binding']['path'])
        assert terminal['terminal'] is True and terminal['exit'] == 0
        assert terminal['capture'] == policy['current_binding']['path'] and terminal['capture_sha256'] == policy['current_binding']['sha256']
    assert policy['compile_prerequisite'] is policy['native_owner_binding'] is policy['typecheck_binding'] is policy['predecessor_binding'] is None
    assert policy['required_typecheck_inputs'] == {}
    admission = load('admission')
    source = admission.authenticate(ROOT, policy['source_binding'])
    assert source == ROOT / 'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1'
    assert policy['source_binding']['manifest_sha256'] == '21d43edd04e7bf7c58c15c336b7ff8361f80c359f2ae1ae4324ae130cc80a33d'
    assert not policy['control_suite_pending']
    assert policy['suite_bindings']['reparse'] == policy['source_binding']
    assert set(policy['suite_bindings']) == set(policy['wpt_lanes']) == {'reparse','fallback','controls'}
    assert policy['lane_order'] == ['reparse','fallback','controls'] and policy['diagnostic_lane_order'] == []
    roles = read(HERE / 'SOURCE-ROLES.json')
    source_roles = read(source / 'SOURCE.json')['roles']
    expected_roles = {name: {kind + '_capture': row[kind]['path'] for kind in ('base', 'candidate')} | {kind + '_sha256': row[kind]['sha256'] for kind in ('base', 'candidate')} for name, row in source_roles.items()}
    assert roles == expected_roles and set(roles) == {'servo/components/style/custom_properties.rs'}
    assert policy['committed_source_preimages'] == {name: row['base_sha256'] for name, row in roles.items()}
    for row in roles.values():
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
    old = read(ROOT / 'artifacts/css-resumable-font-selection-integrated-pair-v1/POLICY.json')
    for name in ('image_commit','nowrap_commit','language_commit','ownership_commit','ownership_helper','phase_helper','process_helper','state_helper','bundle_helper','bundle_path','extra_backup_paths','rebuilt_binaries','source_context_pins','restored_application_revision','timeout_seconds','metadata_current_pins','preserved_absent_metadata','preserved_absent_resources','capture_source_owner','additional_source_paths'):
        assert policy[name] == old[name], name
    free = read(ROOT/policy['current_binding']['path'])['free_bytes'] if policy['current_binding'] else None
    assert policy['resource_policy'] == dict(old['resource_policy'], captured_free_bytes=free)
    for lane,binding in policy['suite_bindings'].items():
        directory = admission.authenticate(ROOT,binding)
        inputs, roster = read(directory/'INPUTS.json'), read(directory/'ROSTER.json')
        assert inputs['prefs'] == {} and inputs['metadata'] == {}
        expected = copy.deepcopy(old['wpt_lanes']['typedattr'])
        expected.update(resources=inputs['resources'],metadata={'portable':{},'mozilla':{}},expected_subtests=roster,target_subtests=roster,fixture_target_pages=list(roster),candidate_required_pass_pages=list(roster) if lane=='reparse' else [],expected_subtest_count=inputs['callbacks'],expected_target_count=inputs['callbacks'],expected_control_count=0,expected_page_count=inputs['pages'],expected_regression_signature_count=inputs['pages'],harness_revision=policy['head'],phase_revisions={'original':policy['head'],'candidate':policy['head']})
        expected['manifests']['portable'] = inputs['manifest']
        assert policy['wpt_lanes'][lane] == expected
    assert policy['wpt'] == policy['wpt_lanes']['reparse']
    assert policy['wpt_lanes']['reparse']['expected_subtest_count'] == 4
    assert policy['wpt_lanes']['fallback']['expected_subtest_count'] == 28
    assert policy['wpt_lanes']['controls']['expected_page_count'] == 4
    archived = policy['archived_original']
    assert archived['runtime']=='artifacts/css-explicit-attribute-taint-archived-original-runtime-v1'
    assert archived['comparison_performed'] is False and archived['pending'] is False
    assert archived['binding']['directory']==archived['runtime']
    admission.authenticate(ROOT,archived['binding'])
    assert read(ROOT/archived['runtime']/'RESULT.json')['success']
    controls = policy['controls_original']
    assert controls['runtime']=='artifacts/css-explicit-attribute-taint-controls-archived-original-runtime-v1'
    assert controls['comparison_performed'] is False
    if controls['pending']:
        assert controls['binding'] is None and policy['current_binding'] is None and not policy['execution_enabled']
    else:
        assert controls['binding']['directory']==controls['runtime']
        admission.authenticate(ROOT,controls['binding'])
        assert read(ROOT/controls['runtime']/'RESULT.json')['success']
    preservation = policy['preservation_original']
    assert preservation['runtime']=='artifacts/css-attr-fallback-archived-original-runtime-v2'
    admission.authenticate(ROOT,{'directory':preservation['runtime'],'manifest_sha256':preservation['manifest_sha256']})
    assert preservation['expected_pass']==17 and preservation['expected_fail']==11 and preservation['comparison_performed'] is False
    for lane,record,helper in [
        ('reparse',archived,'artifacts/css-explicit-attribute-taint-archived-original-v1/run.py'),
        ('fallback',preservation,'artifacts/css-attr-fallback-archived-validation-v2/run.py'),
        ('controls',controls,'artifacts/css-explicit-attribute-taint-controls-archived-original-v1/run.py'),
    ]:
        if record.get('pending'):
            continue
        assert policy['references'][helper] == sha(ROOT/helper)
        directory = ROOT/record['runtime']
        result = read(directory/'RESULT.json')
        events = [json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines() if line.strip()]
        baseline_assessor = load('baseline_'+lane,ROOT/helper)
        assessment = baseline_assessor.assess(events,policy['wpt_lanes'][lane]['expected_subtests'],result['exit'])
        assert assessment == read(directory/'ASSESSMENT.json') and assessment['complete']
        assert result['source_role']=='archived-original' and result['success'] and result['archive_preserved'] and result['staged_preserved']
        staged = read(directory/'STAGED-RESOURCES.json')
        for url,row in policy['wpt_lanes'][lane]['resources'].items():
            assert staged['tests'+url] == row['sha256']
        if lane=='reparse': assert assessment['counts']=={'PASS':3,'FAIL':1}
        if lane=='fallback': assert assessment['counts']=={'PASS':17,'FAIL':11}
        if lane=='controls': assert assessment['counts']=={'PASS':47}
    for path,pin in policy['references'].items():
        assert sha(ROOT/path) == pin,path
    external = load('closure').external_inputs(ROOT,policy,roles)
    assert external == policy['intermediate_consumed_inputs']
    for path,pin in external.items():
        if path.startswith('artifacts/'):
            assert pin is not None and sha(ROOT/path) == pin,path
    import difflib
    for name,path in read(HERE/'ORIGINS.json').items():
        original = (ROOT/path).read_text()
        actual = (HERE/name).read_text()
        difference = ''.join(difflib.unified_diff(original.splitlines(True), actual.splitlines(True), fromfile=path, tofile=str((HERE/name).relative_to(ROOT))))
        patch = HERE/(name+'.diff')
        assert (patch.read_text() if patch.exists() else '') == difference, name
    parent_driver = (ROOT / read(HERE/'ORIGINS.json')['run.py']).read_text()
    assert (HERE/'run.py').read_text().split('    finally:\n', 1)[1] == parent_driver.split('    finally:\n', 1)[1]
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
    mutations = [('head','0'*40),('current_binding',{}),('execution_enabled',True),('candidate_execution_enabled',True),('activation_pending',[] if policy['current_binding'] is None else ['unexpected']),('committed_source_preimages',{}),('intermediate_consumed_inputs',{}),('source_binding',dict(policy['source_binding'],manifest_sha256='0'*64)),('archived_original',dict(policy['archived_original'],comparison_performed=True)),('controls_original',dict(policy['controls_original'],runtime='unexpected')),('controls_original',None)]
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
    events,code,metadata=synthetic(synthetic_policy,'fallback','FAIL','candidate')
    settings=comparison.phase_policy(synthetic_policy['wpt_lanes']['fallback'],{'candidate':{'application_metadata':metadata}},synthetic_policy['head'])
    failed=assessor.assess(events,code,settings,checks,run_binding=metadata)
    assert failed['complete'] and len(failed['rows'])==28
    crashed=[row for row in events if row.get('action')!='test_status']
    for row in crashed:
        if row.get('action')=='test_end':row.update(status='CRASH',expected='OK')
    failed=assessor.assess(crashed,1,settings,checks,run_binding=metadata)
    assert not failed['complete'] and not failed['rows']
    import subprocess
    identity = subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE/'check_identity.py')], capture_output=True, text=True)
    assert identity.returncode == 0, identity.stderr
    print(identity.stdout)
    print(json.dumps({'consumed_inputs':count,'binding_negatives':len(mutations)+(1 if policy['current_binding'] is None else 0),'active_two_gates_positive':policy['current_binding'] is not None,'streams':streams,'staged_lanes':stages,'candidate_only_FAIL_complete_CRASH_incomplete':True,'current_admission_pending':policy['current_binding'] is None,'native_or_browser_run':False},sort_keys=True))
