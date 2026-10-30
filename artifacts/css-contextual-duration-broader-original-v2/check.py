import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def check(policy):
    assessor = load('broader_assessor', HERE / 'assess.py')
    checks = load('broader_checks', ROOT / policy['wpt']['checks_helper'])
    counts = {'normative':(49,10), 'reftest':(0,1), 'feedback':(3,1)}
    positives = 0
    rejected = []
    for kind, settings in policy['phases'].items():
        assert sum(map(len, settings['expected_subtests'].values())) == counts[kind][0]
        assert len(settings['expected_subtests']) == counts[kind][1]
        config = dict(settings, tests=settings['test_types'], held_subtests={}, cardinality_description='synthetic only')
        config['regression_subtests'] = {page:[n for n in names if n not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
        app = policy['prepared_application_metadata']
        events = [{'action':'suite_start','run_info':{'os':'mac','debug':False,'browser_build_id':app['browser_build_id'],'revision':settings['harness_revision']}}]
        for page,names in settings['expected_subtests'].items():
            events.append({'action':'test_start','test':page})
            events.extend({'action':'test_status','test':page,'subtest':name,'status':'PASS'} for name in names)
            events.append({'action':'test_end','test':page,'status':'PASS' if kind=='reftest' else 'OK'})
        events.append({'action':'suite_end'})
        def assess(stream, code=0):
            return assessor.assess(stream, code, config, checks, run_binding=app)
        assert assess(events)['complete']
        positives += 1
        failing = copy.deepcopy(events)
        next(e for e in failing if e['action']==('test_end' if kind=='reftest' else 'test_status')).update(status='FAIL',expected='PASS',message='synthetic existing assertion')
        assert assess(failing,1)['complete']
        positives += 1
        def reject(label, change, code=0):
            stream = copy.deepcopy(events)
            change(stream)
            assert not assess(stream,code)['complete'], (kind,label)
            rejected.append(kind+': '+label)
        reject('missing end',lambda s:s.remove(next(e for e in s if e['action']=='test_end')))
        reject('duplicate start',lambda s:s.insert(1,copy.deepcopy(s[1])))
        reject('missing suite end',lambda s:s.pop())
        reject('timeout ending',lambda s:next(e for e in s if e['action']=='test_end').update(status='TIMEOUT'),1)
        reject('wrong BuildID',lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
        reject('wrong harness',lambda s:s[0]['run_info'].update(revision='0'*40))
        reject('crash',lambda s:s.append({'action':'crash'}))
        reject('wrong exit',lambda s:None,1)
        if kind=='reftest':
            reject('invented callback',lambda s:s.insert(2,{'action':'test_status','test':s[1]['test'],'subtest':'invented','status':'PASS'}))
            reject('testharness OK ending',lambda s:next(e for e in s if e['action']=='test_end').update(status='OK'))
        else:
            reject('missing callback',lambda s:s.remove(next(e for e in s if e['action']=='test_status')))
            reject('renamed callback',lambda s:next(e for e in s if e['action']=='test_status').update(subtest='unknown'))
    print(json.dumps({'positive_streams':positives,'rejected':rejected,'browser_executed':False,'feedback_numeric_oracle':False},indent=2))


if __name__ == '__main__':
    check(json.loads((HERE / 'POLICY.json').read_bytes()))
