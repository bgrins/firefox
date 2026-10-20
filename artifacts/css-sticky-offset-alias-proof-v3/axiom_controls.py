import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
out=ROOT/"axiom-controls-v1"
if out.exists():raise RuntimeError("output exists")
out.mkdir();receipts=[]
for name,body,error in [("custom-axiom","by\n  exact False.elim injectedUnsound","unsupported axiom"),("sorry","by\n  sorry","Lean warning OffsetEncoding")]:
    folder=out/(name+"-source");shutil.copytree(ROOT/"capsule",folder)
    path=folder/"lean/OffsetEncoding.lean";text=path.read_text()
    start=text.index("theorem reserved_code_unreachable")
    proof=text.index(":= by",start);end=text.index("\n\ntheorem auto_exactly",proof)
    text=text[:proof]+":= "+body+text[end:]
    if name=="custom-axiom":text=text.replace("theorem reserved_code_unreachable","axiom injectedUnsound : False\n\ntheorem reserved_code_unreachable")
    path.write_text(text)
    transfer=json.loads((folder/"TRANSFER-v1.json").read_text())
    for entry in transfer:
        if entry["source"].endswith("/lean/OffsetEncoding.lean"):entry["sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    (folder/"TRANSFER-v1.json").write_text(json.dumps(transfer,indent=2)+"\n")
    entries=[{"path":str(f.relative_to(folder)),"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(folder.rglob("*")) if f.is_file() and str(f.relative_to(folder)) not in ["FILES.json","FREEZE.json"]]
    (folder/"FILES.json").write_text(json.dumps({"files":entries},indent=2)+"\n");digest=hashlib.sha256((folder/"FILES.json").read_bytes()).hexdigest();(folder/"FREEZE.json").write_text(json.dumps({"files_sha256":digest})+"\n")
    target=out/(name+"-output")
    command=[sys.executable,"-I","-S",str(folder/"check.py"),"--manifest-sha",digest,"--out",str(target)]
    proc=subprocess.run(command,capture_output=True,text=True,env={"PATH":"/usr/bin:/bin"})
    (out/(name+".log")).write_text(proc.stdout+proc.stderr)
    valid=proc.returncode!=0 and error in proc.stderr and not (target/"RESULT.json").exists() and not (target/"native").exists()
    record={"id":name,"command":command,"exit":proc.returncode,"expected":error,"pass":valid,"injected_source_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    receipts.append(record)
    if not valid:raise RuntimeError(name)
    (out/(name+"-OffsetEncoding.lean")).write_text(text)
    shutil.rmtree(folder)
removed=[]
for f in sorted(out.rglob("*")):
    if f.is_file() and (f.suffix in [".olean",".ilean",".ir"] or f.name.endswith((".olean.private",".olean.server"))):
        removed.append({"path":str(f.relative_to(out)),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"bytes":f.stat().st_size});f.unlink()
(out/"RESULT.json").write_text(json.dumps({"complete":True,"controls":receipts,"cleanup":removed},indent=2)+"\n")
print(json.dumps({"complete":True,"controls":len(receipts)}))
