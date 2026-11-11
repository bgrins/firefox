import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def module(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert sys.flags.isolated and not sys.flags.optimize
    a,o=module('analyze'),module('observe');schema=json.loads((HERE/'OBSERVATION-SCHEMA.json').read_text());expected=json.loads((HERE/'EXPECTED-BASELINE.json').read_text());url=expected['harness'][0]['test']
    state={key:0 for key in schema['state_fields']};state.update(playState='paused',pending=False,startTime=None,progress=None,currentIteration=None)
    records=[{'id':name,'phase':phase,'before':{key:'anything' for key in schema['style_fields']},'after':{key:'different' for key in schema['style_fields']},'stateBefore':copy.deepcopy(state),'stateAfter':copy.deepcopy(state),'readySettled':False,'animationType':'Anything','frames':[{'offset':None,'computedOffset':0.5,'easing':'linear','composite':'auto','fontSize':'arbitrary'}]} for name in schema['ids'] for phase in schema['phases']]
    rows=[{'action':'suite_start'},{'action':'test_start','test':url}]+[{'action':'process_output','data':schema['marker']+json.dumps(row)} for row in records]+[dict(action='test_status',**row) for row in expected['subtests']]+[dict(action='test_end',**expected['harness'][0]),{'action':'suite_end'}]
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='font-observation-parser-') as directory:
        path=Path(directory)/'raw.jsonl'
        def write(events):path.write_text(''.join(json.dumps(row)+'\n' for row in events))
        def accept():
            result=a.parse(path);assert a.rows(result)==a.rows(expected);assert len(o.parse(path))==15
        def reject(name,events=None,raw=None,observation_only=False):
            if raw is None:write(events)
            else:path.write_text(raw)
            try:o.parse(path) if observation_only else accept()
            except (AssertionError,KeyError,ValueError,TypeError):rejected.append(name)
            else:raise AssertionError(name+' accepted')
        write(rows);accept()
        for action in ['suite_start','test_start','test_end','suite_end']:
            reject('missing-'+action,[r for r in rows if r['action']!=action])
        reject('missing-callback',rows[:-3]+rows[-2:]);reject('duplicate-callback',rows[:-2]+[rows[-3]]+rows[-2:]);reject('duplicate-harness',rows[:-1]+[rows[-2]]+rows[-1:]);reject('duplicate-suite-end',rows+[rows[-1]])
        reject('crash',rows+[{'action':'crash'}]);reject('error-log',rows+[{'action':'log','level':'ERROR'}]);reject('critical-log',rows+[{'action':'log','level':'CRITICAL'}]);reject('assertion-count',rows+[{'action':'assertion_count','count':1,'min_expected':0,'max_expected':0}])
        for name,index,field,value in [('callback-fail',-3,'status','FAIL'),('callback-timeout',-3,'status','TIMEOUT'),('wrong-name',-3,'subtest','unknown'),('harness-timeout',-2,'status','TIMEOUT')]:
            changed=copy.deepcopy(rows);changed[index][field]=value;reject(name,changed)
        reject('missing-observation',rows[:2]+rows[3:]);reject('duplicate-observation',rows[:3]+[rows[2]]+rows[3:])
        reordered=copy.deepcopy(rows);reordered[2],reordered[3]=reordered[3],reordered[2];reject('phase-order',reordered,observation_only=True)
        def mutate(name,fn):
            changed=copy.deepcopy(rows);row=copy.deepcopy(records[0]);fn(row);changed[2]['data']=schema['marker']+json.dumps(row);reject(name,changed,observation_only=True)
        for name,key,value in [('wrong-id','id','unknown'),('wrong-phase','phase','unknown'),('bad-ready','readySettled',1),('bad-type','animationType',1),('empty-type','animationType',''),('frames-not-list','frames',{}),('style-not-map','before',[]),('extra-field','unknown',0)]:
            mutate(name,lambda row,k=key,v=value:row.__setitem__(k,v))
        mutate('missing-field',lambda row:row.pop('after'));mutate('missing-style-field',lambda row:row['before'].pop('fontSize'));mutate('nonstring-style',lambda row:row['before'].__setitem__('fontSize',10));mutate('extra-state-field',lambda row:row['stateBefore'].__setitem__('unknown',0));mutate('missing-state-field',lambda row:row['stateAfter'].pop('progress'))
        for name,key,value in [('bool-time','currentTime',True),('string-time','currentTime','0'),('nan-progress','progress',float('nan')),('infinite-duration','duration',float('inf')),('null-duration','duration',None),('bad-pending','pending',0),('bad-play-state','playState','unknown')]:
            mutate(name,lambda row,k=key,v=value:row['stateBefore'].__setitem__(k,v))
        mutate('missing-frame-field',lambda row:row['frames'][0].pop('offset'));mutate('bool-offset',lambda row:row['frames'][0].__setitem__('offset',True));mutate('null-computed-offset',lambda row:row['frames'][0].__setitem__('computedOffset',None));mutate('bad-frame-value',lambda row:row['frames'][0].__setitem__('fontSize',12))
        for name,data in [('wrong-version',rows[2]['data'].replace('V1','V2',1)),('prefixed-marker','prefix '+rows[2]['data']),('inner-truncation',rows[2]['data'][:-3]),('merged-lines',rows[2]['data']+rows[3]['data']),('duplicate-inner-key',schema['marker']+'{"id":"x",'+json.dumps(records[0])[1:])]:
            changed=copy.deepcopy(rows);changed[2]['data']=data;reject(name,changed,observation_only=True)
        changed=copy.deepcopy(rows);changed[2]['action']='log';reject('wrong-marker-event',changed,observation_only=True)
        changed=copy.deepcopy(rows);changed[2]['message']=changed[2].pop('data');reject('wrong-marker-field',changed,observation_only=True)
        write(rows);raw=path.read_text();reject('outer-truncation',raw=raw[:-5]);reject('duplicate-outer-key',raw=raw.replace('{"action": "suite_start"}','{"action":"suite_start","action":"suite_start"}',1))
        arbitrary=copy.deepcopy(rows)
        for index in range(2,17):
            row=json.loads(arbitrary[index]['data'][len(schema['marker']):]);row['frames']=[];row['before']['fontSize']='10px';row['after']['fontSize']='uninterpreted';row['stateBefore']['progress']=42;arbitrary[index]['data']=schema['marker']+json.dumps(row)
        write(arbitrary);accept()
    print(json.dumps({'status':'PASS','rejected_controls':rejected,'positive_controls':['complete-three-callback-fifteen-record-stream','arbitrary-style-progress-empty-frames-no-value-oracle']},indent=2))

if __name__=='__main__':main()
