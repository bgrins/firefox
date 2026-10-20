import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

a=argparse.ArgumentParser()
a.add_argument('--files-sha256',required=True)
a.add_argument('--repo',type=Path,required=True)
o=a.parse_args()
p=Path(__file__).resolve().parent
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p/'FILES.json')==o.files_sha256
files=json.loads((p/'FILES.json').read_text())
assert {str(q.relative_to(p)) for q in p.rglob('*') if q.is_file()}==set(files)|{'FILES.json','FREEZE.json'}
assert not any(q.is_symlink() for q in p.rglob('*'))
for n,h in files.items():assert sha(p/n)==h,n
inputs=json.loads((p/'INPUTS.json').read_text())
for n,h in inputs.items():assert sha(o.repo/n)==h,n
for dirname,receipt in [('css-overflow-relative-position-runtime-v1','RUNTIME-RECHECK.json'),('css-overflow-relative-position-rtl-runtime-v1','RTL-RECHECK.json')]:
    root=o.repo/'artifacts'/dirname
    for n,h in json.loads((root/'FILES.json').read_text()).items():
        assert not (root/n).is_symlink() and sha(root/n)==h,n
    r=subprocess.run([sys.executable,'-I','-S',str(root/'verify.py')],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    assert json.loads(r.stdout)==json.loads((p/receipt).read_text())
r=subprocess.run([sys.executable,'-I','-S',str(p/'coordinate-challenges.py')],capture_output=True,text=True)
assert r.returncode==0,r.stderr
assert json.loads(r.stdout)==json.loads((p/'COORDINATES.json').read_text())
print(json.dumps({'review':'GO_BOUNDED_NATIVE','runtime_payloads':497,'coordinate_cases':144,'formal_acceptance':False}))
