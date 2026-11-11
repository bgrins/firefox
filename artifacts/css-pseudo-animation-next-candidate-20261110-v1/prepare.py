from pathlib import Path
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
pins=json.loads((HERE/'SOURCES.json').read_text())
for name,digest in pins['files'].items():
    assert hashlib.sha256((HERE/'source'/name).read_bytes()).hexdigest() == digest
names=['dom/animation/KeyframeEffect.h','dom/animation/KeyframeEffect.cpp']
roles={}
patch=''
for name in names:
    before=(HERE/'source'/name).read_text()
    after=before
    if name.endswith('.h'):
        anchor='  const nsTArray<AnimationProperty>& Properties() const { return mProperties; }\n'
        assert after.count(anchor)==1
        addition='\n  // Owns array storage and references; declaration blocks remain shared.\n  // Generated endpoint defaults and offsets are captured, not refreshed.\n  struct PropertyInputSnapshot {\n    OwningAnimationTarget mTarget;\n    CompositeOperation mComposite;\n    nsTArray<Keyframe> mSpecifiedKeyframes;\n    nsTArray<Keyframe> mComputedKeyframes;\n    bool mHasComputedKeyframes;\n  };\n\n  PropertyInputSnapshot CapturePropertyInputs() const;\n  static nsTArray<AnimationProperty> BuildPropertiesFromInputs(\n      const PropertyInputSnapshot& aInputs, const ComputedStyle* aStyle,\n      const AnimationTimeline* aTimeline, bool& aReferencesAttributes);\n'
        after=after.replace(anchor,anchor+addition)
    else:
        start=after.index('nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(')
        end=after.index('\ntemplate <typename FrameEnumFunc>',start)
        original=after[start:end]
        comment_start=original.index('  // When GetComputedKeyframeValues')
        comments_end=original.index('  nsTArray<Keyframe> computedKeyframes;')
        capture_comments=original[comment_start:comments_end]
        capture_comments=capture_comments.replace('  auto keyframesCopy(mKeyframes.Clone());','  auto specifiedKeyframes(mKeyframes.Clone());')
        new='KeyframeEffect::PropertyInputSnapshot KeyframeEffect::CapturePropertyInputs()\n    const {\n  if (!mTarget) {\n    return {{}, mEffectOptions.mComposite, {}, {}, false};\n  }\n\n'+capture_comments+'  nsTArray<Keyframe> computedKeyframes;\n  const bool hasComputedKeyframes = GetComputedKeyframes(computedKeyframes);\n  return {mTarget, mEffectOptions.mComposite, std::move(specifiedKeyframes),\n          std::move(computedKeyframes), hasComputedKeyframes};\n}\n\n/* static */\nnsTArray<AnimationProperty> KeyframeEffect::BuildPropertiesFromInputs(\n    const PropertyInputSnapshot& aInputs, const ComputedStyle* aStyle,\n    const AnimationTimeline* aTimeline, bool& aReferencesAttributes) {\n  MOZ_ASSERT(aStyle);\n  aReferencesAttributes = false;\n  if (!aInputs.mTarget) {\n    return {};\n  }\n\n  const nsTArray<Keyframe>& keyframes = aInputs.mHasComputedKeyframes\n                                            ? aInputs.mComputedKeyframes\n                                            : aInputs.mSpecifiedKeyframes;\n  return KeyframeUtils::GetAnimationPropertiesFromKeyframes(\n      keyframes, aInputs.mTarget.mElement, aInputs.mTarget.mPseudoRequest,\n      aStyle, aInputs.mComposite, aTimeline, aReferencesAttributes);\n}\n\nnsTArray<AnimationProperty> KeyframeEffect::BuildProperties(\n    const ComputedStyle* aStyle, const AnimationTimeline* aTimeline,\n    bool& aReferencesAttributes) {\n  MOZ_ASSERT(aStyle);\n  aReferencesAttributes = false;\n\n  nsTArray<AnimationProperty> result;\n  // If mTarget is false (i.e. mTarget.mElement is null), return an empty\n  // property array.\n  if (!mTarget) {\n    return result;\n  }\n\n  auto inputs = CapturePropertyInputs();\n  result = BuildPropertiesFromInputs(inputs, aStyle, aTimeline,\n                                     aReferencesAttributes);\n\n#ifdef DEBUG\n  MOZ_ASSERT(\n      SpecifiedKeyframeArraysAreEqual(mKeyframes, inputs.mSpecifiedKeyframes),\n      "Apart from the computed offset members, the keyframes array"\n      " should not be modified");\n#endif\n\n  mKeyframes = std::move(inputs.mSpecifiedKeyframes);\n  return result;\n}\n'
        after=after[:start]+new+after[end:]
    path=HERE/'candidate'/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(after)
    patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    roles[name]={'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest()}
(HERE/'snapshot.patch').write_text(patch)
(HERE/'ROLES.json').write_text(json.dumps({'revision':pins['revision'],'files':roles},indent=2)+'\n')
print('Prepared two copied files')
