import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("isolated unoptimized Python required")
sys.dont_write_bytecode=True
from pathlib import Path
import os,shutil,subprocess,json,tempfile,hashlib,re
R=Path(__file__).resolve().parent
S=R/"relocated-capsule"
lean=Path(json.loads((S/"LEAN-TOOLCHAIN.json").read_text())["root"])/"bin/lean"
if hashlib.sha256(lean.read_bytes()).hexdigest()!="d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf":raise RuntimeError("Lean")
out=Path(sys.argv[1]).resolve();out.mkdir(exist_ok=False)
names=re.findall(r"^theorem (\w+)",(R/"Challenges.lean").read_text(),re.M)
with tempfile.TemporaryDirectory(prefix="sentinel-independent-lean-") as t:
    w=Path(t);env={k:v for k,v in os.environ.items() if not k.startswith("LEAN_")};env["LEAN_PATH"]=str(w)
    for n in ["MaskedSticky","StickyComposition","StickyLifecycle"]:shutil.copyfile(S/"lean"/(n+".lean"),w/(n+".lean"))
    shutil.copyfile(R/"Challenges.lean",w/"Challenges.lean")
    (w/"Audit.lean").write_text("import Challenges\n"+"\n".join("#print axioms Review."+n for n in names)+"\n")
    rows=[]
    for n in ["MaskedSticky","StickyComposition","StickyLifecycle","Challenges","Audit"]:
        p=subprocess.run([str(lean),"-o",str(w/(n+".olean")),str(w/(n+".lean"))],cwd=w,env=env,capture_output=True,text=True)
        (out/(n+".log")).write_text(p.stdout+p.stderr);rows.append({"module":n,"exit":p.returncode})
        if p.returncode:raise RuntimeError(n)
    lines=(out/"Audit.log").read_text().splitlines()
    if len(lines)!=len(names):raise RuntimeError("audit count")
    for name,line in zip(names,lines):
        m=re.fullmatch(r"'Review\."+name+r"' (?:does not depend on any axioms|depends on axioms: \[([^]]*)\])",line)
        if not m:raise RuntimeError("audit syntax")
        axioms=[] if not m.group(1) else m.group(1).split(", ")
        if not set(axioms)<={"propext","Quot.sound","Classical.choice"}:raise RuntimeError("axioms")
    (out/"RESULT.json").write_text(json.dumps({"status":"PASS","results":names,"compilations":rows,"temporary_products_removed":True},indent=2)+"\n")
print("10 independent kernel challenges passed")
