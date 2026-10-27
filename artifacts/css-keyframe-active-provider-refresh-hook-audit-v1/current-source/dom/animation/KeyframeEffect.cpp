void KeyframeEffect::NotifyAnimationTimingUpdated(
    PostRestyleMode aPostRestyle) {
  UpdateTargetRegistration();

  // If the effect is not relevant it will be removed from the target
  // element's effect set. However, effects not in the effect set
  // will not be included in the set of candidate effects for running on
  // the compositor and hence they won't have their compositor status
  // updated. As a result, we need to make sure we clear their compositor
  // status here.
  bool isRelevant = mAnimation && mAnimation->IsRelevant();
  if (!isRelevant) {
    ResetIsRunningOnCompositor();
  }

  // Request restyle if necessary.
  if (aPostRestyle == PostRestyleMode::IfNeeded && mAnimation &&
      !mProperties.IsEmpty() && HasComputedTimingChanged()) {
    EffectCompositor::RestyleType restyleType =
        CanThrottle() ? EffectCompositor::RestyleType::Throttled
                      : EffectCompositor::RestyleType::Standard;
    RequestRestyle(restyleType);
  }

  // Detect changes to "in effect" status since we need to recalculate the
  // animation cascade for this element whenever that changes.
  // Note that updating mInEffectOnLastAnimationTimingUpdate has to be done
  // after above CanThrottle() call since the function uses the flag inside it.
  bool inEffect = IsInEffect();
  if (inEffect != mInEffectOnLastAnimationTimingUpdate) {
    MarkCascadeNeedsUpdate();
    mInEffectOnLastAnimationTimingUpdate = inEffect;
  }

  // If we're no longer "in effect", our ComposeStyle method will never be
  // called and we will never have a chance to update mProgressOnLastCompose
  // and mCurrentIterationOnLastCompose.
  // We clear them here to ensure that if we later become "in effect" we will
  // request a restyle (above).
  if (!inEffect) {
    mProgressOnLastCompose.SetNull();
    mCurrentIterationOnLastCompose = 0;
  }
}

void KeyframeEffect::UpdateProperties(const ComputedStyle* aStyle,
                                      const AnimationTimeline* aTimeline) {
  MOZ_ASSERT(aStyle);

  bool referencesAttributes = false;
  nsTArray<AnimationProperty> properties = BuildProperties(
      aStyle,
      aTimeline ? aTimeline
                : (mAnimation ? mAnimation->GetTimeline() : nullptr),
      referencesAttributes);

  bool propertiesChanged = mProperties != properties;
  if (!propertiesChanged) {
    auto attrTainted = [](const AnimationValue& aValue) {
      return aValue.mServo && Servo_AnimationValue_IsAttrTainted(aValue.mServo);
    };
    for (size_t i = 0; i < properties.Length() && !propertiesChanged; ++i) {
      if (!properties[i].mProperty.IsCustom()) {
        continue;
      }
      const auto& oldSegments = mProperties[i].mSegments;
      const auto& newSegments = properties[i].mSegments;
      for (size_t j = 0; j < newSegments.Length(); ++j) {
        const auto& oldSegment = oldSegments[j];
        const auto& newSegment = newSegments[j];
        if (attrTainted(oldSegment.mFromValue) !=
                attrTainted(newSegment.mFromValue) ||
            attrTainted(oldSegment.mToValue) !=
                attrTainted(newSegment.mToValue)) {
          propertiesChanged = true;
          break;
        }
      }
    }
  }

  // We need to update base styles even if any properties are not changed at all
  // since base styles might have been changed due to parent style changes, etc.
  bool baseStylesChanged = false;
  EnsureBaseStyles(aStyle, properties, aTimeline,
                   !propertiesChanged ? &baseStylesChanged : nullptr);

  mReferencesAttributes = referencesAttributes;

  if (!propertiesChanged) {
    for (size_t i = 0; i < properties.Length(); ++i) {
      auto& oldSegments = mProperties[i].mSegments;
      const auto& newSegments = properties[i].mSegments;
      for (size_t j = 0; j < newSegments.Length(); ++j) {
        oldSegments[j].mFromEndpoint = newSegments[j].mFromEndpoint;
        oldSegments[j].mToEndpoint = newSegments[j].mToEndpoint;
      }
    }
    if (baseStylesChanged) {
      RequestRestyle(EffectCompositor::RestyleType::Layer);
    }
    return;
  }

  // Preserve the state of the mIsRunningOnCompositor flag.
  nsCSSPropertyIDSet runningOnCompositorProperties;

  for (const AnimationProperty& property : mProperties) {
    if (property.mIsRunningOnCompositor) {
      runningOnCompositorProperties.AddProperty(property.mProperty.mId);
    }
  }

  mProperties = std::move(properties);
  UpdateEffectSet();

  mCumulativeChanges = {};
  for (AnimationProperty& property : mProperties) {
    property.mIsRunningOnCompositor =
        runningOnCompositorProperties.HasProperty(property.mProperty);
    CalculateCumulativeChangesForProperty(property);
  }

  MarkCascadeNeedsUpdate();

  if (mAnimation) {
    mAnimation->NotifyEffectPropertiesUpdated();
  }

  RequestRestyle(EffectCompositor::RestyleType::Layer);
}

void KeyframeEffect::ComposeStyleRule(
    const AnimationComposeResult& aAnimationValues,
    const AnimationProperty& aProperty, const AnimationPropertySegment& aSegment,
    const ComputedTiming& aComputedTiming) {
  auto* opaqueTable =
      reinterpret_cast<RawServoAnimationValueTable*>(&mBaseValues);
  aAnimationValues.match(
      [&](StyleAnimationValueMap* aValues) {
        Servo_AnimationCompose(aValues, opaqueTable, &aProperty.mProperty,
                               &aSegment, &aProperty.mSegments.LastElement(),
                               &aComputedTiming,
                               mEffectOptions.mIterationComposite);
      },
      [&](StyleAnimationRuleSample* aSample) {
        Servo_AnimationRuleSample_Compose(
            aSample, opaqueTable, &aProperty.mProperty, &aSegment,
            &aProperty.mSegments.LastElement(), &aComputedTiming,
            mEffectOptions.mIterationComposite);
      });
}

void KeyframeEffect::ComposeStyle(
    const AnimationComposeResult& aComposeResult,
    const InvertibleAnimatedPropertyIDSet& aPropertiesToSkip,
    EndpointBehavior aEndpointBehavior) {
  ComputedTiming computedTiming = GetComputedTiming(nullptr, aEndpointBehavior);

  // If the progress is null, we don't have fill data for the current
  // time so we shouldn't animate.
  if (computedTiming.mProgress.IsNull()) {
    return;
  }

  for (size_t propIdx = 0, propEnd = mProperties.Length(); propIdx != propEnd;
       ++propIdx) {
    const AnimationProperty& prop = mProperties[propIdx];

    MOZ_ASSERT(prop.mSegments[0].mFromKey <= 0.0, "incorrect first from key");
    MOZ_ASSERT(prop.mSegments[prop.mSegments.Length() - 1].mToKey >= 1.0,
               "incorrect last to key");

    if (aPropertiesToSkip.HasProperty(prop.mProperty)) {
      continue;
    }

    MOZ_ASSERT(prop.mSegments.Length() > 0,
               "property should not be in animations if it has no segments");

    // FIXME: Maybe cache the current segment?
    const AnimationPropertySegment *segment = prop.mSegments.Elements(),
                                   *segmentEnd =
                                       segment + prop.mSegments.Length();
    while (segment->mToKey <= computedTiming.mProgress.Value()) {
      MOZ_ASSERT(segment->mFromKey <= segment->mToKey, "incorrect keys");
      if ((segment + 1) == segmentEnd) {
        break;
      }
      ++segment;
      MOZ_ASSERT(segment->mFromKey == (segment - 1)->mToKey, "incorrect keys");
    }
    MOZ_ASSERT(segment->mFromKey <= segment->mToKey, "incorrect keys");
    MOZ_ASSERT(segment >= prop.mSegments.Elements() &&
                   size_t(segment - prop.mSegments.Elements()) <
                       prop.mSegments.Length(),
               "out of array bounds");

    ComposeStyleRule(aComposeResult, prop, *segment, computedTiming);
  }

  // If the animation produces a change hint that affects the overflow region,
  // we need to record the current time to unthrottle the animation
  // periodically when the animation is being throttled because it's scrolled
  // out of view.
  if (HasPropertiesThatMightAffectOverflow()) {
    nsPresContext* presContext =
        nsContentUtils::GetContextForContent(mTarget.mElement);
    EffectSet* effectSet = EffectSet::Get(mTarget);
    if (presContext && effectSet) {
      TimeStamp now = presContext->RefreshDriver()->MostRecentRefresh();
      effectSet->UpdateLastOverflowAnimationSyncTime(now);
    }
  }
}
