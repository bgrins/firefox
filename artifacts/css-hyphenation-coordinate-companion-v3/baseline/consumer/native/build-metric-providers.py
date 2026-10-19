import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "development-build/full"
TARGET = OUT / "metric-providers"
TARGET.mkdir(parents=True,exist_ok=True)
records=[]
def run(name,args):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180)
    (TARGET/(name+".log")).write_text(r.stdout+r.stderr)
    records.append({"name":name,"args":list(map(str,args)),"exit":r.returncode})
    (TARGET/"BUILD.json").write_text(json.dumps(records,indent=2)+"\n")
    print(name,r.returncode,flush=True)
    if r.returncode:raise SystemExit(r.returncode)
run("extract",[sys.executable,ROOT/"native/extract-metric-providers.py"])
args=next(r["args"]for r in json.loads((OUT/"commands.json").read_text())if r["name"]=="compile-provider")
args=args[:args.index("-c")]
for name in ["measurement","hyphen-consumer"]:
    run(name,args+["-I"+str(OUT),str(TARGET/(name+".cpp")),"-licucore","-o",str(TARGET/name)])
