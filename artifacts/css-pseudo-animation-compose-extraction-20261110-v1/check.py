#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CPP = "dom/animation/KeyframeEffect.cpp"
HEADER = "dom/animation/KeyframeEffect.h"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def function(source, signature, following):
    start = source.index(signature)
    return source[start:source.index(following, start)]

m = json.loads((ROOT / "SOURCES.json").read_text())
for name, expected in m["files"].items():
    data = (ROOT / "source" / name).read_bytes()
    assert digest(data) == expected, name
    assert data == subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", f"{m['revision']}:{name}"], cwd=REPO), name
old = (ROOT / "source" / CPP).read_text()
new = (ROOT / "candidate" / CPP).read_text()
start = "void KeyframeEffect::ComposeStyle(\n"
end = "bool KeyframeEffect::IsRunningOnCompositor()"
old_fn = function(old, start, end)
new_fn = function(new, start, end)
loop_start = old_fn.index("  for (size_t propIdx")
overflow = "  // If the animation produces a change hint"
loop_end = old_fn.index(overflow)
call = """  ComposeProperties(aComposeResult, mProperties, mBaseValues, computedTiming,
                    mEffectOptions.mIterationComposite, aPropertiesToSkip);

"""
assert new_fn == old_fn[:loop_start] + call + old_fn[loop_end:]
helper = function(new, "void KeyframeEffect::ComposeProperties(\n", start)
new_loop = helper[helper.index("  for (size_t propIdx"):]
assert new_loop.endswith("}\n\n")
new_loop = new_loop[:-3]
new_loop = new_loop.replace("aProperties", "mProperties").replace("aComputedTiming", "computedTiming")
# Restore the skip-set name after the property-array rename.
new_loop = new_loop.replace("mPropertiesToSkip", "aPropertiesToSkip")
new_call = """    Servo_AnimationCompose(&aComposeResult, opaqueTable, &prop.mProperty,
                           segment, &prop.mSegments.LastElement(),
                           &computedTiming, aIterationComposite);"""
assert new_loop.count(new_call) == 1
new_loop = new_loop.replace(new_call, "    ComposeStyleRule(aComposeResult, prop, *segment, computedTiming);")
assert new_loop.rstrip() == old_fn[loop_start:loop_end].rstrip()
assert old[:old.index("void KeyframeEffect::ComposeStyleRule(")] == new[:new.index("/* static */\nvoid KeyframeEffect::ComposeProperties(")]
assert old[old.index(end):] == new[new.index(end):]
for forbidden in ["mTarget", "mEffectOptions", "mBaseValues", "mProperties", "GetComputedTiming", "EffectSet::", "RequestRestyle", "mProgressOnLastCompose"]:
    assert forbidden not in helper, forbidden
assert "reinterpret_cast<const RawServoAnimationValueTable*>(&aBaseValues)" in helper
assert "MOZ_ASSERT(!aComputedTiming.mProgress.IsNull());" in helper
assert "base_values: &structs::RawServoAnimationValueTable" in (ROOT / "source/servo/ports/geckolib/glue.rs").read_text()
assert "ComposeStyleRule" not in new
assert "ComposeStyleRule" not in (ROOT / "candidate" / HEADER).read_text()
with tempfile.TemporaryDirectory(prefix="css-pseudo-compose-") as tmp:
    tmp = Path(tmp)
    shutil.copytree(ROOT / "source", tmp / "source")
    shutil.copyfile(ROOT / "prepare.py", tmp / "prepare.py")
    subprocess.run(["python3", str(tmp / "prepare.py")], check=True)
    assert (tmp / "extraction.patch").read_bytes() == (ROOT / "extraction.patch").read_bytes()
    for name in [CPP, HEADER]:
        assert (tmp / "candidate" / name).read_bytes() == (ROOT / "candidate" / name).read_bytes()
    scratch = tmp / "applied"
    shutil.copytree(ROOT / "source", scratch)
    for reverse in [False, True]:
        command = ["patch", "-p1", "-i", str(ROOT / "extraction.patch")]
        if reverse:
            command.append("-R")
        subprocess.run(command, cwd=scratch, check=True, capture_output=True)
        for name in [CPP, HEADER]:
            expected_dir = "source" if reverse else "candidate"
            assert (scratch / name).read_bytes() == (ROOT / expected_dir / name).read_bytes()
print(json.dumps({"result": "PASS", "pinned_files": len(m["files"]), "edited_files": 2, "ordinary_timing_guard_and_overflow": "exact", "selected_segment_loop": "exact modulo explicit operands and inlined FFI call", "deterministic_prepare": True, "apply_reverse": True, "compiled": False, "runtime_tested": False, "patch_sha256": digest((ROOT / "extraction.patch").read_bytes())}, indent=2))
