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
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

name = "contextual-easing-animated-inherited-font.tentative.html"
path = "css/css-animations/" + name
source = (PACKAGE / name).read_text()
document = html5lib.parse(source, namespaceHTMLElements=False)
body = document.find("body")
assert body is not None
scripts = [node.text or "" for node in body.iter("script") if node.get("src") is None]
assert len(scripts) == 1
result = subprocess.run(["node", "-e", "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"], input=scripts[0], text=True, capture_output=True, check=True)
names = json.loads(result.stdout)
assert names == [
    "Normal inherited font mutation refreshes contextual keyframe easing",
    "Animated inherited font refreshes contextual keyframe easing without replacing its effect",
    "Animated inherited font preserves successful literal setKeyframes override",
]
assert len(names) == len(set(names)) == 3
with tempfile.TemporaryDirectory(prefix="css-easing-animated-input-") as temporary:
    scratch = Path(temporary)
    output = scratch / path
    output.parent.mkdir(parents=True)
    output.write_text(source)
    (scratch / "lint.ignore").write_text("")
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True)], parallel=False)
    serialized = manifest.to_json()
    entry = serialized["items"]["testharness"]["css"]["css-animations"][name]
    assert len(entry) == 2 and entry[1][0] is None
    expected = PACKAGE / "SUBSET-MANIFEST.json"
    if expected.exists():
        assert json.loads(expected.read_text()) == serialized
    else:
        expected.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [path], "normal", jobs=1) == 0
    finally:
        os.chdir(previous)
print(json.dumps({"registered_names": names, "callbacks_executed": False,
                  "html5_body_before_callbacks": True, "lint_errors": 0, "scratch_removed": True}))
