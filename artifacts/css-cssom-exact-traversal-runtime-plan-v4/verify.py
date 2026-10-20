import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S without -O')
import argparse
import ast
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--files-sha256', required=True)
args = p.parse_args()
root = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def require(ok, message):
    if not ok:
        raise SystemExit(message)

raw = (root / 'FILES.json').read_bytes()
require(sha(raw) == args.files_sha256, 'Manifest pin')
files = json.loads(raw)
actual = set()
for path in root.rglob('*'):
    require(not path.is_symlink(), 'Symlink')
    if path.is_file():
        actual.add(path.relative_to(root).as_posix())
require(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'Closed roster')
for name, pin in files.items():
    require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe path')
    require(sha((root / name).read_bytes()) == pin, 'Payload: ' + name)
freeze = json.loads((root / 'FREEZE.json').read_text())
require(freeze['files_sha256'] == args.files_sha256, 'Freeze')
inputs = json.loads((root / 'INPUT-REVIEW.json').read_text())
for row in inputs['source_snapshots']:
    data = (root / row['role'] / row['file']).read_bytes()
    require(sha(data) == row['sha256'], 'Snapshot pin')
    if row['file'].endswith('.py'):
        ast.parse(data)
for name in ['run_browser.py', 'TESTS.json', 'getBoundingClientRect-untransformed-edge-precision.html',
             'probe.html', 'benchmark.js', 'capture.js']:
    require((root / 'reviewed-v3' / name).read_bytes() ==
            (root / 'draft-v4' / name).read_bytes(), 'Unchanged input: ' + name)
staged = json.loads((root / 'STAGED-STATE.json').read_text())
require(len(staged['staged_paths']) == 229 and staged['artifacts_only'] and
        not staged['runtime_overlap'] and not staged['index_writes_performed'], 'Staged review record')
print(json.dumps({'status': 'PASS_STATIC_PLAN', 'payloads': len(files),
                  'scope': 'reviewed driver snapshot; no runtime execution'}))
