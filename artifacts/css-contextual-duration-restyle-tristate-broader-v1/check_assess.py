import copy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


policy=json.loads((HERE/'POLICY.json').read_bytes())
source=json.loads((ROOT/policy['baseline_capsule']['directory']/'POLICY.json').read_bytes())
comparison=load('static_broader_compare',HERE/'comparison.py')
assessor=load('static_broader_assess',HERE/'assess.py')
checks=load('static_broader_checks',ROOT/policy['wpt']['checks_helper'])
positive=0
negative=[]
for kind in ('normative','reftest','inactive','reduced'):
    current=dict(policy,phase_kind=kind,wpt=policy['phases'][kind])
    assert current['wpt']==comparison.expected_wpt(ROOT,current)
    settings=comparison.phase_policy(current['wpt'])
    old_source = json.loads((ROOT/policy['reduced_capsule']['directory']/'POLICY.json').read_bytes()) if kind=='reduced' else (json.loads((ROOT/policy['inactive_capsule']['directory']/'POLICY.json').read_bytes()) if kind=='inactive' else source)
    old_wpt = dict(old_source['wpt'],test_types=current['wpt']['test_types']) if kind in ('inactive','reduced') else source['phases'][kind]
    old_settings=comparison.phase_policy(old_wpt)
    if kind in ('inactive','reduced'):old_settings['phase_kind']=kind
    app=source['prepared_application_metadata']
    events=[{'action':'suite_start','run_info':{'os':'mac','debug':False,'browser_build_id':app['browser_build_id'],'revision':policy['head']}}]
    targets={(p,n) for p,names in settings['target_subtests'].items() for n in names}
    for page,names in settings['expected_subtests'].items():
        events.append({'action':'test_start','test':page})
        for name in names:
            event={'action':'test_status','test':page,'subtest':name,'status':'PASS'}
            if (page,name) in targets:event.update(status='FAIL',expected='PASS',message='synthetic original target')
            events.append(event)
        events.append({'action':'test_end','test':page,'status':'PASS' if kind=='reftest' else 'OK'})
    if kind=='reftest':
        next(e for e in events if e['action']=='test_end')['message']='Testing http://web-platform.test:12345/css/css-animations/animation-duration-infinite.html == http://web-platform.test:12345/css/css-animations/animation-duration-infinite-ref.html\n'
    events.append({'action':'suite_end'})
    original=assessor.assess(events,1 if targets else 0,old_settings,checks,run_binding=app)
    assert original['complete']
    candidate_app=dict(app,browser_build_id='synthetic-new',revision=policy['head'],build_revision=policy['head'],source_role='candidate')
    candidate=copy.deepcopy(events);candidate[0]['run_info']['browser_build_id']='synthetic-new'
    for event in candidate:
        if (event.get('test'),event.get('subtest')) in targets:
            event['status']='PASS';event.pop('expected');event.pop('message')
    def assess(stream,code=0):return assessor.assess(stream,code,settings,checks,original=original,run_binding=candidate_app)
    if kind=='reftest':
        end=next(e for e in candidate if e['action']=='test_end');end['message']=end['message'].replace(':12345/', ':54321/')
    assert assess(candidate)['comparison_gate_passed'];positive+=1
    def reject(name,mutate,code=0):
        stream=copy.deepcopy(candidate);mutate(stream)
        assert not assess(stream,code)['comparison_gate_passed'],(kind,name)
        negative.append(kind+': '+name)
    reject('ending signature',lambda s:next(e for e in s if e['action']=='test_end').update(message='changed'))
    reject('wrong BuildID',lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
    reject('wrong exit',lambda s:None,1)
    reject('missing suite end',lambda s:s.pop())
    reject('crash',lambda s:s.append({'action':'crash'}))
    if kind=='reftest':
        for label,before,after in [('wrong path','infinite-ref.html','other-ref.html'),('wrong operator',' == ',' != '),('mixed ports',':54321/css/css-animations/animation-duration-infinite-ref',':54320/css/css-animations/animation-duration-infinite-ref'),('extra error','\n','\nERROR'),('zero port',':54321/',':0/'),('out of range port',':54321/',':65536/')]:
            reject(label,lambda stream,before=before,after=after: next(e for e in stream if e['action']=='test_end').update(message=next(e for e in stream if e['action']=='test_end')['message'].replace(before,after)))
    if kind in ('normative','feedback','reduced'):
        def row(stream,target=False):return next(e for e in stream if e['action']=='test_status' and (((e['test'],e['subtest']) in targets)==target))
        reject('control failure',lambda s:row(s).update(status='FAIL',expected='PASS'),1)
        reject('control expected presence',lambda s:row(s).update(expected='PASS'))
        reject('control intermittent presence',lambda s:row(s).update(known_intermittent=[]))
        reject('missing callback',lambda s:s.remove(row(s)))
    if targets:
        def target_row(stream):return next(e for e in stream if (e.get('test'),e.get('subtest')) in targets)
        reject('target still fails',lambda s:target_row(s).update(status='FAIL',expected='PASS'),1)
        prepass=copy.deepcopy(events)
        item=next(e for e in prepass if (e.get('test'),e.get('subtest')) in targets)
        item.update(status='PASS');item.pop('expected');item.pop('message')
        old=assessor.assess(prepass,1 if len(targets)>1 else 0,old_settings,checks,run_binding=app)
        assert old['complete'] and assessor.assess(candidate,0,settings,checks,original=old,run_binding=candidate_app)['comparison_gate_passed']
        changed=copy.deepcopy(candidate)
        next(e for e in changed if e.get('test')==item['test'] and e.get('subtest')==item['subtest']).update(message='changed prior PASS')
        assert not assessor.assess(changed,0,settings,checks,original=old,run_binding=candidate_app)['comparison_gate_passed']
        negative.append(kind+': originally passing target signature')
    if kind=='normative':
        legacy=next(e for e in events if e['action']=='test_status' and e['test'] not in settings['candidate_required_pass_pages'] and (e['test'],e['subtest']) not in targets)
        prior=copy.deepcopy(events);after=copy.deepcopy(candidate)
        for stream in (prior,after):
            next(e for e in stream if e.get('test')==legacy['test'] and e.get('subtest')==legacy['subtest']).update(status='FAIL',message='synthetic known failure',known_intermittent=[])
        old=assessor.assess(prior,1,old_settings,checks,run_binding=app)
        assert old['complete'] and assessor.assess(after,0,settings,checks,original=old,run_binding=candidate_app)['comparison_gate_passed'];positive+=1
print(json.dumps({'positive_comparisons':positive,'negative_controls':negative,'actual_broader_original_replayed':False,'native_browser_guard_or_build_executed':False},indent=2))
