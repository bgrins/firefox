import ast,difflib,hashlib,json,runpy
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/"MANIFEST.json").read_text())
f=json.loads((p/"FREEZE.json").read_text())
assert hashlib.sha256((p/"MANIFEST.json").read_bytes()).hexdigest()==f["manifest_sha256"]
for name,digest in m["files"].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
ast.parse((p/"run.py").read_text())
pins=json.loads((p/"SOURCE-PINS.json").read_text())
for variant,files in pins.items():
 for name,digest in files.items():
  assert hashlib.sha256((p/"source"/variant/name).read_bytes()).hexdigest()==digest
patch="".join("".join(difflib.unified_diff((p/"source/original"/n).read_text().splitlines(True),(p/"source/candidate"/n).read_text().splitlines(True),"a/"+n,"b/"+n)) for n in pins["original"])
assert patch==(p/"native.patch").read_text()
expected=json.loads((p/"EXPECTED.json").read_text())
assert len(expected)==9 and sum(map(len,expected.values()))==82
module=runpy.run_path(str(p/"run.py"),run_name="authenticated_static_review")
nine=module["NINE"]
r=module["read_results"](p/"evidence/prior-nine-raw.json",{nine:expected[nine]})
assert len(r["rows"])==9 and sum(x["status"]=="FAIL" for x in r["rows"])==4
subset={k:v for k,v in expected.items() if k not in {nine,module["ATTR"]}}
r=module["read_results"](p/"evidence/enumeration-raw.json",subset)
assert len(r["rows"])==41 and all(x["status"]=="PASS" for x in r["rows"])
print("Authenticated source/diff, 82 identities, prior nine and 41 raw parser replay; build/browser NOT_RUN")
