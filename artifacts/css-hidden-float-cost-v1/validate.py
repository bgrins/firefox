import math
import statistics

BUCKETS = ['prepare', 'first', 'repeat']
def need(ok, why):
    if not ok: raise ValueError(why)
def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
def expected(index, width):
    return [10 + (index % 2) * width / 2, 10 + (index // 2) * 16, width / 2, 8]
def configurations(config):
    return [(k,s,n) for k in config['kinds'] for s in config['states'] for n in config['sizes']]
def validate_config(c):
    need(c['version']==1 and c['kinds']==['direct','inline-nested'] and c['states']==['visible','hidden'], 'Configuration kinds')
    need(c['sizes']==[1,32,128], 'Bounded sizes')
    for key,low,high in [('warmup_rounds',0,2),('measured_rounds',1,5),('iterations',1,32),('hot_reads',4096,65536),('startup_ms',0,3000),('fixture_deadline_ms',1000,45000)]:
        need(type(c[key]) is int and low<=c[key]<=high, 'Bounded '+key)
    need(4+2*len(configurations(c))*(c['warmup_rounds']+c['measured_rounds'])<=300, 'Progress bound')
def expected_progress(c,label):
    events=[{'stage':'script-start'}, {'stage':'config-ready','label':label}, {'stage':'fixture-start'}]
    configs=configurations(c)
    for r in range(-c['warmup_rounds'],c['measured_rounds']):
        for slot in range(len(configs)):
            ordinal=(slot+r+c['warmup_rounds'])%len(configs);kind,state,count=configs[ordinal]
            for stage in ['batch-begin','batch-end']:
                events.append({'stage':stage,'round':r,'slot':slot,'ordinal':ordinal,'kind':kind,'state':state,'count':count})
    events.append({'stage':'result-ready','rows':len(configs)*c['measured_rounds']})
    return [{'sequence':i,**v} for i,v in enumerate(events)]
def validate(o,c,label):
    validate_config(c)
    need(o.get('complete') is True and o.get('label')==label and o.get('config')==c,'Observation identity')
    need(finite(o.get('elapsedMs')) and o['elapsedMs']>=0,'Elapsed time')
    configs=configurations(c);rows=o['rows'];need(len(rows)==len(configs)*c['measured_rounds'],'Row count')
    groups={};bad={};hot_bad={};recovery_status={};queries=0
    for position,row in enumerate(rows):
        r,slot=divmod(position,len(configs));ordinal=(slot+r+c['warmup_rounds'])%len(configs);kind,state,count=configs[ordinal]
        need([row.get(k) for k in ['round','slot','ordinal','kind','state','count']]==[r,slot,ordinal,kind,state,count],'Row roster')
        need(row['calibration']==[{'width':w,'rects':[expected(i,w) for i in range(count)]} for w in [160,168,160]],'Visible calibration')
        need(row['hiddenOuter']==[10,10,160,64],'Hidden outer')
        need(row['outers']==[[10,10,168 if i%2==0 else 160,64] for i in range(c['iterations'])],'Outer flush geometry')
        for key in ['restored','cleanVisible','cleanReady','cleanAfter']:
            need(row[key]==[expected(i,160) for i in range(count)],'Clean/restored geometry '+key)
        need(set(row['times'])==set(BUCKETS),'Timer roster');timers={}
        for key in BUCKETS:
            values=row['times'][key];need(len(values)==c['iterations'] and all(finite(x) and x>=0 for x in values),'Timer samples')
            timers[key]=sum(values)
        roster=[(bucket,i,count-1,168 if i%2==0 else 160) for i in range(c['iterations']) for bucket in ['first','repeat']]
        need(len(row['observations'])==len(roster),'Geometry read count');group=f'{kind}/{state}/{count}'
        for value,identity in zip(row['observations'],roster):
            need(tuple(value[k] for k in ['bucket','iteration','index','width'])==identity,'Recovery order')
            rect=value['rect'];need(isinstance(rect,list) and len(rect)==4 and all(finite(x) for x in rect) and min(rect[2:])>=0,'Malformed geometry')
            status=recovery_status.setdefault(group,{'first':{'correct':0,'incorrect':0},'repeat':{'correct':0,'incorrect':0}})
            correct=rect==expected(identity[2],identity[3])
            status[value['bucket']]['correct' if correct else 'incorrect']+=1
            if not correct:bad[group]=bad.get(group,0)+1
        need(len(row['hotRows'])==2,'Hot bucket count')
        for hot,bucket in zip(row['hotRows'],['hotSame','hotCycle']):
            need(hot['bucket']==bucket and hot['reads']==c['hot_reads'],'Hot identity')
            need(finite(hot['elapsedMs']) and hot['elapsedMs']>=0 and finite(hot['checksum']),'Hot values')
            need(type(hot['mismatches']) is int and 0<=hot['mismatches']<=c['hot_reads'],'Hot mismatch count')
            checksum=sum(sum(expected(count-1 if bucket=='hotSame' else i%count,160)) for i in range(c['hot_reads']))
            if hot['mismatches']==0:
                need(hot['firstMismatch'] is None and hot['checksum']==checksum,'Hot checksum')
            else:
                first=hot['firstMismatch'];need(isinstance(first,dict) and type(first.get('iteration')) is int and 0<=first['iteration']<c['hot_reads'],'Hot first mismatch')
                index=count-1 if bucket=='hotSame' else first['iteration']%count
                need(first.get('index')==index and len(first['rect'])==4 and all(finite(x) for x in first['rect']) and first['rect']!=expected(index,160),'Hot mismatch witness')
                hot_bad[group]=hot_bad.get(group,0)+hot['mismatches']
            timers[bucket]=hot['elapsedMs']
        queries+=len(roster)+2*c['hot_reads']
        g=groups.setdefault(group,{k:[] for k in timers})
        for k,v in timers.items():g[k].append(v)
    dist={g:{k:{'samplesMs':v,'medianMs':statistics.median(v),'minMs':min(v),'maxMs':max(v),'p90Ms':sorted(v)[math.ceil(len(v)*0.9)-1],'zeroSamples':v.count(0)} for k,v in timers.items()} for g,timers in groups.items()}
    return {'measuredRows':len(rows),'queryReads':queries,'geometryMismatches':sum(bad.values())+sum(hot_bad.values()),'recoveryMismatchesByGroup':bad,'hotMismatchesByGroup':hot_bad,'recoveryGeometryByGroup':recovery_status,'groups':dist,'recoveryGeometryCorrect':not bad,'cleanGeometryCorrect':not hot_bad,'interpretation':'First/repeat timings sum post-mutation rounds. Hot timings cover fixed read counts after calibrated clean setup; include JS comparison/checksum overhead. Recovery geometry mismatches are not equivalent work.'}
