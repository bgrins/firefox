import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument("--check-git", action="store_true")
options = args.parse_args()
pins = json.loads((HERE / "SOURCES.json").read_text())
roles = json.loads((HERE / "ROLES.json").read_text())
for name, digest in pins["files"].items():
    data = (HERE / "source" / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, name
    if options.check_git:
        assert data == subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", "show", pins["revision"] + ":" + name],
            cwd=HERE,
        ), name
assert roles["revision"] == pins["revision"]
assert len(roles["files"]) == 4
for name, role in roles["files"].items():
    assert role["before_sha256"] == pins["files"][name]
    assert hashlib.sha256((HERE / "candidate" / name).read_bytes()).hexdigest() == role["after_sha256"]
with tempfile.TemporaryDirectory(prefix="keyframe-group-order-") as directory:
    scratch = Path(directory)
    for name in roles["files"]:
        dest = scratch / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / "source" / name, dest)
    for reverse, expected in [(False, "candidate"), (True, "source")]:
        command = ["patch", "--batch", "-p1", "-i", str(HERE / "ordering.patch")]
        if reverse:
            command.append("-R")
        subprocess.run(command, cwd=scratch, check=True, capture_output=True)
        for name in roles["files"]:
            assert (scratch / name).read_bytes() == (HERE / expected / name).read_bytes(), name
name = "layout/style/GeckoBindings.cpp"
before = (HERE / "source" / name).read_text()
after = (HERE / "candidate" / name).read_text().replace("\n#include <algorithm>\n", "", 1)
start = before.index("Keyframe* Gecko_GetOrCreateKeyframeForPercentageOffset(")
end = before.index("\nKeyframe* Gecko_GetOrCreateKeyframeForTimelineRangeOffset(", start)
new_start = after.index("Keyframe* Gecko_GetOrCreateKeyframeForPercentageOffset(")
new_end = after.index("\nKeyframe* Gecko_GetOrCreateKeyframeForTimelineRangeOffset(", new_start)
assert before[:start] == after[:new_start] and before[end:] == after[new_end:]
assert "std::rotate(keyframe, keyframe + 1," in after[new_start:new_end]
assert "return &aKeyframes->LastElement();" in after[new_start:new_end]
metadata = "testing/web-platform/meta/css/css-animations/KeyframeEffect-getKeyframes.tentative.html.ini"
old = (HERE / "source" / metadata).read_text()
new = (HERE / "candidate" / metadata).read_text()
start = old.index("  [KeyframeEffect.getKeyframes() returns expected frames for an animation with multiple keyframes for the same time and with different easing functions and composite operations]")
end = old.index("  [", start + 3)
assert old[:start] + old[end:] == new
assert new.count("expected: FAIL") == 2
manifest = json.loads((HERE / "FILES.json").read_text())
for name, digest in manifest.items():
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
print(json.dumps({"status": "PASS", "frozen_files": len(manifest), "source_pins": len(pins["files"]), "git_checked": options.check_git, "patch_paths": 4, "forward_reverse_replay": True, "unchanged_shared_and_range_helpers": True, "metadata_removal_only_known_bug": True, "native_or_browser_execution": False}, indent=2))
