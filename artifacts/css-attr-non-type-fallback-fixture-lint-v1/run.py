import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WPT = ROOT / "testing/web-platform/tests"
REL = "css/css-values/attr-non-type-used-fallback-cycle.html"
SOURCE = ROOT / "artifacts/css-attr-non-type-fallback-repair-v2/candidate-head/testing/web-platform/tests" / REL
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE) == "6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3"
sys.path.insert(0, str(WPT))
from tools.lint import lint
pins = {str(p): sha(p) for p in [SOURCE, WPT / "lint.ignore", WPT / ".gitignore", Path(lint.__file__)]}
with tempfile.TemporaryDirectory(prefix="css-attr-fixture-lint-", dir="/private/tmp") as name:
    scratch = Path(name)
    path = scratch / REL
    path.parent.mkdir(parents=True)
    shutil.copyfile(SOURCE, path)
    for n in ["lint.ignore", ".gitignore"]:
        shutil.copyfile(WPT / n, scratch / n)
    subprocess.run(["git", "init", "--quiet"], cwd=scratch, check=True)
    os.chdir(scratch)
    errors = lint.lint(str(scratch), [REL], "json", jobs=1)
    assert sha(path) == pins[str(SOURCE)]
    os.chdir(ROOT)
assert not scratch.exists()
assert all(sha(Path(p)) == v for p, v in pins.items())
result = {"errors": errors, "fixture_sha256": pins[str(SOURCE)], "owned_scratch_removed": True, "native_source_changed": False, "scope": "Real WPT lint API on the exact fixture in an isolated root, with upstream lint.ignore and .gitignore", "inputs": pins}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(1 if errors else 0)
