#!/usr/bin/env python3
"""Check frozen pins, scratch patch replay, and the finite compatibility model."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
if (ROOT / "FILES.json").exists():
    for name, digest in json.loads((ROOT / "FILES.json").read_text()).items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
parser = argparse.ArgumentParser()
parser.add_argument("--check-git", action="store_true")
args = parser.parse_args()
manifest = json.loads((ROOT / "SOURCES.json").read_text())
roles = json.loads((ROOT / "ROLES.json").read_text())
assert roles["revision"] == manifest["revision"]
for name, digest in manifest["files"].items():
    data = (ROOT / "source" / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, name
    if args.check_git:
        pinned = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", manifest["revision"]+":"+name], cwd=ROOT)
        assert data == pinned, name
for name, role in roles["files"].items():
    assert role["before_sha256"] == manifest["files"][name]
    assert hashlib.sha256((ROOT/"candidate"/name).read_bytes()).hexdigest() == role["after_sha256"]
with tempfile.TemporaryDirectory(prefix="clip-auto-candidate-") as directory:
    scratch = Path(directory)
    for name in roles["files"]:
        target = scratch/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/"source"/name, target)
    for reverse, expected in ((False, "candidate"), (True, "source")):
        command = ["patch", "--batch", "-p1", "-i", str(ROOT/"native.patch")]
        if reverse:
            command.append("-R")
        subprocess.run(command, cwd=scratch, check=True, capture_output=True)
        for name in roles["files"]:
            assert (scratch/name).read_bytes() == (ROOT/expected/name).read_bytes(), name

cpp = "dom/smil/SMILCSSValueType.cpp"
old = (ROOT/"source"/cpp).read_text()
new = (ROOT/"candidate"/cpp).read_text()
for operation in ("Add", "Accumulate"):
    new = new.replace("Servo_AnimationValues_"+operation+"ForSMIL(", "Servo_AnimationValues_"+operation+"(")
assert old.split() == new.split(), "C++ logic changed beyond names/formatting"
glue = (ROOT/"candidate/servo/ports/geckolib/glue.rs").read_text()
assert glue.count("animate_for_smil(") == 3, "Two arithmetic-only callers required"
assert "animate_for_smil(a, b, Procedure::Add)" in glue
assert "animate_for_smil(a, b, Procedure::Accumulate { count })" in glue
assert "AnimationValue::Clip(computed::ClipRectOrAuto::Rect(rect))" in glue
for side in ("top", "right", "bottom", "left"):
    assert f"rect.{side}.is_auto()" in glue

spec = importlib.util.spec_from_file_location("clip_model", ROOT/"model.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
model = module.main()
assert json.loads(json.dumps(model)) == json.loads((ROOT/"MODEL.json").read_text())
print(json.dumps({"status": "PASS", "pinned_files": len(manifest["files"]),
    "git_objects_checked": len(manifest["files"]) if args.check_git else 0,
    "patch_files": len(roles["files"]), "forward_reverse_replay": True,
    "abstract_result_category_cases": model["abstract_result_category_cases"],
    "tagged_integer_cases": model["tagged_integer_cases"],
    "semantic_mutants_rejected": len(model["rejected_mutants"]),
    "native_build_or_browser_claim": False}, indent=2))
