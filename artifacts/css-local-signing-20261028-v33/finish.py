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
files = [HERE / n for n in ['commit.py', 'finish.py', 'synchronize.py', 'SYNC-PLAN.json', 'CHECKPOINT.md', 'ARCHIVE-STATUS.json', 'INVENTORY.json', 'INITIAL-EPOCH.json', 'BEFORE.json', 'PRE-CURRENT-EPOCH.json', 'PRE-ROLE.json', 'PRE-OWNED.json']]
for ident in plan["receipt_ids"][:-1]:
    receipt, item = read(HERE / (ident + "-receipt.json")), read(HERE / (ident + "-item.json"))
    assert receipt["signature_verified"] and receipt["working_bodies_and_nested_index_preserved"]
    assert receipt["parent"] == parent and sorted(receipt["files"]) == sorted(item["files"])
    parent = receipt["commit"]
    files += [HERE / (ident + suffix) for suffix in ["-selection.json", "-item.json", "-message.txt", "-receipt.json", "-commit.log", "-signature.log"]]
assert read(HERE / "CURRENT-EPOCH.json")["semantic_index"]["head"] == parent
previous = ROOT / "artifacts/css-local-signing-20261028-v32"
files += [previous / n for n in ["FINAL-CHECK.json", "checkpoint-receipt.json", "checkpoint-commit.log", "checkpoint-signature.log"]]
files += [ROOT / n for n in [
    "artifacts/css-random-counter-native-execution-v1/adopt.py",
    "artifacts/css-random-counter-native-execution-v1/build.py",
    "artifacts/css-random-counter-native-execution-v1/POLICY.json",
    "artifacts/css-random-counter-wpt-install-v1/INSTALLED.json",
    "artifacts/css-random-counter-plan-v1/PLAN.md",
]]
assert read(ROOT / "artifacts/css-random-counter-native-execution-v1/POLICY.json")["execution_enabled"] is False
assert read(ROOT / "artifacts/css-registered-random-index-wpt-comparison-v1/POLICY.json")["execution_enabled"] is False
pins = {}
for path in files:
    assert path.is_file() and not path.is_symlink()
    name = str(path.relative_to(ROOT))
    assert name.startswith("artifacts/") and not name.startswith("artifacts/css-spec-lean/")
    pins[name] = sha(path)
item = {"id":"checkpoint", "files":sorted(pins), "source_pins":pins, "message":"No bug - Checkpoint unaccepted random and line-height research. r?#firefox-style-system-reviewers"}
selection = HERE / "checkpoint-selection.json"
with selection.open("x") as stream:
    json.dump(item, stream, indent=2, sort_keys=True)
    stream.write("\n")
with (HERE / "checkpoint-driver.log").open("x") as stream:
    subprocess.run([sys.executable, "-I", "-S", "-B", str(HERE / "commit.py"), str(selection)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
with (HERE / "synchronize-driver.log").open("x") as stream:
    subprocess.run([sys.executable, "-I", "-S", "-B", str(HERE / "synchronize.py")], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
print("Signed checkpoint and runtime synchronization complete")
