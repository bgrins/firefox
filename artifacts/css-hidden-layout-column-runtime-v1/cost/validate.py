import math
import statistics

BUCKETS = ['prepare', 'first', 'repeat', 'distinct', 'secondPass', 'noMutation']

def finite(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

def expected(kind, index, width):
    return [(width - 8) / 2 if kind == 'oof' else index * 8, 0, 8, 8]

def validate(observation, config, label):
    if observation.get('complete') is not True or observation.get('label') != label or observation.get('config') != config:
        raise ValueError('Incomplete or mismatched observation')
    if not finite(observation.get('elapsedMs')) or observation['elapsedMs'] < 0:
        raise ValueError('Invalid elapsed time')
    configs = [(kind, state, count) for kind in config['kinds'] for state in config['states'] for count in config['sizes']]
    rows = observation['rows']
    if len(rows) != len(configs) * config['measured_rounds']:
        raise ValueError('Wrong row count')
    queries = mismatches = 0
    groups = {}
    bad_by_bucket = {k:0 for k in BUCKETS if k != 'prepare'}
    for position, row in enumerate(rows):
        round_no, slot = divmod(position, len(configs))
        ordinal = (slot + round_no + config['warmup_rounds']) % len(configs)
        kind, state, count = configs[ordinal]
        if [row.get(k) for k in ('round','slot','ordinal','kind','state','count')] != [round_no,slot,ordinal,kind,state,count]:
            raise ValueError('Wrong row identity/order')
        n = min(count, config['query_limit'])
        indices = [0] if n == 1 else [i * (count - 1) // (n - 1) for i in range(n)]
        if row['indices'] != indices:
            raise ValueError('Wrong sampled leaves')
        calibration = [{'width':w,'index':i,'rect':expected(kind,i,w)} for w in [160,168] for i in indices]
        if row['calibration'] != calibration or row['initial'] != [expected(kind,i,160) for i in indices]:
            raise ValueError('Visible full-rectangle calibration failure')
        if row['outerChecksum'] != sum((168 if i % 2 == 0 else 160) + 64 for i in range(config['iterations'])):
            raise ValueError('Wrong mutation work')
        timers = {key:row[key] for key in ['constructionMs','establishMs','mutationFlushMs']}
        if set(row['times']) != set(BUCKETS):
            raise ValueError('Wrong timing buckets')
        for bucket in BUCKETS:
            samples = row['times'][bucket]
            length = config['no_mutation_iterations'] if bucket == 'noMutation' else config['iterations']
            if len(samples) != length or any(not finite(t) or t < 0 for t in samples):
                raise ValueError('Invalid timer samples')
            timers[bucket] = sum(samples)
        if any(not finite(t) or t < 0 for t in timers.values()):
            raise ValueError('Invalid timer')
        roster = []
        for iteration in range(config['iterations']):
            width = 168 if iteration % 2 == 0 else 160
            for bucket, selected in [('first',indices[:1]),('repeat',indices[:1]),('distinct',indices[1:]),('secondPass',indices)]:
                roster.extend((bucket,iteration,i,width) for i in selected)
        final_width = 168 if (config['iterations'] - 1) % 2 == 0 else 160
        roster.extend(('noMutation',iteration,i,final_width) for iteration in range(config['no_mutation_iterations']) for i in indices)
        actual = row['observations']
        if len(actual) != len(roster):
            raise ValueError('Missing/extra geometry reads')
        for record, identity in zip(actual, roster):
            if tuple(record[k] for k in ['bucket','iteration','index','width']) != identity:
                raise ValueError('Wrong query identity/order')
            value = record['rect']
            if not isinstance(value,list) or len(value) != 4 or any(not finite(v) for v in value) or value[2] < 0 or value[3] < 0:
                raise ValueError('Malformed rectangle')
            bad = value != expected(kind, identity[2], identity[3])
            mismatches += bad
            bad_by_bucket[identity[0]] += bad
        queries += len(actual)
        group = groups.setdefault(f'{kind}/{state}/{count}', {k:[] for k in timers})
        for key, value in timers.items():
            group[key].append(value)
    summary = {name:{key:{'samplesMs':values,'medianMs':statistics.median(values),'minMs':min(values),'maxMs':max(values),'zeroSamples':values.count(0)} for key,values in timers.items()} for name,timers in groups.items()}
    return {'measuredRows':len(rows),'queryReads':queries,'geometryMismatches':mismatches,
            'geometryMismatchesByBucket':bad_by_bucket,'groups':summary,
            'interpretation':'Summed per-bucket batch timings; n=1 distinct has zero reads. Full rectangle mismatches retained, not equivalent-work acceptance.'}
