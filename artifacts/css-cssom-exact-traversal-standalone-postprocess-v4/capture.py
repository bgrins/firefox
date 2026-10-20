import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S without -O')
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
EXPECTED = json.loads((ROOT / 'EXPECTED-PINS.json').read_text())
SOURCE = ROOT.parent / EXPECTED['runtime_directory']
DEST = ROOT / 'runtime-capture'
sha = lambda b: hashlib.sha256(b).hexdigest()

def require(ok, message):
    if not ok:
        raise SystemExit(message)

require(sys.argv[1:] == ['--terminal-confirmed'], 'Root terminal notice required')
require(not DEST.exists(), 'Capture already exists')
state = json.loads((SOURCE / 'STATE.json').read_text())
require(state['status'] in ['terminal', 'terminal-failed'], 'Experiment not terminal')
for name, pin in EXPECTED['inputs'].items():
    require(sha((SOURCE / name).read_bytes()) == pin, 'Reviewed input changed: ' + name)

def roster():
    result = {}
    for path in SOURCE.rglob('*'):
        require(not path.is_symlink(), 'Symlink in runtime')
        if path.is_file():
            result[path.relative_to(SOURCE).as_posix()] = sha(path.read_bytes())
    return result

before = roster()
shutil.copytree(SOURCE, DEST)
after = roster()
require(before == after, 'Runtime changed during capture; preserve and investigate')
for name, pin in before.items():
    require(sha((DEST / name).read_bytes()) == pin, 'Capture mismatch: ' + name)
(ROOT / 'CAPTURE.json').write_text(json.dumps({'source': str(SOURCE),
    'state': state['status'], 'files': before, 'stable_during_capture': True,
    'runtime_modified': False}, indent=2) + '\n')
print(json.dumps({'captured_files': len(before), 'terminal_state': state['status']}))
