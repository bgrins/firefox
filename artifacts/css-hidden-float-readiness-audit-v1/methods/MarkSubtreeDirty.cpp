void nsIFrame::MarkSubtreeDirty() {
  if (HasAnyStateBits(NS_FRAME_IS_DIRTY)) {
    return;
  }
  // Unconditionally mark given frame dirty.
  AddStateBits(NS_FRAME_IS_DIRTY);

  // Mark all descendants dirty, unless:
  // - Already dirty.
  // - TableColGroup
  AutoTArray<nsIFrame*, 32> stack;
  for (const auto& childLists : ChildLists()) {
    for (nsIFrame* kid : childLists.mList) {
      stack.AppendElement(kid);
    }
  }
  while (!stack.IsEmpty()) {
    nsIFrame* f = stack.PopLastElement();
    if (f->HasAnyStateBits(NS_FRAME_IS_DIRTY) || f->IsTableColGroupFrame()) {
      continue;
    }

    f->AddStateBits(NS_FRAME_IS_DIRTY);

    for (const auto& childLists : f->ChildLists()) {
      for (nsIFrame* kid : childLists.mList) {
        stack.AppendElement(kid);
      }
    }
  }
}
