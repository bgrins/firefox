import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require python3 -I -S without optimization")
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,stat
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/"FILES.json").read_text())
expected={"FILES.json","FREEZE.json"}|{r["path"] for r in rows}
actual=set()
for f in ROOT.rglob("*"):
    if f.is_symlink(): raise ValueError("symlink")
    if f.is_file():
        if not stat.S_ISREG(f.lstat().st_mode): raise ValueError("nonregular")
        actual.add(f.relative_to(ROOT).as_posix())
if actual!=expected: raise ValueError("receipt roster")
for row in rows:
    f=ROOT/row["path"]
    if f.stat().st_size!=row["bytes"] or hashlib.sha256(f.read_bytes()).hexdigest()!=row["sha256"]: raise ValueError(row["path"])
freeze=json.loads((ROOT/"FREEZE.json").read_text())
for field,file in [("FILES_sha256","FILES.json"),("check_sha256","check.py")]:
    if freeze[field]!=hashlib.sha256((ROOT/file).read_bytes()).hexdigest(): raise ValueError("seal")
capsule=ROOT/"relocated-capsule"
m=json.loads((capsule/"FILES.json").read_text())
if {f.relative_to(capsule).as_posix() for f in capsule.rglob("*") if f.is_file()}!={"FILES.json","FREEZE.json"}|{r["path"] for r in m}: raise ValueError("nested producer closure")
for mode in ["canonical","relocated"]:
    result=json.loads((ROOT/mode/"RESULT.json").read_text())
    if result["replay"]!="PASS" or result["audits"]!=48 or result["native"]["cases"]!=1536: raise ValueError("replay receipt")
print("PASS: retained canonical/relocated results and closed source capsule; this checker does not rerun Lean")
