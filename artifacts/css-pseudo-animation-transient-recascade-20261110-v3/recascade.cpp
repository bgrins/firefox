already_AddRefed<ComputedStyle> ServoStyleSet::RecascadeStyleForMissingPseudo(
    const Element& aElement, const PseudoStyleRequest& aPseudo,
    const ComputedStyle& aBase, const ComputedStyle& aPrimary,
    const StyleAnimationValueMap& aAnimations,
    const StyleAnimationValueMap& aTransitions) {
  nsPresContext* pc = GetPresContext();
  if (!pc || !pc->IsDynamic() || IsInServoTraversal() || StylistNeedsUpdate() ||
      aElement.OwnerDoc() != mDocument || !aElement.IsInComposedDoc() ||
      aPseudo.mIdentifier ||
      (aPseudo.mType != PseudoStyleType::Before &&
       aPseudo.mType != PseudoStyleType::After &&
       aPseudo.mType != PseudoStyleType::Marker) ||
      aElement.GetPseudoElement(aPseudo) ||
      aBase.GetPseudoType() != aPseudo.mType ||
      aPrimary.GetPseudoType() != PseudoStyleType::NotPseudo) {
    return nullptr;
  }
  AutoSetInServoTraversal guard(this);
  return Servo_RecascadeStyleForMissingPseudo(
             &aElement, aPseudo.mType, &aBase, &aPrimary, &aAnimations,
             &aTransitions, &pc->RestyleManager()->Snapshots(), mRawData.get())
      .Consume();
}
