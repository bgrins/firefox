import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[1]
runtime=root/'artifacts/css-hidden-mathml-trace-runtime-v3'
proposal=root/'artifacts/css-hidden-mathml-repair-proposal-v2'
draft=root/'artifacts/css-hidden-mathml-query-draft-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError(why)
def read(p):return json.loads(p.read_text())
raw_path=runtime/'marked/raw.json'
need(sha(raw_path)=='284842c0b57ecd30d30a3f10f44fc6bc86d00d6f54dec4791cc0773b4f2f66ae','Raw trace pin')
need(sha(proposal/'FILES.json')=='88f80c45dbcc0e3828d42be9958a277661fdb315988e795bafdfbaaf17919918','Proposal pin')
for name,pin in read(proposal/'FILES.json').items():need(sha(proposal/name)==pin,'Proposal '+name)
raw=[json.loads(line) for line in raw_path.read_text().splitlines()]
native=[];results=[];phases=[]
for i,e in enumerate(raw):
    data=e.get('data','')
    if data.startswith('HMQ_NATIVE '):
        fields=[v.split('=',1) for v in data[len('HMQ_NATIVE '):].split()]
        need(all(len(v)==2 for v in fields) and len(dict(fields))==len(fields),'Native field syntax')
        native.append({'raw_event':i,'process':e['process'],**dict(fields)})
    if data.startswith('console.log: '):
        decoded=json.loads(data[len('console.log: '):])
        if decoded.startswith('HMQ_RESULT '):results.append({'raw_event':i,**json.loads(decoded[len('HMQ_RESULT '):])})
        if decoded.startswith('HMQ_PHASE '):phases.append(decoded)
need(native==read(runtime/'recount/NATIVE.json') and len(native)==2210,'Independent native extraction')
summary=read(runtime/'recount/SUMMARY.json')
need(results==summary['results'] and len(results)==8 and len(phases)==256,'Independent copied results/phases')
rows=[e for e in raw if e.get('action')=='test_status']
need(len(rows)==8 and [e['status'] for e in rows]==['PASS','FAIL','PASS','FAIL','PASS','PASS','PASS','PASS'],'Diagnostic statuses')
ends=[e for e in raw if e.get('action')=='test_end'];need(len(ends)==1 and ends[0]['status']=='OK','Harness OK')
joins=[]
for case,selected in [(1,'mrow'),(3,'mspace')]:
    prefix=f'mathml-trace-c{case}-target-';phase=f'c{case}:mutate:outer'
    outer=[e for e in native if e['phase']==phase and e['id']==prefix+'mrow']
    def one(event,records=outer):
        found=[e for e in records if e['event']==event]
        need(len(found)==1,'Unique event '+event);return found[0]
    ordered=[one(e) for e in ['before-input','after-input','math-enter','math-hidden-return','after-child-reflow','place-child','publish-before','publish-after','did-enter','did-hidden-return']]
    need([e['raw_event'] for e in ordered]==sorted(e['raw_event'] for e in ordered),'Native ordering')
    row=ordered[0];rowptr=row['frame'];leafptr=row['kid'];ownerptr=row['parent']
    need(all(e['frame']==rowptr and e['parent']==e['inflow']==ownerptr and e['kid']==leafptr and e['primary']=='1' for e in ordered),'Within-case row identity')
    need(all(e[k]=='0' for e in ordered for k in ['dirty','dirtyChildren','subtree','kidDirty','kidSubtree','forcing','parentForcing']),'Clean native row/leaf throughout skip/publication')
    need(all(e['hiddenParent']=='1' for e in ordered),'Same hidden predicate')
    need(any(e['id']==prefix+'mspace' and e['frame']==leafptr and e['primary']=='1' for e in native if e['phase'].startswith(f'c{case}:')),'Leaf identity in same case')
    need(one('before-input')['rect']=='3600,0,2400,960' and one('publish-after')['rect']=='3600,0,0,0','Zero rectangle publication')
    cached=[e for e in outer if e['event']=='cache-output'];need(cached and all(e['size']=='0,0' and e['ascent']=='0' for e in cached),'Zero cached output')
    queries=[]
    for step in ['first','repeat']:
        relevant=[e for e in native if e['phase']==f'c{case}:mutate:{step}' and e['id']==prefix+selected]
        enter=one('query-enter',relevant);reject=one('query-clean-reject',relevant)
        need(enter['frame']==reject['frame']==(rowptr if selected=='mrow' else leafptr) and enter['raw_event']<reject['raw_event'],'Query frame/order')
        need(enter['primary']==reject['primary']=='1' and all(e[k]=='0' for e in [enter,reject] for k in ['dirty','dirtyChildren','subtree']),'Clean queried primary frame')
        need(not any(e['event']=='query-admitted' for e in relevant),'No admitted selected query')
        queries.extend([enter,reject])
    need(all(e['process']==row['process'] for e in ordered+cached+queries),'Same-process frame joins')
    observed=next(x for x in results if x['index']==case)
    mutate=next(x for x in observed['rows'] if x['stage']=='mutate')
    need(mutate['visible']==[30,10,40,16] and mutate['first']==mutate['repeat']==([70,25,0,0] if case==1 else [70,25,40,16]),'Copied geometry join')
    joins.append({'case':case,'selected':selected,'process':row['process'],'row_frame':rowptr,'leaf_frame':leafptr,'owner_frame':ownerptr,'ordered_row_events':ordered,'cached_events':cached,'query_events':queries,'observed_mutate':mutate})
base=(draft/'source/layout/mathml/nsMathMLContainerFrame.cpp').read_text();candidate=(proposal/'candidate-nsMathMLContainerFrame.cpp').read_text()
needle='  if (IsHiddenByContentVisibilityOfInFlowParentForLayout()) {\n    return;\n  }\n\n  MarkInReflow();'
need(base.count(needle)==1 and candidate==base.replace(needle,needle.replace('    return;','    MarkSubtreeDirty();\n    return;')),'Only one native call')
original=(draft/'hidden-mathml-owner-queries.html').read_text();final=(proposal/'hidden-mathml-owner-queries.html').read_text()
original=original.replace('window.hiddenMathMLQueryResults = [];\n','').replace('    window.hiddenMathMLQueryResults.push(result);\n','')
def split_cases(text):
    before,rest=text.split('const cases = ',1);cases,after=rest.split(';',1)
    return before,json.loads(cases),after
before,cases,after=split_cases(original);fbefore,fcases,fafter=split_cases(final)
need(before==fbefore and after==fafter and fcases==[c for c in cases if c['owner']=='internal-mrow'] and len(fcases)==4,'Only independent case partition and unused global removal')
answer={'status':'TRACE_SUPPORTS_MINIMAL_BRANCH_EXPERIMENT','raw_sha256':sha(raw_path),'proposal_FILES_sha256':sha(proposal/'FILES.json'),'native_records':len(native),'phase_records':len(phases),'copied_results':len(results),'diagnostic_PASS':6,'diagnostic_FAIL':2,'same_case_only_pointer_joins':True,'cases':joins,'candidate_native_sha256':sha(proposal/'candidate-nsMathMLContainerFrame.cpp'),'candidate_WPT_sha256':sha(proposal/'hidden-mathml-owner-queries.html'),'candidate_tested':False,'root_block_standalone_outcome':'not measured','restoration_authenticated':False,'native_accepted':False}
(here/'TRACE-JOIN.json').write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps({k:v for k,v in answer.items() if k!='cases'}))
