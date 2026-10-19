import hashlib
import json
from pathlib import Path
import shutil

here = Path(__file__).resolve().parent
source = here.parent / "css-hyphenation-coordinate-companion-v2"
target = here.parent / "css-hyphenation-coordinate-companion-v3"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


expected = "c1f708254222193e5e48d032099a28747d92e2501473824ba0a6e24321cb117f"
assert digest(source / "MANIFEST.json") == expected
original = json.loads((source / "MANIFEST.json").read_text())["files"]
target.mkdir()
for name, pinned in original.items():
    assert digest(source / name) == pinned, name
    destination = target / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / name, destination)
checker = target / "check.py"
text = checker.read_text()
old = "rootOriginal=helper['full'](R/'guard/source/original-gfxTextRun.cpp',marker)\nrootCandidate=helper['full'](R/'guard/source/candidate-gfxTextRun.cpp',marker)"
new = """shutil.copy2(R/'guard/source/original-gfxTextRun.cpp',full/'coordinate-original.cpp')
shutil.copy2(R/'guard/source/candidate-gfxTextRun.cpp',full/'coordinate-candidate.cpp')
rootOriginal=helper['full'](full/'coordinate-original.cpp',marker)
rootCandidate=helper['full'](full/'coordinate-candidate.cpp',marker)"""
assert text.count(old) == 1
checker.write_text(text.replace(old, new))
readme = target / "README.md"
readme.write_text(readme.read_text() + """

## Version 3 extraction paths

Root's relocated v2 run passed the complete baseline native/model replay and
the guard kernel replay, then stopped before candidate compilation because the
extractor records paths relative to its consumer source tree. This version
copies the two authenticated complete source snapshots into the freshly built
consumer's development directory before extraction. Source bytes, complete
method comparison, compiler commands, fixtures and expected outputs are
unchanged. Original v1/v2 capsules and root failure receipts are preserved.
""")
origin = {"manifest_sha256": expected,
          "unchanged_files": {name: pinned for name, pinned in original.items()
                              if digest(target / name) == pinned},
          "changed": ["check.py", "README.md"], "new": ["V2-ORIGIN.json"],
          "scope_unchanged": True}
(target / "V2-ORIGIN.json").write_text(json.dumps(origin, indent=2) + "\n")
files = {str(p.relative_to(target)): digest(p) for p in sorted(target.rglob("*")) if p.is_file()}
(target / "MANIFEST.json").write_text(json.dumps({"files": files}, indent=2) + "\n")
freeze = {"manifest_sha256": digest(target / "MANIFEST.json"), "files": len(files),
          "bytes": sum((target / name).stat().st_size for name in files),
          "status": "Frozen source-only wrapper; root complete fresh replay pending.",
          "no_generated_inputs": True}
(target / "FREEZE.json").write_text(json.dumps(freeze, indent=2) + "\n")
print(json.dumps(freeze, indent=2))
