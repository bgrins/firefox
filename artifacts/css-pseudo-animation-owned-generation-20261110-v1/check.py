import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(text):
    return re.sub(r"\s+", "", text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-git", action="store_true")
    args = parser.parse_args()
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, digest in pins["files"].items():
        data = (HERE / "source" / name).read_bytes()
        assert sha(data) == digest, name
        if args.check_git:
            assert data == subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", pins["revision"] + ":" + name], cwd=HERE), name
    tests = json.loads((HERE / "TEST-SOURCES.json").read_text())
    for name, digest in tests["files"].items():
        if digest is not None:
            assert sha((HERE / "test-source" / name).read_bytes()) == digest, name
        else:
            assert not (HERE / "test-source" / name).exists()
        if args.check_git:
            result = subprocess.run(["git", "-c", "core.fsmonitor=false", "show", tests["revision"] + ":" + name], cwd=HERE, capture_output=True)
            assert (result.returncode != 0) if digest is None else (result.returncode == 0 and sha(result.stdout) == digest), name
    for name, fixture in tests["fixtures"].items():
        data = (HERE / fixture["copy"]).read_bytes()
        assert sha(data) == fixture["sha256"]
        if args.check_git:
            assert data == subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", tests["revision"] + ":" + fixture["origin"]], cwd=HERE)
    roles = json.loads((HERE / "ROLES.json").read_text())
    assert roles["revision"] == pins["revision"] and len(roles["files"]) == 4
    for name, role in roles["files"].items():
        assert role["before_sha256"] == pins["files"][name]
        assert sha((HERE / "candidate" / name).read_bytes()) == role["after_sha256"]
    with tempfile.TemporaryDirectory(prefix="owned-keyframe-generation-") as directory:
        scratch = Path(directory)
        for name in roles["files"]:
            destination = scratch / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / "source" / name, destination)
        for reverse, expected in [(False, "candidate"), (True, "source")]:
            command = ["patch", "--batch", "-p1", "-i", str(HERE / "owned-generation.patch")]
            if reverse:
                command.append("-R")
            subprocess.run(command, cwd=scratch, check=True, capture_output=True)
            for name in roles["files"]:
                assert (scratch / name).read_bytes() == (HERE / expected / name).read_bytes()
    name = "dom/animation/KeyframeEffect.cpp"
    before = (HERE / "source" / name).read_text()
    after = (HERE / "candidate" / name).read_text()
    start = before.index("nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(")
    end = before.index("\ntemplate <typename FrameEnumFunc>", start)
    new_start = after.index("bool KeyframeEffect::GetComputedKeyframes(")
    new_end = after.index("\ntemplate <typename FrameEnumFunc>", new_start)
    assert before[:start] == after[:new_start] and before[end:] == after[new_end:]
    ordinary_start = after.index("nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(", new_start)
    ordinary = after[ordinary_start:new_end]
    old_body = before[start:end]
    assert ordinary.startswith(old_body[:old_body.index("  // When GetComputedKeyframeValues")])
    assert compact(old_body[old_body.index("#ifdef DEBUG"):].replace("keyframesCopy", "inputs.mSpecifiedKeyframes")) == compact(ordinary[ordinary.index("#ifdef DEBUG"):])
    assert "RefreshComputedOffsets" not in ordinary
    assert after[new_start:new_end].count("mKeyframes.Clone()") == 1
    capture_start = after.index("KeyframeEffect::PropertyInputSnapshot KeyframeEffect::CapturePropertyInputs()", new_start)
    capture_end = after.index("/* static */", capture_start)
    capture = after[capture_start:capture_end]
    assert capture.index("mKeyframes.Clone()") < capture.index("CaptureCSSGenerationOptions()") < capture.index("PropertyInputSnapshot(mTarget")
    helper_start = after.index("nsTArray<AnimationProperty> KeyframeEffect::BuildPropertiesFromInputs(", capture_end)
    helper = after[helper_start:ordinary_start]
    assert "aReferencesAttributes = false;" in helper
    assert compact("aInputs.mCSSGenerationOptions->GenerateComputedKeyframes(aInputs.mSpecifiedKeyframes, computedKeyframes);") in compact(helper)
    assert compact("keyframes, aInputs.mTarget.mElement, aInputs.mTarget.mPseudoRequest, aStyle, aInputs.mComposite, aTimeline, aReferencesAttributes") in compact(helper)
    for forbidden in ["UpdateProperties(", "RequestRestyle(", "EnsureBaseStyle", "mReferencesAttributes", "mProperties ="]:
        assert forbidden not in helper
    refresh_start = after.index("KeyframeEffect::PropertyInputSnapshot::RefreshComputedOffsets(")
    refresh = after[refresh_start:after.index("\n}", refresh_start)]
    assert compact("return KeyframeUtils::ComputeMissingKeyframeOffsets(mSpecifiedKeyframes, aTimeline, aRange);") in compact(refresh)
    name = "dom/animation/CSSAnimation.cpp"
    before = (HERE / "source" / name).read_text()
    after = (HERE / "candidate" / name).read_text()
    old_start = before.index("// The step 3 (Generate Initial and Final Frames) in")
    old_end = before.index("\nvoid CSSAnimationKeyframeEffect::MaybeFlushUnanimatedStyle", old_start)
    new_start = after.index("Maybe<KeyframeEffect::CSSKeyframeGenerationOptions>")
    new_end = after.index("\nvoid CSSAnimationKeyframeEffect::MaybeFlushUnanimatedStyle", new_start)
    assert before[:old_start] == after[:new_start] and before[old_end:] == after[new_end:]
    old_generation = before[before.index("  // FIXME:", old_start):old_end]
    new_generation = after[after.index("  // FIXME:", new_start):new_end]
    expected = old_generation.replace("mKeyframes", "aSpecifiedKeyframes").replace("  return true;\n", "")
    assert compact(expected) == compact(new_generation), "generation algorithm changed beyond explicit array and void result"
    capture = after[new_start:after.index("// The step 3", new_start)]
    assert compact("if (mIgnoreKeyframesGeneration) { return Nothing(); }") in compact(capture)
    assert compact("CSSKeyframeGenerationOptions{mDefaultTimingFunction, mDefaultComposite}") in compact(capture)
    header = (HERE / "candidate/dom/animation/KeyframeEffect.h").read_text()
    assert "mComputedKeyframes" not in header and "mHasComputedKeyframes" not in header
    assert "virtual bool GetComputedKeyframes" not in header
    assert header.count("virtual Maybe<CSSKeyframeGenerationOptions> CaptureCSSGenerationOptions()") == 1
    manifest = json.loads((HERE / "FILES.json").read_text())
    for name, digest in manifest.items():
        assert sha((HERE / name).read_bytes()) == digest, name
    print(json.dumps({"status": "PASS", "source_pins": len(pins["files"]), "test_presence_pins": len(tests["files"]), "retained_fixtures": len(tests["fixtures"]), "git_checked": args.check_git, "patch_paths": 4, "forward_reverse_replay": True, "ordinary_admission_and_writeback_preserved": True, "single_specified_clone": True, "CSS_generation_algorithm_preserved": True, "no_cached_completed_array": True, "GetKeyframes_and_live_offset_refresh_unchanged": True, "native_or_browser_execution": False}, indent=2))


if __name__ == "__main__":
    main()
