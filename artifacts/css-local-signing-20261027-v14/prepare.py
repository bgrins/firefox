import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ident,title,*dirs=sys.argv[1:]
pins={}
for name in dirs:
 p=ROOT/'artifacts'/name;m=p/'FILES.json';data=json.loads(m.read_text());data=data.get('files',data)
 for n,h in data.items():
  f=p/n;digest=h['sha256'] if isinstance(h,dict) else h
  assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,(name,n)
  pins[str(f.relative_to(ROOT))]=digest
 pins[str(m.relative_to(ROOT))]=hashlib.sha256(m.read_bytes()).hexdigest()
item={'id':ident,'message':'No bug - '+title+'. r?#firefox-style-system-reviewers','files':sorted(pins),'source_pins':pins}
with (HERE/(ident+'-selection.json')).open('x') as f: json.dump(item,f,indent=2,sort_keys=True);f.write('\n')
print(ident,len(pins),flush=True)
