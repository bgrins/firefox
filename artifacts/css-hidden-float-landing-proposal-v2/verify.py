import difflib
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(body, patch, reverse=False):
    lines = patch.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith("@@ ")]
    for index, start in enumerate(starts):
        stop = starts[index + 1] if index + 1 < len(starts) else len(lines)
        match = re.fullmatch(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@\n", lines[start])
        assert match
        hunk = lines[start + 1:stop]
        assert all(line[:1] in (" ", "+", "-") for line in hunk)
        old = "".join(line[1:] for line in hunk if line[0] != "+")
        new = "".join(line[1:] for line in hunk if line[0] != "-")
        assert len(old.splitlines()) == int(match[2])
        assert len(new.splitlines()) == int(match[4])
        if reverse:
            old, new = new, old
        assert body.count(old) == 1
        body = body.replace(old, new, 1)
    assert starts
    return body


bindings = json.loads((HERE / "BINDINGS.json").read_text())
for parent, pin in bindings["parent_FILES_sha256"].items():
    manifest = ROOT / "artifacts" / parent / "FILES.json"
    assert digest(manifest) == pin
    for name, expected in json.loads(manifest.read_text()).items():
        assert digest(manifest.parent / name) == expected, name

bodies = {}
for role, entry in bindings["source_roles"].items():
    path = ROOT / entry["path"]
    assert digest(path) == entry["sha256"]
    bodies[role] = path.read_text()
patch = (HERE / "gecko.patch").read_text()
assert apply(bodies["head"], patch) == bodies["float_without_block"]
assert apply(bodies["float_without_block"], patch, True) == bodies["head"]
assert apply(bodies["block_without_float"], patch) == bodies["tested_block_and_float"]
assert apply(bodies["tested_block_and_float"], patch, True) == bodies["block_without_float"]
block_patch = "".join(difflib.unified_diff(
    bodies["head"].splitlines(True), bodies["block_without_float"].splitlines(True)
))
assert apply(bodies["float_without_block"], block_patch) == bodies["tested_block_and_float"]
assert apply(bodies["tested_block_and_float"], block_patch, True) == bodies["float_without_block"]

draft = ROOT / "artifacts/css-hidden-float-wpt-draft-v1"
name = "hidden-float-owner-queries.html"
original = (draft / name).read_text()
final = (HERE / name).read_text()
cleanup = (HERE / "wpt-cleanup.patch").read_text()
assert apply(original, cleanup) == final
assert apply(final, cleanup, True) == original
assert "nested-block" not in final and "floatOwnerQueryResults" not in final
push = "visible-float-push-calibration.html"
push_original = (draft / push).read_text()
push_final = (HERE / push).read_text()
push_cleanup = (HERE / "push-cleanup.patch").read_text()
assert apply(push_original, push_cleanup) == push_final
assert apply(push_final, push_cleanup, True) == push_original
assert "visibleFloatPushResults" not in push_final and "getComputedStyle" not in push_final
combined = patch
for filename in (name, push):
    target = "testing/web-platform/tests/css/css-contain/content-visibility/" + filename
    combined += "".join(difflib.unified_diff(
        [], (HERE / filename).read_text().splitlines(True),
        fromfile="/dev/null", tofile="b/" + target
    ))
assert combined == (HERE / "proposed-fix.patch").read_text()
assert len(bindings["proposed_commit_paths"]) == 3
print("PASS: parent seals, source composition/apply/reverse, WPT cleanup/reverse, exact three-path patch")
