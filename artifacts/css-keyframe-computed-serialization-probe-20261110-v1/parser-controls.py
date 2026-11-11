import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def main():
    assert sys.flags.isolated and not sys.flags.optimize
    spec=importlib.util.spec_from_file_location('analyze',HERE/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    expected=json.loads((HERE/'EXPECTED-BASELINE.json').read_text());url=expected['harness'][0]['test']
    rows=[{'action':'suite_start'},{'action':'test_start','test':url}]+[dict(action='test_status',message='actual arbitrary diagnostic',**r) for r in expected['subtests']]+[dict(action='test_end',**expected['harness'][0]),{'action':'suite_end'}]
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='computed-keyframe-parser-') as directory:
        path=Path(directory)/'raw.jsonl'
        def write(events):path.write_text(''.join(json.dumps(r)+'\n' for r in events))
        def accept():
            result=a.parse(path);assert a.rows(result)==a.rows(expected);return result
        def reject(name,events=None,raw=None):
            if raw is None:write(events)
            else:path.write_text(raw)
            try:accept()
            except (AssertionError,KeyError,ValueError,TypeError):rejected.append(name)
            else:raise AssertionError(name+' accepted')
        write(rows);result=accept();assert all(r['message']=='actual arbitrary diagnostic' for r in result['subtests'])
        for action in ['suite_start','test_start','test_end','suite_end']:
            reject('missing-'+action,[r for r in rows if r['action']!=action])
        reject('missing-callback',rows[:2]+rows[3:])
        reject('duplicate-callback',rows[:3]+[rows[2]]+rows[3:])
        reject('duplicate-harness',rows[:-1]+[rows[-2]]+rows[-1:])
        reject('duplicate-suite-end',rows+[rows[-1]])
        reject('crash',rows+[{'action':'crash'}])
        reject('error-log',rows+[{'action':'log','level':'ERROR'}])
        reject('critical-log',rows+[{'action':'log','level':'CRITICAL'}])
        reject('assertion-count',rows+[{'action':'assertion_count','count':1,'min_expected':0,'max_expected':0}])
        for name,index,field,value in [('unexpected-improvement',2,'status','PASS'),('control-regression',4,'status','FAIL'),('callback-timeout',2,'status','TIMEOUT'),('unknown-name',2,'subtest','x'),('harness-timeout',-2,'status','TIMEOUT'),('wrong-test',-2,'test','/wrong')]:
            changed=copy.deepcopy(rows);changed[index][field]=value;reject(name,changed)
        write(rows);raw=path.read_text();reject('truncation',raw=raw[:-5]);reject('duplicate-json-key',raw=raw.replace('{"action": "suite_start"}','{"action":"suite_start","action":"suite_start"}',1))
        changed=copy.deepcopy(rows);changed[2]['message']='different real failure detail';write(changed);assert accept()['subtests']!=result['subtests']
    print(json.dumps({'status':'PASS','rejected_controls':rejected,'positive_controls':['exact-five-fail-three-pass-vector','actual-messages-preserved-not-guessed']},indent=2))
if __name__=='__main__':main()
