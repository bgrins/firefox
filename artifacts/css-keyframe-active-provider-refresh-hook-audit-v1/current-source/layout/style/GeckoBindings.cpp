void Gecko_UpdateAnimations(const Element* aElement,
                            const ComputedStyle* aOldComputedData,
                            const ComputedStyle* aComputedData,
                            UpdateAnimationsTasks aTasks) {
  MOZ_ASSERT(NS_IsMainThread());
  MOZ_ASSERT(aElement);

  if (!aElement->IsInComposedDoc()) {
    return;
  }

  nsPresContext* presContext = nsContentUtils::GetContextForContent(aElement);
  if (!presContext || !presContext->IsDynamic()) {
    return;
  }

  nsAutoAnimationMutationBatch mb(aElement->OwnerDoc());

  const auto [element, pseudoRequest] =
      AnimationUtils::GetElementPseudoPair(aElement);

  // Handle timeline scopes first, because our own scroll/view-linked animations
  // may be affected.
  if (aTasks & UpdateAnimationsTasks::TimelineScopes) {
    presContext->TimelineManager()->UpdateTimelineScopes(element,
                                                         aComputedData);
    // We could try to limit the impact here, at least for changes involving not
    // `all`. However, defer any such optimization until after bug 2024012.
    presContext->AnimationManager()->UpdateAllNamedTimelineAnimations();
  }

  // Handle scroll/view timelines first because CSS animations may refer to the
  // timeline defined by itself.
  if (aTasks & UpdateAnimationsTasks::ScrollTimelines) {
    const auto affected = presContext->TimelineManager()->UpdateTimelines(
        const_cast<Element*>(element), pseudoRequest, aComputedData,
        TimelineManager::ProgressTimelineType::Scroll);
    presContext->AnimationManager()->UpdateNamedTimelineAnimations(affected);
  }

  if (aTasks & UpdateAnimationsTasks::ViewTimelines) {
    const auto affected = presContext->TimelineManager()->UpdateTimelines(
        const_cast<Element*>(element), pseudoRequest, aComputedData,
        TimelineManager::ProgressTimelineType::View);
    presContext->AnimationManager()->UpdateNamedTimelineAnimations(affected);
  }

  if (aTasks & UpdateAnimationsTasks::CSSAnimations) {
    presContext->AnimationManager()->UpdateAnimations(
        const_cast<Element*>(element), pseudoRequest, aComputedData);
  }

  // aComputedData might be nullptr if the target element is now in a
  // display:none subtree. We still call Gecko_UpdateAnimations in this case
  // because we need to stop CSS animations in the display:none subtree.
  // However, we don't need to update transitions since they are stopped by
  // RestyleManager::AnimationsWithDestroyedFrame so we just return early
  // here.
  if (!aComputedData) {
    return;
  }

  if (aTasks & UpdateAnimationsTasks::CSSTransitions) {
    MOZ_ASSERT(aOldComputedData);
    presContext->TransitionManager()->UpdateTransitions(
        const_cast<Element*>(element), pseudoRequest, *aOldComputedData,
        *aComputedData);
  }

  if (aTasks & UpdateAnimationsTasks::EffectProperties) {
    presContext->EffectCompositor()->UpdateEffectProperties(
        aComputedData, const_cast<Element*>(element), pseudoRequest);
  }

  if (aTasks & UpdateAnimationsTasks::CascadeResults) {
    EffectSet* effectSet = EffectSet::Get(element, pseudoRequest);
    // CSS animations/transitions might have been destroyed as part of the above
    // steps so before updating cascade results, we check if there are still any
    // animations to update.
    if (effectSet) {
      // We call UpdateCascadeResults directly (intead of
      // MaybeUpdateCascadeResults) since we know for sure that the cascade has
      // changed, but we were unable to call MarkCascadeUpdated when we noticed
      // it since we avoid mutating state as part of the Servo parallel
      // traversal.
      presContext->EffectCompositor()->UpdateCascadeResults(
          *effectSet, const_cast<Element*>(element), pseudoRequest);
    }
  }

  if (aTasks & UpdateAnimationsTasks::DisplayChangedFromNone) {
    presContext->EffectCompositor()->RequestRestyle(
        const_cast<Element*>(element), pseudoRequest,
        EffectCompositor::RestyleType::Standard,
        EffectCompositor::CascadeLevel::Animations);
  }
}
