import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Run with python3 -I -S and without -O")

import collections
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / 'css-hidden-layout-column-runtime-v1'
PRIOR = HERE.parent / 'css-hidden-layout-compact-runtime-v3'
pins = {}


def read(path):
    data = path.read_bytes()
    pins[str(path)] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def lines(path):
    data = path.read_bytes()
    pins[str(path)] = hashlib.sha256(data).hexdigest()
    return [json.loads(line) for line in data.splitlines() if line]


def wpt(base, phase):
    records = lines(base / phase / 'raw.json')
    rows, ends = {}, {}
    for r in records:
        if r['action'] == 'test_status':
            key = (r['test'], r['subtest'])
            assert key not in rows
            rows[key] = (r['status'], r.get('message'))
        elif r['action'] == 'test_end':
            assert r['test'] not in ends
            ends[r['test']] = r['status']
    run = read(base / phase / 'RUN.json')
    assert run['complete'] and run['before'] == run['after']
    assert run['exit'] == 1
    assert len(run['rows']) == len(rows) and len(run['ends']) == len(ends)
    assert {(r['test'],r['subtest']):(r['status'],r.get('message')) for r in run['rows']} == rows
    assert {r['test']:r['status'] for r in run['ends']} == ends
    return rows, ends


cfg = read(ROOT / 'CONFIG.json')
inputs = read(ROOT / 'INPUTS.json')
for name,digest in inputs['payload_pins'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
execution = read(ROOT/'COST-EXECUTION-INPUTS.json')
assert len(execution)==6
for name,digest in execution.items():
    assert hashlib.sha256((ROOT/'cost'/name).read_bytes()).hexdigest()==digest
expected = {(url, name) for url, names in cfg['expected_subtests'].items() for name in names}
result = {'wpt': {}, 'cost': {}}
maps = {}
root_analysis = read(HERE.parent / 'css-hidden-layout-column-analysis-v1/RESULT.json')
root_cost = read(HERE.parent / 'css-hidden-layout-column-analysis-v1/COST.json')
for phase in ['baseline', 'both']:
    rows, ends = wpt(ROOT, phase)
    assert set(rows) == expected and len(rows) == 66 and len(ends) == 7
    assert set(ends.values()) == {'OK'}
    old, old_ends = wpt(PRIOR, phase)
    assert len(old) == 58 and set(old) < set(rows)
    assert {k: rows[k] for k in old} == old
    assert {k: ends[k] for k in old_ends} == old_ends
    counts = dict(collections.Counter(v[0] for v in rows.values()))
    assert counts == root_analysis['phases'][phase]['counts']
    assert ends == root_analysis['phases'][phase]['ends']
    result['wpt'][phase] = {'counts': counts, 'file_ends': ends,
        'prior_58_exact_status_message_match': True,
        'new_8': [{'test': k[0], 'subtest': k[1], 'status': rows[k][0], 'message': rows[k][1]} for k in sorted(set(rows)-set(old))]}
    maps[phase] = rows
    r = read(ROOT / (phase+'-timing') / 'RESULT.json')
    parent = read(ROOT / (phase+'-timing-parent.json'))
    assert parent['before'] == parent['after'] and parent['cleanup_verified'] and parent['measurement_complete']
    assert parent['exit'] == 0 and r['stable'] and r['before'] == r['after']
    assert r['failure'] is None and r['cleanupErrors'] == [] and r['profileRemoved']
    assert r['terminal'] and r['noLiveGroup'] and r['termination']['terminal'] and r['termination']['noLiveGroup']
    env = read(ROOT / (phase+'-timing') / 'STARTUP-ENV.json')
    assert env == r['startupEnvironment'] == parent['startup_environment']
    assert read(ROOT/(phase+'-timing')/'SPAWN.json')['startupEnvironment']==env
    assert {Path(k).name:v for k,v in parent['execution_inputs'].items()}==execution
    for name,digest in execution.items():
        assert r['before'][str((ROOT/'cost'/name).resolve())]==digest
    wpt_run=read(ROOT/phase/'RUN.json')
    assert parent['before']==wpt_run['before']
    for native,digest in parent['before'].items():
        absolute=str((HERE.parents[1]/native).resolve())
        if absolute in r['before']: assert r['before'][absolute]==digest
    assert env['MOZ_DISABLE_UPDATE_PROCESSING'] == env['MOZ_DISABLE_SAFE_MODE_KEY'] == '1'
    assert env['MOZ_SAFE_MODE_RESTART_removed'] is True
    assert len(r['observations']) == 1
    observation = r['observations'][0]
    assert observation['complete'] and len(observation['rows']) == 84
    configurations = list(itertools.product(['principal', 'oof'], ['visible', 'hidden'], [1,32,256]))
    progress = [x['value'] for x in lines(ROOT/(phase+'-timing')/'REQUESTS.jsonl') if x.get('event')=='progress-persisted']
    planned = [{'stage':'script-start'}, {'stage':'config-ready','label':phase}, {'stage':'fixture-start'}]
    for round_ in range(-2,7):
        for slot in range(12):
            ordinal = (slot+round_+2)%12
            kind,state,count = configurations[ordinal]
            for stage in ['batch-begin','batch-end']:
                planned.append(dict(stage=stage,round=round_,slot=slot,ordinal=ordinal,kind=kind,state=state,count=count))
    planned.append({'stage':'result-ready','rows':84})
    assert progress == [dict(sequence=i,**x) for i,x in enumerate(planned)]
    assert r['progressReceipts']==parent['progress_count']==220
    groups = {}
    for index,row in enumerate(observation['rows']):
        round_,slot=divmod(index,12); ordinal=(slot+round_+2)%12
        assert (row['round'],row['slot'],row['ordinal'])==(round_,slot,ordinal)
        kind,state,count=configurations[ordinal]
        assert (row['kind'],row['state'],row['count'])==(kind,state,count)
        n=min(count,4); indices=[0] if n==1 else [math.floor(i*(count-1)/(n-1)) for i in range(n)]
        assert row['indices']==indices
        def rect(i,w): return [8*i if kind=='principal' else (w-8)/2,0,8,8]
        assert row['initial']==[rect(i,160) for i in indices]
        assert row['calibration']==[dict(width=w,index=i,rect=rect(i,w)) for w in [160,168] for i in indices]
        assert row['outerChecksum']==3648
        queries=[]
        for iteration in range(16):
            w=168 if iteration%2==0 else 160
            for bucket,selected in [('first',indices[:1]),('repeat',indices[:1]),('distinct',indices[1:]),('secondPass',indices)]:
                queries.extend((bucket,iteration,i,w) for i in selected)
        queries.extend(('noMutation',iteration,i,160) for iteration in range(16) for i in indices)
        assert [(q['bucket'],q['iteration'],q['index'],q['width']) for q in row['observations']]==queries
        key=f'{kind}/{state}/{count}'
        g=groups.setdefault(key,{'reads':collections.Counter(),'mismatches':collections.Counter(),'samples':collections.defaultdict(list)})
        for q in row['observations']:
            g['reads'][q['bucket']]+=1
            if q['rect'] != rect(q['index'],q['width']): g['mismatches'][q['bucket']]+=1
        for name,values in row['times'].items():
            assert len(values)==16 and all(isinstance(v,(float,int)) and math.isfinite(v) and v>=0 for v in values)
            g['samples'][name].append(sum(values))
        for name in ['constructionMs','establishMs','mutationFlushMs']:
            g['samples'][name].append(row[name])
    for key,g in groups.items():
        g['medians_ms']={name:statistics.median(v) for name,v in g['samples'].items()}
        reference=root_cost[phase]['groups'][key]
        assert dict(g['reads'])==reference['reads']
        assert all(g['mismatches'][bucket]==value for bucket,value in reference['mismatches'].items())
        assert {name:g['samples'][name] for name in reference['samples']}==reference['samples']
        assert {name:g['medians_ms'][name] for name in reference['medians_ms']}==reference['medians_ms']
    result['cost'][phase]={'rows':84,'progress':220,'reads':sum(sum(g['reads'].values()) for g in groups.values()),'mismatches':sum(sum(g['mismatches'].values()) for g in groups.values()),'elapsed_ms':observation['elapsedMs'],'groups':groups,'cleanup_and_stability':True}
    assert result['cost'][phase]['reads']==13440
result['wpt']['comparison']=dict(collections.Counter(f'{maps["baseline"][k][0]}->{maps["both"][k][0]}' for k in expected))
baseline_before=read(ROOT/'baseline/RUN.json')['before']
both_before=read(ROOT/'both/RUN.json')['before']
assert {k for k in baseline_before if baseline_before[k]!=both_before[k]}=={
    'layout/generic/AbsoluteContainingBlock.cpp','layout/generic/nsFlexContainerFrame.cpp',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'}
for phase,role in [('baseline','baseline'),('both','principal')]:
    before=read(ROOT/phase/'RUN.json')['before']
    for native,selected in [('layout/generic/nsFlexContainerFrame.cpp','flex-'+role+'.cpp'),
        ('layout/generic/AbsoluteContainingBlock.cpp','absolute-'+('baseline' if phase=='baseline' else 'oof')+'.cpp'),
        ('layout/base/PresShell.cpp','pres-shell-before.cpp'),('layout/tables/nsTableFrame.cpp','table-frame-before.cpp')]:
        assert before[native]==hashlib.sha256((ROOT/'selected'/selected).read_bytes()).hexdigest()
trace_rows,trace_ends=wpt(ROOT,'trace-both-column')
assert len(trace_rows)==16 and len(trace_ends)==2
assert trace_rows=={k:maps['both'][k] for k in trace_rows}
trace_before=read(ROOT/'trace-both-column/RUN.json')['before']
for native,selected in [('layout/base/PresShell.cpp','pres-shell-trace.cpp'),('layout/tables/nsTableFrame.cpp','table-frame-trace.cpp')]:
    assert trace_before[native]==hashlib.sha256((ROOT/'selected'/selected).read_bytes()).hexdigest()
trace_counts=collections.Counter()
trace_records=[]
for ordinal,record in enumerate(lines(ROOT/'trace-both-column/raw.json')):
    data=record.get('data','')
    if not data.startswith('CV_COLUMN_'): continue
    fields=dict(part.split('=',1) for part in data.split()[1:])
    if data.startswith('CV_COLUMN_QUERY '):
        assert set(fields)=={'target','kind','d','h','provider','table','pd','ph'}
        assert all(fields[k] in ['0','1'] for k in ['d','h','table','pd','ph'])
        dirty=fields['d']=='1' or fields['h']=='1'
        pd=fields['pd']=='1' or fields['ph']=='1'
        trace_counts[f'query/{fields["kind"]}/target-dirty={dirty}/table={fields["table"]=="1"}/provider-dirty={pd}']+=1
    else:
        assert data.startswith('CV_COLUMN_PUBLISH ')
        assert set(fields)=={'table','target','kind','rect'}
        assert len(fields['rect'].split(','))==4
        list(map(int,fields['rect'].split(',')))
        trace_counts['publish/'+fields['kind']]+=1
    trace_records.append({'raw_ordinal':ordinal,'output_process':record['process'],'data':data})
root_trace=read(HERE.parent/'css-hidden-layout-column-analysis-v1/TRACE.json')
assert dict(trace_counts)==root_trace['counts']
assert len(trace_records)==len(root_trace['records'])
result['trace']={'outcomes_equal_both':True,'counts':trace_counts,'records':len(trace_records),'limitations':'No DOM identity, pointer lifetime or cross-event causation follows from numeric pointer equality.'}
(HERE/'TRACE-RECORDS.json').write_text(json.dumps(trace_records,indent=2)+'\n')
(HERE/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'READ-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps({'wpt':result['wpt']['comparison'],'cost':{p:{k:v for k,v in r.items() if k!='groups'} for p,r in result['cost'].items()}},indent=2))
