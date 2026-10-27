void EffectCompositor::UpdateEffectProperties(
    const ComputedStyle* aStyle, Element* aElement,
    const PseudoStyleRequest& aPseudoRequest) {
  EffectSet* effectSet = EffectSet::Get(aElement, aPseudoRequest);
  if (!effectSet) {
    return;
  }

  // Style context (Gecko) or computed values (Stylo) change might cause CSS
  // cascade level, e.g removing !important, so we should update the cascading
  // result.
  effectSet->MarkCascadeNeedsUpdate();

  for (KeyframeEffect* effect : *effectSet) {
    effect->UpdateProperties(aStyle);
  }
}

static void ComposeSortedEffects(
    const nsTArray<KeyframeEffect*>& aSortedEffects,
    const EffectSet* aEffectSet, EffectCompositor::CascadeLevel aCascadeLevel,
    const AnimationComposeResult& aAnimationValues,
    dom::EndpointBehavior aEndpointBehavior =
        dom::EndpointBehavior::Exclusive) {
  const bool isTransition =
      aCascadeLevel == EffectCompositor::CascadeLevel::Transitions;
  // Transitions should be overridden by running animations of the same
  // property per https://drafts.csswg.org/css-transitions/#application:
  //
  // > Implementations must add this value to the cascade if and only if that
  // > property is not currently undergoing a CSS Animation on the same element.
  //
  InvertibleAnimatedPropertyIDSet propertiesToSkip;
  AnimatedPropertyIDSet animatedProperties;

  // FIXME(emilio, bug 1606176): This should assert that
  // aEffectSet->PropertiesForAnimationsLevel() is up-to-date, and it may not
  // follow the spec in those cases. There are various places where we get style
  // without flushing that would trigger the below assertion.
  //
  // MOZ_ASSERT_IF(aEffectSet, !aEffectSet->CascadeNeedsUpdate());
  if (aEffectSet) {
    animatedProperties.AddProperties(
        aEffectSet->PropertiesForAnimationsLevel());
    // When CommitStyles is called and its endpoint-inclusive behavior is
    // enabled, the animation that CommitStyles targets is already finished and
    // so aEffectSet doesn't include it. But its properties still has to be
    // included in propertiesToSkip. So its properties have to be added manually
    // here.
    if (aEndpointBehavior == dom::EndpointBehavior::Inclusive &&
        aCascadeLevel == EffectCompositor::CascadeLevel::Animations) {
      animatedProperties.AddProperties(
          aSortedEffects.LastElement()->GetPropertySet());
    }
    // Note that we do invert the set on CascadeLevel::Animations because we
    // don't want to skip those properties when composing the animation rule on
    // CascadeLevel::Animations.
    propertiesToSkip.Setup(&animatedProperties, !isTransition);
  }

  for (KeyframeEffect* effect : aSortedEffects) {
    auto* animation = effect->GetAnimation();
    MOZ_ASSERT(!isTransition || animation->CascadeLevel() == aCascadeLevel);
    animation->ComposeStyle(aAnimationValues, propertiesToSkip,
                            aEndpointBehavior);
  }
}

bool EffectCompositor::GetServoAnimationRule(
    const dom::Element* aElement, const PseudoStyleRequest& aPseudoRequest,
    CascadeLevel aCascadeLevel, StyleAnimationRuleSample* aAnimationValues) {
  MOZ_ASSERT(aAnimationValues);
  // Gecko_GetAnimationRule should have already checked this
  MOZ_ASSERT(nsContentUtils::GetPresShellForContent(aElement),
             "Should not be trying to run animations on elements in documents"
             " without a pres shell (e.g. XMLHttpRequest documents)");

  EffectSet* effectSet = EffectSet::Get(aElement, aPseudoRequest);
  if (!effectSet) {
    return false;
  }

  const bool isTransition = aCascadeLevel == CascadeLevel::Transitions;

  // Get a list of effects sorted by composite order.
  nsTArray<KeyframeEffect*> sortedEffectList(effectSet->Count());
  for (KeyframeEffect* effect : *effectSet) {
    if (isTransition &&
        effect->GetAnimation()->CascadeLevel() != aCascadeLevel) {
      // We may need to use transition rules for the animations level for the
      // case of missing keyframes in animations, but we don't ever need to look
      // at non-transition levels to build a transition rule. When the effect
      // set information is out of date (see above), this avoids creating bogus
      // transition rules, see bug 1605610.
      continue;
    }
    sortedEffectList.AppendElement(effect);
  }

  if (sortedEffectList.IsEmpty()) {
    return false;
  }

  sortedEffectList.Sort(EffectCompositeOrderComparator());

  ComposeSortedEffects(sortedEffectList, effectSet, aCascadeLevel,
                       AnimationComposeResult(aAnimationValues));

  MOZ_ASSERT(effectSet == EffectSet::Get(aElement, aPseudoRequest),
             "EffectSet should not change while composing style");

  return true;
}

void EffectCompositor::RequestRestyle(dom::Element* aElement,
                                      const PseudoStyleRequest& aPseudoRequest,
                                      RestyleType aRestyleType,
                                      CascadeLevel aCascadeLevel) {
  if (!mPresContext) {
    // Pres context will be null after the effect compositor is disconnected.
    return;
  }

  // Ignore animations on orphaned elements and elements in documents without
  // a pres shell (e.g. XMLHttpRequest responseXML documents).
  if (!nsContentUtils::GetPresShellForContent(aElement)) {
    return;
  }

  auto& elementsToRestyle = mElementsToRestyle[aCascadeLevel];
  PseudoElementHashEntry::KeyType key = {aElement, aPseudoRequest};

  bool& restyleEntry = elementsToRestyle.LookupOrInsert(key, false);
  if (aRestyleType == RestyleType::Throttled) {
    mPresContext->PresShell()->SetNeedThrottledAnimationFlush();
  } else {
    // Update hashtable first in case PostRestyleForAnimation mutates it
    // and invalidates the restyleEntry reference.
    // (It shouldn't, but just to be sure.)
    bool skipRestyle = std::exchange(restyleEntry, true);
    if (!skipRestyle) {
      PostRestyleForAnimation(aElement, aPseudoRequest, aCascadeLevel);
    }
  }

  if (aRestyleType == RestyleType::Layer) {
    mPresContext->RestyleManager()->IncrementAnimationGeneration();
    if (auto* effectSet = EffectSet::Get(aElement, aPseudoRequest)) {
      effectSet->UpdateAnimationGeneration(mPresContext);
    }
  }
}

void EffectCompositor::PostRestyleForAnimation(
    dom::Element* aElement, const PseudoStyleRequest& aPseudoRequest,
    CascadeLevel aCascadeLevel) {
  if (!mPresContext) {
    return;
  }

  // FIXME: Bug 1615083 KeyframeEffect::SetTarget() and
  // KeyframeEffect::SetPseudoElement() may set a non-existing pseudo element,
  // and we still have to update its style, based on the wpt. However, we don't
  // have the generated element here, so we failed the wpt.
  //
  // See wpt for more info: web-animations/interfaces/KeyframeEffect/target.html
  Element* element = aElement->GetPseudoElement(aPseudoRequest);
  if (!element) {
    return;
  }

  RestyleHint hint = aCascadeLevel == CascadeLevel::Transitions
                         ? RestyleHint::RESTYLE_CSS_TRANSITIONS
                         : RestyleHint::RESTYLE_CSS_ANIMATIONS;

  MOZ_ASSERT(NS_IsMainThread(),
             "Restyle request during restyling should be requested only on "
             "the main-thread. e.g. after the parallel traversal");
  if (ServoStyleSet::IsInServoTraversal() || mIsInPreTraverse) {
    MOZ_ASSERT(hint == RestyleHint::RESTYLE_CSS_ANIMATIONS ||
               hint == RestyleHint::RESTYLE_CSS_TRANSITIONS);

    // We can't call Servo_NoteExplicitHints here since AtomicRefCell does not
    // allow us mutate ElementData of the |aElement| in SequentialTask.
    // Instead we call Servo_NoteExplicitHints for the element in PreTraverse()
    // which will be called right before the second traversal that we do for
    // updating CSS animations.
    // In that case PreTraverse() will return true so that we know to do the
    // second traversal so we don't need to post any restyle requests to the
    // PresShell.
    return;
  }

  MOZ_ASSERT(!mPresContext->RestyleManager()->IsInStyleRefresh());

  mPresContext->PresShell()->RestyleForAnimation(element, hint);
}
