import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / 'css-hidden-query-boundaries-runtime-v2'
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_bytes())
def mapped(rows):
    result = {(r['test'], r['subtest']): (r['status'], r.get('message')) for r in rows}
    need(len(result) == len(rows), 'duplicate rows')
    return result

parser = argparse.ArgumentParser()
parser.add_argument('phase', choices=['baseline', 'column-provider', 'skipped-line-block', 'both',
                    'standalone-baseline', 'standalone-column-provider', 'standalone-skipped-line-block'])
args = parser.parse_args()
need(sha(RUNTIME/'INPUTS.json') == '7f8b3a0e3d5892d65a1a6472f283a7c942f4f172b10ca4b7630f0bfb51ee4fbd', 'INPUTS')
inputs = load(RUNTIME/'INPUTS.json')
for name, pin in inputs['payload_pins'].items():
    need(sha(RUNTIME/name) == pin, 'payload '+name)
config = load(RUNTIME/'CONFIG.json')
run = load(RUNTIME/args.phase/'RUN.json')
raw_path = RUNTIME/args.phase/'raw.json'
events = [json.loads(line) for line in raw_path.read_bytes().splitlines() if line]
rows = [e for e in events if e.get('action') == 'test_status']
ends = [e for e in events if e.get('action') == 'test_end']
values = mapped(rows)
need(run['complete'] and run['exit'] in [0, 1] and run['before'] == run['after']
     and mapped(run['rows']) == values and run['ends'] == ends, 'complete raw/RUN join')
need(len(rows) == 100 and len(ends) == 10 and len({r['test'] for r in ends}) == 10
     and all(r['status'] == 'OK' for r in ends) and sum(e.get('action') == 'suite_end' for e in events) == 1,
     'complete100/10')
for url, names in config['expected_subtests'].items():
    need([r['subtest'] for r in rows if r['test'] == url] == names, 'ordered identities')
need(all(v[0] in ['PASS', 'FAIL'] for v in values.values()), 'status domain')
for name, pin in inputs['resource_pins'].items():
    need(run['before'][name] == pin, 'resource join '+name)
standalone = args.phase.startswith('standalone-')
basephase = args.phase.removeprefix('standalone-')
roles = {'layout/base/PresShell.cpp': 'pres-shell-column.cpp' if basephase in ['column-provider', 'both'] else 'pres-shell-before.cpp',
         'layout/generic/nsBlockFrame.cpp': 'block-skipped-line.cpp' if basephase in ['skipped-line-block', 'both'] else 'block-before.cpp',
         'layout/generic/nsFlexContainerFrame.cpp': 'flex-without104.cpp' if standalone else 'flex-accepted.cpp',
         'layout/generic/AbsoluteContainingBlock.cpp': 'absolute-without105.cpp' if standalone else 'absolute-accepted.cpp'}
for name in config['guard_sources']:
    pin = sha(RUNTIME/'selected'/roles[name]) if name in roles else (
        sha(RUNTIME/'prepared/head'/name) if name in config['sources'] else inputs['source_pins'][name])
    need(run['before'][name] == pin, 'native role '+name)
need(load(RUNTIME/(args.phase+'-build.json'))['exit'] == 0, 'build exit')
prior = load(RUNTIME/'evidence/prior-baseline-RUN.json')
oldkeys = set(mapped(prior['rows']))
compact = {k for k in values if k[0].endswith('/hidden-skipped-block-line-queries.html')}
span = {k for k in values if k[0].endswith('/hidden-table-span-queries.html')}
auto = {k for k in values if k[0].endswith('/hidden-column-auto-scroll.html')}
tracked = {k for k in values if 'testing/web-platform/tests'+k[0] in config['tracked_tests']}
need([len(oldkeys), len(compact), len(span), len(auto), len(tracked)] == [66, 18, 12, 4, 50], 'partitions')
oracle = RUNTIME/'evidence'/('prior-'+args.phase+'-RUN.json')
if oracle.exists():
    expected = load(oracle)
    need({k:values[k] for k in oldkeys} == mapped(expected['rows']), 'historical66 oracle')
groups = {'prior66': oldkeys, 'compact18': compact, 'span12': span, 'auto4': auto,
          'tracked50': tracked, 'candidate50': set(values)-tracked}
failures = [{'test': k[0], 'subtest': k[1], 'message': v[1],
             'calibration': any(t in (v[1] or '').lower() for t in ['calibration', 'independently constructed visible reference'])}
            for k, v in sorted(values.items()) if v[0] == 'FAIL']
result = {'phase': args.phase, 'counts': dict(Counter(v[0] for v in values.values())),
          'subsets': {name: dict(Counter(values[k][0] for k in keys)) for name, keys in groups.items()},
          'failures': failures, 'calibrationFailures': sum(v['calibration'] for v in failures),
          'raw_sha256': sha(raw_path), 'RUN_sha256': sha(RUNTIME/args.phase/'RUN.json'),
          'historical66_exact': oracle.exists(), 'source28_resource_joins': True,
          'final_restoration_reviewed': False}
baseline_path = RUNTIME/('standalone-baseline' if standalone else 'baseline')/'RUN.json'
if baseline_path.exists():
    baseline = load(baseline_path)
    need(baseline['complete'], 'family baseline incomplete')
    baseline = mapped(baseline['rows'])
    result['transitions'] = {name: dict(Counter(baseline[k][0]+'->'+values[k][0] for k in keys)) for name, keys in groups.items()}
    result['changes'] = [{'test': k[0], 'subtest': k[1], 'before': baseline[k], 'after': values[k]}
                         for k in sorted(values) if baseline[k] != values[k]]
(HERE/(args.phase+'.json')).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({n:result[n] for n in ['phase', 'counts', 'subsets', 'calibrationFailures']}))
