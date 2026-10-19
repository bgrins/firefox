#!/usr/bin/env python3
"""Authenticate and check proposal packaging without running browser callbacks."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    assert result.returncode == 0, (command, result.stdout, result.stderr)
    return result.stdout

def main():
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    assert digest(ROOT / "MANIFEST.json") == freeze["manifest_sha256"]
    entries = json.loads((ROOT / "MANIFEST.json").read_text())
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}
    assert actual == set(entries) | {"MANIFEST.json", "FREEZE.json"}
    for name, expected in entries.items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT) and not path.is_symlink()
        assert digest(path) == expected, name
    html = "fontface-loaded-size-adjust-update.html"
    js = "fontface-loaded-size-adjust-canvas.any.js"
    assert (ROOT / "proposal" / html).read_bytes() == (ROOT / "original" / html).read_bytes()
    assert (ROOT / "proposal" / js).read_bytes() == (ROOT / "original" / js).read_bytes() + (ROOT / "expanded-cases.js").read_bytes()
    registered = json.loads(run(["node", str(ROOT / "register.cjs"), str(ROOT)], ROOT))
    assert registered == json.loads((ROOT / "CASES.json").read_text())
    assert [len(v) for v in registered.values()] == [12, 28, 28]
    with tempfile.TemporaryDirectory(prefix="fontface-wpt-proposal-") as temp:
        work = Path(temp)
        dest = work / "testing/web-platform/tests/css/css-font-loading"
        dest.mkdir(parents=True)
        for name in [html, js]:
            shutil.copyfile(ROOT / "original" / name, dest / name)
        run(["patch", "-p1", "--batch", "-i", str(ROOT / "extension.patch")], work)
        for name in [html, js]:
            assert (dest / name).read_bytes() == (ROOT / "proposal" / name).read_bytes()
        run(["node", "--check", str(dest / js)], work)
        scripts = re.findall(r"<script>(.*?)</script>", (dest / html).read_text(), re.S)
        assert len(scripts) == 1
        script = work / "dom.js"
        script.write_text(scripts[0])
        run(["node", "--check", str(script)], work)
        run(["patch", "-R", "-p1", "--batch", "-i", str(ROOT / "extension.patch")], work)
        for name in [html, js]:
            assert (dest / name).read_bytes() == (ROOT / "original" / name).read_bytes()
    print(json.dumps({"status": "PASS", "authenticated_files": len(entries), "registered_counts": [12, 28, 28], "registered_total": 68, "old_case_bytes_preserved": True, "exact_extension_apply_reverse": True, "javascript_syntax": "PASS", "callbacks_executed": False, "browser_execution": False}, indent=2))

if __name__ == "__main__":
    main()
