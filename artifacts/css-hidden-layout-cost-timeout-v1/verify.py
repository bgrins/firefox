import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S')
sys.dont_write_bytecode=True
import argparse
import hashlib
import json
from pathlib import Path
import stat
p=argparse.ArgumentParser();p.add_argument('--files-sha256',required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(here/'FILES.json')!=a.files_sha256: raise RuntimeError('manifest pin')
m=json.loads((here/'FILES.json').read_text())
expected=set(m)|{'FILES.json','FREEZE.json'}
actual=set()
for f in here.rglob('*'):
    mode=f.lstat().st_mode
    if stat.S_ISDIR(mode):
        rel=str(f.relative_to(here))+'/'
        if not any(n.startswith(rel) for n in expected): raise RuntimeError('extra directory')
        continue
    if not stat.S_ISREG(mode): raise RuntimeError('nonregular entry')
    actual.add(str(f.relative_to(here)))
if actual!=expected: raise RuntimeError('file roster')
for n,v in m.items():
    if Path(n).is_absolute() or '..' in Path(n).parts: raise RuntimeError('unsafe path')
    if sha(here/n)!=v['sha256'] or (here/n).stat().st_size!=v['bytes']: raise RuntimeError('payload '+n)
if json.loads((here/'FREEZE.json').read_text())['FILES_sha256']!=a.files_sha256: raise RuntimeError('freeze join')
print(json.dumps({'status':'PASS','payloads':len(m)}))
