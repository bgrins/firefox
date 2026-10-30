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

page = "css/css-animations/animation-duration-masked-font-update.tentative.html"
tests = HERE / "tests"
source = (tests / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter("script") if not node.get("src")]
assert len(scripts) == 1
for node in dom.iter("script"):
    if node.get("src"):
        assert (tests / node.get("src").lstrip("/")).is_file()
assert all(word not in source for word in ("fetch(", "run_id", "record("))
window = source.split('target.style.fontSize = "32px";', 1)[1]
assert window.index("getComputedStyle(target).opacity") < window.index("getTiming()") < window.index("getAnimations()")
program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(input,{promise_test:(_,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
names = json.loads(subprocess.run(["node", "-e", program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
assert len(names) == 1
errors = lint.check_path(str(tests), page) + lint.check_file_contents(str(tests), page)
assert not errors, errors
paths = sorted(str(p.relative_to(tests)) for p in tests.rglob("*") if p.is_file())
manifest = Manifest(str(tests), "/")
manifest.update([(path, None, True) for path in paths], parallel=False)
actual = json.loads(json.dumps(manifest.to_json()))
assert set(actual["items"]["testharness"]["css"]["css-animations"]) == {Path(page).name}
(HERE / "MANIFEST.json").write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
role = json.loads((HERE / "SOURCE-ROLES.json").read_text())
base = ROOT / role["base"]
assert hashlib.sha256(base.read_bytes()).hexdigest() == role["base_sha256"]
with tempfile.TemporaryDirectory(prefix="masked-admission-patch-", dir="/private/tmp") as temporary:
    scratch = Path(temporary)
    destination = scratch / role["native_path"]
    destination.parent.mkdir(parents=True)
    shutil.copyfile(base, destination)
    forward = subprocess.run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(HERE / "native.patch")], cwd=scratch, text=True, capture_output=True, check=True)
    assert "fuzz" not in forward.stdout and "offset" not in forward.stdout
    assert destination.read_bytes() == (ROOT / role["candidate"]).read_bytes()
    subprocess.run(["patch", "--batch", "--fuzz=0", "-R", "-p1", "-i", str(HERE / "native.patch")], cwd=scratch, text=True, capture_output=True, check=True)
    assert destination.read_bytes() == base.read_bytes()
assert not scratch.exists()
refs = json.loads((HERE / "REFERENCES.json").read_text())
for path, digest in refs.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
result = {"callbacks_inertly_registered": names, "lint_path_and_contents_errors": 0,
          "git_ignore_repository_scan_not_run": True, "genuine_manifest_generated": True,
          "first_getter_before_timing_and_membership": True, "no_private_transport": True,
          "exact_patch_forward_reverse": True, "scratch_removed": True,
          "references_authenticated": len(refs), "browser_or_native_build_executed": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
