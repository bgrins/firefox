import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint


def digest(body):
    return hashlib.sha256(body).hexdigest()


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


coverage = ROOT / "artifacts/css-sibling-count-focused-regression-plan-v1"
selection = json.loads((coverage / "SOURCE-COVERAGE.json").read_text())
head = selection["head"]
resources = {}
origins = {}
for record in selection["records"][:6]:
    name = record["path"]
    body = subprocess.check_output(["git", "show", head + ":" + name])
    assert digest(body) == record["sha256"]
    destination = HERE / "capture" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
    relative = name.removeprefix("testing/web-platform/tests/")
    resources[relative] = {"path": str(destination.relative_to(ROOT)), "sha256": digest(body)}
    origins[relative] = record
landing = ROOT / "artifacts/css-sibling-count-rule-cache-landing-v2"
target_names = json.loads((landing / "TARGET-SUBTESTS.json").read_text())
target = next(iter(target_names)).removeprefix("/")
source = landing / "candidate/testing/web-platform/tests" / target
resources[target] = {"path": str(source.relative_to(ROOT)), "sha256": digest(source.read_bytes())}
pages = list(resources)
old_policy = json.loads((ROOT / "artifacts/css-sibling-count-rule-cache-browser-v3/POLICY.json").read_text())
for name, record in old_policy["wpt"]["resources"].items():
    if name.startswith("resources/"):
        assert digest((ROOT / record["path"]).read_bytes()) == record["sha256"]
        resources[name] = record
metadata_names = set()
for name in pages:
    metadata_names.add(name + ".ini")
    directory = Path(name).parent
    while True:
        metadata_names.add(str(directory / "__dir__.ini"))
        if directory == Path("."):
            break
        directory = directory.parent
metadata = {}
for name in sorted(metadata_names):
    path = "testing/web-platform/meta/" + name
    result = subprocess.run(["git", "show", head + ":" + path], capture_output=True)
    if result.returncode:
        assert result.returncode == 128 and b"does not exist" in result.stderr, result.stderr
        metadata[name] = {"path": path, "sha256": None}
    else:
        destination = HERE / "capture" / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result.stdout)
        metadata[name] = {"path": str(destination.relative_to(ROOT)), "sha256": digest(result.stdout)}
roster = {}
node = """const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const scripts=JSON.parse(s),names=[];const context=vm.createContext({test:(fn,name)=>names.push(name),promise_test:(fn,name)=>names.push(name),host:{attachShadow:()=>({})},rm1:{remove(){}},rm2:{remove(){}}});for(const script of scripts)vm.runInContext(script,context);process.stdout.write(JSON.stringify(names));});"""
for name in pages:
    document = html5lib.parse((ROOT / resources[name]["path"]).read_text(), namespaceHTMLElements=False)
    scripts = [n.text or "" for n in document.iter("script") if n.get("src") is None]
    for element in document.iter("script"):
        if element.get("src"):
            assert element.get("src").removeprefix("/") in resources
    result = subprocess.run(["node", "-e", node], input=json.dumps(scripts), text=True, capture_output=True, check=True)
    names = json.loads(result.stdout)
    assert names and len(names) == len(set(names))
    roster["/" + name] = names
assert sum(map(len, roster.values())) == 36
assert roster["/" + target] == target_names["/" + target]
with tempfile.TemporaryDirectory(prefix="sibling-regression-wpt-") as directory:
    scratch = Path(directory)
    for name, record in resources.items():
        destination = scratch / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / record["path"]).read_bytes())
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(name, None, True) for name in pages], parallel=False)
    serialized = manifest.to_json()
    assert len(list(manifest.itertypes("testharness"))) == 7
    Manifest.from_json(str(scratch), json.loads(json.dumps(serialized)))
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), pages, "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
write_json("SUBSET-MANIFEST.json", serialized)
write_json("ROSTER.json", roster)
write_json("SOURCE-ORIGINS.json", origins)
write_json("INPUTS.json", {"head": head, "resources": resources, "metadata": metadata,
    "expected_subtests": roster, "target_subtests": target_names,
    "fixture_target_pages": list(target_names), "execution_enabled": False})
write_json("CHECK.json", {"pages": 7, "callbacks": 36, "targets": 2, "controls": 34,
    "lint_errors": 0, "callbacks_executed": False, "browser_executed": False,
    "scratch_removed": not scratch.exists()})
print("7 genuine pages; 36 inert callbacks; 2 targets/34 controls; lint0; scratch removed")
