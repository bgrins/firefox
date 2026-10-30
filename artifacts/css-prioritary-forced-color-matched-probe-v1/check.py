import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "artifacts/css-prioritary-selection-suite-v1"
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]

def audit(event, args):
    if event == "subprocess.Popen":
        assert Path(args[0]).name != "git"

sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

PAGE = "forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html"
program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const context=vm.createContext({window:{},test:(_,name)=>names.push(name),promise_test:(_,name)=>names.push(name)});for(const source of JSON.parse(input))vm.runInContext(source,context);process.stdout.write(JSON.stringify(names));});"
roster = {}
for path in sorted((HERE / "tests").rglob("*.html")):
    relative = str(path.relative_to(HERE / "tests"))
    dom = html5lib.parse(path.read_text(), namespaceHTMLElements=False)
    scripts = [node.text for node in dom.iter("script") if not node.get("src")]
    result = subprocess.run(["node", "-e", program], input=json.dumps(scripts), text=True, capture_output=True, check=True)
    names = json.loads(result.stdout)
    assert names and len(names) == len(set(names))
    assert not lint.check_path(str(HERE / "tests"), relative)
    assert not lint.check_file_contents(str(HERE / "tests"), relative)
    roster["/" + relative] = names
assert len(roster) == 2 and sum(map(len, roster.values())) == 3
assert roster["/" + PAGE] == ["Prioritary forced-color selection: auto", "Prioritary forced-color selection: none"]
unchanged = ["tests/forced-colors-mode/forced-colors-mode-51.html", "tests/resources/testharness.js", "tests/resources/testharnessreport.js", "meta/__dir__.ini", "meta/forced-colors-mode/__dir__.ini", "meta/forced-colors-mode/forced-colors-mode-51.html.ini"]
for name in unchanged:
    assert (HERE / name).read_bytes() == (SOURCE / name).read_bytes(), name
assert (HERE / "base.html").read_bytes() == (SOURCE / "tests" / PAGE).read_bytes()
old = (HERE / "base.html").read_text()
new = (HERE / "tests" / PAGE).read_text()
expected = "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile="sealed-v1/registered-prioritary-forced-color-selection.tentative.html", tofile="matched-v1/registered-prioritary-forced-color-selection.tentative.html"))
assert (HERE / "FIXTURE-DELTA.patch").read_text() == expected
paths = sorted(str(p.relative_to(HERE / "tests")) for p in (HERE / "tests").rglob("*") if p.is_file())
assert len(paths) == 4
manifest = Manifest(str(HERE / "tests"), "/")
manifest.update([(path, None, True) for path in paths], parallel=False)
(HERE / "MANIFEST.json").write_text(json.dumps(manifest.to_json(), indent=2, sort_keys=True) + "\n")
(HERE / "ROSTER.json").write_text(json.dumps(roster, indent=2) + "\n")
references = {}
for name in unchanged + ["tests/" + PAGE, "FILES.json"]:
    path = SOURCE / name
    references[str(path.relative_to(ROOT))] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
for package in ["css-prioritary-forced-color-oracle-review-v1"]:
    path = ROOT / "artifacts" / package / "FILES.json"
    references[str(path.relative_to(ROOT))] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
(HERE / "REFERENCES.json").write_text(json.dumps(references, indent=2) + "\n")
result = {"callbacks": 3, "pages": 2, "signatures": 5, "resources": 4, "new_callbacks": 2, "unchanged_controls": 1, "lint_errors": 0, "genuine_manifest": True, "unchanged_payloads": len(unchanged), "references": len(references), "browser_execution": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
