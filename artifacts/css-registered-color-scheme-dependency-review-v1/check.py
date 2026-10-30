import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]


def audit(event, args):
    if event == "subprocess.Popen":
        assert Path(args[0]).name != "git", "Git execution prohibited"


sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

tests = HERE / "tests"
roster = {}
for kind in ["registered-ident-color-scheme-dependency"]:
    page = f"css/css-properties-values-api/{kind}.tentative.html"
    source = (tests / page).read_text()
    assert source.index("<body>") < source.index("window.colorSchemeDependencyObservations")
    assert '<pre id="observations" hidden>' in source
    dom = html5lib.parse(source, namespaceHTMLElements=False)
    scripts = [node.text for node in dom.iter("script") if not node.get("src")]
    assert len(scripts) == 1
    for node in dom.iter("script"):
        if node.get("src"):
            assert (tests / node.get("src").lstrip("/")).is_file()
    program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(input,{window:{},promise_test:(_,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
    names = json.loads(subprocess.run(["node", "-e", program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
    expected = [f"Selected identifier color-scheme dependency: {mode}" for mode in ["union-plain", "union-unused-attr", "color-first-unused-attr", "ident-unused-attr", "literal"]]
    assert names == expected
    roster["/" + page] = names
    errors = lint.check_path(str(tests), page) + lint.check_file_contents(str(tests), page)
    assert not errors, errors
for name in ["testharness.js", "testharnessreport.js"]:
    assert (tests / "resources" / name).read_bytes() == (ROOT / "artifacts/css-contextual-duration-animation-taint-probe-v1/tests/resources" / name).read_bytes()
refs = json.loads((HERE / "REFERENCES.json").read_bytes())
for name, digest in refs.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
paths = sorted(str(p.relative_to(tests)) for p in tests.rglob("*") if p.is_file())
manifest = Manifest(str(tests), "/")
manifest.update([(path, None, True) for path in paths], parallel=False)
actual = json.loads(json.dumps(manifest.to_json()))
assert set(actual["items"]["testharness"]["css"]["css-properties-values-api"]) == {Path(page).name for page in roster}
(HERE / "MANIFEST.json").write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
(HERE / "ROSTER.json").write_text(json.dumps(roster, indent=2) + "\n")
result = {"callbacks_inertly_registered": 5, "pages": 1, "resources": len(paths),
          "lint_path_and_contents_errors": 0, "genuine_manifest_generated": True,
          "git_ignore_repository_scan_not_run": True, "private_transport": False,
          "browser_or_native_build_executed": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
