import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('published_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    roles = read(HERE / 'SOURCE-ROLES.json')
    diagnostic = read(ROOT / policy['diagnostic_binding']['directory'] / 'SOURCE-ROLES.json')
    assert roles == {name: {k:v for k,v in row.items() if k != 'modified'} for name,row in diagnostic.items()}
    assert len(roles) == 3
    assert [name for name,row in roles.items() if row['candidate_sha256'] != row['base_sha256']] == ['servo/components/style/properties/cascade.rs']
    for name,row in roles.items():
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
        assert policy['source_context_pins'][name] == policy['committed_source_preimages'][name] == policy['semantic_original_sources'][name] == row['base_sha256']
    source_dir = ROOT / policy['baseline_capsule']['directory']
    source = read(source_dir / 'POLICY.json')
    for name in ('assess.py', 'inputs.py', 'review_scope.py', 'intermediate.py'):
        assert (HERE / name).read_bytes() == (source_dir / name).read_bytes()
    previous = ROOT / 'artifacts/css-prioritary-selection-candidate-v4'
    for name in ('wpt.py', 'phases.py', 'TARGETS.json'):
        assert (HERE / name).read_bytes() == (previous / name).read_bytes()
    for key in ('suite_binding', 'capture_binding', 'lane_order', 'metadata_current_pins', 'preserved_absent_metadata', 'preserved_absent_resources', 'source_context_pins', 'rebuilt_binaries', 'extra_backup_paths'):
        assert policy[key] == source[key], key
    published = read(HERE / 'PUBLISHED-CASES.json')
    targets = read(HERE / 'TARGETS.json')
    assert policy['wpt']['expected_subtest_count'] == 77 and policy['wpt']['expected_page_count'] == 12
    assert policy['wpt']['expected_target_count'] == 24
    for lane in ['wpt', *policy['lane_order']]:
        actual = policy['wpt'] if lane == 'wpt' else policy['wpt_lanes'][lane]
        old = source['wpt'] if lane == 'wpt' else source['wpt_lanes'][lane]
        prior = read(previous / 'POLICY.json')
        target_settings = prior['wpt'] if lane == 'wpt' else prior['wpt_lanes'][lane]
        assert actual['target_subtests'] == target_settings['target_subtests']
        assert actual['published_subtests'] == {page:names for page,names in published.items() if page in actual['expected_subtests']}
        for key in ('expected_target_count', 'expected_control_count', 'expected_regression_signature_count'):
            assert actual[key] == target_settings[key]
        assert len(set(actual['fixture_target_pages'])) == actual['expected_page_count']
        assert set(actual['fixture_target_pages']) == set(actual['expected_subtests'])
        assert all(value == policy['head'] for value in actual['phase_revisions'].values())
        assert actual['harness_revision'] == policy['head']
        a,b = copy.deepcopy(actual),copy.deepcopy(old)
        for key in ('target_subtests', 'expected_target_count', 'expected_control_count', 'expected_regression_signature_count', 'phase_revisions', 'harness_revision'):
            a.pop(key);b.pop(key)
        a.pop('published_subtests')
        assert a == b, lane
    assert sum(map(len,published.values())) == 8
    admission = load('admission')
    original, review, capture = admission.validate_original(ROOT, policy, roles)
    admission.validate_bridge(ROOT, policy, original, review)
    if policy['current_binding'] is None:
        assert policy['controls'] is None and policy['accepted_current_payloads'] == {}
        assert policy['intermediate_consumed_inputs'] is None and policy['activation_pending']
        assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    else:
        admission.validate_current(ROOT, policy, roles)
    closure = load('closure').external_inputs(ROOT, policy, roles)
    for path,pin in closure.items():
        if pin is not None:
            assert sha(ROOT / path) == pin, path
    if policy['current_binding'] is not None:
        assert policy['intermediate_consumed_inputs'] == closure
    return len(closure)


def rejected(action):
    try:
        action()
    except (AssertionError, TypeError, KeyError):
        return
    raise AssertionError('invalid binding admitted')


def behavior_checks(policy, lanes):
    comparison = load('comparison')
    assessor = load('assess')
    signature = assessor.signature
    rows = sum((v['rows'] for v in lanes.values()), [])
    ends = sum((v['ends'] for v in lanes.values()), [])
    counts = (sum(r['status'] == 'PASS' for r in rows),sum(r['status'] == 'FAIL' for r in rows),len(ends))
    assert counts == (64,13,12)
    tests = 0
    for lane,original in lanes.items():
        settings = policy['wpt_lanes'][lane]
        targets = {(page,name) for page,names in settings['target_subtests'].items() for name in names}
        candidate = copy.deepcopy(original)
        candidate['comparison_errors'] = []
        for row in candidate['rows']:
            if (row['test'], row['subtest']) in targets and row['status'] != 'PASS':
                row['status'] = 'PASS'; row.pop('message', None); row.pop('stack', None)
        result = comparison.behavior(original,candidate,settings,signature)
        assert result['repair_observation_gate'], result['errors']
        assert result == json.loads(json.dumps(result))
        for row in original['rows']:
            if row['status'] != 'PASS': continue
            mutated = copy.deepcopy(candidate)
            selected = next(x for x in mutated['rows'] if x['test']==row['test'] and x['subtest']==row['subtest'])
            selected['message'] = 'changed passing signature'
            assert not comparison.behavior(original,mutated,settings,signature)['repair_observation_gate']
            tests += 1
        mutated = copy.deepcopy(candidate); mutated['ends'].pop()
        assert not comparison.behavior(original,mutated,settings,signature)['repair_observation_gate']
        mutated = copy.deepcopy(candidate)
        for row in mutated['rows']: row['status']='FAIL'
        retained = comparison.behavior(original,mutated,settings,signature)
        assert not retained['repair_observation_gate'] and len(retained['candidate_signatures'])==len(original['rows'])+len(original['ends'])
        for row in original['rows']:
            if row['subtest'] not in settings['published_subtests'].get(row['test'],[]):continue
            before,after=copy.deepcopy(original),copy.deepcopy(candidate)
            for stream in (before,after):
                selected=next(x for x in stream['rows'] if x['test']==row['test'] and x['subtest']==row['subtest'])
                selected['status']='FAIL'
            selected['message']='changed published failure'
            result=comparison.behavior(before,after,settings,signature)
            assert 'published callback full signatures changed or missing' in result['errors']
    return {'original':counts,'preserved_PASS_mutations':tests,'all_FAIL_rows_retained':77,'endings_removed_negatives':3,'published_signature_negatives':8}


def main():
    policy=read(HERE/'POLICY.json')
    count=validate_policy(policy)
    comparison=load('comparison')
    lanes=comparison.replay_all(ROOT,policy)
    behavior=behavior_checks(policy,lanes)
    mutations=[('head','invented'),('baseline_head','invented'),('controls',{}),('current_binding',None),('accepted_current_payloads',{}),('intermediate_consumed_inputs',{}),('execution_handoff',None)]
    for key,value in mutations:
        changed=copy.deepcopy(policy);changed[key]=value
        rejected(lambda:validate_policy(changed))
    for key,value in [('committed_paths',[]),('receipt',dict(policy['checkpoint_bridge']['receipt'],sha256='0'*64))]:
        changed=copy.deepcopy(policy);changed['checkpoint_bridge'][key]=value
        rejected(lambda:validate_policy(changed))
    old=ROOT/policy['baseline_capsule']['directory']
    for name,path in [('candidate.py',old/'run.py'),('baseline.py',old/'baseline.py'),('closure.py',old/'closure.py'),('comparison.py',ROOT/'artifacts/css-prioritary-selection-candidate-v4/comparison.py')]:
        expected=''.join(difflib.unified_diff(path.read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile='a/'+path.name,tofile='b/'+name))
        assert (HERE/(name.split('.')[0].upper()+'-DELTA.patch')).read_text()==expected
    marker='    assert not restoration_errors, restoration_errors\n'
    a=(old/'run.py').read_text();b=(HERE/'candidate.py').read_text()
    expected=a[a.index(marker):].replace("'RESULT.json'","'CANDIDATE-RESULT.json'")
    assert expected==b[b.index(marker):]
    roles=read(HERE/'SOURCE-ROLES.json'); candidate=load('candidate')
    assert candidate.expected_modified_paths([],roles,policy['committed_source_preimages'])==['servo/components/style/properties/cascade.rs']
    assert candidate.expected_modified_paths(['unrelated'],roles,policy['committed_source_preimages'])==['servo/components/style/properties/cascade.rs','unrelated']
    rejected(lambda:candidate.expected_modified_paths([],roles,{}))
    print(json.dumps({'consumed_inputs':count,'binding_negatives':9,'comparison':behavior,'only_cascade_modified':True,'final_restoration_tail_unchanged_except_result_filename':True,'live_guard_executed':False,'native_build':False,'browser_run':False}))


if __name__ == '__main__':main()
