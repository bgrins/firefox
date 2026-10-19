from pathlib import Path
import hashlib
import json
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


root = Path(__file__).resolve().parent
manifest = json.loads((root / "MANIFEST.json").read_text())
seal = json.loads((root / "FREEZE.json").read_text())
assert digest(root / "MANIFEST.json") == seal["manifest_sha256"]
assert all(not p.is_symlink() for p in root.rglob("*"))
assert {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} == (
    set(manifest) | {"MANIFEST.json", "FREEZE.json"}
)
for name, expected in manifest.items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert digest(root / name) == expected, name
sources = json.loads((root / "SOURCES.json").read_text())
for name, record in sources["files"].items():
    assert digest(root / "source" / name) == record["sha256"], name
    if len(sys.argv) == 2:
        assert digest(Path(sys.argv[1]) / name) == record["sha256"], name
print(json.dumps({
    "status": "PASS",
    "inputs": len(manifest),
    "sources": len(sources["files"]),
    "live_sources_checked": len(sys.argv) == 2,
    "scope": "source identity only; no behavioral proof or native execution",
}))
