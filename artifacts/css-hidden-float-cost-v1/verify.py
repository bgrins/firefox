import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse, hashlib, json, stat
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
repo = here.parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def need(ok, message):
    if not ok: raise RuntimeError(message)
need(sha(here / "FILES.json") == args.manifest_sha, "Manifest identity")
manifest = json.loads((here / "FILES.json").read_text())
actual = set()
for path in here.iterdir():
    need(stat.S_ISREG(path.lstat().st_mode), "Nonregular payload")
    actual.add(path.name)
need(actual == set(manifest) | {"FILES.json", "FREEZE.json"}, "Closed roster")
for name, pin in manifest.items():
    need(Path(name).name == name and sha(here / name) == pin, "Payload " + name)
deps = json.loads((here / "DEPENDENCIES.json").read_text())
prior = repo / deps["predecessor"]
need(sha(prior / "FILES.json") == deps["manifest_sha256"], "Predecessor manifest")
prior_manifest = json.loads((prior / "FILES.json").read_text())
for name, pin in deps["unchanged_files"].items():
    need(sha(prior / name) == sha(here / name) == prior_manifest[name] == pin, "Preserved " + name)
geometry = deps["geometry_predecessor"]
need(sha(repo / geometry["path"]) == geometry["sha256"], "Geometry predecessor")
print(f"PASS {len(manifest)} sealed source-only payloads; browser calibration remains required")
