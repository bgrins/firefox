import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
FILES = ["dom/animation/KeyframeEffect.h", "dom/animation/KeyframeEffect.cpp", "dom/animation/CSSAnimation.h", "dom/animation/CSSAnimation.cpp"]


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)


def prepare():
    texts = {name: (HERE / "source" / name).read_text() for name in FILES}
    name = "dom/animation/KeyframeEffect.h"
    texts[name] = replace_once(texts[name], """  virtual bool GetComputedKeyframes(nsTArray<Keyframe>& aKeyframes) const {
    return false;
  }
""", """  struct CSSKeyframeGenerationOptions {
    StyleComputedTimingFunction mDefaultTimingFunction;
    CompositeOperation mDefaultComposite;

    void GenerateComputedKeyframes(const nsTArray<Keyframe>& aSpecifiedKeyframes,
                                  nsTArray<Keyframe>& aKeyframes) const;
  };

  bool GetComputedKeyframes(nsTArray<Keyframe>& aKeyframes) const;
""")
    texts[name] = replace_once(texts[name], """  const nsTArray<AnimationProperty>& Properties() const { return mProperties; }
""", """  const nsTArray<AnimationProperty>& Properties() const { return mProperties; }

  // Owns specified keys and CSS defaults; declaration blocks remain shared.
  class PropertyInputSnapshot {
   public:
    KeyframeOffsetsHasRangeOffset RefreshComputedOffsets(
        const AnimationTimeline* aTimeline, const AnimationRange* aRange);
    const OwningAnimationTarget& Target() const { return mTarget; }

   private:
    friend class KeyframeEffect;

    PropertyInputSnapshot(
        const OwningAnimationTarget& aTarget, CompositeOperation aComposite,
        nsTArray<Keyframe>&& aSpecifiedKeyframes,
        Maybe<CSSKeyframeGenerationOptions>&& aCSSGenerationOptions)
        : mTarget(aTarget),
          mComposite(aComposite),
          mSpecifiedKeyframes(std::move(aSpecifiedKeyframes)),
          mCSSGenerationOptions(std::move(aCSSGenerationOptions)) {}

    OwningAnimationTarget mTarget;
    CompositeOperation mComposite;
    nsTArray<Keyframe> mSpecifiedKeyframes;
    Maybe<CSSKeyframeGenerationOptions> mCSSGenerationOptions;
  };

  PropertyInputSnapshot CapturePropertyInputs() const;
  static nsTArray<AnimationProperty> BuildPropertiesFromInputs(
      const PropertyInputSnapshot& aInputs, const ComputedStyle* aStyle,
      const AnimationTimeline* aTimeline, bool& aReferencesAttributes);
""")
    texts[name] = replace_once(texts[name], """ protected:
  ~KeyframeEffect() override = default;
""", """ protected:
  ~KeyframeEffect() override = default;

  virtual Maybe<CSSKeyframeGenerationOptions> CaptureCSSGenerationOptions()
      const {
    return Nothing();
  }
""")
    name = "dom/animation/KeyframeEffect.cpp"
    start = texts[name].index("nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(")
    end = texts[name].index("\ntemplate <typename FrameEnumFunc>", start)
    old = texts[name][start:end]
    admission = old[:old.index("  // When GetComputedKeyframeValues")]
    comment = old[old.index("  // When GetComputedKeyframeValues"):old.index("  auto keyframesCopy")]
    suffix = old[old.index("#ifdef DEBUG"):].replace("keyframesCopy", "inputs.mSpecifiedKeyframes")
    replacement = """bool KeyframeEffect::GetComputedKeyframes(
    nsTArray<Keyframe>& aKeyframes) const {
  auto options = CaptureCSSGenerationOptions();
  if (!options) {
    return false;
  }
  options->GenerateComputedKeyframes(mKeyframes, aKeyframes);
  return true;
}

KeyframeOffsetsHasRangeOffset
KeyframeEffect::PropertyInputSnapshot::RefreshComputedOffsets(
    const AnimationTimeline* aTimeline, const AnimationRange* aRange) {
  return KeyframeUtils::ComputeMissingKeyframeOffsets(mSpecifiedKeyframes,
                                                     aTimeline, aRange);
}

KeyframeEffect::PropertyInputSnapshot KeyframeEffect::CapturePropertyInputs()
    const {
""" + comment + """  auto specifiedKeyframes = mKeyframes.Clone();
  auto options = CaptureCSSGenerationOptions();
  return PropertyInputSnapshot(mTarget, mEffectOptions.mComposite,
                               std::move(specifiedKeyframes),
                               std::move(options));
}

/* static */
nsTArray<AnimationProperty> KeyframeEffect::BuildPropertiesFromInputs(
    const PropertyInputSnapshot& aInputs, const ComputedStyle* aStyle,
    const AnimationTimeline* aTimeline, bool& aReferencesAttributes) {
  MOZ_ASSERT(aStyle);
  aReferencesAttributes = false;
  if (!aInputs.mTarget) {
    return {};
  }

  nsTArray<Keyframe> computedKeyframes;
  if (aInputs.mCSSGenerationOptions) {
    aInputs.mCSSGenerationOptions->GenerateComputedKeyframes(
        aInputs.mSpecifiedKeyframes, computedKeyframes);
  }
  const nsTArray<Keyframe>& keyframes = aInputs.mCSSGenerationOptions
                                          ? computedKeyframes
                                          : aInputs.mSpecifiedKeyframes;
  return KeyframeUtils::GetAnimationPropertiesFromKeyframes(
      keyframes, aInputs.mTarget.mElement, aInputs.mTarget.mPseudoRequest,
      aStyle, aInputs.mComposite, aTimeline, aReferencesAttributes);
}

""" + admission + """  auto inputs = CapturePropertyInputs();
  result = BuildPropertiesFromInputs(inputs, aStyle, aTimeline,
                                     aReferencesAttributes);

""" + suffix
    texts[name] = texts[name][:start] + replacement + texts[name][end:]
    name = "dom/animation/CSSAnimation.h"
    texts[name] = replace_once(texts[name], """  bool GetComputedKeyframes(nsTArray<Keyframe>& aKeyframes) const override;

 private:
""", """ private:
  Maybe<CSSKeyframeGenerationOptions> CaptureCSSGenerationOptions()
      const override;

""")
    name = "dom/animation/CSSAnimation.cpp"
    start = texts[name].index("bool CSSAnimationKeyframeEffect::GetComputedKeyframes(")
    comment_start = texts[name].rfind("// The step 3 (Generate Initial and Final Frames) in", 0, start)
    assert comment_start >= 0
    generation_comment = texts[name][comment_start:start]
    end = texts[name].index("\nvoid CSSAnimationKeyframeEffect::MaybeFlushUnanimatedStyle", start)
    old = texts[name][start:end]
    body = old[old.index("  // FIXME:"):]
    body = body.replace("mKeyframes", "aSpecifiedKeyframes")
    assert body.count("  return true;\n") == 1
    body = body.replace("  return true;\n", "")
    replacement = """Maybe<KeyframeEffect::CSSKeyframeGenerationOptions>
CSSAnimationKeyframeEffect::CaptureCSSGenerationOptions() const {
  // Check if we do need to do this. This flag is set if the keyframes come from
  // the JS API.
  if (mIgnoreKeyframesGeneration) {
    return Nothing();
  }
  return Some(CSSKeyframeGenerationOptions{mDefaultTimingFunction,
                                          mDefaultComposite});
}

""" + generation_comment + """void KeyframeEffect::CSSKeyframeGenerationOptions::GenerateComputedKeyframes(
    const nsTArray<Keyframe>& aSpecifiedKeyframes,
    nsTArray<Keyframe>& aKeyframes) const {
""" + body
    texts[name] = texts[name][:comment_start] + replacement + texts[name][end:]
    fmt = "/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format"
    formats = {}
    for name, text in texts.items():
        command = [fmt, "--style=file", "--assume-filename=" + str(HERE.parents[1] / name)]
        data = subprocess.check_output(command, input=text.encode())
        assert subprocess.check_output(command, input=data) == data
        destination = HERE / "candidate" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        formats[name] = {"command": command, "output_sha256": hashlib.sha256(data).hexdigest(), "idempotent": True}
    (HERE / "FORMAT.json").write_text(json.dumps(formats, indent=2) + "\n")
    pins = json.loads((HERE / "SOURCES.json").read_text())
    roles = {"revision": pins["revision"], "files": {}}
    patch = ""
    for name in FILES:
        before = (HERE / "source" / name).read_bytes()
        after = (HERE / "candidate" / name).read_bytes()
        roles["files"][name] = {"before_sha256": hashlib.sha256(before).hexdigest(), "after_sha256": hashlib.sha256(after).hexdigest()}
        patch += "diff --git a/" + name + " b/" + name + "\n"
        patch += "".join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True), fromfile="a/" + name, tofile="b/" + name))
    (HERE / "ROLES.json").write_text(json.dumps(roles, indent=2) + "\n")
    (HERE / "owned-generation.patch").write_text(patch)


if __name__ == "__main__":
    prepare()
