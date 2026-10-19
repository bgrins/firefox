#!/usr/bin/env python3
"""Authenticate and check the isolated source proposal; never touch live sources."""
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


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)


def main():
    frozen = json.loads((ROOT / "FREEZE.json").read_text())
    assert digest(ROOT / "INPUTS.json") == frozen["inputs_sha256"]
    entries = json.loads((ROOT / "INPUTS.json").read_text())
    for name, expected in entries.items():
        assert digest(ROOT / name) == expected, name
    base = json.loads((ROOT / "BASE.json").read_text())["pins"]
    candidate = json.loads((ROOT / "CANDIDATE-PINS.json").read_text())
    for path, expected in candidate.items():
        assert digest(ROOT / path) == expected, path
    paths = {
        "servo/components/style/custom_properties.rs": "custom_properties.rs",
        "servo/components/style/properties/cascade.rs": "properties__cascade.rs",
        "servo/components/style/properties/mod.rs": "properties__mod.rs",
    }
    wpt = Path("testing/web-platform/tests/css/css-values/attr-typed-fallback-eligibility.html")
    with tempfile.TemporaryDirectory(prefix="typed-eligibility-") as tmp:
        work = Path(tmp)
        for path, flat in paths.items():
            assert digest(ROOT / "original" / flat) == base[path]
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "original" / flat, target)
        (work / wpt).parent.mkdir(parents=True, exist_ok=True)
        run(["patch", "-p1", "--batch", "-i", str(ROOT / "fix.patch")], work)
        for path, flat in paths.items():
            assert (work / path).read_bytes() == (ROOT / "candidate" / flat).read_bytes()
        assert (work / wpt).read_bytes() == (ROOT / wpt.name).read_bytes()
        run(["patch", "-R", "-p1", "--batch", "-i", str(ROOT / "fix.patch")], work)
        for path in paths:
            assert digest(work / path) == base[path]
        assert not (work / wpt).exists()
        html = (ROOT / wpt.name).read_text()
        script = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
        assert len(script) == 1
        cases = json.loads(re.search(r"const cases = (.*?);\n", script[0], re.S)[1])
        assert cases == json.loads((ROOT / "CASES.json").read_text())
        assert len(cases) == 12 and len({case["name"] for case in cases}) == 12
        js = work / "test.js"
        js.write_text(script[0])
        node = shutil.which("node") or "/opt/homebrew/bin/node"
        run([node, "--check", str(js)], work)
    print(json.dumps({
        "status": "PASS",
        "authenticated_entries": len(entries),
        "exact_combined_patch_apply_reverse": True,
        "wpt_cases": len(cases),
        "javascript_syntax": "PASS",
        "rust_compilation": "NOT RUN",
        "browser_execution": "NOT RUN",
        "semantic_proof": "NOT CLAIMED",
    }, indent=2))


if __name__ == "__main__":
    main()
