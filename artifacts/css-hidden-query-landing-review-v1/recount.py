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
RUNTIME = HERE.parent/'css-hidden-query-landing-runtime-v1'
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_bytes())
def mapping(rows):
    result = {(r['test'], r['subtest']): (r['status'], r.get('message')) for r in rows}
    need(len(result) == len(rows), 'duplicate test identity')
    return result

parser = argparse.ArgumentParser()
parser.add_argument('phase', choices=['baseline','column-only','block-only','grid-only','all-three'])
args = parser.parse_args()
need(sha(RUNTIME/'INPUTS.json') == 'e582fdf18c401b30289fbaf26bf461c2f421808020718f263d83d176e55809fb', 'INPUTS')
inputs = load(RUNTIME/'INPUTS.json')
c = load(RUNTIME/'CONFIG.json')
run = load(RUNTIME/args.phase/'RUN.json')
raw = RUNTIME/args.phase/'raw.json'
events = [json.loads(line) for line in raw.read_bytes().splitlines() if line]
rows = [e for e in events if e.get('action') == 'test_status']
ends = [e for e in events if e.get('action') == 'test_end']
values = mapping(rows)
need(run['complete'] and run['exit'] in [0,1] and run['before'] == run['after']
     and mapping(run['rows']) == values and run['ends'] == ends, 'RUN/raw/stability')
need(len(rows) == 79 and len(ends) == 9 and len({e['test'] for e in ends}) == 9
     and all(e['status'] == 'OK' for e in ends)
     and sum(e.get('action') == 'suite_end' for e in events) == 1, '79/9 completeness')
for url, names in c['expected_subtests'].items():
    need([r['subtest'] for r in rows if r['test'] == url] == names, 'ordered names')
for name in c['guard_sources']:
    if name in c['phases'][args.phase]:
        pin = sha(RUNTIME/c['phases'][args.phase][name])
    elif name in c['baseline_sources']:
        pin = sha(RUNTIME/c['baseline_sources'][name])
    else:
        pin = inputs['source_pins'][name]
    need(run['before'][name] == pin, 'exact phase native role '+name)
for name, pin in inputs['resource_pins'].items():
    need(run['before'][name] == pin, 'resource join '+name)
need(load(RUNTIME/(args.phase+'-build.json'))['exit'] == 0, 'build exit')
tracked = {k for k in values if 'testing/web-platform/tests'+k[0] in c['tracked_tests']}
column = {k for k in values if k[0].endswith(('/hidden-table-column-size-query.html','/hidden-column-auto-scroll.html'))}
block = {k for k in values if k[0].endswith('/hidden-skipped-block-line-queries.html')}
grid = set(values)-tracked-column-block
need([len(tracked),len(column),len(block),len(grid)] == [50,7,14,8], 'partition')
predicted = mapping(load(RUNTIME/'EXPECTED-OUTCOMES.json')['phases'][args.phase])
need(set(predicted) == set(values), 'prediction identities')
failures = [{'test':k[0], 'subtest':k[1], 'message':v[1],
             'calibration': any(s in (v[1] or '').lower() for s in ['calibration','independently constructed visible reference'])}
            for k,v in sorted(values.items()) if v[0] == 'FAIL']
result = {'phase':args.phase, 'counts':dict(Counter(v[0] for v in values.values())),
          'subsets':{n:dict(Counter(values[k][0] for k in keys)) for n,keys in
                     [('tracked50',tracked),('column7',column),('block14',block),('grid8',grid)]},
          'failures':failures,'calibrationFailures':sum(r['calibration'] for r in failures),
          'predictionDifferences':[{'test':k[0],'subtest':k[1],'expected':predicted[k],'actual':values[k]}
                                   for k in sorted(values) if predicted[k] != values[k]],
          'raw_sha256':sha(raw),'RUN_sha256':sha(RUNTIME/args.phase/'RUN.json'),
          'native29ResourceJoins':True,'finalRestorationReviewed':False}
basepath = RUNTIME/'baseline/RUN.json'
if basepath.exists():
    base = mapping(load(basepath)['rows'])
    result['baselineTransitions'] = dict(Counter(base[k][0]+'->'+values[k][0] for k in values))
(HERE/(args.phase+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['phase','counts','subsets','calibrationFailures','predictionDifferences']}))
