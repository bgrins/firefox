#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess
P=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'FILES.json').read_text());freeze=json.loads((P/'FREEZE.json').read_text())
assert sha(P/'FILES.json')==freeze['FILES_sha256']
expected={x['path'] for x in m['files']}|{'FILES.json','FREEZE.json'}
actual={str(x.relative_to(P)) for x in P.rglob('*') if not x.is_dir()}
assert expected==actual,'outer closed file roster'
dirs={str(p) for f in expected for p in pathlib.Path(f).parents if str(p)!='.'}
assert {str(x.relative_to(P)) for x in P.rglob('*') if x.is_dir()}==dirs,'outer closed directory roster'
for x in m['files']:
 p=P/x['path'];assert not p.is_symlink() and sha(p)==x['sha256'] and p.stat().st_size==x['bytes'],x['path']
assert sha(P/'REPORT.md')==freeze['REPORT_sha256']
subprocess.run(['python3',str(P/'verify_inputs.py')],check=True)
print('Sealed native review verified:',len(m['files']),'payload files')
