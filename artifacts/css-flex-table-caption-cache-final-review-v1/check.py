import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
x=argparse.ArgumentParser();x.add_argument('--repo',required=True,type=Path);x.add_argument('--files-sha256',required=True);a=x.parse_args()
p=Path(__file__).resolve().parent;sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p/'FILES.json')==a.files_sha256
for n,h in json.loads((p/'FILES.json').read_text()).items():assert sha(p/n)==h,n
for n,h in json.loads((p/'INPUTS.json').read_text()).items():assert sha(a.repo/n)==h,n
r=a.repo/'artifacts/css-flex-table-caption-fix-runtime-v1'
for n,h in json.loads((r/'FILES.json').read_text()).items():assert sha(r/n)==h,n
z=subprocess.run([sys.executable,'-I','-S',str(r/'verify.py')],capture_output=True,text=True)
assert z.returncode==0,z.stderr
assert json.loads(z.stdout)==json.loads((p/'RUNTIME-RECHECK.json').read_text())
print('PASS: source-reviewed candidate and WPT runtime binding; formal scope separate')
