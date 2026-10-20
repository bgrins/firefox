import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items())
assert sha(p/'FILES.json')==f['files_sha256'] and len(m)==f['payload_files']
a=json.loads((p/'release/RESULT.json').read_text());b=json.loads((p/'project/RESULT.json').read_text())
assert a['stable'] and b['stable'] and a['before']==a['after'] and b['before']==b['after']
assert a['profile_removed'] and b['profile_removed'] and not (p/'release/profile').exists() and not (p/'project/profile').exists()
assert a['observations'][0]['rows']==b['observations'][0]['rows']
rows=a['observations'][0]['rows'];r=json.loads((p/'RECOUNT.json').read_text())
assert len(rows)==r['rows'] and all(x['calibrated'] and x['representable'] for x in rows)
print(len(rows),'identical release/project rows; observable discrepancy; source attribution pending')
