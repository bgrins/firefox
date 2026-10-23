import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('requires -I -S without optimization')
sys.dont_write_bytecode=True
import collections
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'
def need(ok,msg):
    if not ok: raise SystemExit('REJECT: '+msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((E/'CONFIG.json').read_text())
owned={n.removeprefix('testing/web-platform/tests'):n for n in config['tests']}
phases=('baseline','candidate','original-key','original-key-candidate')
expected_counts=((621,35),(655,1),(629,27),(647,9))
rows={};ends={};pins={};summary={}
for phase,(passes,fails) in zip(phases,expected_counts):
    run=json.loads((E/phase/'RUN.json').read_text())
    need(run['complete'] and run['exit']==1,'phase completion')
    need(run['before']==run['after'] and len(run['before'])==70,'stable pins')
    pins[phase]=run['before']
    for n,h in run['before'].items():
        if h is not None and not n.startswith('objdir-full.noindex/'):
            need(sha(ROOT/'blobs'/h)==h,'input blob:'+n)
    need(json.loads((E/(phase+'-build.json')).read_text())['exit']==0,'build')
    need(json.loads((E/(phase+'-wpt.json')).read_text())['exit']==1,'WPT exit')
    events=[json.loads(l) for l in (E/phase/'raw.json').read_text().splitlines()]
    sub=[r for r in events if r['action']=='test_status']
    end=[r for r in events if r['action']=='test_end']
    need(run['rows']==sub and run['ends']==end,'RUN rows exactly raw')
    need(sum(r['action']=='suite_end' for r in events)==1,'suite complete')
    need(len(sub)==656 and len(end)==15,'observation count')
    need(all(r['test'] in owned and r['status'] in ('PASS','FAIL') for r in sub),'subtest domain')
    need({r['test'] for r in end}==set(owned) and len({r['test'] for r in end})==len(end),'file roster')
    need(collections.Counter(r['status'] for r in end)=={'OK':14,'PASS':1},'harness/reftest statuses')
    need(collections.Counter(r['status'] for r in sub)=={'PASS':passes,'FAIL':fails},'counts')
    keyed={(r['test'],r['subtest']):(r['status'],r.get('message')) for r in sub}
    need(len(keyed)==len(sub),'duplicate subtest')
    for test,names in config['expected_new_subtests'].items():
        need([r['subtest'] for r in sub if r['test']==test]==names,'new test roster')
    rows[phase]=keyed
    ends[phase]={r['test']:(r['status'],r.get('message')) for r in end}
    summary[phase]={'pass':passes,'fail':fails,'files':15,'harness_ok':14,'reftest_pass':1,'stable_pins':70,'failures':[{'test':k[0],'subtest':k[1],'status':v[0],'message':v[1]} for k,v in keyed.items() if v[0]=='FAIL']}
need(all(set(rows[p])==set(rows['baseline']) for p in phases),'cross phase roster')
need(all(ends[p]==ends['baseline'] for p in phases),'unchanged ends')
pairs=[]
for before,after,fixes in [('baseline','candidate',34),('original-key','original-key-candidate',18)]:
    changed=[]
    for k,v in rows[before].items():
        w=rows[after][k]
        if v!=w: changed.append({'test':k[0],'subtest':k[1],'before':v,'after':w})
    need(len(changed)==fixes and all(r['before'][0]=='FAIL' and r['after'][0]=='PASS' for r in changed),'only intended improvements')
    diff=[n for n in pins[before] if pins[before][n]!=pins[after][n]]
    need(set(diff)=={'layout/generic/nsFlexContainerFrame.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'},'pair source/binary delta')
    old=(ROOT/'blobs'/pins[before]['layout/generic/nsFlexContainerFrame.cpp']).read_text()
    new=(ROOT/'blobs'/pins[after]['layout/generic/nsFlexContainerFrame.cpp']).read_text()
    marker='  if (HidesContentForLayout()) {\n'
    need(old.count(marker)==1 and new==old.replace(marker,marker+'    MarkPrincipalChildrenDirty();\n',1),'one-line candidate delta')
    pairs.append({'before':before,'after':after,'fixed':fixes,'unchanged_status_message':656-fixes,'regressions':0,'changed_pins':diff,'improvements':changed})
commonfail=set(k for k,v in rows['candidate'].items() if v[0]=='FAIL')
need(len(commonfail)==1 and all(rows[p][k]==rows['candidate'][k] for p in phases for k in commonfail),'same residual failure')
removed=[n for n in pins['baseline'] if pins['baseline'][n]!=pins['original-key'][n]]
need(set(removed)=={'layout/generic/nsFlexContainerFrame.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'},'key-removal pins')
before=json.loads((E/'BEFORE.json').read_text())
final=json.loads((E/'FINAL.json').read_text())
state=json.loads((E/'STATE.json').read_text())
need(before==final and len(final['sources'])==25,'restored HEAD/index/source receipt')
need(state['status']=='terminal' and state['restored'] and state['restore_build_exit']==0 and not state['recovery_errors'] and 'failure' not in state,'terminal restoration')
need(json.loads((E/'wpt-lint.json').read_text())['exit']==0,'lint')
result={'outcome':'PASS_FOUR_PHASE_RECOUNT_WITH_RESIDUAL_FAILURE','phases':summary,'pairs':pairs,'whole_upstream_runtime':False,'restoration':{'BEFORE_equals_FINAL':True,'source_pins':25,'restore_build_exit':0,'recovery_errors':[],'historical_head':final['head'],'historical_index_diff_sha256':final['index_diff_sha256']}}
print(json.dumps(result,indent=2))
