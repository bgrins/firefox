import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("isolated unoptimized Python required")
sys.dont_write_bytecode=True
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parent
S=R/"relocated-capsule"
M="3c22b32c3840977fcb195a5aa0eb28e1e324417014b027a8140a87c8ff4c5cee"
results=[]
for name in ["optimize","double-optimize","unsafe-shadow","site-enabled","empty-dir","fifo","nested-source","output-inside"]:
    with tempfile.TemporaryDirectory(prefix="sentinel-review-guard-") as t:
        w=Path(t); s=w/"capsule";shutil.copytree(S,s); output=w/"out";flags=["-I","-S"]
        if name=="optimize": flags += ["-O"]
        if name=="double-optimize": flags += ["-OO"]
        if name=="unsafe-shadow":
            flags=["-S"];(s/"json.py").write_text("from pathlib import Path\nPath("+repr(str(w/"EXECUTED"))+").write_text('bad')\n")
        if name=="site-enabled": flags=["-I"]
        if name=="empty-dir": (s/"extra").mkdir()
        if name=="fifo": os.mkfifo(s/"fifo")
        if name=="nested-source":
            f=s/"native-source/core.py";f.write_text(f.read_text()+"\n")
        if name=="output-inside": output=s/"output"
        p=subprocess.run([sys.executable,*flags,str(s/"check.py"),"--manifest-sha",M,"--output",str(output)],capture_output=True,text=True)
        (R/("guard-"+name+".log")).write_text(p.stdout+p.stderr)
        if p.returncode==0 or output.exists() or (w/"EXECUTED").exists(): raise RuntimeError(name)
        results.append({"name":name,"exit":p.returncode,"before_output":True,"shadow_not_executed":True})
(R/"GUARDS.json").write_text(json.dumps(results,indent=2)+"\n")
lean=Path(json.loads((S/"LEAN-TOOLCHAIN.json").read_text())["root"])/"bin/lean"
results=[]
for name in ["sorry","custom"]:
    with tempfile.TemporaryDirectory(prefix="sentinel-review-axiom-") as t:
        w=Path(t);shutil.copytree(S/"lean",w/"lean")
        for f in ["check_lean.py","AUDIT-ROSTER.json"]:shutil.copyfile(S/f,w/f)
        f=w/"lean/MaskedSticky.lean";text=f.read_text();old="native auto none n l = n := rfl"
        if text.count(old)!=1:raise RuntimeError("site")
        if name=="sorry":text=text.replace(old,"native auto none n l = n := by sorry")
        else:
            text=text.replace("theorem missing_identity", "axiom reviewBad : False\ntheorem missing_identity")
            text=text.replace(old,"native auto none n l = n := False.elim reviewBad")
        f.write_text(text);output=R/("axiom-"+name)
        p=subprocess.run([sys.executable,"-I","-S",str(w/"check_lean.py"),"--lean",str(lean),"--output",str(output)],capture_output=True,text=True)
        (R/("axiom-"+name+".log")).write_text(p.stdout+p.stderr)
        if p.returncode==0 or "unsupported axiom" not in p.stderr or (output/"FAILED.json").exists():raise RuntimeError(name)
        results.append({"name":name,"exit":p.returncode,"compiled_but_axiom_rejected":True})
(R/"AXIOMS.json").write_text(json.dumps(results,indent=2)+"\n")
print("8 guards and 2 axiom controls passed")
