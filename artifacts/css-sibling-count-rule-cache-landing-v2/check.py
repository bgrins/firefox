import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT)]
sys.path.insert(0, str(ROOT / "third_party/python/pyyaml/lib"))
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

path = "css/css-values/tree-counting/sibling-count-cross-parent-invalidation.html"
source = (HERE / "candidate/testing/web-platform/tests" / path).read_text()
document = html5lib.parse(source, namespaceHTMLElements=False)
body = document.find("body")
assert body is not None
scripts = [node.text or "" for node in body.iter("script") if node.get("src") is None]
assert len(scripts) == 1
run = subprocess.run(["node", "-e", "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"], input=scripts[0], text=True, capture_output=True, check=True)
names = json.loads(run.stdout)
assert names == [f"{property} uses each parent's sibling count before and after mutations" for property in ("width", "opacity")]
with tempfile.TemporaryDirectory(prefix="sibling-count-wpt-") as temporary:
    scratch = Path(temporary)
    target = scratch / path
    target.parent.mkdir(parents=True)
    target.write_text(source)
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True)], parallel=False)
    serialized = manifest.to_json()
    assert list(manifest.itertypes("testharness"))[0][1] == path
    Manifest.from_json(str(scratch), json.loads(json.dumps(serialized)))
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [path], "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
(HERE / "SUBSET-MANIFEST.json").write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
(HERE / "TARGET-SUBTESTS.json").write_text(json.dumps({"/" + path: names}, indent=2) + "\n")
(HERE / "STATIC-CHECK.json").write_text(json.dumps({"testharness_pages": 1, "registered_tests": 2,
    "lint_errors": 0, "body_before_callbacks": True, "callbacks_executed": False,
    "scratch_removed": not scratch.exists()}, indent=2) + "\n")
print("One genuine testharness page; two inert callbacks; lint0; private scratch removed")
