import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(HERE / "SYNC-PLAN.json")
assert plan["receipt_ids"] == ["provider-v5-observations","atan2-research","checkpoint"]
parent = read(HERE / "INITIAL-EPOCH.json")["semantic_index"]["head"]
for name in plan["receipt_ids"][:-1]:
    receipt, item = read(HERE / (name+"-receipt.json")), read(HERE / (name+"-item.json"))
    assert receipt["signature_verified"] and receipt["working_bodies_and_nested_index_preserved"]
    assert receipt["parent"] == parent and sorted(receipt["files"]) == sorted(item["files"])
    parent = receipt["commit"]
assert read(HERE / "CURRENT-EPOCH.json")["semantic_index"]["head"] == parent
files = [HERE/n for n in ["commit.py","finish.py","synchronize.py","SYNC-PLAN.json","CHECKPOINT.md","HELPER-CHECK.json","publication-appendix.py","PUBLICATION-APPENDIX-CHECK.json","INITIAL-EPOCH.json","BEFORE.json","PRE-CURRENT-EPOCH.json","PRE-ROLE.json","PRE-OWNED.json"]]
for name in plan["receipt_ids"][:-1]:
    files += [HERE/(name+suffix) for suffix in ["-selection.json","-item.json","-message.txt","-receipt.json","-commit.log","-signature.log"]]
review = ROOT / plan["review"]
assert sha(review / "FILES.json") == plan["review_manifest_sha256"]
for name, pin in read(review / "FILES.json").items():
    expected = pin["sha256"] if isinstance(pin,dict) else pin
    assert sha(review / name) == expected
    files.append(review / name)
files.append(review / "FILES.json")
files.append(ROOT / "artifacts/css-provider-post-signing-plan-v1/PLAN.md")
for directory, manifest_sha in plan["additional_packages"].items():
    package = ROOT / directory
    assert sha(package / "FILES.json") == manifest_sha
    for name, pin in read(package / "FILES.json").items():
        expected = pin["sha256"] if isinstance(pin,dict) else pin
        assert sha(package / name) == expected
        files.append(package / name)
    files.append(package / "FILES.json")
previously_selected = set()
for name in plan["receipt_ids"][:-1]:
    previously_selected.update(read(HERE / (name+"-item.json"))["files"])
pins = {}
for path in files:
    assert path.is_file() and not path.is_symlink(),str(path)
    name = str(path.relative_to(ROOT))
    assert name.startswith("artifacts/") and not name.startswith("artifacts/css-spec-lean/")
    if name not in previously_selected:
        pins[name] = sha(path)
item = {"id":"checkpoint","files":sorted(pins),"source_pins":pins,"message":"No bug - Record partial provider observations and atan2 verification checkpoint. r?#firefox-style-system-reviewers"}
selection = HERE / "checkpoint-selection.json"
with selection.open("x") as stream:
    json.dump(item,stream,indent=2,sort_keys=True);stream.write("\n")
with (HERE / "checkpoint-driver.log").open("x") as stream:
    subprocess.run([sys.executable,"-I","-S","-B",str(HERE / "commit.py"),str(selection)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
with (HERE / "synchronize-driver.log").open("x") as stream:
    subprocess.run([sys.executable,"-I","-S","-B",str(HERE / "synchronize.py")],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
print("Signed checkpoint and runtime synchronization complete")
