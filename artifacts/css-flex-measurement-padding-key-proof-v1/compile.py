import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require isolated nonoptimized Python without site")
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(root):
    raise SystemExit("fresh absolute external output required")
config = json.loads((root / "TOOLCHAIN.json").read_text())
if hashlib.sha256(Path(config["lean"]).read_bytes()).hexdigest() != config["lean_sha256"]:
    raise SystemExit("Lean executable mismatch")
out.mkdir(parents=True)
env = {k:v for k,v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
env["LEAN_PATH"] = str(out)
records = []
for name in json.loads((root / "MODULES.json").read_text()):
    command = [config["lean"], "--root=" + str(root / "lean"), "-o", str(out / (name + ".olean")), str(root / "lean" / (name + ".lean"))]
    p = subprocess.run(command, env=env, capture_output=True, text=True)
    records.append({"module":name,"command":command,"exit":p.returncode,"stdout":p.stdout,"stderr":p.stderr})
    (out / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
    if p.returncode or p.stderr or "warning:" in p.stdout:
        raise RuntimeError("module failed: " + name + "\n" + p.stdout + p.stderr)
print(json.dumps({"status":"PASS", "modules":len(records)}))
