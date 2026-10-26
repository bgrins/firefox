import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import stat

parser = argparse.ArgumentParser()
parser.add_argument('--files-sha256', required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
need(sha(here / 'FILES.json') == args.files_sha256, 'manifest identity')
files = json.loads((here / 'FILES.json').read_text())
need({p.name for p in here.iterdir()} == set(files) | {'FILES.json', 'FREEZE.json'}, 'closed roster')
for name, pin in files.items():
    need(Path(name).name == name and stat.S_ISREG((here / name).lstat().st_mode)
         and sha(here / name) == pin, 'payload ' + name)
print(json.dumps({'verified': len(files), 'files_sha256': args.files_sha256}))
