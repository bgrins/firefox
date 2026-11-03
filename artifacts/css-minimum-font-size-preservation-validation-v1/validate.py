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
SOURCE = ROOT / "artifacts/css-minimum-font-size-preservation-probe-v1"
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]

def audit(event, args):
    if event == "subprocess.Popen":
        assert Path(args[0]).name != "git"

sys.addaudithook(audit)
from manifest.manifest import Manifest
from tools.lint import lint
from wptrunner.wptmanifest import parser

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(SOURCE / "FILES.json") == "77f5f5aaf82ca22b0963c65f2ac15b47b5eb1830523e8567a96e7d770c9766bc"
for name, value in json.loads((SOURCE / "FILES.json").read_text()).items():
    assert sha(SOURCE / name) == value["sha256"]
scratch = Path(tempfile.mkdtemp(prefix="minimum-font-size-wpt-"))
result = {"scratch": str(scratch), "browser_execution": False, "live_installation": False, "git_execution": False}
try:
    tests = scratch / "tests"
    metadata = scratch / "metadata"
    integration = json.loads((SOURCE / "INTEGRATION.json").read_text())
    for url, value in integration["resources"].items():
        source = ROOT / value["path"]
        assert sha(source) == value["sha256"]
        target = tests / url.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    authored = sorted(str(p.relative_to(tests)) for p in (tests / "css").rglob("*") if p.is_file())
    findings = {}
    for name in authored:
        findings[name] = lint.check_path(str(tests), name) + lint.check_file_contents(str(tests), name)
    (HERE / "LINT.json").write_text(json.dumps(findings, indent=2) + "\n")
    result["lint_files"] = authored
    result["lint_errors"] = sum(len(v) for v in findings.values())
    manifest = Manifest(str(tests), "/")
    paths = sorted(str(p.relative_to(tests)) for p in tests.rglob("*") if p.is_file())
    manifest.update([(path, None, True) for path in paths], parallel=False)
    data = manifest.to_json()
    (HERE / "MANIFEST.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    entries = []
    for item_type, path, values in manifest:
        if item_type == "testharness":
            for value in values:
                entries.append({"path": path, "url": value.url, "timeout": value.timeout})
    result["testharness_entries"] = entries
    assert len(entries) == 2 and all(e["timeout"] == "long" for e in entries)
    metadata_files = []
    for name, value in integration["metadata"].items():
        source = ROOT / value["path"]
        assert sha(source) == value["sha256"]
        target = metadata / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        with target.open("rb") as stream:
            parsed = parser.parse(stream)
        assert parsed is not None
        metadata_files.append(name)
    result["metadata_syntax_parsed"] = metadata_files
    result["manifest_version"] = data["version"]
    assert result["lint_errors"] == 0, findings
    result["success"] = True
finally:
    shutil.rmtree(scratch)
    result["scratch_removed"] = not scratch.exists()
    result["source_manifest_sha256"] = sha(SOURCE / "FILES.json")
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
