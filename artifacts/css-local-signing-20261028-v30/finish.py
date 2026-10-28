import hashlib
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(HERE / "SYNC-PLAN.json")
parent = read(HERE / "INITIAL-EPOCH.json")["semantic_index"]["head"]
files = [HERE / n for n in ["commit.py", "finish.py", "synchronize.py", "SYNC-PLAN.json", "CHECKPOINT.md", "INITIAL-EPOCH.json", "BEFORE.json", "PRE-CURRENT-EPOCH.json", "PRE-ROLE.json", "PRE-OWNED.json"]]
for ident in plan["receipt_ids"][:-1]:
    receipt, item = read(HERE / (ident + "-receipt.json")), read(HERE / (ident + "-item.json"))
    assert receipt["signature_verified"] and receipt["working_bodies_and_nested_index_preserved"]
    assert receipt["parent"] == parent and sorted(receipt["files"]) == sorted(item["files"])
    parent = receipt["commit"]
    files += [HERE / (ident + suffix) for suffix in ["-selection.json", "-item.json", "-message.txt", "-receipt.json", "-commit.log", "-signature.log"]]
assert read(HERE / "CURRENT-EPOCH.json")["semantic_index"]["head"] == parent
previous = ROOT / "artifacts/css-local-signing-20261028-v29"
files += [previous / n for n in ["FINAL-CHECK.json", "checkpoint-receipt.json", "checkpoint-commit.log", "checkpoint-signature.log"]]
package = ROOT / "artifacts/css-next-lead-page-selector-v1"
assert sha(package / "FILES.json") == "b3b131512078f0b6fc0c55d22da18dada13c43a632971774b45e21403cc00874"
manifest = read(package / "FILES.json")
manifest = manifest.get("files", manifest)
for name, pin in manifest.items():
    assert sha(package / name) == pin["sha256"]
    files.append(package / name)
files.append(package / "FILES.json")
files.append(ROOT / "artifacts/css-continuation-roadmap-20261028-v1/PLAN.md")
pins = {}
for path in files:
    assert path.is_file() and not path.is_symlink()
    name = str(path.relative_to(ROOT))
    assert name.startswith("artifacts/") and not name.startswith("artifacts/css-spec-lean/")
    pins[name] = sha(path)
item = {"id":"checkpoint", "files":sorted(pins), "source_pins":pins, "message":"No bug - Update CSS verification roadmap and next print repair. r?#firefox-style-system-reviewers"}
selection = HERE / "checkpoint-selection.json"
with selection.open("x") as stream:
    json.dump(item, stream, indent=2, sort_keys=True)
    stream.write("\n")
with (HERE / "checkpoint-driver.log").open("x") as stream:
    subprocess.run([sys.executable, "-I", "-S", "-B", str(HERE / "commit.py"), str(selection)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
with (HERE / "synchronize-driver.log").open("x") as stream:
    subprocess.run([sys.executable, "-I", "-S", "-B", str(HERE / "synchronize.py")], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
print("Signed checkpoint and runtime synchronization complete")
