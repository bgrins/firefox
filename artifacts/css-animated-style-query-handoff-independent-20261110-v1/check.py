#!/usr/bin/env python3
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
repo = base.parent.parent
sources = json.loads((base / "SOURCES.json").read_text())
for name, pin in sources.items():
    data = (repo / pin["location"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == pin["sha256"], name
    original = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "show", f"{pin['revision']}:{name}"],
        cwd=repo, capture_output=True, check=True,
    ).stdout
    assert data == original, name
reviewed = json.loads((base / "REVIEWED.json").read_text())
patch = (base / reviewed["candidate"]).read_bytes()
assert hashlib.sha256(patch).hexdigest() == reviewed["sha256"]
paths = ["servo/components/style/gecko/traversal.rs", "servo/ports/geckolib/glue.rs"]
originals = {path: (repo / sources[path]["location"]).read_text() for path in paths}
candidates = {path: (base / reviewed["candidate_directory"] / path).read_text() for path in paths}
expected = "".join(
    "".join(difflib.unified_diff(originals[path].splitlines(True),
        candidates[path].splitlines(True), fromfile="a/" + path, tofile="b/" + path))
    for path in paths
)
assert expected.encode() == patch
source = originals[paths[0]]
start = source.index("            if self.shared.traversal_flags.for_animation_only()")
end = source.index("\n            }", start) + len("\n            }")
assert source[start:end] in candidates[paths[0]]
source = originals[paths[1]]
start = source.index("    if traversal.needs_normal_descendant_restyle() {")
end = source.index("\n}\n", start)
assert source[start:end] in candidates[paths[1]]
print(json.dumps({
    "result": "PASS", "source_count": len(sources), "candidate_files": paths,
    "patch_sha256": reviewed["sha256"], "font_capture_byte_identical": True,
    "font_replay_byte_identical": True,
    "scope": "Pinned source and candidate authentication, font preservation; no native build or browser test",
}, indent=2))
