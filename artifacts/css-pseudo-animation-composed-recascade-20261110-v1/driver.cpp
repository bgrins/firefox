NS_IMETHODIMP
nsDOMWindowUtils::GetMissingPseudoCompositedStyleForTesting(
    Element* aElement, const nsAString& aPseudoElement,
    const nsAString& aProperty, int32_t aFlushType, nsAString& aResult) {
  RefPtr<Document> document = GetDocument();
  RefPtr<PresShell> presShell = GetPresShell();
  RefPtr<Element> element = aElement;
  if (!document || !presShell || !element || element->OwnerDoc() != document ||
      !element->IsInComposedDoc()) {
    return NS_ERROR_INVALID_ARG;
  }
  const NS_ConvertUTF16toUTF8 propertyName(aProperty);
  const auto propertyId = nsCSSProps::LookupProperty(propertyName);
  if (propertyId == eCSSProperty_UNKNOWN ||
      propertyId == eCSSPropertyExtra_variable ||
      nsCSSProps::IsShorthand(propertyId)) {
    return NS_ERROR_INVALID_ARG;
  }
  const auto property =
      CSSPropertyId::FromIdOrCustomProperty(propertyId, propertyName);
  const auto pseudo = PseudoStyleRequest::Parse(
      aPseudoElement, document->DefaultStyleAttrURLData());
  if (!pseudo) {
    return NS_ERROR_INVALID_ARG;
  }
  if (aFlushType == FLUSH_STYLE) {
    document->FlushPendingNotifications(FlushType::Style);
  } else if (aFlushType != FLUSH_NONE) {
    return NS_ERROR_INVALID_ARG;
  }
  if (document->GetPresShell() != presShell ||
      element->GetComposedDoc() != document) {
    return NS_ERROR_FAILURE;
  }

  struct State {
    RefPtr<mozilla::dom::Animation> mAnimation;
    RefPtr<KeyframeEffect> mEffect;
    OwningAnimationTarget mTarget;
    RefPtr<AnimationTimeline> mTimeline;
    AnimationRange mRange;
    Nullable<TimeDuration> mHold;
    Nullable<TimeDuration> mStart;
    mozilla::dom::Animation::PendingState mPending;
    double mRate;
    Maybe<double> mPendingRate;
    TimeStamp mReady;
    bool mAutoAlign;
    EffectCompositor::CascadeLevel mLevel;
  };
  nsTArray<State> states;
  uint32_t animations = 0;
  uint32_t transitions = 0;
  uint32_t cssAnimations = 0;
  uint32_t inEffectAnimations = 0;
  uint32_t inEffectTransitions = 0;
  uint32_t unresolved = 0;
  uint32_t wallclockPending = 0;
  {
    EffectSet* effects = EffectSet::Get(element, *pseudo);
    if (effects) {
      for (KeyframeEffect* effect : *effects) {
        RefPtr<mozilla::dom::Animation> animation = effect->GetAnimation();
        if (!animation) {
          return NS_ERROR_FAILURE;
        }
        const auto target = effect->GetAnimationTarget();
        states.AppendElement(
            State{animation, effect,
                  OwningAnimationTarget(target.mElement, target.mPseudoRequest),
                  animation->mTimeline, animation->mTimelineRange,
                  animation->mHoldTime, animation->mStartTime,
                  animation->mPendingState, animation->mPlaybackRate,
                  animation->mPendingPlaybackRate, animation->mPendingReadyTime,
                  animation->mAutoAlignStartTime, animation->CascadeLevel()});
        if (animation->CascadeLevel() ==
            EffectCompositor::CascadeLevel::Transitions) {
          ++transitions;
          inEffectTransitions += effect->IsInEffect();
        } else {
          ++animations;
          inEffectAnimations += effect->IsInEffect();
        }
        cssAnimations += animation->AsCSSAnimation() != nullptr;
        unresolved += animation->mTimeline &&
                      animation->mTimeline->IsUnresolvedTimeline();
        wallclockPending +=
            animation->Pending() && animation->mHoldTime.IsNull() &&
            !animation->mStartTime.IsNull() && animation->mTimeline &&
            animation->mTimeline->TracksWallclockTime();
      }
    }
  }

  RefPtr<ComputedStyle> primaryStyle =
      presShell->StyleSet()->ResolveStyleLazily(*element);
  RefPtr<ComputedStyle> rawStyle = presShell->StyleSet()->ResolveStyleLazily(
      *element, *pseudo, StyleRuleInclusion::All);
  if (!primaryStyle || !rawStyle) {
    return NS_ERROR_FAILURE;
  }
  auto sameEffects = [&] {
    EffectSet* effects = EffectSet::Get(element, *pseudo);
    if (!effects) {
      return states.IsEmpty();
    }
    if (effects->Count() != states.Length()) {
      return false;
    }
    for (KeyframeEffect* effect : *effects) {
      bool found = false;
      for (const State& state : states) {
        if (state.mEffect == effect &&
            state.mAnimation == effect->GetAnimation()) {
          found = true;
          break;
        }
      }
      if (!found) {
        return false;
      }
    }
    return true;
  };
  bool unchanged = sameEffects();
  const OwningAnimationTarget target(element, *pseudo);
  EffectCompositor* compositor =
      presShell->GetPresContext()->EffectCompositor();
  UniquePtr<StyleAnimationValueMap> aliased;
  const bool guardedAlias =
      !compositor->ComposeServoAnimationRulesForMissingPseudo(
          target, rawStyle, rawStyle, aliased, aliased) &&
      !aliased;
  UniquePtr<StyleAnimationValueMap> occupied(Servo_AnimationValueMap_Create());
  UniquePtr<StyleAnimationValueMap> other(Servo_AnimationValueMap_Create());
  const auto* occupiedPointer = occupied.get();
  const auto* otherPointer = other.get();
  const bool guardedNonempty =
      !compositor->ComposeServoAnimationRulesForMissingPseudo(
          target, rawStyle, rawStyle, occupied, other) &&
      occupied.get() == occupiedPointer && other.get() == otherPointer;
  UniquePtr<StyleAnimationValueMap> animationValues;
  UniquePtr<StyleAnimationValueMap> transitionValues;
  const bool admitted = compositor->ComposeServoAnimationRulesForMissingPseudo(
      target, rawStyle, rawStyle, animationValues, transitionValues);
  RefPtr<ComputedStyle> cascadedStyle;
  if (admitted) {
    cascadedStyle = presShell->StyleSet()->RecascadeStyleForMissingPseudo(
        *element, *pseudo, *rawStyle, *primaryStyle, *animationValues,
        *transitionValues);
  }
  unchanged &= sameEffects();
  for (const State& state : states) {
    const mozilla::dom::Animation& animation = *state.mAnimation;
    unchanged &= animation.mEffect == state.mEffect &&
                 state.mEffect->GetAnimationTarget().mElement ==
                     state.mTarget.mElement &&
                 state.mEffect->GetAnimationTarget().mPseudoRequest ==
                     state.mTarget.mPseudoRequest &&
                 state.mEffect->GetAnimation() == &animation &&
                 animation.mTimeline == state.mTimeline &&
                 animation.mTimelineRange == state.mRange &&
                 animation.mHoldTime == state.mHold &&
                 animation.mStartTime == state.mStart &&
                 animation.mPendingState == state.mPending &&
                 animation.mPlaybackRate == state.mRate &&
                 animation.mPendingPlaybackRate == state.mPendingRate &&
                 animation.mPendingReadyTime == state.mReady &&
                 animation.mAutoAlignStartTime == state.mAutoAlign &&
                 animation.CascadeLevel() == state.mLevel;
  }

  JSONStringWriteFunc<nsCString> output;
  JSONWriter writer(output, JSONWriter::SingleLineStyle);
  writer.Start();
  writer.BoolProperty("admitted", admitted);
  writer.BoolProperty("recascadeAdmitted", !!cascadedStyle);
  writer.BoolProperty("originUnchanged", Servo_Element_GetMaybeOutOfDateStyle(
                                             element) == primaryStyle);
  writer.BoolProperty(
      "pseudoMatches",
      cascadedStyle && cascadedStyle->GetPseudoType() == pseudo->mType);
  writer.BoolProperty("noPseudoCreated", !element->GetPseudoElement(*pseudo));
  writer.IntProperty("inEffectAnimations", inEffectAnimations);
  writer.IntProperty("inEffectTransitions", inEffectTransitions);
  writer.BoolProperty("guardedAlias", guardedAlias);
  writer.BoolProperty("guardedNonempty", guardedNonempty);
  writer.BoolProperty("separateMaps", animationValues && transitionValues &&
                                          animationValues != transitionValues);
  writer.BoolProperty("stateUnchanged", unchanged);
  writer.IntProperty("animations", animations);
  writer.IntProperty("transitions", transitions);
  writer.IntProperty("cssAnimations", cssAnimations);
  writer.IntProperty("unresolved", unresolved);
  writer.IntProperty("wallclockPending", wallclockPending);
  auto writeValue = [&](const Span<const char>& name,
                        const UniquePtr<StyleAnimationValueMap>& map) {
    RefPtr<StyleAnimationValue> value =
        map ? Servo_AnimationValueMap_GetValue(map.get(), &property).Consume()
            : nullptr;
    if (!value) {
      writer.NullProperty(name);
      return;
    }
    nsAutoCString text;
    Servo_AnimationValue_Serialize(value, &property,
                                   presShell->StyleSet()->RawData(), &text);
    writer.StringProperty(name, Span<const char>(text.Data(), text.Length()));
  };
  writeValue("animationValue", animationValues);
  writeValue("transitionValue", transitionValues);
  auto writeStyleValue = [&](const Span<const char>& name,
                             const ComputedStyle* style) {
    RefPtr<StyleAnimationValue> value =
        style ? Servo_ComputedValues_ExtractAnimationValue(style, &property)
                    .Consume()
              : nullptr;
    if (!value) {
      writer.NullProperty(name);
      return;
    }
    nsAutoCString text;
    Servo_AnimationValue_Serialize(value, &property,
                                   presShell->StyleSet()->RawData(), &text);
    writer.StringProperty(name, Span<const char>(text.Data(), text.Length()));
  };
  writeStyleValue("baseValue", rawStyle);
  writeStyleValue("cascadedValue", cascadedStyle);
  writer.End();
  CopyUTF8toUTF16(output.StringCRef(), aResult);
  return NS_OK;
}
