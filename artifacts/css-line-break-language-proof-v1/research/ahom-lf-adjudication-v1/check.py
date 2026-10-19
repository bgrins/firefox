import hashlib,json,re,collections
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/'MANIFEST.json').read_text())
for n,h in m['files'].items():
 q=p/n
 assert not q.is_symlink() and q.resolve().is_relative_to(p)
 assert hashlib.sha256(q.read_bytes()).hexdigest()==h,n
assert {str(q.relative_to(p)) for q in p.rglob('*') if q.is_file()}==set(m['files'])|{'MANIFEST.json','FREEZE.json'}
s=(p/'css-text3.html').read_text()
for a in ['text-encoding','white-space-property','line-break-transform','line-break-details','valdef-word-break-normal']:
 assert 'id="'+a+'"' in s,a
r=json.loads((p/'evidence/project-v1-receipt.json').read_text())
a=[json.loads(l) for l in (p/'evidence/project-v1.jsonl').read_text().splitlines()]
a=[x for x in a if x['action'] in ['test_status','test_end']]
assert [(x.get('subtest'),x['status']) for x in a]==[(x.get('subtest'),x['status']) for x in r['statuses']]
assert collections.Counter(x['status'] for x in a)=={'PASS':305,'FAIL':8,'OK':1}
assert r['pins_before']==r['pins_after']
for n,sha in [('pr8143.json','fb5e25f59bb1addb8da87d592ecb810923383257'),('pr8144.json','a9cbb9cda7cc0b1e832ace6a0f633fc6a3f3726d')]:
 j=json.loads((p/n).read_text());assert j['merged'] and j['merge_commit_sha']==sha
print('authenticated',len(m['files']),'files; raw browser and primary-source checks passed')
