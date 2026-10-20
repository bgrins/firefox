import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent
RUN=ROOT.parent/'css-cssom-rectangle-four-variant-runtime-v1'
PROPOSAL=ROOT.parent/'css-exact-size-observer-repair-proposal-v1'
PINS={}

def read(p):
    b=p.read_bytes();PINS[str(p.relative_to(ROOT.parent))]=hashlib.sha256(b).hexdigest()
    return b

def load(p): return json.loads(read(p))

def require(v,msg):
    if not v: raise SystemExit(msg)

def status(row): return (row['status'],row.get('expected'),tuple(row.get('known_intermittent',[])))

def index(rows, fields):
    d={}
    for row in rows:
        key=tuple(row[f] for f in fields);require(key not in d,'Duplicate row');d[key]=row
    return d

def identity(row):
    if row['kind']=='non-flex':return (row['kind'],row['basis'],row['axis'],row['padded'])
    return (row['kind'],row['basis'],json.dumps(row['configuration'],sort_keys=True))

def emit(name,value):
    text=json.dumps(value,indent=2)+'\n'
    p=ROOT/name
    if '--check' in sys.argv:
        require(p.read_text()==text,'Changed receipt '+name)
    else:p.write_text(text)

def main():
    state=load(RUN/'STATE.json')
    require(state['status']=='terminal' and state['source_restored'] and state['head_unchanged'] and state['index_unchanged'],'Terminal restoration')
    variants=['baseline','dom-only','integer-only','both']
    expected_new={'baseline':{'PASS':12,'FAIL':16},'dom-only':{'PASS':20,'FAIL':8},'integer-only':{'PASS':16,'FAIL':12},'both':{'PASS':28}}
    new_test='/css/cssom-view/getBoundingClientRect-large-absolute-edge.html'
    summaries={};outcomes={};ends={};runs={};probes={};sources={};probe_summary={}
    for variant in variants:
        run=load(RUN/variant/'RUN.json');runs[variant]=run
        require(run['complete'] and run['before']==run['after'],'WPT stable')
        events=[json.loads(x) for x in read(RUN/variant/'raw.json').splitlines()]
        rows=[r for r in events if r.get('action')=='test_status']
        tail=[r for r in events if r.get('action')=='test_end']
        require(rows==run['rows'] and tail==run['ends'],'Raw/summary equality')
        require(len(rows)==57 and len(tail)==14,'Closed outcome roster')
        outcomes[variant]=index(rows,['test','subtest']);ends[variant]=index(tail,['test'])
        new=[r for r in rows if r['test']==new_test]
        require(dict(Counter(r['status'] for r in new))==expected_new[variant],'New status inventory')
        for r in new:
            n=r['subtest']
            if n.startswith('coordinate effect:') or 'box 120.125px' in n:expected='PASS'
            elif 'box 131072.0666667px' in n:expected='PASS' if variant in ['dom-only','both'] else 'FAIL'
            elif 'box 139808.125px' in n:
                expected='PASS' if variant=='both' or (variant=='integer-only' and 'host 100px' in n) else 'FAIL'
            else:raise SystemExit('Unexpected named case')
            require(r['status']==expected,'Independent named-case expectation')
        sources[variant]={}
        folder='source-before' if variant=='baseline' else 'source-'+variant
        for rel,f,changed in [('dom/base/DOMRect.cpp','DOMRect.cpp',variant in ['dom-only','both']),('layout/base/nsLayoutUtils.cpp','nsLayoutUtils.cpp',variant in ['integer-only','both'])]:
            actual=read(RUN/folder/rel);expected=read(PROPOSAL/('candidate' if changed else 'original')/f)
            require(actual==expected,'Exact source variant')
            require(hashlib.sha256(actual).hexdigest()==run['before'][rel],'Source-to-run binding')
            sources[variant][rel]=run['before'][rel]
        for rel,h in run['before'].items():
            if h is None or rel.startswith('objdir-'):continue
            require(hashlib.sha256(read(RUN/variant/'inputs'/rel)).hexdigest()==h,'Retained input binding')
        driver=load(RUN/(variant+'-wpt.json'));require(driver['exit']==run['exit'],'Driver exit')
        read(RUN/(variant+'-wpt.log'))
        if variant!='baseline':
            build=load(RUN/(variant+'-build.json'));require(build['exit']==0,'Build exit');read(RUN/(variant+'-build.log'))
        probe=load(RUN/(variant+'-probe')/'RESULT.json')
        require(probe['stable'] and probe['before']==probe['after'],'Probe stable')
        for rel in ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',*sources[variant]]:
            matching=[v for k,v in probe['before'].items() if k.endswith('/'+rel)]
            require(matching==[run['before'][rel]],'Probe/WPT native identity')
        rr=probe['observations'][0]['rows'];require(len(rr)==56,'Probe roster')
        pd={identity(r):r for r in rr};require(len(pd)==56,'Unique probe names');probes[variant]=pd
        selected=[r for r in rr if r['kind']=='non-flex'];require(len(selected)==8,'Nonflex roster')
        result=[]
        for r in selected:
            edge='right' if r['axis']=='horizontal' else 'bottom';large=r['basis']>1000
            expected=100 if not large or variant in ['integer-only','both'] else 100.015625 if variant=='baseline' else 100.01666259765625
            require(r['item']['bounding'][edge]==expected,'Probe numeric expectation')
            require(r['marker']['bounding'][edge]==100 and not r['scalar']['missing'],'Marker/RO calibration')
            result.append({'case':identity(r),'edge':r['item']['bounding'][edge]})
        probe_summary[variant]=result
        summaries[variant]={'new':dict(Counter(r['status'] for r in new)),'existing_subtests':dict(Counter(r['status'] for r in rows if r['test']!=new_test)), 'file_outcomes':dict(Counter(r['status'] for r in tail)), 'exit':run['exit'],'stable_pins':len(run['before'])}
    base=outcomes['baseline'];base_ends=ends['baseline'];content_rect_changes={}
    for v in variants[1:]:
        require(base.keys()==outcomes[v].keys() and base_ends.keys()==ends[v].keys(),'Identical outcome keys')
        require(all(status(base[k])==status(outcomes[v][k]) for k in base if k[0]!=new_test),'Existing subtests unchanged')
        require(all(status(base_ends[k])==status(ends[v][k]) for k in base_ends),'All harness/reftest outcomes unchanged')
        changed={k for k in runs['baseline']['before'] if runs['baseline']['before'][k]!=runs[v]['before'][k]}
        expected={'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
        if v in ['dom-only','both']:expected.add('dom/base/DOMRect.cpp')
        if v in ['integer-only','both']:expected.add('layout/base/nsLayoutUtils.cpp')
        require(changed==expected,'Unexpected cross-variant pin change')
        require(probes[v].keys()==probes['baseline'].keys(),'Probe identity roster')
        changes=[]
        for k in probes[v]:
            a=probes['baseline'][k]['scalar'];b=probes[v][k]['scalar']
            require(a.keys()==b.keys()=={'values','missing'} and a['missing']==b['missing']==[], 'RO callback completeness')
            require(a['values'].keys()==b['values'].keys(), 'RO target roster')
            row_changes={}
            for target in a['values']:
                x=a['values'][target];y=b['values'][target]
                require(x.keys()==y.keys()=={'borderBoxSize','contentBoxSize','contentRect'}, 'RO field roster')
                require(all(x[f]==y[f] for f in ['borderBoxSize','contentBoxSize']), 'RO size arrays changed')
                if x['contentRect']!=y['contentRect']:
                    row_changes[target]={'before':x['contentRect'],'after':y['contentRect']}
                if v=='both':
                    require(y['contentRect']==probes['dom-only'][k]['scalar']['values'][target]['contentRect'], 'DOM-only/both contentRect difference')
            if row_changes:changes.append({'case':k,'targets':row_changes})
        require(len(changes)==(0 if v=='integer-only' else 28), 'ContentRect changed-row inventory')
        content_rect_changes[v]=changes
    for f in ['getBoundingClientRect-svg.html.ini','range-client-rects-surrogate-indexing.html.ini']:
        text=read(RUN/'baseline/inputs/testing/web-platform/meta/css/cssom-view'/f).decode()
        test='/css/cssom-view/'+f.removesuffix('.ini')
        failures=[r for k,r in base.items() if k[0]==test and r['status']=='FAIL']
        require(len(failures)==1 and ('  ['+failures[0]['subtest']+']\n    expected: FAIL') in text,'Named existing expected failure metadata')
    require(load(RUN/'restore-build.json')['exit']==0,'Restore build');read(RUN/'restore-build.log')
    load(RUN/'BEFORE.json');load(RUN/'RESTORED.json');load(RUN/'INPUTS.json');load(RUN/'TESTS.json')
    result={'status':'PASS','variants':summaries,'source_variants':sources,'nonflex_numeric_observations':probe_summary,'all56_RO_size_arrays_unchanged':True,'RO_contentRect_changes':content_rect_changes,'full_safe_origin':'OPEN','native_path_trace':'not supplied'}
    emit('RESULT.json',result)
    emit('INPUT-PINS.json',PINS)
    print(json.dumps({'status':'PASS','inputs':len(PINS),'variants':summaries}))

if __name__=='__main__':main()
