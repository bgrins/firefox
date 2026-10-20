import sys
sys.dont_write_bytecode=True
import json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cap=ROOT/"capsule"
out=ROOT/sys.argv[1]
out.mkdir()
modules=[]
def visit(name):
    if name in modules:return
    text=(cap/"lean"/(name+".lean")).read_text()
    for dep in re.findall(r"^import (\w+)$",text,re.M):
        if dep!="Std":visit(dep)
    modules.append(name)
for module in sys.argv[2:]:visit(module)
tool=json.loads((cap/"TOOLCHAIN.json").read_text());commands=[]
for name in modules:
    src=out/(name+".lean");shutil.copy2(cap/"lean"/(name+".lean"),src)
    cmd=[tool["lean"],"-o",str(out/(name+".olean")),str(src)]
    proc=subprocess.run(cmd,cwd=out,env={"PATH":"/usr/bin:/bin","LEAN_PATH":str(out)},capture_output=True,text=True)
    (out/(name+".log")).write_text(proc.stdout+proc.stderr)
    commands.append({"name":name,"command":cmd,"exit":proc.returncode})
    (out/"COMMANDS.json").write_text(json.dumps(commands,indent=2)+"\n")
    if proc.returncode or "declaration uses 'sorry'" in proc.stdout+proc.stderr:
        print(name,proc.stdout,proc.stderr);raise SystemExit(1)
print("pass",modules)
