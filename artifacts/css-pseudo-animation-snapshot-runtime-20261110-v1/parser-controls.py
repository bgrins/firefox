import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('analysis',HERE/'analyze.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def names(test):
    if test in a.expected_controls():return sorted(a.expected_controls()[test])
    if test.endswith('/KeyframeEffect/target.html'):return [f'target-{i}' for i in range(24)]
    if test.endswith('/keyframe-attribute-mutation.html'):
        values=[f'Keyframe attr mutation: {mode}, {qualification}, {history}'
                for mode,qualification in [(m,'unqualified') for m in ['CSS ordinary','CSS registered','WAAPI ordinary','WAAPI registered']]+[('CSS ordinary','qualified')]
                for history in ['retained','fresh']]
        return values+[f'Keyframe attr mutation: ordinary-style control, {q}' for q in ['qualified','unqualified']]
    return [None, 'synthetic callback']


def fixture():
    rows=[{'action':'suite_start'}]
    for path in json.loads((HERE/'RUN-PLAN.json').read_text())['suites']:
        test='/'+path.removeprefix('testing/web-platform/tests/')
        rows.append({'action':'test_start','test':test})
        for name in names(test):rows.append({'action':'test_status','test':test,'subtest':name,'status':'PASS'})
        rows.append({'action':'test_end','test':test,'status':'OK'})
    rows.append({'action':'suite_end'})
    return rows


def main():
    rejected=[]
    def rejects(name, operation):
        try:operation()
        except (AssertionError,ValueError,TypeError,KeyError):rejected.append(name)
        else:raise AssertionError('Malformed control accepted: '+name)
    with tempfile.TemporaryDirectory(prefix='snapshot-parser-controls-') as directory:
        def parse(rows):
            path=Path(directory)/'raw.jsonl';path.write_text(''.join((r if isinstance(r,str) else json.dumps(r))+'\n' for r in rows));return a.parse(path)
        original=fixture();baseline=parse(original)
        assert a.compare(baseline,copy.deepcopy(baseline))['identical_callback_statuses_and_inventory']
        baseline_failure=copy.deepcopy(original)
        next(r for r in baseline_failure if r['action']=='test_status')['status']='FAIL'
        parsed_failure=parse(baseline_failure)
        assert a.compare(parsed_failure,parsed_failure)['identical_callback_statuses_and_inventory']
        callback=next(i for i,r in enumerate(original) if r['action']=='test_status')
        ending=next(i for i,r in enumerate(original) if r['action']=='test_end')
        rejects('duplicate-callback',lambda:parse(original[:callback]+[original[callback]]+original[callback:]))
        rejects('duplicate-harness-end',lambda:parse(original[:ending]+[original[ending]]+original[ending:]))
        rejects('missing-required-control',lambda:parse(original[:callback]+original[callback+1:]))
        rejects('missing-harness-end',lambda:parse(original[:ending]+original[ending+1:]))
        rejects('missing-suite-end',lambda:parse(original[:-1]))
        rejects('early-suite-end',lambda:parse([original[0],original[-1]]+original[1:-1]))
        rejects('duplicate-test-start',lambda:parse(original[:1]+[original[1]]+original[1:]))
        rejects('crash',lambda:parse(original+[{'action':'crash'}]))
        rejects('generic-error-log',lambda:parse(original+[{'action':'log','level':'ERROR','message':'infrastructure error'}]))
        rejects('unexpected-assertion-count',lambda:parse(original+[{'action':'assertion_count','count':1,'min_expected':0,'max_expected':0}]))
        rejects('duplicate-json-key',lambda:parse(['{"action":"suite_start","action":"suite_start"}']+original[1:]))
        for name,field,value,index in [('wrong-harness-kind','status','PASS',ending),('timeout-callback','status','TIMEOUT',callback),('non-string-name','subtest',42,callback)]:
            changed=copy.deepcopy(original);changed[index][field]=value;rejects(name,lambda changed=changed:parse(changed))
        changed=copy.deepcopy(baseline);changed['subtests'].append(copy.deepcopy(changed['subtests'][0]))
        rejects('duplicate-comparison-assertion',lambda:a.compare(baseline,changed))
        changed=copy.deepcopy(baseline);changed['harness'].append(copy.deepcopy(changed['harness'][0]))
        rejects('duplicate-comparison-harness',lambda:a.compare(baseline,changed))
        for name,change in [('changed-status',lambda d:d['subtests'][0].update(status='FAIL')),
                            ('removed-assertion',lambda d:d['subtests'].pop()),
                            ('removed-harness',lambda d:d['harness'].pop()),
                            ('null-name-assertion-collision',lambda d:next(r for r in d['subtests'] if r['subtest'] is None).update(status='FAIL'))]:
            changed=copy.deepcopy(baseline);change(changed)
            assert not a.compare(baseline,changed)['identical_callback_statuses_and_inventory'],name
            rejected.append(name)
        collision=copy.deepcopy(baseline)
        next(r for r in collision['subtests'] if r['subtest'] is None)['status']='FAIL'
        def old_keys(result):
            return {(r['test'],r.get('subtest')):r['status'] for field in ['subtests','harness'] for r in result[field]}
        assert old_keys(baseline)==old_keys(collision), 'old collision control must reproduce'
        assert len(a.rows(baseline))==len(baseline['subtests'])+len(baseline['harness'])
    return {'status':'PASS','synthetic_only':True,'untyped_key_collision_reproduced_and_rejected':True,
            'known_subtest_failures_preserved_without_waiver':True,'rejected_controls':rejected,
            'builds_or_browser_tests_executed':False}


if __name__=='__main__':print(json.dumps(main(),indent=2))
