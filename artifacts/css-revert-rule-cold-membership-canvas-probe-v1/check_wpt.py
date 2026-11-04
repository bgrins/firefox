import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]


def audit(event, args):
    if event == "subprocess.Popen":
        assert Path(args[0]).name != "git"


sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
name = "canvas-font-revert-rule-preservation.tentative.html"
relative = "css/css-cascade/" + name
resource_dir = ROOT / "artifacts/css-root-font-cancellation-normal-handoff-fix-v1/tests/resources"
resources = {
    "/" + relative: HERE / name,
    "/resources/testharness.js": resource_dir / "testharness.js",
    "/resources/testharnessreport.js": resource_dir / "testharnessreport.js",
}
assert sha(resources["/resources/testharness.js"]) == "7a108d7cfa98ac413ddb38f82fd509fb2037dfcc25ccf466567520cbb6bdf1fa"
assert sha(resources["/resources/testharnessreport.js"]) == "3777176fc736b0a78cf7617b9613b220f635daae7536ec7ebb99c61dbb525aae"
staging = Path(tempfile.mkdtemp(prefix="cold-canvas-wpt-"))
try:
    for url, source in resources.items():
        target = staging / url.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    dom = html5lib.parse((HERE / name).read_text(), namespaceHTMLElements=False)
    scripts = [node.text or "" for node in dom.iter("script") if not node.get("src")]
    assert len(scripts) == 1
    syntax_path = staging / "fixture.js"
    syntax_path.write_text(scripts[0])
    subprocess.run(["node", "--check", str(syntax_path)], check=True, capture_output=True)
    program = "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{window:{},test:(_,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
    names = json.loads(subprocess.run(["node", "-e", program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
    assert names == [
        "Canvas font literal revert-rule preserves the previous font",
        "Canvas font substituted revert-rule preserves the previous font and remains usable",
    ]
    findings = lint.check_path(str(staging), relative) + lint.check_file_contents(str(staging), relative)
    assert not findings, findings
    manifest = Manifest(str(staging), "/")
    manifest.update([(url.lstrip("/"), None, True) for url in resources], parallel=False)
    entries = [{"path": path, "url": value.url, "timeout": value.timeout} for kind, path, values in manifest if kind == "testharness" for value in values]
    assert len(entries) == 1 and entries[0]["url"] == "/" + relative
    outputs = {
        "MANIFEST.json": manifest.to_json(),
        "ROSTER.json": {"/" + relative: names},
        "LINT.json": {relative: findings},
        "INPUTS.json": {"pages": 1, "callbacks": 2, "prefs": {"layout.css.revert-rule.enabled": True}, "resources": {url: {"path": str(source.relative_to(ROOT)), "sha256": sha(source)} for url, source in resources.items()}},
    }
    for filename, data in outputs.items():
        (HERE / filename).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    result = {"callbacks": 2, "pages": entries, "lint_findings": 0, "genuine_manifest": True, "inert_registration_only": True, "browser_execution": False, "scratch": str(staging), "tested_inputs": {str(path.relative_to(ROOT)): sha(path) for path in [HERE / "check_wpt.py", *resources.values()]}}
finally:
    shutil.rmtree(staging)
result["scratch_absent"] = not staging.exists()
(HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
