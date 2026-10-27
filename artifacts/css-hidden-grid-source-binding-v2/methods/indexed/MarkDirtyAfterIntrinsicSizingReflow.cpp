static void MarkDirtyAfterIntrinsicSizingReflow(nsIFrame* aChild) {
  aChild->MarkSubtreeDirty();
  auto* cur = aChild;
  while (true) {
    nsIFrame* parent = cur->GetParent();
    if (!parent || parent->IsSubtreeDirty() ||
        parent->HasAnyStateBits(NS_FRAME_IN_REFLOW)) {
      return;
    }
    parent->ChildIsDirty(cur);
    cur = parent;
  }
}
