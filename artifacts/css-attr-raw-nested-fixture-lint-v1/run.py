import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WPT = ROOT / "testing/web-platform/tests"
PROPOSAL = ROOT / "artifacts/css-attr-raw-nested-repair-v1"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PROPOSAL / "FILES.json") == "0f3b2b6d970fc0a5ffca89190d97726b8eacdd121f574b14a2b5e735a1828866"
manifest = json.loads((PROPOSAL / "FILES.json").read_text())
paths = ["css/css-values/attr-cycle.html", "css/css-values/attr-raw-nested-cycle.html"]
sources = {n: PROPOSAL / "candidate/testing/web-platform/tests" / n for n in paths}
for n, p in sources.items():
    pin = manifest[str(p.relative_to(PROPOSAL))]
    assert sha(p) == (pin["sha256"] if isinstance(pin, dict) else pin)
sys.path.insert(0, str(WPT))
from tools.lint import lint
pins = {str(p): sha(p) for p in [*sources.values(), WPT / "lint.ignore", WPT / ".gitignore", Path(lint.__file__)]}
with tempfile.TemporaryDirectory(prefix="css-raw-fixture-lint-", dir="/private/tmp") as name:
    scratch = Path(name)
    for n, source in sources.items():
        target = scratch / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for n in ["lint.ignore", ".gitignore"]:
        shutil.copyfile(WPT / n, scratch / n)
    subprocess.run(["git", "init", "--quiet"], cwd=scratch, check=True)
    os.chdir(scratch)
    errors = lint.lint(str(scratch), paths, "json", jobs=1)
    assert all(sha(scratch / n) == sha(source) for n, source in sources.items())
    os.chdir(ROOT)
assert not scratch.exists()
assert all(sha(Path(n)) == v for n, v in pins.items())
result = {"errors": errors, "fixtures": {n: sha(p) for n,p in sources.items()}, "owned_scratch_removed": True, "live_source_changed": False, "inputs": pins, "scope": "Real WPT lint API on exact two proposed fixtures in isolated root"}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(1 if errors else 0)
