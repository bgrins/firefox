COMPARATOR='static bool KeyframesEqualIgnoringComputedOffsets('
ARRAY='void KeyframeEffect::SetKeyframes(nsTArray<Keyframe>&&'
UPDATE='void KeyframeEffect::UpdateProperties('
MUTATIONS={
 'omit-composite':(COMPARATOR,'a.mComposite != b.mComposite ||',''),
 'omit-offset':(COMPARATOR,'a.mOffset != b.mOffset ||',''),
 'omit-easing':(COMPARATOR,'a.mTimingFunction != b.mTimingFunction ||',''),
 'omit-properties':(COMPARATOR,'a.mPropertyValues != b.mPropertyValues','false'),
 'first-only':(COMPARATOR,'i < len','i < std::min(len, size_t(1))'),
 'last-only':(COMPARATOR,'size_t i = 0, len = aLhs.Length()','size_t i = aLhs.IsEmpty() ? 0 : aLhs.Length() - 1, len = aLhs.Length()'),
 'ignore-length':(COMPARATOR,'return false;\n  }\n\n  for','return true;\n  }\n\n  for'),
 'auto-is-replace':(COMPARATOR,'a.mComposite != b.mComposite','(a.mComposite == CompositeOperationOrAuto::Auto ? CompositeOperationOrAuto::Replace : a.mComposite) != (b.mComposite == CompositeOperationOrAuto::Auto ? CompositeOperationOrAuto::Replace : b.mComposite)'),
 'drop-store':(ARRAY,'mKeyframes = std::move(aKeyframes);','(void)aKeyframes;'),
 'skip-recompute':(ARRAY,'mKeyframeOffsetsHasRangeOffset = KeyframeUtils::ComputeMissingKeyframeOffsets(\n      mKeyframes, aTimeline, aRange);','(void)aTimeline; (void)aRange;'),
 'notify-irrelevant':(ARRAY,'mAnimation && mAnimation->IsRelevant()','mAnimation'),
 'suppress-notify':(ARRAY,'mAnimation && mAnimation->IsRelevant()','false'),
 'skip-update':(ARRAY,'if (aStyle) {','if (false) {'),
 'suppress-restyle':(UPDATE,'RequestRestyle(EffectCompositor::RestyleType::Layer);\n}','(void)0;\n}'),
 'suppress-effect-updated':(UPDATE,'mAnimation->NotifyEffectPropertiesUpdated();','(void)0;'),
 'suppress-base-restyle':(UPDATE,'if (baseStylesChanged) {','if (false) {'),
 'collapse-endpoint-auto':('nsTArray<AnimationProperty> KeyframeUtils::GetAnimationPropertiesFromKeyframes(','? aEffectComposite','? CompositeOperation::Replace'),
 'drop-endpoint-composite':('static void BuildSegmentsFromValueEntries(','segment->mToComposite = aEntries[j].mComposite;','segment->mToComposite = CompositeOperation::Replace;'),
 'suppress-default-rebuild':('void KeyframeEffect::SetComposite(','if (computedStyle) {','if (false) {'),
 'suppress-range-rebuild':('void KeyframeEffect::MaybeUpdateKeyframeComputedOffsets(','if (needsRebuildProperties && mTarget) {','if (false) {'),
}
