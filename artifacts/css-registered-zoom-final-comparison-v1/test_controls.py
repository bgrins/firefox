import copy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_text())
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
records=read(HERE/'EVIDENCE.json')['phases'];old=[read(ROOT/r['runtime']/'ASSESSMENT.json') for r in records[:2]]
previous={'rows':old[0]['rows']+old[1]['rows'],'ends':old[0]['ends']+old[1]['ends']}
current=read(ROOT/records[-1]['runtime']/'ASSESSMENT.json');capsule=ROOT/records[-1]['capsule'];experiment=read(capsule/'EXPERIMENT.json')
normalizer=load('ports',ROOT/'artifacts/css-registered-zoom-reftest-port-adjudication-v1/replay.py');declared=normalizer.references(read(capsule/'SUBSET-MANIFEST.json'),experiment);compare=load('comparison',HERE/'compare.py').compare
assert compare(previous,current,experiment,normalizer,declared)['test_evidence_supports_acceptance']
rejected=[]
def reject(name,change):
    value=copy.deepcopy(current);change(value)
    try:result=compare(previous,value,experiment,normalizer,declared)
    except (ValueError,KeyError):rejected.append(name);return
    assert not result['test_evidence_supports_acceptance'],name;rejected.append(name)
first=lambda a:next(r for r in a['rows'] if r['test'] in experiment['focus_subtests'])
held=lambda a:next(r for r in a['rows'] if r['status']=='FAIL')
ref=lambda a:next(r for r in a['ends'] if r['test'] in declared)
for name,change in [
 ('focused PASS to FAIL',lambda a:first(a).update(status='FAIL')),
 ('unchanged PASS message drift',lambda a:first(a).update(message='different')),
 ('unchanged failure message drift',lambda a:held(a).update(message='different failure')),
 ('expected field drift',lambda a:first(a).update(expected='FAIL')),
 ('intermittent field drift',lambda a:first(a).update(known_intermittent=['FAIL'])),
 ('message absence versus null',lambda a:first(a).update(message=None)),
 ('missing assertion',lambda a:a['rows'].pop()),
 ('duplicate assertion',lambda a:a['rows'].append(copy.deepcopy(a['rows'][0]))),
 ('unknown assertion',lambda a:first(a).update(subtest='unknown')),
 ('missing completion',lambda a:a['ends'].pop()),
 ('duplicate completion',lambda a:a['ends'].append(copy.deepcopy(a['ends'][0]))),
 ('failed reference',lambda a:ref(a).update(status='FAIL')),
 ('reference expectation drift',lambda a:ref(a).update(expected='PASS')),
 ('reference intermittent drift',lambda a:ref(a).update(known_intermittent=['FAIL'])),
 ('reference host rewrite',lambda a:ref(a).update(message=ref(a)['message'].replace('web-platform.test','example.test'))),
 ('reference scheme rewrite',lambda a:ref(a).update(message=ref(a)['message'].replace('http://','https://'))),
 ('reference operator rewrite',lambda a:ref(a).update(message=ref(a)['message'].replace(' == ',' != '))),
 ('reference extra message text',lambda a:ref(a).update(message=ref(a)['message']+'extra')),
]:reject(name,change)
(HERE/'CONTROLS.json').write_text(json.dumps({'actual_complete_comparison_positive':True,'negative_controls':rejected,'uses_unchanged_previously_reviewed_strict_normalizer':True,'runtime_files_mutated':False,'browser_executed':False},indent=2)+'\n')
print(json.dumps({'positive':1,'negative':len(rejected)}))
