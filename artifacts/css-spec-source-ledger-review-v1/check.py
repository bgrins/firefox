import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
source=json.loads((R/'SOURCE.json').read_text());raw=(R/'fragmentation.html').read_bytes();assert sha(raw)==source['sha256'] and len(raw)==source['bytes']
pub=json.loads((R/'PUBLISHED-SOURCE.json').read_text());assert sha((R/'published-cr.html').read_bytes())==pub['sha256']
s=raw.decode();i=s.index('id="unforced-breaks"');a=s.rfind('<h3',0,i);b=s.index('<h3',i);part=s[a:b].encode();assert part==(R/'unforced-breaks.html').read_bytes()
assert 'id="best-breaks"' in s[b:b+150]
audit=json.loads((R/'ACCOUNTING.json').read_text());assert audit['candidate']['start']==len(s[:a].encode()) and audit['candidate']['end']==len(s[:b].encode())
assert audit['section_units']==174 and audit['section_start_tags']['p']==5 and audit['section_start_tags']['dd']==4
requirements=json.loads((R/'requirements.json').read_text());assert len(requirements['requirements'])==13 and len({x['id'] for x in requirements['requirements']})==13
assert sha((R/'requirements.json').read_bytes())==audit['independent_inventory_sha256']
assert len(json.loads((R/'scenarios.json').read_text())['scenarios'])==8
roster=json.loads((R/'FILES.json').read_text());assert {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}==set(roster)|{'FILES.json'}
for n,h in roster.items():assert sha((R/n).read_bytes())==h,n
print(json.dumps({'status':'PASS','source_bytes':len(raw),'section_units':174,'requirement_candidates':13,'scenarios':8,'semantic_status':'proposed interpretation; no Lean or native conformance claim'}))
