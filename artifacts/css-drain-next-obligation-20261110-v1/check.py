from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
h=lambda b:hashlib.sha256(b).hexdigest()
for name,r in json.loads((P/'SOURCES.json').read_text()).items():
 data=(P/'source'/name).read_bytes()
 assert h(data)==r['sha256'],name
 assert data==subprocess.check_output(['git','-c','core.fsmonitor=false','show',r['revision']+':'+name],cwd=ROOT),name
for name,r in json.loads((P/'EXCERPTS.json').read_text()).items():
 full=subprocess.check_output(['git','-c','core.fsmonitor=false','show',r['revision']+':'+r['path']],cwd=ROOT)
 assert h(full)==r['source_sha256'],name
 excerpt=b''.join(full.splitlines(keepends=True)[r['first_line']-1:r['last_line']])
 assert excerpt==(P/name).read_bytes() and h(excerpt)==r['sha256'],name
for r in json.loads((P/'REFERENCES.json').read_text()).values():assert h((P/r['copy']).read_bytes())==r['sha256']
for name,digest in json.loads((P/'FILES.json').read_text()).items():assert h((P/name).read_bytes())==digest,name
print('PASS:21 Git source objects,2 exact excerpts,context copies,and complete capsule hashes')
