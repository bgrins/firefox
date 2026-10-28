import hashlib, json, shutil, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIXTURE = ROOT / "artifacts/css-registered-number-wpt-fixture-v2"
manifest = json.loads((FIXTURE / "FILES.json").read_text())
manifest = manifest.get("files", manifest)
for name, pin in manifest.items():
    digest = pin["sha256"] if isinstance(pin, dict) else pin
    assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == digest
sys.path.insert(0, str(ROOT / "testing/web-platform/tests"))
from tools.lint.lint import lint
path = (FIXTURE / "NEW-WPT-PATH.txt").read_text().strip()
prefix = "testing/web-platform/tests/"
assert path.startswith(prefix)
relative = path[len(prefix):]
source = FIXTURE / "candidate" / path
with tempfile.TemporaryDirectory(prefix="css-number-wpt-lint-", dir="/private/tmp") as tmp:
    root = Path(tmp)
    shutil.copytree(FIXTURE / "capture" / "testing/web-platform/tests", root, dirs_exist_ok=True)
    ignore = ROOT / "testing/web-platform/tests/lint.ignore"
    shutil.copy2(ignore, root / "lint.ignore")
    assert (root / relative).read_bytes() == source.read_bytes()
    count = lint(str(root), [relative], "json", jobs=1)
    result = {"errors": count, "source": path,
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "fixture_manifest_sha256": hashlib.sha256((FIXTURE / "FILES.json").read_bytes()).hexdigest(),
              "lint_ignore_sha256": hashlib.sha256(ignore.read_bytes()).hexdigest(),
              "real_wpt_lint": True, "isolated_capture": True,
              "live_wpt_installed": (ROOT / path).exists()}
for name, pin in manifest.items():
    digest = pin["sha256"] if isinstance(pin, dict) else pin
    assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == digest
result["fixture_preserved"] = True
(HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
assert count == 0
