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
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT / "third_party/python/PyYAML/lib")] + [
    str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()
] + [str(WPT / "tools"), str(WPT)]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

fixture = PACKAGE / "declaring-root-easing.tentative.html"
digest = "30556c2b86c91e26e58783b557d326ec6320708bf1e3bdedb0e59ab28a697d58"
data = fixture.read_bytes()
assert hashlib.sha256(data).hexdigest() == digest
path = "css/css-animations/" + fixture.name
document = html5lib.parse(data.decode(), namespaceHTMLElements=False)
scripts = [n.text or "" for n in document.find("body").iter("script") if n.get("src") is None]
assert len(scripts) == 1
code = scripts[0]
subprocess.run(["node", "--check"], input=code, text=True, check=True)
registered = {}
for query, label in [("", "literal"), ("?variant=literal", "literal"), ("?variant=contextual", "contextual")]:
    probe = 'const vm=require("node:vm");let s="";process.stdin.on("data",x=>s+=x);process.stdin.on("end",()=>{const names=[];vm.runInNewContext(s,{URLSearchParams,location:{search:' + json.dumps(query) + '},test:(_,n)=>names.push(n)});process.stdout.write(JSON.stringify(names));});'
    result = subprocess.run(["node", "-e", probe], input=code, text=True, capture_output=True, check=True)
    registered[query] = json.loads(result.stdout)
    assert registered[query] == ["Changing only the declaring root of animation-name selects " + label + " keyframe easing"]
with tempfile.TemporaryDirectory(prefix="declaring-root-wpt-") as temporary:
    scratch = Path(temporary)
    copied = scratch / path
    copied.parent.mkdir(parents=True)
    copied.write_bytes(data)
    (scratch / "lint.ignore").write_text("")
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True)], parallel=False)
    serialized = manifest.to_json()
    node = serialized["items"]["testharness"]["css"]["css-animations"][fixture.name]
    assert len(node) == 3, node
    variants = [item[0] for item in node[1:]]
    assert sorted(variants) == [path + "?variant=contextual", path + "?variant=literal"], variants
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        lint_errors = lint.lint(str(scratch), [path], "normal", jobs=1)
    finally:
        os.chdir(previous)
    assert lint_errors == 0
    (PACKAGE / "SUBSET-MANIFEST.json").write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n")
assert hashlib.sha256(fixture.read_bytes()).hexdigest() == digest
check = {"fixture_sha256": digest, "lint_errors": lint_errors, "manifest_version": serialized["version"], "manifest_variants": variants, "html5_body_before_inline_callback": True, "javascript_syntax_exit": 0, "registered_without_callback_execution": registered, "scratch_removed": not Path(temporary).exists(), "fixture_installed_in_native_wpt_tree": False, "browser_execution_by_this_check": False}
(PACKAGE / "CHECK.json").write_text(json.dumps(check, indent=2, sort_keys=True) + "\n")
print(json.dumps(check, indent=2))
