#!/usr/bin/env python3
"""Authenticate both closed inputs before any replay; never read live sources."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root, manifest_name, expected, excludes, nested):
    assert digest(root / manifest_name) == expected, "manifest authentication"
    content = json.loads((root / manifest_name).read_text())
    entries = content["files"] if nested else content
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    assert actual == set(entries) | set(excludes), "closed inventory"
    for name, value in entries.items():
        rel = Path(name)
        assert not rel.is_absolute() and ".." not in rel.parts
        path = root / rel
        assert path.resolve().is_relative_to(root)
        for part in [path, *path.parents]:
            if part == root:
                break
            assert not part.is_symlink(), "symlink dependency"
        assert digest(path) == value, "input authentication: " + name
    return len(entries)

def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, (command, result.stdout, result.stderr)
    return result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dependency", type=Path, default=ROOT.parent / "css-fontface-provider-integration-review-v1")
    parser.add_argument("--checks", action="store_true")
    args = parser.parse_args()
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    count = authenticate(ROOT, "MANIFEST.json", freeze["manifest_sha256"], ["MANIFEST.json", "FREEZE.json"], False)
    pin = json.loads((ROOT / "DEPENDENCY.json").read_text())
    dep = args.dependency.resolve()
    assert digest(dep / "FREEZE.json") == pin["freeze_sha256"]
    external = authenticate(dep, "MANIFEST.json", pin["manifest_sha256"], ["MANIFEST.json", "FREEZE.json"], True)
    package = dep / "candidate-package"
    observations = {}
    for phase in ["baseline-v2", "canvas-baseline-v1"]:
        receipt = json.loads((ROOT / "evidence" / (phase + "-receipt.json")).read_text())
        assert receipt["all_inputs_unchanged"] and receipt["pins_before"] == receipt["pins_after"]
        for name, sha in receipt["pins_before"].items():
            path = ROOT / "evidence" / Path(name).name
            if path.exists() and name.startswith("testing/"):
                assert digest(path) == sha
        statuses = defaultdict(Counter)
        for line in (ROOT / "evidence" / (phase + ".jsonl")).read_text().splitlines():
            row = json.loads(line)
            if row.get("action") in ["test_status", "test_end"]:
                statuses[row["test"]][row["status"]] += 1
        observations[phase] = {name: dict(counts) for name, counts in statuses.items() if "loaded-size-adjust" in name}
        for name, counts in observations[phase].items():
            assert counts == receipt["counts"][name]
    if args.checks:
        run([sys.executable, "-I", "-S", "-B", str(dep / "check.py"), "--manifest-sha", pin["manifest_sha256"]], dep)
        with tempfile.TemporaryDirectory(prefix="fontface-independent-source-") as tmp:
            work = Path(tmp)
            expected = {}
            for relative, patch in [("", "common.patch"), ("backend", "backend-clone.patch")]:
                part = package / relative
                for source in (part / "original").rglob("*"):
                    if source.is_file():
                        name = source.relative_to(part / "original")
                        assert name not in expected
                        dest = work / name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, dest)
                        expected[name] = (source, part / "candidate" / name)
                run(["patch", "-p1", "--batch", "-i", str(part / patch)], work)
            assert len(expected) == 16
            for name, (_, candidate) in expected.items():
                assert (work / name).read_bytes() == candidate.read_bytes(), str(name)
            for relative, patch in [("backend", "backend-clone.patch"), ("", "common.patch")]:
                run(["patch", "-R", "-p1", "--batch", "-i", str(package / relative / patch)], work)
            for name, (original, _) in expected.items():
                assert (work / name).read_bytes() == original.read_bytes(), str(name)
            html = (ROOT / "evidence/fontface-loaded-size-adjust-update.html").read_text()
            scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
            assert len(scripts) == 1
            js = work / "dom.js"
            js.write_text(scripts[0])
            run(["node", "--check", str(js)], work)
            run(["node", "--check", str(ROOT / "evidence/fontface-loaded-size-adjust-canvas.any.js")], work)
    print(json.dumps({"status": "PASS", "local_files": count, "external_files": external, "source_checks": args.checks, "raw_observations": observations, "native_compilation": False, "browser_execution": False}, indent=2))

if __name__ == "__main__":
    main()
