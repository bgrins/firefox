import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('partial_runner', HERE / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
policy = json.loads((HERE / 'POLICY.json').read_text())
assert not policy['execution_enabled']
for browser in ['firefox', 'chrome']:
    m.authenticate(policy, browser)
def sample(browser='firefox', duration=1500):
    def details(value):
        return dict(opacity=750/value, font='32px', cssDuration='2s, 1s', timings=[dict(duration=v, computedDuration=v, progress=750/v, time=750, state='paused') for v in [2000,value]])
    rows=[]
    for mode,font in [('contextual',24),('literal',24),('contextual',32),('literal',32)]:
        rows.append(dict(id=f'{mode}-{font}', mode=mode, finalFont=font, authoredInitialFont=16, stage='complete', error=None, acquired=[], initial=details(1000), samples=[dict(phase=n,opacity=750/duration) for n in ['first-read','passive-frame-1','passive-frame-2','passive-frame-3']], beforeMembership=details(duration), afterMembership=details(duration), membership=dict(count=2,currentNames=['constant-font','fade'],held=[dict(name=n,animation=True,effect=True) for n in ['constant-font','fade']]), referenceChecks=[dict(name='synthetic calibration',passed=False)], contextualTimingVerdict=None))
    return dict(run_id='run',report=dict(schema='partial-base-observation-v1',status='complete',userAgent='Firefox/158.0' if browser=='firefox' else 'HeadlessChrome/156.0.8078.80',contextualTimingVerdict=None,observations=rows))
for browser in ['firefox','chrome']:
    for duration in [1000,1500,2000]:
        v=sample(browser,duration);assert m.validate(v,'run',browser) is v['report']
v=sample();v['report']['observations'][0]['beforeMembership']['timings'][1]['duration']=None
v['report']['observations'][0]['samples'][0]['opacity']={'nonfinite':'NaN'}
m.validate(v,'run','firefox')
v=sample();v['report']['status']='incomplete';v['report']['observations'][0].update(stage='acquisition',error=dict(name='Error',message='failed',stack=None),initial=None,samples=[],beforeMembership=None,membership=None,afterMembership=None)
m.validate(v,'run','firefox')
neg=[]
for name,mutate in [
 ('run',lambda v:v.update(run_id='wrong')),
 ('UA',lambda v:v['report'].update(userAgent='Firefox/157.0')),
 ('unfinished',lambda v:v['report'].update(status='running')),
 ('verdict',lambda v:v['report'].update(contextualTimingVerdict=True)),
 ('missing case',lambda v:v['report']['observations'].pop()),
 ('order',lambda v:v['report']['observations'].reverse()),
 ('missing sample',lambda v:v['report']['observations'][0]['samples'].pop()),
 ('field',lambda v:v['report']['observations'][0]['initial'].update(extra=True)),
 ('empty calibration',lambda v:v['report']['observations'][0].update(referenceChecks=[])),
]:
    v=sample();mutate(v)
    try:m.validate(v,'run','firefox')
    except AssertionError:neg.append(name)
    else:raise AssertionError(name)
with tempfile.TemporaryDirectory(prefix='partial-static-',dir='/private/tmp') as tmp:
    receiver=m.Receiver(policy,'firefox',Path(tmp));receiver.origin='http://127.0.0.1:1'
    v=sample();v['run_id']=receiver.run_id;body=json.dumps(v).encode()
    assert receiver.receive('/report/'+receiver.nonce,receiver.origin,body)=={'accepted':True}
    assert json.loads((Path(tmp)/'REPORT.json').read_text())==v
    for path,origin in [('/report/'+receiver.nonce,receiver.origin),('/wrong',receiver.origin),('/report/'+receiver.nonce,'http://other')]:
        try:receiver.receive(path,origin,body)
        except AssertionError:neg.append('exclusive/nonce/origin')
        else:raise AssertionError('unexpected accept')
    assert receiver.resources['/observe.js']==Path(policy['resources']['/observe.js']['path']).read_bytes()
    assert receiver.resources['/observe.html'].removesuffix(b'\n<script src="/report.js" defer></script>\n')==Path(policy['resources']['/observe.html']['path']).read_bytes()
binary='/Applications/Firefox.app/Contents/MacOS/firefox';profile='/private/tmp/owned/profile';url='http://127.0.0.1:1/observe.html?run=x&nonce=y'
rows=[dict(pid=100,ppid=1,pgid=100,command=f'{binary} --profile {profile} {url}'),dict(pid=101,ppid=100,pgid=100,command=f'/Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -profile {profile} child')]
assert m.firefox_relaunch_group(rows,binary,profile,url)==(rows[0],rows)
for name,mutate in [('nonce',lambda v:v[0].update(command=v[0]['command'].replace('nonce=y','nonce=z'))),('leader',lambda v:v[0].update(pgid=99)),('unrelated child',lambda v:v[1].update(command='/bin/other')),('parent',lambda v:v[1].update(ppid=42)),('profile',lambda v:v[1].update(command=v[1]['command'].replace(profile,'/other/profile'))),('duplicate main',lambda v:v.append(copy.deepcopy(v[0])))]:
    v=copy.deepcopy(rows);mutate(v)
    try:m.firefox_relaunch_group(v,binary,profile,url)
    except AssertionError:neg.append(name)
    else:raise AssertionError(name)
print(json.dumps(dict(schema_positive=6,unknown_nonfinite_and_partial_preserved=True,exclusive_transport_positive=True,fixture_exact_plus_bridge=True,relaunch_group_positive=True,negative=neg,no_live_operations=True),indent=2))
