from pathlib import Path
import shutil
import difflib
import subprocess
import json
import hashlib
import argparse

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE)
    output = parser.parse_args().out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'candidate'
    assert not target.exists()
    shutil.copytree(HERE / 'prerequisite', target)
    path = target / 'dom/animation/Animation.h'
    text = path.read_text()
    anchor = '  friend class AsyncFinishNotification;'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + '\n  friend class mozilla::EffectCompositor;')
    anchor = '  Nullable<TimeDuration> GetCurrentTimeForHoldTime('
    assert text.count(anchor) == 1
    text = text.replace(anchor, '  Nullable<TimeDuration> GetHoldTimeForComposition(\n      const TimeStamp* aSampleTime = nullptr) const;\n' + anchor)
    path.write_text(text)
    path = target / 'dom/animation/Animation.cpp'
    text = path.read_text()
    start = text.index('    if (pending && mHoldTime.IsNull() && !mStartTime.IsNull()) {', text.index('void Animation::ComposeStyle('))
    end = text.index('\n\n    KeyframeEffect* keyframeEffect', start)
    original = text[start:end]
    helper_body = original.replace('    if (pending && mHoldTime.IsNull()', '    if (Pending() && mHoldTime.IsNull()').replace('mHoldTime = CurrentTimeFromTimelineTime(', 'holdTime = CurrentTimeFromTimelineTime(').replace('mTimeline->ToTimelineTime(TimeStamp::Now())', 'mTimeline->ToTimelineTime(aSampleTime ? *aSampleTime : TimeStamp::Now())')
    helper_body = '\n'.join(line[2:] if line.startswith('  ') else line for line in helper_body.splitlines())
    helper = 'Nullable<TimeDuration> Animation::GetHoldTimeForComposition(\n    const TimeStamp* aSampleTime) const {\n  auto holdTime = mHoldTime;\n' + helper_body + '\n  return holdTime;\n}\n\n'
    text = text[:start] + '    mHoldTime = GetHoldTimeForComposition();' + text[end:]
    anchor = 'void Animation::ComposeStyle('
    text = text.replace(anchor, helper + anchor, 1)
    path.write_text(text)
    path = target / 'dom/animation/EffectCompositor.h'
    text = path.read_text().replace('#include "mozilla/ServoTypes.h"', '#include "mozilla/ServoTypes.h"\n#include "mozilla/UniquePtr.h"')
    anchor = '  bool HasPendingStyleUpdates() const;'
    api = '''  // The styles must describe the same sample and target. Base style excludes
  // target animation/transition rules; endpoint style includes its providers.
  // Lazy-resolution borrows must be released, and preparation must not reenter
  // mutation of the captured target, animation or provider context.
  bool ComposeServoAnimationRulesForMissingPseudo(
      const OwningAnimationTarget& aTarget, const ComputedStyle* aBaseStyle,
      const ComputedStyle* aEndpointStyle,
      UniquePtr<StyleAnimationValueMap>& aAnimationValues,
      UniquePtr<StyleAnimationValueMap>& aTransitionValues);

'''
    assert text.count(anchor) == 1
    text = text.replace(anchor, api + anchor)
    path.write_text(text)
    path = target / 'dom/animation/EffectCompositor.cpp'
    text = path.read_text()
    anchor = 'bool EffectCompositor::HasPendingStyleUpdates() const {'
    implementation = '''bool EffectCompositor::ComposeServoAnimationRulesForMissingPseudo(
    const OwningAnimationTarget& aTarget, const ComputedStyle* aBaseStyle,
    const ComputedStyle* aEndpointStyle,
    UniquePtr<StyleAnimationValueMap>& aAnimationValues,
    UniquePtr<StyleAnimationValueMap>& aTransitionValues) {
  MOZ_ASSERT(NS_IsMainThread());
  if (!mPresContext || !mPresContext->IsDynamic() || !aTarget ||
      !aBaseStyle || !aEndpointStyle ||
      nsContentUtils::GetContextForContent(aTarget.mElement) != mPresContext ||
      aAnimationValues || aTransitionValues ||
      &aAnimationValues == &aTransitionValues) {
    return false;
  }
  const auto pseudo = aTarget.mPseudoRequest.mType;
  if ((pseudo != PseudoStyleType::Before && pseudo != PseudoStyleType::After &&
       pseudo != PseudoStyleType::Marker) ||
      aBaseStyle->GetPseudoType() != pseudo ||
      aEndpointStyle->GetPseudoType() != pseudo ||
      aTarget.mElement->GetPseudoElement(aTarget.mPseudoRequest)) {
    return false;
  }

  const OwningAnimationTarget target = aTarget;
  RefPtr<const ComputedStyle> baseStyle = aBaseStyle;
  RefPtr<const ComputedStyle> endpointStyle = aEndpointStyle;
  nsTArray<RefPtr<KeyframeEffect>> sortedEffects;
  {
    EffectSet* effects = EffectSet::Get(target.mElement, target.mPseudoRequest);
    if (!effects) {
      return false;
    }
    for (KeyframeEffect* effect : *effects) {
      if (!effect->GetAnimation()) {
        return false;
      }
      sortedEffects.AppendElement(effect);
    }
  }
  if (sortedEffects.IsEmpty()) {
    return false;
  }
  sortedEffects.Sort(EffectCompositeOrderComparator());

  struct PreparedEffect {
    RefPtr<KeyframeEffect> mEffect;
    RefPtr<Animation> mAnimation;
    RefPtr<dom::AnimationTimeline> mTimeline;
    dom::AnimationRange mRange;
    KeyframeEffect::PropertyInputSnapshot mInputs;
    ComputedTiming mTiming;
    dom::IterationCompositeOperation mIterationComposite;
    CascadeLevel mLevel;
    nsTArray<AnimationProperty> mProperties;
  };
  nsTArray<PreparedEffect> prepared;
  const TimeStamp sampleTime = TimeStamp::Now();
  for (const RefPtr<KeyframeEffect>& effect : sortedEffects) {
    RefPtr<Animation> animation = effect->GetAnimation();
    const auto& effectTarget = effect->GetAnimationTarget();
    if (!animation || animation->GetEffect() != effect.get() ||
        effectTarget.mElement != target.mElement ||
        effectTarget.mPseudoRequest != target.mPseudoRequest) {
      return false;
    }
    RefPtr<dom::AnimationTimeline> timeline = animation->GetTimeline();
    const dom::AnimationRange range = animation->GetTimelineRange();
    auto inputs = effect->CapturePropertyInputs();
    inputs.RefreshComputedOffsets(timeline, &range);
    ComputedTiming timing;
    if (!timeline || !timeline->IsUnresolvedTimeline()) {
      TimingParams parameters = effect->SpecifiedTiming();
      if (timeline && !timeline->IsMonotonicallyIncreasing()) {
        const auto duration = timeline->TimelineDuration(range);
        MOZ_ASSERT(!duration.IsNull());
        parameters = parameters.Normalize(duration.Value());
      }
      timing = dom::AnimationEffect::GetComputedTimingAt(
          animation->GetCurrentTimeForHoldTime(
              animation->GetHoldTimeForComposition(&sampleTime)),
          parameters, animation->PlaybackRateInternal(),
          animation->AtTimelineBoundary(), dom::EndpointBehavior::Exclusive);
    }
    prepared.AppendElement(PreparedEffect{
        effect, animation, timeline, range, std::move(inputs), timing,
        effect->IterationComposite(), animation->CascadeLevel(), {}});
  }

  AnimatedPropertyIDSet allProperties;
  AnimatedPropertyIDSet animationProperties;
  for (PreparedEffect& effect : prepared) {
    bool referencesAttributes = false;
    effect.mProperties = KeyframeEffect::BuildPropertiesFromInputs(
        effect.mInputs, endpointStyle, effect.mTimeline, referencesAttributes);
    for (const AnimationProperty& property : effect.mProperties) {
      allProperties.AddProperty(property.mProperty);
      if (effect.mLevel == CascadeLevel::Animations) {
        animationProperties.AddProperty(property.mProperty);
      }
    }
  }
  KeyframeEffect::BaseValuesHashmap baseValues;
  for (const auto& property : allProperties) {
    RefPtr<StyleAnimationValue> value =
        Servo_ComputedValues_ExtractAnimationValue(baseStyle, &property).Consume();
    baseValues.InsertOrUpdate(property, std::move(value));
  }

  aAnimationValues.reset(Servo_AnimationValueMap_Create());
  aTransitionValues.reset(Servo_AnimationValueMap_Create());
  InvertibleAnimatedPropertyIDSet animationSkip;
  InvertibleAnimatedPropertyIDSet transitionSkip;
  animationSkip.Setup(&animationProperties, true);
  transitionSkip.Setup(&animationProperties, false);
  for (const PreparedEffect& effect : prepared) {
    if (effect.mTiming.mProgress.IsNull()) {
      continue;
    }
    KeyframeEffect::ComposeProperties(
        *aAnimationValues, effect.mProperties, baseValues, effect.mTiming,
        effect.mIterationComposite, animationSkip);
    if (effect.mLevel == CascadeLevel::Transitions) {
      KeyframeEffect::ComposeProperties(
          *aTransitionValues, effect.mProperties, baseValues, effect.mTiming,
          effect.mIterationComposite, transitionSkip);
    }
  }
  return true;
}

'''
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, implementation + anchor))
    formats = {}
    for f in sorted(target.rglob('*')):
        if not f.is_file():
            continue
        relative = str(f.relative_to(target))
        command = ['/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format', '--style=file', '--assume-filename=' + str(HERE.parents[1] / relative)]
        formatted = subprocess.check_output(command, input=f.read_bytes())
        assert subprocess.check_output(command, input=formatted) == formatted
        f.write_bytes(formatted)
        formats[relative] = {'command': command, 'sha256': hashlib.sha256(formatted).hexdigest(), 'idempotent': True}
    (output / 'FORMAT.json').write_text(json.dumps(formats, indent=2) + '\n')
    for basis, name in [('prerequisite', 'query-inputs.patch'), ('source', 'candidate.patch')]:
        patch = []
        for f in sorted(target.rglob('*')):
            if not f.is_file():
                continue
            relative = str(f.relative_to(target))
            before = (HERE / basis / relative).read_text()
            after = f.read_text()
            if before == after:
                continue
            patch.append('diff --git a/' + relative + ' b/' + relative + '\n')
            patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/' + relative, tofile='b/' + relative))
        (output / name).write_text(''.join(patch))


if __name__ == '__main__':
    main()
