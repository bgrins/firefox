import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT)]
sys.path.insert(0, str(ROOT / "third_party/python/PyYAML/lib"))
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
refs = json.loads((PACKAGE / "REFERENCES.json").read_text())
experiment = json.loads((PACKAGE / "EXPERIMENT.json").read_text())
for path, digest in refs.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
sources = {}
for origin, entry in pins.items():
    if not entry["exists"]:
        continue
    data = (ROOT / entry["capture"]).read_bytes()
    assert len(data) == entry["bytes"] and hashlib.sha256(data).hexdigest() == entry["sha256"], origin
    if origin.startswith("testing/web-platform/tests/"):
        sources[origin.removeprefix("testing/web-platform/tests/")] = data
pages = [path.lstrip("/") for path in experiment["target_subtests"]]
registered = {}
for path in pages:
    document = html5lib.parse(sources[path].decode(), namespaceHTMLElements=False)
    body = document.find("body")
    assert body is not None
    scripts = [node.text or "" for node in body.iter("script") if node.get("src") is None]
    assert scripts, path
    code = "\n".join(scripts)
    result = subprocess.run(["node", "-e", "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"], input=code, text=True, capture_output=True, check=True)
    names = json.loads(result.stdout)
    assert names == experiment["target_subtests"]["/" + path]
    registered["/" + path] = names
with tempfile.TemporaryDirectory(prefix="css-move-boundary-") as temporary:
    scratch = Path(temporary)
    for path, data in sources.items():
        output = scratch / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True) for path in sorted(sources)], parallel=False)
    serialized = manifest.to_json()
    for path in pages:
        node = serialized["items"]["testharness"]
        for part in path.split("/"):
            node = node[part]
        assert len(node) == 2 and node[1][0] is None, path
    expected = PACKAGE / "SUBSET-MANIFEST.json"
    if expected.exists():
        assert json.loads(expected.read_text()) == serialized
    else:
        expected.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), pages, "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
assert sum(map(len, registered.values())) == 18
print(json.dumps({"pages": 1, "registered_tests": 18, "cases": 18, "expected_records": 162, "lint_errors": 0, "html5_body_before_inline_callbacks": True, "callbacks_executed": False, "scratch_removed": True}))
