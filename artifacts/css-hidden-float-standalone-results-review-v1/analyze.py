import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse, collections, hashlib, json, math, statistics
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument("--phase",choices=["baseline","float-only"],required=True)
parser.add_argument("--runtime-files-sha")
args=parser.parse_args()
here=Path(__file__).resolve().parent
root=here.parents[1]
runtime=root/"artifacts/css-hidden-float-standalone-runtime-v1"
def read(path):return json.loads(path.read_text())
def need(ok,why):
    if not ok:raise RuntimeError(why)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def authenticate(directory,manifest):
    for name,pin in manifest.items():
        p=directory/name
        need(not Path(name).is_absolute() and ".." not in Path(name).parts and not p.is_symlink() and p.is_file() and sha(p)==pin,"Payload "+name)
def finite(n):return isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n)
def rect(i,width):return [10+(i%2)*width/2,10+(i//2)*16,width/2,8]
state=read(runtime/"STATE.json")
need(not state['status'].startswith('measuring '),'Do not analyze during measurements')
need(sha(runtime/'INPUTS.json')=='302161a4e78278e2be91d46c32e82b4758c68e27b833cff9d16c5cd03b6bfce9','Prepared inputs')
inputs=read(runtime/'INPUTS.json')
need(inputs['draft_sha256']==sha(runtime/'DRAFT-FILES.json')=='b971fe4a05a9e8dae4929c8ede80850f665333c6d1176574c84649822b556834','Enabled draft')
authenticate(runtime,inputs['payload_pins']);authenticate(root,inputs['external_pins'])
ready=root/'artifacts/css-hidden-float-standalone-readiness-v1'
need(sha(ready/'FILES.json')=='c1d9ee1849103ea922f5ea4dad5dd4b87f572e4e6bdc16eae90c5c990278133d','Readiness seal')
authenticate(ready,read(ready/'FILES.json'))
old=read(ready/'disabled-DRAFT-FILES.json');new=read(ready/'enabled-DRAFT-FILES.json')
need(set(old)==set(new) and {k for k in old if old[k]!=new[k]}=={'CONFIG.json','README.md'},'Enabled changes')
old_config=read(ready/'disabled-CONFIG.json');old_config['ready_for_preparation']=True
need(old_config==read(ready/'enabled-CONFIG.json')==read(runtime/'CONFIG.json'),'Enabled CONFIG only readiness')
c=read(runtime/'CONFIG.json');phase=args.phase;record=state['phases'][phase]
need(record.get('cost',{}).get('phase_join_verified') is True,'Phase not complete')
need(record['build_exit']==read(runtime/(phase+'-build.json'))['exit']==0,'Successful phase build')
run=read(runtime/phase/'RUN.json')
events=[json.loads(line) for line in (runtime/phase/'raw.json').read_text().splitlines()]
rows=[e for e in events if e.get('action')=='test_status'];ends=[e for e in events if e.get('action')=='test_end']
need(rows==run['rows'] and ends==run['ends'] and len(rows)==12 and len(ends)==2,'Raw WPT receipt join')
need(len([e for e in events if e.get('action')=='suite_end'])==1,'WPT suite end')
expected={(test,name) for test,names in c['expected_subtests'].items() for name in names}
actual={(r['test'],r['subtest']):(r['status'],r.get('message')) for r in rows}
need(set(actual)==expected and len(actual)==12,'Exact12 keys')
need({e['test'] for e in ends}==set(c['expected_subtests']) and all(e['status']=='OK' for e in ends),'Two OK harness ends')
for test,names in c['expected_subtests'].items():need([r['subtest'] for r in rows if r['test']==test]==names,'Exact WPT order')
oracle=read(runtime/'EXPECTED-OUTCOMES.json')['phases'][phase]
need(all(list(actual[(r['test'],r['subtest'])]) in r['allowed'] for r in oracle),'Exact expected status/first-failure message')
need(run['complete'] and run['before']==run['after'] and run['exit'] in [0,1],'Complete stable WPT')
source_pins=dict(c['baseline_guard_pins'])
for name,payload in c['phases'][phase].items():source_pins[name]=sha(runtime/payload)
binaries=['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
resources=set(c['run_tests']+c['support_paths'])
for test in c['run_tests']:
    meta=Path('testing/web-platform/meta')/Path(test).relative_to('testing/web-platform/tests')
    resources.add(str(meta)+'.ini')
    resources.update(str(parent/'__dir__.ini') for parent in meta.parents if parent==Path('testing/web-platform/meta') or Path('testing/web-platform/meta') in parent.parents)
need(set(run['before'])==set(source_pins)|set(binaries)|resources,'Exact WPT pin roster')
need(all(run['before'][n]==h for n,h in source_pins.items()),'All29 phase sources')
need(all(run['before'][n]==inputs['resource_pins'][n] for n in resources),'WPT historical resources')
captured={str(f.relative_to(runtime/phase/'inputs')):sha(f) for f in (runtime/phase/'inputs').rglob('*') if f.is_file()}
need(captured=={n:h for n,h in run['before'].items() if h is not None and n not in binaries},'Closed captured source/resource roster')
cost_dir=root/c['cost']['directory'];manifest=read(cost_dir/'FILES.json')
need(sha(cost_dir/'FILES.json')==c['cost']['manifest_sha256']=='0f3412d79952ca54d0d793dcae2e1a26c86b14187d04bc8ec04289d91a06ba8c','Cost fixture')
authenticate(cost_dir,manifest)
out=runtime/(phase+'-cost');cost=read(out/'RESULT.json');summary=read(out/'SUMMARY.json')
joined={str((root/n).resolve()):run['after'][n] for n in c['guard_sources']+binaries}
for n in ['probe.html','benchmark.js','CONFIG.json','run.py','validate.py','cleanup.py']:joined[str(cost_dir/n)]=manifest[n]
need(cost['before']==cost['after']==read(out/'BEFORE.json')==joined==record['cost']['expected_pins'],'Cost all source/binary/input joins')
need(cost['label']==phase and cost['stable'] and cost['terminal'] and cost['noLiveGroup'] and cost['profileRemoved'] and not cost['failure'] and not cost['cleanupErrors'],'Cost terminal cleanup')
need(record['cost']['exit']==read(runtime/(phase+'-cost-run.json'))['exit']==0,'Cost exit')
for n in ['BEFORE.json','RESULT.json','SUMMARY.json']:need(record['cost'][n+'_sha256']==sha(out/n),'Stored cost receipt hash')
need(len(cost['observations'])==1,'One cost observation')
o=cost['observations'][0];cfg=read(cost_dir/'CONFIG.json')
need(o['complete'] and o['config']==cfg and o['label']==phase,'Cost observation identity')
configs=[(kind,state,n) for kind in ['direct','inline-nested'] for state in ['visible','hidden'] for n in [1,32,128]]
need(cfg['warmup_rounds']==1 and cfg['measured_rounds']==5 and cfg['iterations']==16 and cfg['hot_reads']==16384,'Exact workload config')
progress=[{'stage':'script-start'},{'stage':'config-ready','label':phase},{'stage':'fixture-start'}]
for round_no in range(-1,5):
    for slot in range(12):
        ordinal=(slot+round_no+1)%12;kind,visibility,count=configs[ordinal]
        for stage in ['batch-begin','batch-end']:progress.append({'stage':stage,'round':round_no,'slot':slot,'ordinal':ordinal,'kind':kind,'state':visibility,'count':count})
progress.append({'stage':'result-ready','rows':60})
progress=[{'sequence':i,**e} for i,e in enumerate(progress)]
requests=[json.loads(line) for line in (out/'REQUESTS.jsonl').read_text().splitlines()]
need([e['value'] for e in requests if e.get('event')=='progress-persisted']==progress and cost['progressReceipts']==len(progress)==148,'Exact progress')
need(len(o['rows'])==60,'Cost60 raw rows')
bad={};geometry={};samples={};queries=0
for position,row in enumerate(o['rows']):
    round_no,slot=divmod(position,12);ordinal=(slot+round_no+1)%12;kind,visibility,count=configs[ordinal]
    group=f'{kind}/{visibility}/{count}'
    need([row[k] for k in ['round','slot','ordinal','kind','state','count']]==[round_no,slot,ordinal,kind,visibility,count],'Cost row order')
    need(row['calibration']==[{'width':w,'rects':[rect(i,w) for i in range(count)]} for w in [160,168,160]],'Visible calibration')
    need(row['hiddenOuter']==[10,10,160,64] and row['outers']==[[10,10,168 if i%2==0 else 160,64] for i in range(16)],'Outer flush')
    for key in ['restored','cleanVisible','cleanReady','cleanAfter']:need(row[key]==[rect(i,160) for i in range(count)],'Restored/clean calibration')
    need(set(row['times'])=={'prepare','first','repeat'},'Timing buckets')
    values={}
    for key,ts in row['times'].items():
        need(len(ts)==16 and all(finite(t) and t>=0 for t in ts),'Finite timings');values[key]=sum(ts)
    need(len(row['observations'])==32,'Recovery read count')
    counts=geometry.setdefault(group,{'first':{'correct':0,'incorrect':0},'repeat':{'correct':0,'incorrect':0}})
    for j,ob in enumerate(row['observations']):
        iteration=j//2;bucket=['first','repeat'][j%2];width=168 if iteration%2==0 else 160
        need([ob[k] for k in ['bucket','iteration','index','width']]==[bucket,iteration,count-1,width],'Recovery read identity')
        need(len(ob['rect'])==4 and all(finite(x) for x in ob['rect']) and min(ob['rect'][2:])>=0,'Finite recovery geometry')
        correct=ob['rect']==rect(count-1,width)
        counts[bucket]['correct' if correct else 'incorrect']+=1
        if not correct:bad[group]=bad.get(group,0)+1
    need(len(row['hotRows'])==2,'Two clean batches')
    for hot,bucket in zip(row['hotRows'],['hotSame','hotCycle']):
        total=16384*sum(rect(count-1,160)) if bucket=='hotSame' else (16384//count)*sum(sum(rect(i,160)) for i in range(count))
        need(hot['bucket']==bucket and hot['reads']==16384 and hot['checksum']==total and hot['mismatches']==0 and hot['firstMismatch'] is None,'Clean geometry/checksum')
        need(finite(hot['elapsedMs']) and hot['elapsedMs']>=0,'Finite hot timing');values[bucket]=hot['elapsedMs']
    queries+=32+32768
    group_samples=samples.setdefault(group,{k:[] for k in values})
    for key,value in values.items():group_samples[key].append(value)
need(queries==summary['queryReads']==1968000 and summary['measuredRows']==60,'Exact query count')
need(summary['geometryMismatches']==sum(bad.values()) and summary['recoveryMismatchesByGroup']==bad and summary['recoveryGeometryByGroup']==geometry and summary['hotMismatchesByGroup']=={},'Independent geometry recount')
need(summary['recoveryGeometryCorrect']==(not bad) and summary['cleanGeometryCorrect'] is True,'Geometry gates')
need(not any('/visible/' in g for g in bad) and (phase=='baseline' or not bad),'Required phase geometry')
dists={g:{k:{'samplesMs':v,'medianMs':statistics.median(v),'minMs':min(v),'maxMs':max(v),'p90Ms':max(v),'zeroSamples':v.count(0)} for k,v in buckets.items()} for g,buckets in samples.items()}
need(summary['groups']==dists,'Independent distribution recount')
answer={'status':'AUTHENTICATED_PHASE','phase':phase,'WPT':dict(collections.Counter(r['status'] for r in rows)),'raw_subtests':12,'harness_OK':2,'sources':29,'resources':len(resources),'binaries':2,'captured_inputs':len(captured),'cost_rows':60,'cost_progress':148,'cost_queries':queries,'cost_recovery_mismatches':bad,'cost_clean_mismatches':0,'cost_distributions':dists,'restoration_authenticated':False,'native_acceptance':False}
if args.runtime_files_sha:
    need(sha(runtime/'FILES.json')==args.runtime_files_sha,'Runtime final seal')
    sealed=read(runtime/'FILES.json');authenticate(runtime,sealed)
    actual_files={str(p.relative_to(runtime)) for p in runtime.rglob('*') if p.is_file()}
    need(actual_files==set(sealed)|{'FILES.json'},'Final runtime closed roster')
    need(state['status']=='terminal' and state['restored'] and state['restore_build_exit']==0 and not state['recovery_errors'] and 'failure' not in state,'Successful historical restoration')
    need(read(runtime/'BEFORE.json')==read(runtime/'FINAL.json')==inputs['before'],'Historical original/final/prepared equality')
    receipt=read(runtime/'ROOT-FINAL-CHECK.json')
    need(receipt['status']=='PASS' and receipt['source_guards']==29 and receipt['staged_research_paths']==925 and receipt['head']==inputs['before']['head'],'Root final receipt identity')
    need(receipt['inputs_sha256']==sha(runtime/'INPUTS.json') and receipt['state_sha256']==sha(runtime/'STATE.json') and receipt['final_sha256']==sha(runtime/'FINAL.json'),'Root historical receipt hashes')
    need(receipt['live_snapshot_equals_before_final_inputs'] and receipt['existing_tests_preserved']==9 and receipt['owned_temporary_tests_absent'] and receipt['resource_pins_stable'] and receipt['restore_build_exit']==0,'Root immediate restoration receipt')
    answer['root_immediate_restoration_receipt_authenticated']=True
    text=(runtime/'restore-build.log').read_text()
    answer['restoration_authenticated']=True
    answer['runtime_files_sha256']=args.runtime_files_sha
    answer['runtime_payloads']=len(sealed)
    answer['restore_log_monitor_KeyError']="KeyError: 'export'" in text
    answer['restore_log_success_marker']='Your build was successful!' in text
(here/(phase+'-ANALYSIS.json')).write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps({k:v for k,v in answer.items() if k!='cost_distributions'}))
