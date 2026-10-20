import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
RUN=ROOT.parent/'css-cssom-rectangle-standalone-runtime-v1'
PROPOSAL=ROOT.parent/'css-exact-size-observer-repair-proposal-v1'
SPLIT=ROOT.parent/'css-exact-size-observer-repair-review-v1'
PINS={}
def read(p):
    b=p.read_bytes();PINS[str(p.relative_to(ROOT.parent))]=hashlib.sha256(b).hexdigest();return b
def load(p):return json.loads(read(p))
def require(v,msg):
    if not v:raise SystemExit(msg)
def index(rows,fields):
    d={}
    for r in rows:
        k=tuple(r[f] for f in fields);require(k not in d,'Duplicate outcome');d[k]=r
    return d
def status(r):return(r['status'],r.get('expected'),r.get('known_intermittent'))
def emit(name,value):
    text=json.dumps(value,indent=2)+'\n'
    p=ROOT/name
    if '--check' in sys.argv:
        require(p.read_text()==text,'Changed receipt '+name)
    else:p.write_text(text)

def main():
    state=load(RUN/'STATE.json')
    require(state['status']=='terminal' and all(state[f] for f in ['source_restored','head_unchanged','index_unchanged']),'Terminal restored state')
    require(state['wpt_lint_exit']==0 and state['restore_build_exit']==0,'Lint/restoration exit')
    variants=['baseline','dom-only','integer-only','both'];outcomes={};ends={};runs={};summary={}
    names=['getBoundingClientRect-transformed-edge-precision.html','getBoundingClientRect-untransformed-edge-precision.html']
    wording={
        'DOMRect conversion preserves an aligned edge on an identity-transformed box':'Identity-transformed boxes preserve aligned client rectangle edges',
        'explicit transform retains matrix route':'identity transform is applied',
        'Ordinary client rectangles preserve an aligned edge without a graphics round trip':'Untransformed boxes preserve aligned client rectangle edges',
        'ordinary translation eligibility calibration':'no transform is applied'}
    for name,author in zip(names,['dom-only.html','integer-only.html']):
        text=read(SPLIT/author).decode()
        for a,b in wording.items():text=text.replace(a,b)
        require(read(RUN/name)==text.encode(),'Only enumerated title/assertion-message split WPT changes')
    tests=load(RUN/'TESTS.json');require(len(tests)==len(set(tests))==23,'Closed test roster')
    for v in variants:
        run=load(RUN/v/'RUN.json');runs[v]=run
        require(run['complete'] and run['before']==run['after'],'Run complete/stable')
        raw=[json.loads(x) for x in read(RUN/v/'raw.json').splitlines()]
        rows=[r for r in raw if r.get('action')=='test_status'];tail=[r for r in raw if r.get('action')=='test_end']
        require(rows==run['rows'] and tail==run['ends'],'Raw summary correspondence')
        require(len(rows)==74 and len(tail)==23,'Closed outcome counts')
        outcomes[v]=index(rows,['test','subtest']);ends[v]=index(tail,['test'])
        require({k[0] for k in ends[v]}=={t.removeprefix('testing/web-platform/tests') for t in tests},'Exact file roster')
        new=[r for r in rows if r['test'].split('/')[-1] in names]
        require(len(new)==8,'Split WPT count')
        for r in new:
            n=r['subtest'];which=r['test'].split('/')[-1]
            require(n in [a+', '+b+'px' for a in ['horizontal','vertical'] for b in ['120.125','131072.0666667' if which==names[0] else '139808.125']],'Named case roster')
            expect='PASS' if '120.125px' in n or v=='both' or (v=='dom-only' and which==names[0]) or (v=='integer-only' and which==names[1]) else 'FAIL'
            require(r['status']==expect,'Independent split expectation')
        folder='source-before' if v=='baseline' else 'source-'+v
        for rel,f,changed in [('dom/base/DOMRect.cpp','DOMRect.cpp',v in ['dom-only','both']),('layout/base/nsLayoutUtils.cpp','nsLayoutUtils.cpp',v in ['integer-only','both'])]:
            b=read(RUN/folder/rel)
            require(b==read(PROPOSAL/('candidate' if changed else 'original')/f),'Exact proposal source')
            require(hashlib.sha256(b).hexdigest()==run['before'][rel],'Runtime source binding')
        for rel,h in run['before'].items():
            if h is not None and not rel.startswith('objdir-'):
                require(hashlib.sha256(read(RUN/v/'inputs'/rel)).hexdigest()==h,'Retained input binding')
        require(load(RUN/(v+'-wpt.json'))['exit']==run['exit'],'Driver exit');read(RUN/(v+'-wpt.log'))
        if v!='baseline':
            require(load(RUN/(v+'-build.json'))['exit']==0,'Variant build');read(RUN/(v+'-build.log'))
            load(RUN/(v+'-format-check.json'));read(RUN/(v+'-format-check.log'))
        summary[v]={'new':dict(Counter(r['status'] for r in new)),'existing':dict(Counter(r['status'] for r in rows if r not in new)),'file_outcomes':dict(Counter(r['status'] for r in tail)),'stable_pins':len(run['before']),'exit':run['exit']}
    for v in variants[1:]:
        require(outcomes[v].keys()==outcomes['baseline'].keys() and ends[v].keys()==ends['baseline'].keys(),'Outcome identity')
        require(all(status(r)==status(outcomes[v][k]) for k,r in outcomes['baseline'].items() if k[0].split('/')[-1] not in names),'Existing subtests unchanged')
        require(all(status(r)==status(ends[v][k]) for k,r in ends['baseline'].items()),'File outcomes unchanged')
        expected={'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
        if v in ['dom-only','both']:expected.add('dom/base/DOMRect.cpp')
        if v in ['integer-only','both']:expected.add('layout/base/nsLayoutUtils.cpp')
        require({k for k,h in runs['baseline']['before'].items() if runs[v]['before'][k]!=h}==expected,'Cross-variant pins')
    for f in ['wpt-lint.log','format-warning-details-v2.log','restore-build.log']:read(RUN/f)
    for f in ['BEFORE.json','RESTORED.json','INPUTS.json','INSTALL.json','wpt-lint.json']:load(RUN/f)
    require(load(RUN/'restore-build.json')['exit']==0,'Restoration build')
    emit('STANDALONE-RESULT.json',{'status':'PASS','variants':summary,'format_warning':'Integer helper signature formatting remains separate; default exit0 was not warning-free.','full_safe_origin':'OPEN'})
    emit('STANDALONE-INPUT-PINS.json',PINS)
    print(json.dumps({'status':'PASS','inputs':len(PINS),'variants':summary}))
if __name__=='__main__':main()
