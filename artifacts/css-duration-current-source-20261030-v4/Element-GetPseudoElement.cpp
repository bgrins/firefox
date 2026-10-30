Element* Element::GetPseudoElement(const PseudoStyleRequest& aRequest) const {
  switch (aRequest.mType) {
    case PseudoStyleType::NotPseudo:
      // It's unfortunate we have to do const cast, so we don't have to write
      // the almost duplicate function for the non-const function.
      return const_cast<Element*>(this);
    case PseudoStyleType::Before:
      return nsLayoutUtils::GetBeforePseudo(this);
    case PseudoStyleType::After:
      return nsLayoutUtils::GetAfterPseudo(this);
    case PseudoStyleType::Marker:
      return nsLayoutUtils::GetMarkerPseudo(this);
    case PseudoStyleType::Backdrop:
      return nsLayoutUtils::GetBackdropPseudo(this);
    case PseudoStyleType::Checkmark:
      return nsLayoutUtils::GetCheckmarkPseudo(this);
    case PseudoStyleType::PickerIcon:
      return nsLayoutUtils::GetPickerIconPseudo(this);
    case PseudoStyleType::ViewTransition:
    case PseudoStyleType::ViewTransitionGroup:
    case PseudoStyleType::ViewTransitionImagePair:
    case PseudoStyleType::ViewTransitionOld:
    case PseudoStyleType::ViewTransitionNew: {
      Element* result = SearchViewTransitionPseudo(this, aRequest);
      MOZ_ASSERT(!result || result->GetPseudoElementType() == aRequest.mType,
                 "The type should match");
      MOZ_ASSERT(!result || !result->HasName() ||
                     result->GetParsedAttr(nsGkAtoms::name)->GetAtomValue() ==
                         aRequest.mIdentifier,
                 "The identifier should match");
      return result;
    }
    default:
      return nullptr;
  }
}
