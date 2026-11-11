#!/usr/bin/env python3
"""Recreate only the copied candidate and its three-file patch."""
from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "SOURCES.json").read_text())
for name, digest in manifest["files"].items():
    assert hashlib.sha256((ROOT / "source" / name).read_bytes()).hexdigest() == digest, name

names = [
    "servo/components/style/properties/helpers/animated_properties.mako.rs",
    "servo/ports/geckolib/glue.rs",
    "dom/smil/SMILCSSValueType.cpp",
]
patch = []
roles = {}
for name in names:
    before = (ROOT / "source" / name).read_text()
    after = before
    if name.endswith("animated_properties.mako.rs"):
        start = after.index("        use crate::values::computed::LengthOrAuto;", after.index("impl Animate for ClipRect {"))
        end = after.index("        Ok(ClipRect {", start)
        after = after[:start] + after[end:]
        for side in ("top", "right", "bottom", "left"):
            old = f"{side}: animate_component(&self.{side}, &other.{side})?"
            new = f"{side}: self.{side}.animate(&other.{side}, procedure)?"
            assert after.count(old) == 1
            after = after.replace(old, new)
    elif name.endswith("glue.rs"):
        start = after.index('#[unsafe(no_mangle)]\npub extern "C" fn Servo_AnimationValues_Add(')
        end = after.index('#[unsafe(no_mangle)]\npub extern "C" fn Servo_AnimationValues_GetZeroValue(', start)
        after = after[:start] + 'fn animate_for_smil(\n    a: &AnimationValue,\n    b: &AnimationValue,\n    procedure: Procedure,\n) -> Strong<AnimationValue> {\n    let Ok(value) = a.animate(b, procedure) else {\n        return Strong::null();\n    };\n    // Preserve SMIL\'s rejection of additive clip rectangles containing auto.\n    if let AnimationValue::Clip(computed::ClipRectOrAuto::Rect(rect)) = &value {\n        if rect.top.is_auto()\n            || rect.right.is_auto()\n            || rect.bottom.is_auto()\n            || rect.left.is_auto()\n        {\n            return Strong::null();\n        }\n    }\n    Arc::new(value).into()\n}\n\n#[unsafe(no_mangle)]\npub extern "C" fn Servo_AnimationValues_AddForSMIL(\n    a: &AnimationValue,\n    b: &AnimationValue,\n) -> Strong<AnimationValue> {\n    animate_for_smil(a, b, Procedure::Add)\n}\n\n#[unsafe(no_mangle)]\npub extern "C" fn Servo_AnimationValues_AccumulateForSMIL(\n    a: &AnimationValue,\n    b: &AnimationValue,\n    count: u64,\n) -> Strong<AnimationValue> {\n    animate_for_smil(a, b, Procedure::Accumulate { count })\n}\n\n' + after[end:]
    else:
        for op in ("Add", "Accumulate"):
            old = f"Servo_AnimationValues_{op}("
            assert after.count(old) == 1
            after = after.replace(old, f"Servo_AnimationValues_{op}ForSMIL(")
        after = after.replace(
            "      result = Servo_AnimationValues_AddForSMIL(*destValue, *valueToAdd).Consume();",
            "      result =\n          Servo_AnimationValues_AddForSMIL(*destValue, *valueToAdd).Consume();",
        ).replace(
            "      result = Servo_AnimationValues_AccumulateForSMIL(*destValue, *valueToAdd, aCount)",
            "      result = Servo_AnimationValues_AccumulateForSMIL(*destValue, *valueToAdd,\n                                                       aCount)",
        )
    assert before != after
    target = ROOT / "candidate" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(after)
    patch.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile="a/"+name, tofile="b/"+name))
    roles[name] = {"before_sha256": hashlib.sha256(before.encode()).hexdigest(), "after_sha256": hashlib.sha256(after.encode()).hexdigest()}
(ROOT / "native.patch").write_text("".join(patch))
(ROOT / "ROLES.json").write_text(json.dumps({"revision": manifest["revision"], "files": roles}, indent=2)+"\n")
print("Prepared three copied files and native.patch")
