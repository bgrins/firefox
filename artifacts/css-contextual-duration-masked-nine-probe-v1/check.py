import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

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
previous = ROOT / "artifacts/css-contextual-duration-masked-admission-controls-v1"
api = ROOT / "artifacts/css-contextual-duration-masked-api-first-probe-v1"
old_roster = json.loads((previous / "ROSTER.json").read_text())
api_roster = json.loads((api / "ROSTER.json").read_text())
pseudo_page = "css/css-animations/animation-duration-masked-pseudo-font-update.tentative.html"
expected = dict(old_roster, **api_roster)
expected["/" + pseudo_page] = ["Changing an inherited host variable updates masked ::before duration on the first opacity read"]
for source_root in [previous, api]:
    for path in json.loads((source_root / "ROSTER.json").read_text()):
        assert (tests / path.lstrip("/")).read_bytes() == (source_root / "tests" / path.lstrip("/")).read_bytes()
for name in ["testharness.js", "testharnessreport.js"]:
    assert (tests / "resources" / name).read_bytes() == (previous / "tests/resources" / name).read_bytes() == (api / "tests/resources" / name).read_bytes()
program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(input,{promise_test:(_,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
roster = {}
for url in expected:
    page = url.lstrip("/")
    source = (tests / page).read_text()
    dom = html5lib.parse(source, namespaceHTMLElements=False)
    scripts = [node.text for node in dom.iter("script") if not node.get("src")]
    assert len(scripts) == 1
    for node in dom.iter("script"):
        if node.get("src"):
            assert (tests / node.get("src").lstrip("/")).is_file()
    assert all(word not in source for word in ("fetch(", "run_id", "record("))
    roster[url] = json.loads(subprocess.run(["node", "-e", program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
    errors = lint.check_path(str(tests), page) + lint.check_file_contents(str(tests), page)
    assert not errors, errors
assert roster == expected and sum(map(len, roster.values())) == 9
source = (tests / pseudo_page).read_text()
window = source.split('target.style.setProperty("--font", "32px");', 1)[1]
assert window.lstrip().startswith('const firstOpacity = Number(win.getComputedStyle(target, "::before").opacity);')
assert window.index("getComputedStyle") < window.index("getTiming()") < window.index("getAnimations(")
assert 'font-size: var(--font)' in source and 'style="--font: 16px"' in source
paths = sorted(str(p.relative_to(tests)) for p in tests.rglob("*") if p.is_file())
manifest = Manifest(str(tests), "/")
manifest.update([(path, None, True) for path in paths], parallel=False)
actual = json.loads(json.dumps(manifest.to_json()))
assert set(actual["items"]["testharness"]["css"]["css-animations"]) == {Path(url).name for url in expected}
(HERE / "MANIFEST.json").write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
(HERE / "ROSTER.json").write_text(json.dumps(roster, indent=2) + "\n")
refs = json.loads((HERE / "REFERENCES.json").read_text())
for path, digest in refs.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
result = {"callbacks_inertly_registered": 9, "pages": 4, "resources": 6,
          "lint_path_and_contents_errors": 0, "genuine_manifest_generated": True,
          "git_ignore_repository_scan_not_run": True, "prior_eight_callbacks_byte_identical": True,
          "new_pseudo_first_opacity_before_timing_membership": True,
          "private_transport": False, "references_authenticated": len(refs),
          "browser_or_native_build_executed": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
