import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
x=argparse.ArgumentParser()
x.add_argument('--files-sha256',required=True)
x.add_argument('--repo',required=True,type=Path)
a=x.parse_args();p=Path(__file__).resolve().parent
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p/'FILES.json')==a.files_sha256
f=json.loads((p/'FILES.json').read_text())
assert {str(q.relative_to(p)) for q in p.rglob('*') if q.is_file()}==set(f)|{'FILES.json','FREEZE.json'}
assert not any(q.is_symlink() for q in p.rglob('*'))
for n,h in f.items():assert sha(p/n)==h,n
for n,h in json.loads((p/'INPUTS.json').read_text()).items():assert sha(a.repo/n)==h,n
r=a.repo/'artifacts/css-flex-table-caption-runtime-v1'
for n,h in json.loads((r/'FILES.json').read_text()).items():assert sha(r/n)==h,n
z=subprocess.run([sys.executable,'-I','-S',str(r/'verify.py')],capture_output=True,text=True)
assert z.returncode==0,z.stderr
assert json.loads(z.stdout)==json.loads((p/'BASELINE-RECHECK.json').read_text())
b=a.repo/'artifacts/css-flex-table-caption-cache-repair-v1'
def transform(s):
    first='    const LogicalSize mComputedSize;'
    second='        : mComputedSize(aRI.ComputedSize()),'
    assert s.count(first)==s.count(second)==1
    return s.replace(first,first+'\n    const LogicalSize mContainingBlockSize;').replace(second,second+'\n          mContainingBlockSize(aRI.mContainingBlockSize),')
assert transform((b/'source/nsFlexContainerFrame.cpp').read_text())==(b/'candidate.cpp').read_text()
assert transform((b/'standalone/upstream-before.cpp').read_text())==(b/'standalone/upstream-candidate.cpp').read_text()
print(json.dumps({'source':'GO','baseline_rows_per_browser':16,'baseline_failures':4,'candidate_runtime':'pending','formal_acceptance':False}))
