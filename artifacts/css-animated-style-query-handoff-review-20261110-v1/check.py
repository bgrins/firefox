from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

capsule = Path(__file__).resolve().parent
root = capsule.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def block(text, marker):
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if depth == 0:
            return text[start:end + 1]
    raise AssertionError(marker)


manifest = json.loads((capsule / "FILES.json").read_text())
actual = {str(path.relative_to(capsule)) for path in capsule.rglob("*")
          if path.is_file() and path.name not in {"FILES.json", "CHECK.json"}}
assert actual == set(manifest), "Capsule file set changed"
for name, expected in manifest.items():
    assert digest((capsule / name).read_bytes()) == expected, name

sources = json.loads((capsule / "SOURCES.json").read_text())
for path, record in sources.items():
    data = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "show", record["revision"] + ":" + path],
        cwd=root, capture_output=True, check=True,
    ).stdout
    assert digest(data) == record["sha256"], path
    assert data == (capsule / "source" / path).read_bytes(), path

roles = json.loads((capsule / "SOURCE-ROLES.json").read_text())
assert set(roles) == {"servo/components/style/gecko/traversal.rs", "servo/ports/geckolib/glue.rs"}
with tempfile.TemporaryDirectory(prefix=".replay-", dir=capsule) as directory:
    scratch = Path(directory)
    for path, record in roles.items():
        data = (capsule / record["base"]).read_bytes()
        assert digest(data) == record["base_sha256"]
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    replay = subprocess.run(
        ["patch", "-p1", "-F0", "--batch", "--forward", "-i", str(capsule / "query-handoff.patch")],
        cwd=scratch, capture_output=True, check=True,
    )
    for path, record in roles.items():
        data = (scratch / path).read_bytes()
        assert data == (capsule / record["candidate"]).read_bytes(), path
        assert digest(data) == record["candidate_sha256"], path

for path, marker in [
    ("servo/components/style/gecko/traversal.rs", "pub fn needs_normal_descendant_restyle"),
    ("servo/components/style/gecko/traversal.rs",
     "if self.shared.traversal_flags.for_animation_only()\n                && child_hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)"),
    ("servo/ports/geckolib/glue.rs", "if traversal.needs_normal_descendant_restyle()"),
]:
    assert block((capsule / "source" / path).read_text(), marker) == block(
        (capsule / "candidate" / path).read_text(), marker), marker

for record in json.loads((capsule / "INPUTS.json").read_text()):
    assert digest((capsule / record["file"]).read_bytes()) == record["sha256"]

bug = json.loads((capsule / "bug2085413.json").read_text())["bugs"][0]
assert bug["id"] == 2085413
print(json.dumps({"status": "PASS", "files": len(manifest),
                  "git_sources": len(sources), "patch_files": len(roles),
                  "font_blocks_unchanged": 3, "native_build_or_tests": False,
                  "scratch_removed": not Path(directory).exists()}, indent=2))
