import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--runtime', type=Path, required=True)
p.add_argument('--phases', nargs='+', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
if a.output.exists():
    raise SystemExit('Output exists')
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = json.loads((a.runtime/'timing-capsule/CONFIG.json').read_text())
timers = ['constructionMs', 'establishMs', 'mutationFlushMs', 'recoveryPrepareMs', 'recoveryQueryMs']
result = {}
for phase in a.phases:
    source = a.runtime/f'timing-{phase}/RESULT.json'
    receipt = json.loads(source.read_text())
    run = json.loads((a.runtime/phase/'RUN.json').read_text())
    command = json.loads((a.runtime/f'timing-{phase}.json').read_text())
    if command['exit'] != 0 or not receipt['stable'] or receipt['before'] != receipt['after'] or receipt['failure'] or receipt['cleanupErrors'] or not receipt['profileRemoved'] or receipt['processExitAfterOwnedTermination'] is None:
        raise SystemExit('Timing phase incomplete or unstable')
    for path, sha in run['after'].items():
        if sha is not None:
            actual = receipt['before'].get(str((a.runtime.parents[1]/path).resolve()))
            if actual != sha:
                raise SystemExit('WPT/timing source or binary mismatch: '+path)
    for name in ['probe.html', 'benchmark.js', 'CONFIG.json', 'run.py', 'validate.py']:
        fixture = (a.runtime/'timing-capsule'/name).resolve()
        if receipt['before'][str(fixture)] != h(fixture):
            raise SystemExit('Fixture changed')
    if len(receipt['observations']) != 1:
        raise SystemExit('Wrong observation count')
    obs = receipt['observations'][0]
    if not obs['complete'] or obs['label'] != phase or obs['config'] != config:
        raise SystemExit('Wrong observation')
    identities = [(k,s,n) for k in config['kinds'] for s in config['states'] for n in config['sizes']]
    if len(obs['rows']) != len(identities)*config['measured_rounds']:
        raise SystemExit('Wrong row count')
    groups = {}
    reads = mismatches = 0
    for position, row in enumerate(obs['rows']):
        round_no, slot = divmod(position, len(identities))
        ordinal = (slot+round_no+config['warmup_rounds']) % len(identities)
        kind,state,count = identities[ordinal]
        if [row[k] for k in ['round','slot','ordinal','kind','state','count']] != [round_no,slot,ordinal,kind,state,count]:
            raise SystemExit('Wrong row ordering')
        n = min(count,config['query_limit'])
        indices = [0] if n == 1 else [i*(count-1)//(n-1) for i in range(n)]
        sizes = row['observedSizes']
        if row['indices'] != indices or len(sizes) != n*config['iterations']:
            raise SystemExit('Wrong selected reads')
        if row['outerChecksum'] != sum((168 if i%2 == 0 else 160)+64 for i in range(config['iterations'])):
            raise SystemExit('Outer checksum mismatch')
        if row['queryChecksum'] != sum((ordinal+1)*(i+1)*(j+1) for i in range(config['iterations']) for j in indices):
            raise SystemExit('Query checksum mismatch')
        bad = sum(size != [8,8] for size in sizes)
        if row['mismatches'] != bad or row['geometryChecksum'] != sum(w*17+height*31 for w,height in sizes):
            raise SystemExit('Geometry receipt mismatch')
        reads += len(sizes)
        mismatches += bad
        group = groups.setdefault(f'{kind}/{state}/{count}', {t:[] for t in timers})
        for t in timers:
            value = row[t]
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0:
                raise SystemExit('Invalid timing')
            group[t].append(value)
    result[phase] = {'receipt_sha256':h(source),'WPT_RUN_sha256':h(a.runtime/phase/'RUN.json'),'stable_source_binary_fixture_joins':True,'measured_batches':len(obs['rows']),'leaf_reads':reads,'size_mismatches':mismatches,'groups':{key:{t:{'samples_ms':v,'median_ms':statistics.median(v),'min_ms':min(v),'max_ms':max(v),'zero_samples':v.count(0)} for t,v in values.items()} for key,values in groups.items()}}
a.output.write_text(json.dumps({'config':config,'phase_order':a.phases,'phases':result},indent=2)+'\n')
print('Authenticated '+', '.join(a.phases))
