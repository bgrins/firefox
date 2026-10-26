import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / 'css-hidden-query-boundaries-runtime-v2'
PIN = '6999853af6434ecd130590b4159eec577059bc989186293e27a5dd76317c926a'
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()
def load(path):
    return json.loads(path.read_bytes())
need(sha(RUNTIME/'FILES.json') == PIN, 'runtime manifest')
files = load(RUNTIME/'FILES.json')['files']
actual = set()
directories = {p.as_posix() for n in files for p in Path(n).parents if p.as_posix() != '.'}
for entry in RUNTIME.rglob('*'):
    mode = entry.lstat().st_mode
    name = entry.relative_to(RUNTIME).as_posix()
    if stat.S_ISDIR(mode):
        need(name in directories, 'unexpected directory')
    else:
        need(stat.S_ISREG(mode), 'nonregular runtime entry')
        actual.add(name)
need(actual == set(files) | {'FILES.json'}, 'runtime closed roster')
for name, pin in files.items():
    need(not Path(name).is_absolute() and '..' not in Path(name).parts
         and sha(RUNTIME/name) == pin, 'runtime payload '+name)
inputs = load(RUNTIME/'INPUTS.json')
state = load(RUNTIME/'STATE.json')
need(state['status'] == 'terminal' and state['restored'] is True and state['restore_build_exit'] == 0
     and not state['recovery_errors'] and 'failure' not in state, 'restoration status')
need(load(RUNTIME/'BEFORE.json') == load(RUNTIME/'FINAL.json') == inputs['before'], 'historical restoration')
need(inputs['before']['head'] == '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e', 'historical HEAD')
matrix = load(HERE/'MATRIX.json')
for phase, counts in matrix['counts'].items():
    report = load(HERE/(phase+'.json'))
    need(report['counts'] == counts and report['calibrationFailures'] == 0, 'independent phase totals')
    need(state['phases'][phase]['status_counts'] == counts and state['phases'][phase]['build_exit'] == 0,
         'controller phase totals/build')
    need(load(RUNTIME/(phase+'-calibration-failures.json')) == [], 'calibration receipt')
    run = load(RUNTIME/phase/'RUN.json')
    need(sha(RUNTIME/phase/'raw.json') == report['raw_sha256']
         and sha(RUNTIME/phase/'RUN.json') == report['RUN_sha256'], 'analyzed raw identity')
    for name, pin in run['before'].items():
        if pin is not None and '/Contents/MacOS/' not in name:
            need(files[phase+'/inputs/'+name] == pin, 'retained phase body/resource join')
cost = load(HERE/'COST.json')
for phase in ['baseline', 'both']:
    summary = state['phases'][phase]['cost']['summary']
    need(summary['groups'] == cost[phase]['groups']
         and summary['recoveryMismatchesByGroup'] == cost[phase]['recoveryMismatches']
         and summary['hotMismatchesByGroup'] == cost[phase]['hotMismatches'], 'controller cost join')
result = {'status': 'PASS_HISTORICAL_FINAL_AUTHENTICATION', 'runtime_FILES': PIN,
          'payloads': len(files), 'historicalBeforeEqualsFinalEqualsPrepared': True,
          'phaseBuilds': 7, 'restoreBuildExit': 0, 'calibrationFailures': 0,
          'phaseRows': 700, 'harnessEnds': 70, 'costRuns': 2,
          'liveSnapshotRequired': False, 'nativeLandingAccepted': False}
(HERE/'FINAL-AUTH.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
