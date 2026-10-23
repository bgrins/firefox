import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import collections
import hashlib
import json
import math
import statistics
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--runtime', type=Path, required=True)
parser.add_argument('--prior', type=Path, required=True)
parser.add_argument('--phases', nargs='+', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if args.output.exists():
    raise SystemExit('Fresh output required')
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok, message):
    if not ok:
        raise RuntimeError(message)

need(sha(args.runtime/'DRAFT-FILES.json') == '88cb92504c508a51837d5ce9d7c2957fe9d500d41e0071334d369cf56ed7b9ee', 'Wrong reviewed draft')
draft = read(args.runtime/'DRAFT-FILES.json')
for name,pin in draft.items():
    need(sha(args.runtime/name)==pin, 'Changed draft '+name)
need(sha(args.runtime/'INPUTS.json') == '2cd6a454265161de3d8b948241f0b1b97e88199ea4a6b9f1493fda8e8ee16b88', 'Wrong prepared inputs')
need(sha(args.prior/'FILES.json') == '86e59d39179a46b36f0b3c935b03cbd3b106dd1546d96286ea8ef0b0f31f4d07', 'Wrong prior runtime')
prior_manifest = read(args.prior/'FILES.json')
inputs = read(args.runtime/'INPUTS.json')
config = read(args.runtime/'CONFIG.json')
roles = {
    'baseline': ('flex-baseline.cpp','absolute-baseline.cpp'),
    'principal-only': ('flex-principal.cpp','absolute-baseline.cpp'),
    'oof-only': ('flex-baseline.cpp','absolute-oof.cpp'),
    'both': ('flex-principal.cpp','absolute-oof.cpp'),
    'original-key': ('flex-original-key.cpp','absolute-baseline.cpp'),
    'original-key-principal': ('flex-original-key-principal.cpp','absolute-baseline.cpp'),
    'trace-baseline': ('flex-baseline.cpp','absolute-trace-baseline.cpp'),
    'trace-oof-only': ('flex-baseline.cpp','absolute-trace-oof.cpp'),
}
output = {'draft_sha256':sha(args.runtime/'DRAFT-FILES.json'),'INPUTS_sha256':sha(args.runtime/'INPUTS.json'),'phases':{},'timing':{}}
for phase in args.phases:
    directory = args.runtime/phase
    run = read(directory/'RUN.json')
    events = [json.loads(line) for line in (directory/'raw.json').read_text().splitlines()]
    need(run['complete'] and run['before']==run['after'], 'Incomplete/unstable WPT phase '+phase)
    need(run['rows']==[e for e in events if e.get('action')=='test_status'], 'Wrong raw row projection')
    need(run['ends']==[e for e in events if e.get('action')=='test_end'], 'Wrong raw ends')
    tests = config['trace_tests'] if phase.startswith('trace-') else config['tests']
    names = ['/'+str(Path(t).relative_to('testing/web-platform/tests')) for t in tests]
    need(len(run['ends'])==len(tests) and set(e['test'] for e in run['ends'])==set(names), 'Wrong file ends')
    need(all(e['status']=='OK' for e in run['ends']) and sum(e.get('action')=='suite_end' for e in events)==1, 'Incomplete harness')
    for name in names:
        need([r['subtest'] for r in run['rows'] if r['test']==name]==config['expected_subtests'][name], 'Wrong ordered roster')
    need(len(run['rows'])==sum(len(config['expected_subtests'][name]) for name in names) and all(r['test'] in names and r['status'] in ['PASS','FAIL'] for r in run['rows']), 'Unexpected row')
    need(len({(r['test'],r['subtest']) for r in run['rows']})==len(run['rows']), 'Duplicate rows')
    for source,role in zip(['layout/generic/nsFlexContainerFrame.cpp','layout/generic/AbsoluteContainingBlock.cpp'],roles[phase]):
        need(run['before'][source]==sha(args.runtime/'selected'/role), 'Wrong phase source')
    for path,role in [('layout/base/PresShell.cpp','pres-shell-before.cpp'),('layout/tables/nsTableFrame.cpp','table-frame-before.cpp')]:
        need(run['before'][path]==sha(args.runtime/'selected'/role), 'Wrong noninstrumented column provider role')
    for path,pin in inputs['resource_pins'].items():
        if path in run['before']:
            need(run['before'][path]==pin, 'Wrong resource identity')
    record = {'RUN_sha256':sha(directory/'RUN.json'),'raw_sha256':sha(directory/'raw.json'),'exact_raw_projection':True,'stable_pins':True,'selected_source_roles':list(roles[phase]),'status_counts':dict(collections.Counter(r['status'] for r in run['rows'])),'file_ends':len(run['ends']),'rows':[{'test':r['test'],'name':r['subtest'],'status':r['status'],'message':r.get('message')} for r in run['rows']]}
    if phase in ['baseline','principal-only','oof-only','both']:
        oldpath = args.prior/phase/'RUN.json'
        need(sha(oldpath)==prior_manifest[phase+'/RUN.json'], 'Prior receipt changed')
        old = collections.defaultdict(list)
        for row in read(oldpath)['rows']:
            old[row['subtest']].append(row)
        joined,added = [],[]
        for row in run['rows']:
            matches = old[row['subtest']]
            if not matches:
                added.append(row['subtest'])
                continue
            need(len(matches)==1, 'Ambiguous old test identity')
            need(matches[0]['status']==row['status'], 'Compact status differs from prior corpus')
            joined.append({'name':row['subtest'],'old_test':matches[0]['test'],'compact_test':row['test'],'status':row['status']})
        need(len(joined)==50 and len(added)==16, 'Wrong old/new split')
        record['prior_status_join']=joined
        record['new_names']=added
    output['phases'][phase]=record

timers = ['constructionMs','establishMs','mutationFlushMs']
buckets = ['prepare','first','repeat','distinct','secondPass','noMutation']
cost_config = read(args.runtime/'cost/CONFIG.json')
identities = [(k,s,n) for k in cost_config['kinds'] for s in cost_config['states'] for n in cost_config['sizes']]
for phase in ['baseline','both']:
    source = args.runtime/(phase+'-timing')/'RESULT.json'
    receipt = read(source)
    parent = read(args.runtime/(phase+'-timing-parent.json'))
    expected = dict(parent['execution_inputs'])
    for path in config['guard_sources']+['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']:
        expected[str((args.runtime.parents[1]/path).resolve())]=parent['before'][path]
    need(receipt['before']==receipt['after']==expected and receipt['stable'], 'Runner/parent identity mismatch')
    need(parent['before']==parent['after'], 'Timing parent source/resource drift')
    startup=receipt['startupEnvironment']
    need(startup['MOZ_DISABLE_SAFE_MODE_KEY']=='1' and startup['MOZ_DISABLE_UPDATE_PROCESSING']=='1' and startup['MOZ_SAFE_MODE_RESTART_removed'] is True and type(startup['MOZ_SAFE_MODE_RESTART_inherited_present']) is bool, 'Wrong controlled environment')
    need(startup==read(source.parent/'STARTUP-ENV.json')==read(source.parent/'SPAWN.json')['startupEnvironment'], 'Environment receipt mismatch')
    progress=[e['value'] for e in [json.loads(line) for line in (source.parent/'REQUESTS.jsonl').read_text().splitlines()] if e.get('event')=='progress-persisted']
    expected_progress=[{'stage':'script-start'},{'stage':'config-ready','label':phase},{'stage':'fixture-start'}]
    for round_no in range(-cost_config['warmup_rounds'],cost_config['measured_rounds']):
        for slot in range(len(identities)):
            ordinal=(slot+round_no+cost_config['warmup_rounds'])%len(identities)
            kind,visibility,count=identities[ordinal]
            for stage in ['batch-begin','batch-end']:
                expected_progress.append({'stage':stage,'round':round_no,'slot':slot,'ordinal':ordinal,'kind':kind,'state':visibility,'count':count})
    expected_progress.append({'stage':'result-ready','rows':84})
    expected_progress=[{'sequence':i,**entry} for i,entry in enumerate(expected_progress)]
    need(receipt['progressReceipts']==220 and progress==expected_progress, 'Wrong complete progress roster')
    need(receipt['cleanupErrors']==[] and receipt['terminal'] and receipt['noLiveGroup'] and receipt['profileRemoved'], 'Cleanup failed')
    need(receipt['termination']['terminal'] and receipt['termination']['noLiveGroup'] and receipt['termination']['errors']==[], 'Nested cleanup failed')
    need(not (source.parent/'profile').exists(), 'Profile remains')
    for name in ['probe.html','benchmark.js','CONFIG.json','run.py','validate.py','cleanup.py']:
        file = (args.runtime/'cost'/name).resolve()
        need(receipt['before'][str(file)]==sha(file), 'Timing input changed')
    wpt = read(args.runtime/phase/'RUN.json')
    for path,pin in wpt['after'].items():
        if path in parent['before']:
            need(parent['before'][path]==pin, 'Timing/WPT identity mismatch')
    record = {'RESULT_sha256':sha(source),'parent_sha256':sha(args.runtime/(phase+'-timing-parent.json')),'failure':receipt['failure'],'stable_parent_runner_WPT_joins':True,'cleanup_verified':True,'measurement_complete':parent['measurement_complete']}
    if not parent['measurement_complete']:
        need(parent['exit']!=0 and receipt['failure']=='75-second runner deadline' and receipt['observations']==[], 'Unexpected incomplete observation')
        record['verdict']='INCOMPLETE_MEASUREMENT_NO_OBSERVATIONS_NO_NATIVE_HANG_INFERENCE'
        output['timing'][phase]=record
        continue
    need(parent['exit']==0 and receipt['failure'] is None and len(receipt['observations'])==1, 'Successful observation missing')
    obs=receipt['observations'][0]
    need(obs['complete'] and obs['label']==phase and obs['config']==cost_config, 'Wrong observation')
    need(len(obs['rows'])==84, 'Wrong batch count')
    groups={}
    bad=collections.Counter()
    bad_bucket=collections.Counter({k:0 for k in buckets if k!='prepare'})
    queries=0
    for position,row in enumerate(obs['rows']):
        round_no,slot=divmod(position,len(identities))
        ordinal=(slot+round_no+cost_config['warmup_rounds'])%len(identities)
        kind,state,count=identities[ordinal]
        need([row[k] for k in ['round','slot','ordinal','kind','state','count']]==[round_no,slot,ordinal,kind,state,count], 'Wrong cost row order')
        n=min(count,cost_config['query_limit'])
        indices=[0] if n==1 else [i*(count-1)//(n-1) for i in range(n)]
        need(row['indices']==indices, 'Wrong sampled indices')
        rect=lambda i,w:[(w-8)/2 if kind=='oof' else i*8,0,8,8]
        need(row['calibration']==[{'width':w,'index':i,'rect':rect(i,w)} for w in [160,168] for i in indices], 'Visible calibration failed')
        need(row['initial']==[rect(i,160) for i in indices], 'Initial calibration failed')
        need(row['outerChecksum']==sum((168 if i%2==0 else 160)+64 for i in range(cost_config['iterations'])), 'Wrong mutation count')
        roster=[]
        for iteration in range(cost_config['iterations']):
            width=168 if iteration%2==0 else 160
            for bucket,selected in [('first',indices[:1]),('repeat',indices[:1]),('distinct',indices[1:]),('secondPass',indices)]:
                roster.extend((bucket,iteration,i,width) for i in selected)
        final_width=168 if (cost_config['iterations']-1)%2==0 else 160
        roster.extend(('noMutation',iteration,i,final_width) for iteration in range(cost_config['no_mutation_iterations']) for i in indices)
        need(len(roster)==len(row['observations']), 'Wrong geometry count')
        group=f'{kind}/{state}/{count}'
        for value,identity in zip(row['observations'],roster):
            need(tuple(value[k] for k in ['bucket','iteration','index','width'])==identity, 'Wrong query order')
            observed=value['rect']
            need(len(observed)==4 and all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in observed) and min(observed[2:])>=0, 'Malformed geometry')
            if observed!=rect(identity[2],identity[3]):
                bad[group]+=1
                bad_bucket[identity[0]]+=1
        queries+=len(roster)
        values={key:row[key] for key in timers}
        need(set(row['times'])==set(buckets), 'Wrong timer buckets')
        for bucket in buckets:
            values[bucket]=sum(row['times'][bucket])
            need(len(row['times'][bucket])==(cost_config['no_mutation_iterations'] if bucket=='noMutation' else cost_config['iterations']), 'Wrong timer count')
            need(all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0 for v in row['times'][bucket]), 'Invalid timer sample')
        for key,value in values.items():
            need(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0, 'Invalid timer')
            groups.setdefault(group,{}).setdefault(key,[]).append(value)
    distribution={g:{k:{'samplesMs':v,'medianMs':statistics.median(v),'minMs':min(v),'maxMs':max(v),'zeroSamples':v.count(0)} for k,v in values.items()} for g,values in groups.items()}
    summary=read(source.parent/'SUMMARY.json')
    need(summary==parent['summary'] and summary['groups']==distribution and summary['measuredRows']==84 and summary['queryReads']==queries and summary['geometryMismatches']==sum(bad.values()) and summary['geometryMismatchesByBucket']==dict(bad_bucket), 'Independent summary disagreement')
    record.update({'batches':84,'query_reads':queries,'geometry_mismatches_by_group':dict(bad),'geometry_mismatches_by_bucket':dict(bad_bucket),'groups':distribution})
    output['timing'][phase]=record
args.output.write_text(json.dumps(output,indent=2)+'\n')
print('PASS: '+', '.join(args.phases)+'; two controlled timing observations')
