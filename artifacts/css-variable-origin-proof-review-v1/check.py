import sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError("use -I -S")
import hashlib,json,pathlib,re
r=pathlib.Path(__file__).resolve().parent
files=json.loads((r/"FILES.json").read_text())
assert {p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file()}==set(files)|{"FILES.json","FREEZE.json"}
for n,h in files.items():
 p=r/n
 assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==h,n
assert hashlib.sha256((r/"FILES.json").read_bytes()).hexdigest()==json.loads((r/"FREEZE.json").read_text())["files_sha256"]
result=json.loads((r/"replay-output/RESULT.json").read_text());assert result["status"]=="PASS" and result["audits"]==88
assert result["native"]["rows_per_variant"]==49 and result["native"]["results"]["candidate"]["differences"]==[]
audit=(r/"replay-output/AXIOMS.txt").read_text();names=re.findall(r"'(VariableOrigin\.\w+)' (?:depends on axioms:|does not depend on any axioms)",audit);assert len(names)==88 and len(set(names))==88
for name in ["optimized","double-optimized"]:
 q=json.loads((r/("guard-existing-tool-"+name+".json")).read_text());assert q["output_created"] and len(q["dispatched"])==1 and q["dispatched"][0][0]=="/usr/bin/true"
q=json.loads((r/"guard-existing-tool-normal.json").read_text());assert not q["output_created"] and not q["dispatched"] and q["exception"]=="AssertionError()"
assert len(json.loads((r/"oracle-challenges/RESULT.json").read_text()))==5
assert len(json.loads((r/"integrity-output/RESULT.json").read_text())["controls"])==8
print("PASS independent v1 review evidence; capsule acceptance BLOCKED by optimizer guard")
