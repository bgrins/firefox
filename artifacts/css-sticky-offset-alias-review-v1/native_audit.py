import hashlib,json,re
from pathlib import Path

def require(ok,message):
    if not ok:raise ValueError(message)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(root):
    fix=root/'native-evidence'
    patch=(fix/'fix-candidate-v1.patch').read_text()
    require(sha(fix/'fix-candidate-v1.patch')=='4be581a216c84dc29887c54ee719edcafae40482b36926a2e8c03c0234e6cf0e','patch identity')
    parts=patch.split('--- ')[1:]
    require(len(parts)==2,'two-file patch')
    hunks=[]
    for part in parts:
        lines=part.splitlines(keepends=True)
        require(lines[1].startswith('+++ '),'new file header')
        body=lines[3:]
        require(lines[2].startswith('@@ ') and all(x[0] in ' +-' for x in body),'one hunk')
        old=''.join(x[1:] for x in body if x[0] in ' -')
        new=''.join(x[1:] for x in body if x[0] in ' +')
        hunks.append((lines[0].strip(),lines[1][4:].strip(),old,new))
    native,wpt=hunks
    require(native[:2]==('a/layout/generic/StickyScrollContainer.cpp','b/layout/generic/StickyScrollContainer.cpp'),'native path')
    testpath='testing/web-platform/tests/css/css-position/sticky/position-sticky-explicit-inset-auto-alias.html'
    require(wpt[:2]==('/dev/null','b/'+testpath) and not wpt[2],'WPT path')
    before=(root/'capsule/inputs/before.cpp').read_text()
    candidate=(root/'capsule/inputs/candidate.cpp').read_text()
    formatted=(root/'capsule/inputs/candidate-formatted.cpp').read_text()
    require(before.count(native[2])==1 and before.replace(native[2],native[3])==candidate,'exact retained native repair')
    require(re.sub(r'\s+','',candidate)==re.sub(r'\s+','',formatted),'format-only transfer')
    actual_tested=(fix/'candidate.cpp').read_text()
    actual_formatted=(fix/'candidate-formatted.cpp').read_text()
    receipt=json.loads((fix/'CANDIDATE.json').read_text())
    require(sha(fix/'candidate.cpp')==receipt['candidate_sha256'],'actual tested identity')
    require(sha(fix/'before.cpp')==receipt['before_sha256'],'actual before identity')
    require(before==(fix/'before.cpp').read_text() and formatted==actual_formatted,'native/formal endpoints')
    sig='static nscoord ComputeStickySideOffset('
    def helper(t):
        start=t.index(sig);return t[start:t.index('\n}\n',start)+2]
    require(before.replace(helper(before),helper(actual_tested))==actual_tested,'tested helper-only delta')
    require(actual_tested.replace(helper(actual_tested),helper(actual_formatted))==actual_formatted,'format helper-only delta')
    require(re.sub(r'\s+','',helper(actual_tested))==re.sub(r'\s+','',helper(actual_formatted)),'actual token transfer')
    require(json.loads((fix/'BUILD-v1.json').read_text())['compiled_source_sha256']==sha(fix/'candidate.cpp'),'compiled tested identity')
    base_results=[]
    for b in json.loads((root/'bases/BASES.json').read_text()):
        f=root/'bases'/(b['base']+'.cpp');require(sha(f)==b['sha256'],'base hash')
        text=f.read_text();require(text.count(native[2])==1,'base context')
        applied=text.replace(native[2],native[3]);require(applied.count(native[3])==1 and applied.replace(native[3],native[2])==text,'exact reverse')
        signature='static nscoord ComputeStickySideOffset('
        def body(s):
            start=s.index(signature);end=s.index('\n}\n',start)+2;return s[start:end]
        require(body(applied)==body(candidate),'exact repaired helper')
        require(text.replace(body(text),body(candidate))==applied,'only helper changed')
        base_results.append({'base':b['base'],'apply_and_reverse':True,'only_helper_changed':True})
    runs={}
    for phase in ['baseline-wpt-v2','candidate-wpt-v2','regressions-wpt-v1']:
        d=fix/phase;r=json.loads((d/'RUN.json').read_text())
        require(r['before']==r['after'] and r['stable_pins'] and r['complete'],'stable completed run')
        for name,h in r['before'].items():
            f=d/'inputs'/name
            if f.exists():require(sha(f)==h,'retained input '+name)
            elif h is None:require(not f.exists(),'absent metadata')
            else:require(name.startswith('objdir-full.noindex/'),'missing retained source '+name)
        raw=[json.loads(x) for x in (d/'raw.json').read_text().splitlines()]
        rows=[x for x in raw if x.get('action')=='test_status']
        ends=[x for x in raw if x.get('action')=='test_end']
        require(rows==r['rows'],'raw status/receipt match')
        require(all(x.get('known_intermittent',[])==[] for x in rows+ends),'no intermittent allowance')
        runs[phase]={'receipt':r,'rows':rows,'ends':ends}
        if phase!='regressions-wpt-v1':
            require((d/'inputs'/testpath).read_text()==wpt[3],'exact patch WPT')
    a,b=[runs[n] for n in ['baseline-wpt-v2','candidate-wpt-v2']]
    require(set(a['receipt']['before'])==set(b['receipt']['before']),'pin roster')
    changed=[n for n in a['receipt']['before'] if a['receipt']['before'][n]!=b['receipt']['before'][n]]
    require(changed==['layout/generic/StickyScrollContainer.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'],'cross-run differences')
    labels=['0px','50px','1000px','10000000px','17895696px','17895697px','17895698px','1000000000px','calc(10000000px + 10000000px)','2000000000%']
    numbers=[0,50,1000,10000000,17895696,17895697,17895698,1000000000,20000000,2000000000]
    oracle={}
    for side in ['top','right','bottom','left']:
        near=side in ['top','left']
        for label,inset in zip(labels,numbers):
            for scroll in [0,100]:
                name=f'{side}: {label}, scroll {scroll}'
                expected=min(990,max(0,scroll+inset))-scroll if near else max(0,min(900,scroll+max(0,90-inset)))-scroll
                failure=label in labels[6:]
                old=(-scroll if near else 900-scroll) if failure else expected
                oracle[name]={'expected':expected,'baseline_position':old,'baseline_status':'FAIL' if failure else 'PASS'}
    for phase,run in [('baseline',a),('candidate',b)]:
        rows=run['rows'];require(len(rows)==80 and len({x['subtest'] for x in rows})==80,'80 unique rows')
        require({x['subtest'] for x in rows}==set(oracle),'independent identity roster')
        for row in rows:
            prediction=oracle[row['subtest']];want=prediction['baseline_status'] if phase=='baseline' else 'PASS'
            require(row['status']==want,'expected status')
            if want=='FAIL':
                require(row.get('expected')=='PASS','no metadata laundering')
                m=re.search(r'expected ([\d.e+-]+).*?got ([\d.e+-]+)',row['message'])
                require(m and float(m[1])==prediction['expected'] and float(m[2])==prediction['baseline_position'],'observed failure coordinate')
        require(len(run['ends'])==1 and run['ends'][0]['status']=='OK','harness completion')
    reg=runs['regressions-wpt-v1'];require(len(reg['rows'])==1328 and all(x['status']=='PASS' for x in reg['rows']),'regression rows')
    require(sum(x['status']=='PASS' for x in reg['ends'])==3 and sum(x['status']=='OK' for x in reg['ends'])==5,'regression completion')
    require(json.loads((fix/'BUILD-v1.json').read_text())['exit']==0,'build receipt')
    return {'status':'pass','standalone_bases':base_results,'paired_rows':80,'improvements':32,'unchanged_passes':48,'regression_subtests':1328,'regression_reftests':3,'changed_pins':changed,'oracle':oracle}

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    result=audit(root)
    (root/'NATIVE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='oracle'}))
