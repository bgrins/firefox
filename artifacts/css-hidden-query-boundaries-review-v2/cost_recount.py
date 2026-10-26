import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter
import hashlib
import json
import statistics
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = HERE.parent / 'css-hidden-query-boundaries-runtime-v2'
read_pins = {}
def need(ok, message):
    if not ok: raise RuntimeError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    read_pins[str(path)] = sha(path)
    return json.loads(path.read_bytes())
def events(path):
    read_pins[str(path)] = sha(path)
    return [json.loads(line) for line in path.read_bytes().splitlines() if line]

def cost(phase, run, inputs, config):
    directory = RUNTIME / (phase + '-cost')
    receipt = load(directory / 'RESULT.json')
    expected = {str(ROOT / n): run['after'][n] for n in config['guard_sources']}
    for n, pin in run['after'].items():
        if '/Contents/MacOS/' in n:
            expected[str(ROOT / n)] = pin
    capsule = ROOT / config['cost']['path']
    for n in ['probe.html', 'benchmark.js', 'CONFIG.json', 'run.py', 'validate.py', 'cleanup.py']:
        expected[str(capsule / n)] = inputs['cost_payload_pins'][str((capsule / n).relative_to(ROOT))]
    need(receipt['before'] == receipt['after'] == expected and receipt['stable'], 'cost input join')
    need(receipt['terminal'] and receipt['noLiveGroup'] and receipt['profileRemoved']
         and receipt['termination']['terminal'] and receipt['termination']['noLiveGroup']
         and not receipt['cleanupErrors'] and not receipt['failure']
         and not (directory / 'profile').exists(), 'cost termination/cleanup')
    need(load(RUNTIME / (phase + '-cost-runner.json'))['exit'] == 0, 'cost runner exit')
    startup = load(directory / 'STARTUP-ENV.json')
    need(startup == receipt['startupEnvironment'] == receipt['spawn']['startupEnvironment'], 'startup joins')
    need(startup['MOZ_DISABLE_UPDATE_PROCESSING'] == startup['MOZ_DISABLE_SAFE_MODE_KEY'] == '1'
         and startup['MOZ_SAFE_MODE_RESTART_removed'], 'startup controls')
    c = load(capsule / 'CONFIG.json')
    need(len(receipt['observations']) == 1, 'cost observation cardinality')
    observation = receipt['observations'][0]
    need(observation['complete'] and observation['config'] == c and observation['label'] == phase, 'cost identity')
    configs = [(k, s, n) for k in ['block', 'td', 'col'] for s in ['visible', 'hidden'] for n in [1, 32, 128]]
    progress = [{'stage': 'script-start'}, {'stage': 'config-ready', 'label': phase}, {'stage': 'fixture-start'}]
    for r in range(-1, 5):
        for slot in range(18):
            ordinal = (slot + r + 1) % 18
            kind, state, count = configs[ordinal]
            for stage in ['batch-begin', 'batch-end']:
                progress.append(dict(stage=stage, round=r, slot=slot, ordinal=ordinal, kind=kind, state=state, count=count))
    progress.append({'stage': 'result-ready', 'rows': 90})
    progress = [dict(sequence=i, **v) for i, v in enumerate(progress)]
    persisted = [e['value'] for e in events(directory / 'REQUESTS.jsonl') if e.get('event') == 'progress-persisted']
    need(persisted == progress and receipt['progressReceipts'] == 220, 'cost progress')
    rows = observation['rows']
    need(len(rows) == 90, 'cost row count')
    recovery_bad, hot_bad, groups = Counter(), Counter(), {}
    reads = 0
    def rect(index, width):
        return [10, 10 + index * 32, width / 2, 32]
    for position, row in enumerate(rows):
        r, slot = divmod(position, 18)
        ordinal = (slot + r + 1) % 18
        kind, state, count = configs[ordinal]
        need([row[n] for n in ['round', 'slot', 'ordinal', 'kind', 'state', 'count']]
             == [r, slot, ordinal, kind, state, count], 'cost row order')
        need(row['calibration'] == [{'width': w, 'rects': [rect(i, w) for i in range(count)]}
                                   for w in [160, 168, 160]], 'cost visible calibration')
        need(row['hiddenOuter'] == [10, 10, 160, 64]
             and row['outers'] == [[10, 10, 168 if i % 2 == 0 else 160, 64] for i in range(16)], 'cost outer calibration')
        for name in ['restored', 'cleanVisible', 'cleanReady', 'cleanAfter']:
            need(row[name] == [rect(i, 160) for i in range(count)], 'cost clean calibration')
        group = f'{kind}/{state}/{count}'
        timers = {}
        for name in ['prepare', 'first', 'repeat']:
            need(len(row['times'][name]) == 16 and all(x >= 0 for x in row['times'][name]), 'cost timer count')
            timers[name] = sum(row['times'][name])
        expected_observers = [(bucket, i, count - 1, 168 if i % 2 == 0 else 160)
                              for i in range(16) for bucket in ['first', 'repeat']]
        need(len(row['observations']) == 32, 'cost recovery count')
        for v, identity in zip(row['observations'], expected_observers):
            need(tuple(v[k] for k in ['bucket', 'iteration', 'index', 'width']) == identity, 'cost query order')
            if v['rect'] != rect(identity[2], identity[3]):
                recovery_bad[group] += 1
        need(len(row['hotRows']) == 2, 'hot batch count')
        for hot, bucket in zip(row['hotRows'], ['hotSame', 'hotCycle']):
            need(hot['bucket'] == bucket and hot['reads'] == 16384 and hot['elapsedMs'] >= 0, 'hot workload')
            q, rem = divmod(16384, count)
            index_sum = 16384 * (count - 1) if bucket == 'hotSame' else q * count * (count - 1) // 2 + rem * (rem - 1) // 2
            if hot['mismatches'] == 0:
                need(hot['firstMismatch'] is None and hot['checksum'] == 132 * 16384 + 32 * index_sum, 'hot checksum')
            hot_bad[group] += hot['mismatches']
            timers[bucket] = hot['elapsedMs']
        reads += 32 + 2 * 16384
        for name, value in timers.items():
            groups.setdefault(group, {}).setdefault(name, []).append(value)
    need(reads == 2952000, 'total query reads')
    summary = load(directory / 'SUMMARY.json')
    need(summary['measuredRows'] == 90 and summary['queryReads'] == reads
         and summary['recoveryMismatchesByGroup'] == dict(recovery_bad)
         and summary['hotMismatchesByGroup'] == {k:v for k,v in hot_bad.items() if v}, 'cost summary mismatches')
    distributions = {g: {k: {'samplesMs': v, 'medianMs': statistics.median(v), 'minMs': min(v),
                            'maxMs': max(v), 'zeroSamples': v.count(0)} for k, v in buckets.items()}
                     for g, buckets in groups.items()}
    need(distributions == summary['groups'], 'cost distributions')
    return dict(rows=90, progress=220, queryReads=reads, recoveryMismatches=dict(recovery_bad),
                hotMismatches={k:v for k,v in hot_bad.items() if v}, groups=distributions,
                cleanupVerified=True, sourceBinaryFixtureJoin=True)

need(sha(RUNTIME/'INPUTS.json')=='7f8b3a0e3d5892d65a1a6472f283a7c942f4f172b10ca4b7630f0bfb51ee4fbd','INPUTS')
inputs=load(RUNTIME/'INPUTS.json')
for name,pin in inputs['cost_payload_pins'].items(): need(sha(ROOT/name)==pin,'cost capsule '+name)
config=load(RUNTIME/'CONFIG.json')
result={phase:cost(phase,load(RUNTIME/phase/'RUN.json'),inputs,config) for phase in ['baseline','both']}
for phase,value in result.items(): need(not value['hotMismatches'],'clean hot loop mismatch')
comparisons={}
for group, buckets in result['baseline']['groups'].items():
    comparisons[group]={}
    for bucket,base in buckets.items():
        candidate=result['both']['groups'][group][bucket]
        comparisons[group][bucket]={'baseline':base,'both':candidate,'medianDeltaMs':candidate['medianMs']-base['medianMs']}
result['comparisons']=comparisons
(HERE/'COST.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'COST-READ-PINS.json').write_text(json.dumps(read_pins,indent=2)+'\n')
print(json.dumps({phase:{k:result[phase][k] for k in ['rows','progress','queryReads','recoveryMismatches','hotMismatches','cleanupVerified']} for phase in ['baseline','both']},indent=2))
