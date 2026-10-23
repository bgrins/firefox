bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const {
  const auto* parent = GetInFlowParent();
  // The anonymous children owned by parent are important for properly sizing
  // their parents.
  return parent && parent->HidesContentForLayout() &&
         !(parent->HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES) &&
           Style()->IsAnonBox());
}
