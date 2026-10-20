import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Use python3 -I -S without optimization')
from pathlib import Path
import hashlib
import json
import stat

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def load(name):
    return json.loads((ROOT / name).read_text())

manifest = load('FILES.json')
names = {'FILES.json', 'FREEZE.json'}
for row in manifest:
    name = row['path']
    require(name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts, 'manifest path')
    names.add(name)
actual = set()
for p in ROOT.rglob('*'):
    mode = p.lstat().st_mode
    require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), 'nonregular input')
    if stat.S_ISREG(mode):
        actual.add(p.relative_to(ROOT).as_posix())
require(names == actual, 'file roster')
for row in manifest:
    data = (ROOT / row['path']).read_bytes()
    require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'input identity')
require(load('FREEZE.json')['FILES_sha256'] == hashlib.sha256((ROOT / 'FILES.json').read_bytes()).hexdigest(), 'seal')
receipt = load('v2/runtime-v1/RUN.json')
raw = load('v2/runtime-v1/raw.json')
require(receipt['pins_before'] == receipt['pins_after'] and receipt['stable_pins'], 'runtime stability')
require(raw['complete'] and raw['visibility'] == 'visible' and receipt['callback_received'], 'runtime completion')
labels = [f'{phase}/{op}' for phase in ['synchronous', 'ready'] for op in ['add', 'delete', 'clear', 'add-existing', 'delete-missing', 'clear-empty']]
labels += ['completed/clear', 'completed/add', 'completed/delete', 'old-during-new/add', 'old-during-new/delete', 'old-during-new/clear']
require([r['label'] for r in raw['rows']] == labels, 'case roster')

def expected(alpha, beta, active):
    return dict(alpha=alpha, beta=beta, childMatches=False, active=active,
                color='rgb(0, 0, 255)' if beta else 'rgb(0, 128, 0)' if alpha else 'rgb(10, 20, 30)',
                width='61px' if beta else '43px' if alpha else '17px')

failures = []
for row in raw['rows']:
    phase, op = row['label'].split('/')
    if phase in ['synchronous', 'ready']:
        before = expected(op in ['delete', 'clear', 'add-existing'], False, True)
        after = expected(op in ['add', 'add-existing'], False, True)
        require(row['operation']['types'] == (['alpha'] if after['alpha'] else []), 'public set')
        require(row['operation']['activeIdentity'], 'active identity')
    else:
        before = after = expected(False, phase == 'old-during-new', phase == 'old-during-new')
    require(row['before'] == before and row['beforeExpected'] == before, 'baseline calibration')
    require(row['expected'] == after and row['refreshed'] == after, 'independent expected/refreshed styles')
    observed = [key for key in after if row['actual'][key] != after[key]]
    want = ['color', 'width'] if phase in ['synchronous', 'ready'] and op in ['add', 'delete', 'clear'] else []
    require(observed == want and row['failures'] == want, 'discrepancy identity')
    if want:
        require(row['actual']['color'] == before['color'] and row['actual']['width'] == before['width'], 'stale cached result')
        failures.append(row['label'])
print(json.dumps({'status': 'PASS', 'rows': 18, 'discrepancies': failures, 'controls': 12,
                  'scope': 'recorded calibrated development-browser result; proposed WPT is not executed here'}))
