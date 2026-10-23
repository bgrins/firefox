import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib, json, os, pathlib, re, shutil, subprocess
root = pathlib.Path(__file__).resolve().parent
out = root / "independent-output"
out.mkdir(exist_ok=False)
tools = json.loads((root / "capsule/TOOLS.json").read_text())
lean = tools["lean"]["path"]
assert hashlib.sha256(pathlib.Path(lean).read_bytes()).hexdigest() == tools["lean"]["sha256"]
for name in ("Hidden", "Subtree"):
    shutil.copyfile(root / "capsule/lean" / (name + ".lean"), out / (name + ".lean"))
shutil.copyfile(root / "Independent.lean", out / "Independent.lean")
receipts=[]
env=dict(os.environ, LEAN_PATH=str(out))
for name in ("Hidden", "Subtree", "Independent"):
    cmd=[lean, "-o", name+".olean", name+".lean"]
    r=subprocess.run(cmd,cwd=out,env=env,capture_output=True)
    (out/(name+".stdout")).write_bytes(r.stdout)
    (out/(name+".stderr")).write_bytes(r.stderr)
    receipts.append({"command":cmd,"cwd":str(out),"returncode":r.returncode})
    (out/"COMMANDS.json").write_text(json.dumps(receipts,indent=2)+"\n")
    if r.returncode: raise SystemExit(r.returncode)
audit=(out/"Independent.stdout").read_text()
names=re.findall(r"^theorem ([A-Za-z0-9_]+)", (root/"Independent.lean").read_text(), re.M)
assert len(names)==9 and re.findall(r"^'Independent.([A-Za-z0-9_]+)'",audit,re.M)==names
assert "sorryAx" not in audit and "warning" not in audit and not (out/"Independent.stderr").read_text()
for line in audit.splitlines():
    assert line.endswith("depends on axioms: [propext, Quot.sound]")
removed=[]
for f in out.glob("*.olean"):
    removed.append({"name":f.name,"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
    f.unlink()
(out/"CLEANUP.json").write_text(json.dumps(removed,indent=2)+"\n")
print("PASS nine independent kernel checks")
