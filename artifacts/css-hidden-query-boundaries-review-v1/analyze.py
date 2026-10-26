import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / 'css-hidden-query-boundaries-runtime-v1'
ROOT = HERE.parents[1]
PHASES = ['baseline', 'column-provider', 'skipped-line-block', 'both',
          'standalone-baseline', 'standalone-column-provider', 'standalone-skipped-line-block']
INPUTS_PIN = 'e75b88af92bb13e975ee9eb26062cb403179e0e061a813cc5e34895a9435099b'
read_pins = {}

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    read_pins[str(path)] = sha(path)
    return json.loads(path.read_bytes())

def events(path):
    read_pins[str(path)] = sha(path)
    return [json.loads(line) for line in path.read_bytes().splitlines() if line]

def mapping(rows):
    result = {(r['test'], r['subtest']): (r['status'], r.get('message')) for r in rows}
    need(len(result) == len(rows), 'duplicate subtests')
    return result

def endmap(rows):
    result = {r['test']: r['status'] for r in rows}
    need(len(result) == len(rows), 'duplicate harness end')
    return result

def calibration(message):
    return any(n in (message or '').lower() for n in
               ['calibration', 'independently constructed visible reference'])

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

parser = argparse.ArgumentParser()
parser.add_argument('--phase', choices=PHASES, action='append', default=[])
parser.add_argument('--cost', choices=['baseline', 'both'], action='append', default=[])
parser.add_argument('--final-files-sha256')
args = parser.parse_args()
need(sha(RUNTIME / 'INPUTS.json') == INPUTS_PIN, 'prepared inputs')
inputs = load(RUNTIME / 'INPUTS.json')
need(inputs['before']['head'] == '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e', 'prepared HEAD')
for name, pin in inputs['payload_pins'].items():
    need(not Path(name).is_absolute() and '..' not in Path(name).parts
         and not (RUNTIME / name).is_symlink() and sha(RUNTIME / name) == pin, 'payload ' + name)
for name, pin in inputs['cost_payload_pins'].items():
    need(sha(ROOT / name) == pin, 'cost external ' + name)
need(sha(RUNTIME / 'DRAFT-FILES.json') == inputs['draft_sha256'], 'draft seal')
config = load(RUNTIME / 'CONFIG.json')
expected = {(url, name) for url, names in config['expected_subtests'].items() for name in names}
need(len(expected) == 104 and len(config['tests']) == 9 and len(config['install']) == 4, 'roster')
prior = {name: load(RUNTIME / 'evidence' / ('prior-' + name + '-RUN.json'))
         for name in PHASES[:4] + ['standalone-baseline']}
oldkeys = set(mapping(prior['baseline']['rows']))
compact = {k for k in expected if k[0].endswith('/hidden-skipped-block-line-queries.html')}
provider = expected - oldkeys - compact
tracked = {k for k in expected if 'testing/web-platform/tests' + k[0] in config['tracked_tests']}
need([len(oldkeys), len(compact), len(provider), len(tracked)] == [66, 18, 20, 50], 'subsets')
result = {'final': bool(args.final_files_sha256), 'input_payloads': len(inputs['payload_pins']),
          'external_cost_pins': len(inputs['cost_payload_pins']), 'phases': {}, 'cost': {}}
retained = {}
for phase in args.phase:
    raw = events(RUNTIME / phase / 'raw.json')
    rows = [e for e in raw if e.get('action') == 'test_status']
    ends = [e for e in raw if e.get('action') == 'test_end']
    values, harness = mapping(rows), endmap(ends)
    need(set(values) == expected and len(harness) == 9 and set(harness.values()) == {'OK'}
         and sum(e.get('action') == 'suite_end' for e in raw) == 1, 'complete raw roster')
    for url, names in config['expected_subtests'].items():
        need([r['subtest'] for r in rows if r['test'] == url] == names, 'ordered roster')
    run = load(RUNTIME / phase / 'RUN.json')
    need(run['complete'] and run['before'] == run['after'] and run['exit'] in [0, 1]
         and mapping(run['rows']) == values and endmap(run['ends']) == harness, 'RUN/raw integrity')
    need(all(v[0] in ['PASS', 'FAIL'] for v in values.values()), 'status domain')
    standalone = phase.startswith('standalone-')
    replacements = {'layout/base/PresShell.cpp': 'pres-shell-column.cpp' if phase in ['column-provider', 'both', 'standalone-column-provider'] else 'pres-shell-before.cpp',
                    'layout/generic/nsBlockFrame.cpp': 'block-skipped-line.cpp' if phase in ['skipped-line-block', 'both', 'standalone-skipped-line-block'] else 'block-before.cpp',
                    'layout/generic/nsFlexContainerFrame.cpp': 'flex-without104.cpp' if standalone else 'flex-accepted.cpp',
                    'layout/generic/AbsoluteContainingBlock.cpp': 'absolute-without105.cpp' if standalone else 'absolute-accepted.cpp'}
    for name in config['guard_sources']:
        pin = sha(RUNTIME / 'selected' / replacements[name]) if name in replacements else (
            sha(RUNTIME / 'prepared/head' / name) if name in config['sources'] else inputs['source_pins'][name])
        need(run['before'][name] == pin, 'source role ' + name)
    for name, pin in inputs['resource_pins'].items():
        need(run['before'][name] == pin, 'resource join ' + name)
    for name, pin in run['before'].items():
        if pin is not None and '/Contents/MacOS/' not in name:
            need(sha(RUNTIME / phase / 'inputs' / name) == pin, 'retained phase input ' + name)
    need(load(RUNTIME / (phase + '-build.json'))['exit'] == 0, 'phase build')
    if phase in prior:
        need({k:values[k] for k in oldkeys} == mapping(prior[phase]['rows']), 'historical66 outcomes')
        need(all(harness[k] == v for k, v in endmap(prior[phase]['ends']).items()), 'historical harness')
    subsets = {'old66': oldkeys, 'compact18': compact, 'provider20': provider,
               'tracked50': tracked, 'candidate54': expected - tracked}
    failures = [{'test': k[0], 'subtest': k[1], 'message': v[1], 'calibration': calibration(v[1])}
                for k, v in sorted(values.items()) if v[0] == 'FAIL']
    result['phases'][phase] = {'counts': dict(Counter(v[0] for v in values.values())),
        'subsets': {n: dict(Counter(values[k][0] for k in keys)) for n, keys in subsets.items()},
        'failures': failures, 'calibrationFailures': [v for v in failures if v['calibration']],
        'harness': harness, 'exit': run['exit']}
    retained[phase] = values
    if phase in args.cost:
        result['cost'][phase] = cost(phase, run, inputs, config)
result['comparisons'] = {}
for phase, values in retained.items():
    base = 'standalone-baseline' if phase.startswith('standalone-') else 'baseline'
    if base in retained:
        result['comparisons'][phase] = {name: dict(Counter(retained[base][k][0] + '->' + values[k][0] for k in keys))
            for name, keys in [('all104', expected), ('tracked50', tracked), ('candidate54', expected - tracked)]}
if all(p in retained for p in PHASES[:4]):
    result['main_patterns'] = dict(Counter('/'.join(retained[p][k][0] for p in PHASES[:4]) for k in expected))
if args.final_files_sha256:
    need(sha(RUNTIME / 'FILES.json') == args.final_files_sha256, 'final seal')
    manifest = load(RUNTIME / 'FILES.json')
    manifest = manifest.get('files', manifest)
    for name, pin in manifest.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts
             and not (RUNTIME / name).is_symlink() and sha(RUNTIME / name) == pin, 'final payload')
    actual = {str(p.relative_to(RUNTIME)) for p in RUNTIME.rglob('*') if p.is_file()}
    need(actual - set(manifest) <= {'FILES.json', 'FREEZE.json'}, 'unlisted output')
    state = load(RUNTIME / 'STATE.json')
    need(state['status'] == 'terminal' and state['restored'] and state['restore_build_exit'] == 0
         and not state['recovery_errors'], 'restoration')
    need(load(RUNTIME / 'BEFORE.json') == load(RUNTIME / 'FINAL.json') == inputs['before'], 'historical restoration join')
    result['runtimeFailure'] = state.get('failure')
    result['restoration'] = {'beforeEqualsFinal': True, 'restoreBuild': 0, 'runtimeSeal': args.final_files_sha256,
                             'payloads': len(manifest), 'completedPhasesReviewed': args.phase}
suffix = 'FINAL' if args.final_files_sha256 else '-'.join(args.phase) or 'INPUTS'
(HERE / (suffix + '.json')).write_text(json.dumps(result, indent=2) + '\n')
(HERE / (suffix + '-READ-PINS.json')).write_text(json.dumps(read_pins, indent=2) + '\n')
print(json.dumps({'phases': {k:v['counts'] for k,v in result['phases'].items()}, 'final': result['final']}))
