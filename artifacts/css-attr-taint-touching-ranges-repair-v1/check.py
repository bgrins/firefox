import hashlib,json,difflib
from pathlib import Path
r=Path(__file__).resolve().parent
for f,h in json.loads((r/"MANIFEST.json").read_text())["files"].items():
 assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f
f="servo/components/style/custom_properties.rs"
a=(r/"source/original"/f).read_text();b=(r/"source/candidate"/f).read_text()
assert b==a.replace(".any(|r| r.start <= range.end && r.end >= range.start)",".any(|r| r.start.max(range.start) < r.end.min(range.end))")
assert (r/"native.patch").read_text()=="".join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile="a/"+f,tofile="b/"+f))
raw=[json.loads(x) for x in (r/"baseline/raw.json").read_text().splitlines()]
rows=[x for x in raw if x.get("action")=="test_status"]
assert len(rows)==5 and len({x["subtest"] for x in rows})==5
assert [(x["subtest"],x["status"]) for x in rows if x["status"]!="PASS"]==[("Touching untainted URL and attr resolution","FAIL")]
assert [x["status"] for x in raw if x.get("action")=="test_end"]==["OK"]
assert sum(x.get("action")=="suite_end" for x in raw)==1
count=0
for a in range(6):
 for b in range(a,6):
  for c in range(6):
   for d in range(c,6):
    assert (max(a,c)<min(b,d))==bool(set(range(a,b)) & set(range(c,d)))
    count+=1
print(f"Exact source delta; retained baseline1FAIL4PASS; {count} mathematical range checks (not native execution)")
