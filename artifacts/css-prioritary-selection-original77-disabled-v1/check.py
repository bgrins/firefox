import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def validate_policy(policy):
    ownership = load('preservation_ownership', ROOT / policy['ownership_helper'])
    predecessor = read(HERE / 'PREDECESSOR.json')
    assert policy['predecessor'] == predecessor
    previous = ROOT / predecessor['directory']
    ownership.authenticate(previous, predecessor['manifest_sha256'])
    old = read(previous / 'POLICY.json')
    mutable = {'owner_directory', 'runtime_output', 'predecessor', 'references', 'execution_enabled',
               'candidate_execution_enabled', 'activation_pending', 'head', 'controls',
               'prepared_application_metadata', 'prepared_flag_hashes', 'prepared_flag_capture',
               'execution_handoff', 'restoration_binding', 'suite_binding', 'source_roster', 'wpt',
               'wpt_lanes', 'lane_order', 'capture_binding', 'metadata_current_pins', 'preserved_absent_resources', 'intermediate_guard_binding', 'intermediate_consumed_inputs'}
    assert {k:v for k,v in policy.items() if k not in mutable} == {k:v for k,v in old.items() if k not in mutable}
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-prioritary-selection-original-runtime-2'
    load('restored_original74_admission', HERE / 'admission.py').validate(ROOT, policy)
    suite = ROOT / policy['suite_binding']['directory']
    assert policy['suite_binding']['directory'] == 'artifacts/css-prioritary-selection-suite-v3'
    assert policy['suite_binding']['manifest_sha256'] == '512390cecca0942d0bbe7cb3f21ee4f5878b27ae9350828be3c31f2c771a42f0'
    ownership.authenticate(suite, policy['suite_binding']['manifest_sha256'])
    capture = ROOT / policy['capture_binding']['directory']
    assert policy['capture_binding']['directory'] == 'artifacts/css-prioritary-zoom-capture-v1'
    assert policy['capture_binding']['manifest_sha256'] == 'ed0ed2222d90e2e04437dc033bbcd4a62f6264f89a1135b82a10051e99da0de2'
    ownership.authenticate(capture, policy['capture_binding']['manifest_sha256'])
    union, lanes, roster = read(suite / 'INPUTS.json'), read(suite / 'LANES.json'), read(suite / 'ROSTER.json')
    shared = {k:v for k,v in old['wpt'].items() if k not in ['resources','metadata','manifest','expected_subtests','expected_subtest_count','expected_control_count','expected_page_count','expected_regression_signature_count','fixture_target_pages']}
    shared.update(phase_revisions={'original':policy['head'],'candidate':policy['head']},harness_revision=policy['head'])
    assert policy['wpt'] == dict(shared,expected_subtests=roster,expected_subtest_count=77,expected_control_count=77,expected_page_count=12,expected_regression_signature_count=89,fixture_target_pages=list(roster))
    assert policy['lane_order'] == ['ordinary','forced_colors','mozilla_appearance']
    assert set(policy['wpt_lanes']) == set(lanes)
    def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
    for lane, entry in lanes.items():
        settings = dict(shared,expected_subtests=entry['roster'],expected_subtest_count=entry['callbacks'],expected_control_count=entry['callbacks'],expected_page_count=entry['pages'],expected_regression_signature_count=entry['callbacks']+entry['pages'],fixture_target_pages=list(entry['roster']))
        settings.update(resources=union['copy_resources'],metadata=union['metadata'],manifests={'portable':pin(suite/'MANIFEST.json'),'mozilla':pin(suite/'MOZILLA-MANIFEST.json')},capture=pin(capture/'capture.py') if lane=='ordinary' else None,install_managed_resources=union['install_managed_resource_pins'] if lane=='ordinary' else {})
        assert policy['wpt_lanes'][lane] == settings
    assert policy['metadata_current_pins'] == {name:row['sha256'] for name,row in union['metadata_admission'].items() if row['sha256'] is not None}
    assert policy['preserved_absent_resources'] == sorted(set(old['preserved_absent_resources']) | {name for name,row in union['metadata_admission'].items() if row['sha256'] is None})
    assert policy['source_roster'] == str((suite/'ROSTER.json').relative_to(ROOT))
    assert len(policy['accepted_current_payloads']) == 29
    assert (HERE/'SOURCE-ROLES.json').read_bytes() == (previous/'SOURCE-ROLES.json').read_bytes()
    roles = read(HERE/'SOURCE-ROLES.json')
    assert set(roles) == {'servo/components/style/custom_properties.rs'}
    for name, row in roles.items():
        assert row['base_sha256'] == '2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
        assert row['candidate_sha256'] == '8a4adc903e7d88e218ee087cbe44cc3548df70fac9353dd923d5c32de2c458f9'
        for kind in ['base','candidate']:assert sha(ROOT/row[kind+'_capture']) == row[kind+'_sha256']
    for name,digest in policy['references'].items():assert sha(ROOT/name) == digest,name
    assert policy['predecessor'] == {'directory':'artifacts/css-prioritary-selection-original-v2','manifest_sha256':'2119c8ff41df3ed46f842670865fa85d92e6b8e8e93facfc53a05900dd46c094'}
    for name in ['baseline.py','wpt.py','assess.py','SOURCE-ROLES.json']:
        assert (HERE/name).read_bytes() == (previous/name).read_bytes(), name
    assert (HERE/'phases.py').read_text() == (previous/'phases.py').read_text().replace('== 74','== 77').replace('== 11','== 12')
    original = (previous/'run.py').read_text()
    expected = original.replace("'prioritary-selection-original74-v1'", "'prioritary-selection-original77-v3'")
    expected = expected.replace('    original_before = original_verify()\n', '    original_before = original_verify()\n' +
        "    intermediate = load('owner_intermediate', str((HERE / 'intermediate.py').relative_to(ROOT)))\n" +
        "    input_binding = load('owner_input_binding', str((HERE / 'inputs.py').relative_to(ROOT)))\n" +
        "    closure = load('owner_consumed_closure', str((HERE / 'closure.py').relative_to(ROOT)))\n" +
        "    closure.require_epoch_coverage(original, policy)\n" +
        "    consumed_inputs = input_binding.bind_inputs(str(HERE.relative_to(ROOT)), (HERE / 'FILES.json').read_bytes(), sys.argv[2], policy['intermediate_consumed_inputs'])\n")
    expected = expected.replace('        verified = state.a.verify_current(state.h, ROOT, env, local)\n', '        verified = intermediate.verify_intermediate(state.h, ROOT, env, local, consumed_inputs)\n')
    assert (HERE/'run.py').read_text() == expected
    binding = policy['intermediate_guard_binding']
    assert binding == {'directory':'artifacts/css-prioritary-intermediate-guard-proposal-v1','manifest_sha256':'ff5307801290a210780500d66f06f4a44ac5619894e0065be9ba650a8afde198'}
    guard = ROOT/binding['directory']
    ownership.authenticate(guard,binding['manifest_sha256'])
    for name in ['intermediate.py','inputs.py','review_scope.py']:
        assert (HERE/name).read_bytes() == (guard/name).read_bytes(), name
    closure = load('saved_consumed_closure',HERE/'closure.py')
    assert policy['intermediate_consumed_inputs'] == closure.external_inputs(ROOT,policy,roles)
    for name,digest in policy['intermediate_consumed_inputs'].items():
        if name.startswith('artifacts/'):
            assert digest is not None and sha(ROOT/name) == digest, name
    old_epoch = read(ROOT/policy['original_build']['epoch'])
    closure.require_epoch_coverage(old_epoch,policy)


def synthetic(policy, lane, status, revision='e'*40):
    settings = copy.deepcopy(policy['wpt_lanes'][lane])
    settings['phase_revisions'] = {'original':revision,'candidate':revision}
    settings['harness_revision'] = revision
    settings.update(tests={p:'testharness' for p in settings['expected_subtests']},held_subtests={},regression_subtests=settings['expected_subtests'],cardinality_description='exact lane roster')
    events=[{'action':'suite_start','run_info':{'os':'mac','debug':False,'browser_build_id':'synthetic','revision':revision}}]
    for page,names in settings['expected_subtests'].items():
        events.append({'action':'test_start','test':page})
        for name in names:
            expected = 'FAIL' if page.endswith('/forced-colors-mode-51.html') else 'PASS'
            row={'action':'test_status','test':page,'subtest':name,'status':status}
            if status != expected:row['expected']=expected
            if status=='FAIL':row['message']='ordinary synthetic assertion'
            events.append(row)
        events.append({'action':'test_end','test':page,'status':'OK'})
    events.append({'action':'suite_end'})
    app={'browser_build_id':'synthetic','revision':revision,'build_revision':revision,'harness_revision':revision,'source_role':'original','sha256':'c'*64,'path':'synthetic/application.ini','resolved':'synthetic/application.ini'}
    code=int(any(e.get('status') != e.get('expected',e.get('status')) for e in events if 'status' in e))
    return events, code, settings, app


def check():
    policy = read(HERE/'POLICY.json')
    validate_policy(policy)
    negatives=0
    for change in [lambda p:p.update(execution_enabled=True,candidate_execution_enabled=True),lambda p:p.update(head='e'*40),lambda p:p.update(controls={}),lambda p:p['wpt_lanes']['ordinary'].update(capture=None),lambda p:p['lane_order'].pop(),lambda p:p['wpt_lanes']['forced_colors']['metadata']['portable'].pop('forced-colors-mode/forced-colors-mode-51.html.ini'),lambda p:p['wpt_lanes']['mozilla_appearance']['expected_subtests'].clear(),lambda p:p['intermediate_consumed_inputs'].pop('artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py'),lambda p:p['intermediate_consumed_inputs'].pop('artifacts/css-prioritary-zoom-capture-v1/candidate.html'),lambda p:p['intermediate_consumed_inputs'].update({'artifacts/css-prioritary-selection-original-v3/POLICY.json':'bad'})]:
        bad=copy.deepcopy(policy);change(bad)
        try:validate_policy(bad)
        except (AssertionError,KeyError,TypeError):negatives+=1
        else:raise AssertionError('invalid disabled policy accepted')
    assessor=load('preservation_assessor',HERE/'assess.py')
    checks=load('preservation_stream_checks',ROOT/policy['wpt']['checks_helper'])
    streams=[]
    for lane in policy['lane_order']:
        for status in ['PASS','FAIL']:
            events,code,settings,app=synthetic(policy,lane,status)
            result=assessor.assess(events,code,settings,checks,run_binding=app)
            assert result['complete'],result['errors']
            assert len(result['rows'])==settings['expected_subtest_count']
            assert all(r['status']==status for r in result['rows'])
            streams.append([lane,status,len(result['rows']),len(result['ends'])])
    print(json.dumps({'references':len(policy['references']),'consumed_inputs':len(policy['intermediate_consumed_inputs']),'disabled_binding_negatives':negatives,'streams':streams,'no_live_guard':True}))


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    sys.dont_write_bytecode=True
    check()
