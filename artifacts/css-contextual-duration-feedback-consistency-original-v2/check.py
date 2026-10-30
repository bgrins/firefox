import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic(settings):
    settings = copy.deepcopy(settings)
    settings['harness_revision'] = 'a' * 40
    settings['phase_revisions'] = {'original': 'b' * 40}
    app = {'browser_build_id':'synthetic-original', 'entry_identity':[1,2],
           'entry_type':40960, 'identity':[1,3], 'path':'/synthetic/application.ini',
           'resolved':'/synthetic/target.ini', 'revision':'b'*40, 'sha256':'c'*64,
           'symlink_target':'/synthetic/target.ini', 'build_revision':'b'*40,
           'harness_revision':'a'*40, 'source_role':'original'}
    config = dict(settings, tests=settings['test_types'], held_subtests={},
                  regression_subtests=settings['expected_subtests'], cardinality_description='Synthetic only')
    events = [{'action':'suite_start','run_info':{'os':'mac','debug':False,
              'browser_build_id':app['browser_build_id'],'revision':app['harness_revision']}}]
    for page, names in settings['expected_subtests'].items():
        events.append({'action':'test_start','test':page})
        events.extend({'action':'test_status','test':page,'subtest':name,'status':'PASS'} for name in names)
        events.append({'action':'test_end','test':page,'status':'OK'})
    events.append({'action':'suite_end'})
    return config, app, events


def check(policy):
    pending = policy['head'] is None
    if pending:
        assert not policy['execution_enabled'] and policy['activation_pending']
        assert policy['controls'] is None and policy['prepared_application_metadata'] is None
    else:
        assert isinstance(policy['head'],str) and len(policy['head']) == 40
        assert set(policy['controls']) == {'CURRENT-EPOCH.json','ROLE.json','OWNED.json'}
        assert all(isinstance(pin,str) and len(pin)==64 for pin in policy['controls'].values())
        app = policy['prepared_application_metadata']
        assert app['harness_revision'] == policy['head'] and app['source_role'] == 'original'
        assert app['revision'] == app['build_revision'] == policy['wpt']['phase_revisions']['original']
        assert policy['wpt']['harness_revision'] == policy['head']
        if policy['execution_enabled']:
            assert policy['activation_pending'] == []
    assert set(policy['phases']) == {'feedback'} and policy['wpt'] == policy['phases']['feedback']
    settings = policy['wpt']
    inputs = json.loads((ROOT / policy['feedback_transport']['directory'] / 'INPUTS.json').read_bytes())
    assert settings['expected_subtests'] == inputs['expected_subtests']
    assert all(settings[key] == inputs[key] for key in ('resources','metadata','manifest','test_types'))
    assert policy['record_schema_helper'] == inputs['transport']['helper']
    assert policy['record_kinds'] == {name:kind for kind,name in inputs['transport']['record_files'].items()}
    assert inputs['expected_callbacks'] == 2 and inputs['calibrated_acquisition_requires_all_pass']
    if policy['feedback_transport_pending']:
        assert not policy['execution_enabled']
    assert set(settings['phase_revisions']) == {'original'}
    if pending:
        assert settings['phase_revisions']['original'] is None and settings['harness_revision'] is None
    assert (settings['expected_subtest_count'],settings['expected_control_count'],settings['expected_target_count'],settings['expected_page_count']) == (2,2,0,1)
    authenticated, deferred = 0, []
    for name, pin in policy['references'].items():
        if not name.startswith('artifacts/'):
            deferred.append(name)
            continue
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == pin, name
        authenticated += 1
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    assessor = load('feedback_original_assessor',HERE/'assess.py')
    checks = load('feedback_original_checks',ROOT/settings['checks_helper'])
    config, app, events = synthetic(settings)
    def assess(stream, code=0):
        return assessor.assess(stream,code,config,checks,run_binding=app)
    assert assess(events)['complete']
    failed = copy.deepcopy(events)
    failed[2].update(status='FAIL', expected='PASS', message='synthetic calibration failure')
    assert assess(failed, 1)['complete']
    rejected = []
    def reject(label, change, code=0):
        stream = copy.deepcopy(events)
        change(stream)
        assert not assess(stream,code)['complete'], label
        rejected.append(label)
    reject('missing callback',lambda s:s.pop(2))
    reject('renamed callback',lambda s:s[2].update(subtest='unknown'))
    reject('duplicate callback',lambda s:s.insert(2,copy.deepcopy(s[2])))
    reject('missing end',lambda s:s.pop(-2))
    reject('missing suite end',lambda s:s.pop())
    reject('timeout ending',lambda s:s[-2].update(status='TIMEOUT'),1)
    reject('wrong BuildID',lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
    reject('wrong harness',lambda s:s[0]['run_info'].update(revision='0'*40))
    reject('crash',lambda s:s.append({'action':'crash'}))
    reject('wrong exit',lambda s:None,1)
    return {'positive_streams':2,'rejected':rejected,'artifact_references_authenticated':authenticated,
            'deferred_nonartifact_references':deferred,'future_bindings_null':pending,'fixture_seal_pending':policy['feedback_transport_pending'],
            'browser_build_or_live_guard_executed':False,'numeric_feedback_oracle':False}


if __name__ == '__main__':
    print(json.dumps(check(json.loads((HERE/'POLICY.json').read_bytes())),indent=2))
