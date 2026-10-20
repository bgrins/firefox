import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Use python3 -I -S without optimization')
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def closed(root,pin):
    raw=(root/'FILES.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==pin
    files=json.loads(raw);paths=list(root.rglob('*'));assert not any(f.is_symlink() for f in paths)
    assert sorted(files)==sorted(str(f.relative_to(root)) for f in paths if f.is_file() and str(f.relative_to(root)) not in ['FILES.json','FREEZE.json'])
    for name,value in files.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==value
    return len(files)

if len(sys.argv)!=3 or sys.argv[1]!='--files-sha256':raise SystemExit('verify.py --files-sha256 PIN')
count=closed(ROOT,sys.argv[2])
closed(ROOT/'capsule','e968c0a408a2024f50b4c92b8c172365e67a1d790e3de85d0e777f54cd28342f')
producer=ROOT/'capsule/producer'
closed(producer,'6af2a8ca93ea6129c2c37384e373bd1a9e65aa50ac0f8aa16dfbca4e99dfdfc5')
for row in json.loads((producer/'SOURCE-BINDINGS.json').read_text()):
    body=(producer/row['file']).read_bytes()[row['start_byte_utf8']:row['end_byte_utf8']]
    assert body==row['text'].encode() and hashlib.sha256(body).hexdigest()==row['sha256']
result=json.loads((ROOT/'replay/RESULT.json').read_text())
assert result['status']=='PASS' and result['independent_kernel_boundary_witnesses']==4 and result['axioms']==['propext']
assert all(row['exit']==0 for row in json.loads((ROOT/'replay/COMMANDS.json').read_text()))
assert not list(ROOT.rglob('*.olean')) and not list(ROOT.rglob('*.pyc'))
print(json.dumps({'payloads':count,'verdict':'ACCEPT_SELECTED_MODEL_WITH_EXPLICIT_NATIVE_ADMISSIONS','kernel_boundary_witnesses':4,'native_global_ownership_closure':False}))
