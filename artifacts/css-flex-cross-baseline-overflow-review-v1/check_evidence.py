import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE/'inputs'
result = {}
phases = {}
for phase in ['baseline-wpt-v1','candidate-wpt-v1','regressions-v1']:
    r=json.loads((P/phase/'RUN.json').read_text())
    raw=[json.loads(line) for line in (P/phase/'raw.json').read_text().splitlines()]
    assert r['status']=='done' and r['complete'] and r['before']==r['after']
    rows=[x for x in raw if x.get('action')=='test_status']
    ends=[x for x in raw if x.get('action')=='test_end']
    assert sum(x.get('action')=='suite_end' for x in raw)==1
    assert len(rows)==len({(x['test'],x['subtest']) for x in rows})
    assert len(ends)==len({x['test'] for x in ends})
    assert rows==r.get('rows',r.get('subtests'))
    assert ends==r.get('harness',r.get('tests'))
    if phase!='regressions-v1':
        assert len(rows)==54 and len(ends)==1 and ends[0]['status']=='OK'
        source=P/('before-nsFlexContainerFrame.cpp' if phase.startswith('baseline') else 'candidate-nsFlexContainerFrame.cpp')
        assert hashlib.sha256(source.read_bytes()).hexdigest()==r['before']['layout/generic/nsFlexContainerFrame.cpp']
        assert hashlib.sha256((P/'test.html').read_bytes()).hexdigest()==r['before']['testing/web-platform/tests/css/css-flexbox/flexbox-baseline-cross-size-overflow.html']
    else:
        requested=json.loads((P/'REGRESSION-TESTS.json').read_text())
        assert {x['test'] for x in ends}=={x.removeprefix('testing/web-platform/tests') for x in requested}
        assert len(ends)==29 and len(rows)==63 and all(x['status']=='PASS' for x in rows)
        assert collections.Counter(x['status'] for x in ends)=={'PASS':26,'OK':3}
    result[phase]={'exit':r['exit'],'rows':len(rows),'statuses':dict(collections.Counter(x['status'] for x in rows)),'ends':dict(collections.Counter(x['status'] for x in ends))}
    phases[phase]=(r,{(x['test'],x['subtest']):x for x in rows})
b,br=phases['baseline-wpt-v1'];c,cr=phases['candidate-wpt-v1']
assert br.keys()==cr.keys() and b['exit']==1 and c['exit']==0
changed=[];unchanged=[]
for key in br:
    x,y=br[key],cr[key]
    assert y['status']=='PASS'
    if x['status']=='FAIL':
        assert x['message']=='assert_equals: baseline cross-size remains positive before max-height clamping expected 100 but got 0'
        changed.append(key)
    else:
        assert (x['status'],x.get('message'))==(y['status'],y.get('message'))
        unchanged.append(key)
assert len(changed)==12 and len(unchanged)==42
assert b['before'].keys()==c['before'].keys()
pins=[k for k in b['before'] if b['before'][k]!=c['before'][k]]
assert set(pins)=={'layout/generic/nsFlexContainerFrame.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'}
result.update(improved=changed,unchanged=len(unchanged),different_pins=pins)
(HERE/'EVIDENCE-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
