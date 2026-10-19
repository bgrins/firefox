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
    distribution = lean.parent.parent
    for name, expected in tool["dependencies"].items():
        if digest(distribution / name) != expected:
            raise SystemExit("toolchain dependency authentication failed: " + name)
    version = subprocess.check_output([str(lean), "--version"], text=True).strip()
    if version != tool["version"]:
        raise SystemExit("compiler version mismatch")
    from html.parser import HTMLParser
    class AnchorParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()
        def handle_starttag(self, tag, attrs):
            self.ids.update(v for k, v in attrs if k == "id")
    parser = AnchorParser()
    parser.feed((root / "prior-font-loading-3.html").read_text())
    for anchor in ["fontfaceset", "dom-fontfaceset-delete", "dom-fontfaceset-clear", "fontfacesource-workers"]:
        if anchor not in parser.ids:
            raise SystemExit("missing spec anchor: " + anchor)
    before = root / "source/layout/style/FontFaceSetWorkerImpl.cpp"
    after = root / "candidate/layout/style/FontFaceSetWorkerImpl.cpp"
    insertion = "  for (const auto& fontFamily : mFontFamilies.Values()) {\n    fontFamily->DetachFontEntries();\n  }\n\n"
    candidate = after.read_text()
    if candidate.count(insertion) != 1 or candidate.replace(insertion, "", 1) != before.read_text():
        raise SystemExit("unexpected native delta")
    gate = json.loads((root / "root-evidence/ROOT-NATIVE-WPT-v1.json").read_text())
    for pair in gate["pairs"].values():
        change = pair["changed_pins"]["layout/style/FontFaceSetWorkerImpl.cpp"]
        if digest(before) != change["before"] or digest(after) != change["after"]:
            raise SystemExit("native gate identity mismatch")
        for name, expected in pair["receipts"].items():
            if digest(root / "root-evidence" / Path(name).name) != expected:
                raise SystemExit("root receipt identity mismatch")
    metadata = json.loads((root / "root-evidence/WPT-METADATA-v2.json").read_text())
    test = root / "root-evidence/final-wpt-v2.js"
    if digest(test) != metadata["final_wpt_sha256"]:
        raise SystemExit("final WPT identity mismatch")
    tested = b"".join(line for line in test.read_bytes().splitlines(keepends=True)
                      if not line.startswith(b"// META: spec="))
    if hashlib.sha256(tested).hexdigest() != metadata["tested_wpt_sha256"]:
        raise SystemExit("executable WPT changed")
    if digest(root / "root-evidence/fix-candidate-v2.patch") != metadata["patch_sha256"]:
        raise SystemExit("patch identity mismatch")
    source = (root / "WorkerRebuild.lean").read_text()
    if re.search(r"\b(sorry|admit|axiom)\b", source):
        raise SystemExit("unproved declaration found")
    result = subprocess.run([str(lean), "WorkerRebuild.lean"], cwd=root,
                            capture_output=True, text=True)
    print(result.stdout, end="")
    print(result.stderr, end="")
    if result.returncode:
        raise SystemExit(result.returncode)
    reports = re.findall(r"'WorkerRebuild\.(\w+)' (.*)", result.stdout)
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
