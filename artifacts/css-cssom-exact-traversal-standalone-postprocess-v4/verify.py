import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S without -O')
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def require(ok, message):
    if not ok:
        raise SystemExit(message)

require(len(sys.argv) == 3 and sys.argv[1] == '--files-sha256', 'verify.py --files-sha256 PIN')
raw = (ROOT / 'FILES.json').read_bytes()
require(sha(raw) == sys.argv[2], 'External manifest pin')
files = json.loads(raw)
actual = set()
for path in ROOT.rglob('*'):
    require(not path.is_symlink(), 'Symlink')
    if path.is_file():
        actual.add(path.relative_to(ROOT).as_posix())
require(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'Closed roster')
for name, pin in files.items():
    require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe path')
    require(sha((ROOT / name).read_bytes()) == pin, 'Payload: ' + name)
freeze = json.loads((ROOT / 'FREEZE.json').read_text())
require(freeze['files_sha256'] == sys.argv[2] and freeze['payloads'] == len(files), 'Freeze')
require(freeze['verifier_sha256'] == sha(Path(__file__).read_bytes()), 'Verifier pin')
require(freeze['report_sha256'] == sha((ROOT / 'REPORT.md').read_bytes()), 'Report pin')
result = subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT / 'analyze.py'), '--check'],
                        capture_output=True, text=True)
require(result.returncode == 0, result.stdout + result.stderr)
print(json.dumps({'status': 'PASS_PRODUCER_POSTPROCESSING', 'payloads': len(files),
                  'analysis': json.loads(result.stdout), 'independent_review': False}))
