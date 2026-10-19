import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-sha", required=True)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = root / "MANIFEST.json"
    if digest(manifest) != args.manifest_sha:
        raise SystemExit("manifest authentication failed")
    files = json.loads(manifest.read_text())["files"]
    for name, expected in files.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit("unsafe manifest path")
        path = root / relative
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise SystemExit("symlink in manifest path")
        if digest(path) != expected:
            raise SystemExit("input authentication failed: " + name)
    tool = json.loads((root / "TOOLCHAIN.json").read_text())
    lean = Path(args.lean).resolve()
    if digest(lean) != tool["lean_sha256"]:
        raise SystemExit("compiler authentication failed")
    version = subprocess.check_output([str(lean), "--version"], text=True).strip()
    if version != tool["version"]:
        raise SystemExit("compiler version mismatch")
    source = (root / "FreshProvider.lean").read_text()
    if re.search(r"\b(sorry|admit|axiom)\b", source):
        raise SystemExit("unproved declaration found")
    result = subprocess.run([str(lean), "FreshProvider.lean"], cwd=root,
                            capture_output=True, text=True)
    print(result.stdout, end="")
    print(result.stderr, end="")
    if result.returncode:
        raise SystemExit(result.returncode)
    reports = re.findall(r"'FreshProvider\.(\w+)' (.*)", result.stdout)
    declarations = re.findall(r"^theorem (\w+)", source, re.MULTILINE)
    if sorted(name for name, _ in reports) != sorted(declarations):
        raise SystemExit("incomplete theorem audit")
    for _, report in reports:
        if report == "does not depend on any axioms":
            continue
        match = re.fullmatch(r"depends on axioms: \[(.*)\]", report)
        if not match or not set(match[1].split(", ")).issubset(
                {"propext", "Quot.sound", "Classical.choice"}):
            raise SystemExit("nonstandard theorem axiom")
    print(json.dumps({"authenticated_files": len(files),
                      "theorem_reports": len(reports),
                      "native_execution": False,
                      "browser_execution": False}))


if __name__ == "__main__":
    main()
