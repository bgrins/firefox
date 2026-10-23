void PresShell::UpdateHiddenContentInForcedLayout(nsIFrame* aFrame) {
  if (!aFrame || !aFrame->IsSubtreeDirty()) {
    return;
  }

  nsIFrame* topmostFrameWithContentHidden = nullptr;
  for (nsIFrame* cur = aFrame->GetInFlowParent(); cur;
       cur = cur->GetInFlowParent()) {
    if (cur->HidesContent()) {
      topmostFrameWithContentHidden = cur;
      mHiddenContentInForcedLayout.Insert(cur->GetContent());
    }
  }

  if (mHiddenContentInForcedLayout.IsEmpty()) {
    return;
  }

  // Queue and immediately flush a reflow for this node.
  MOZ_ASSERT(topmostFrameWithContentHidden);
  FrameNeedsReflow(topmostFrameWithContentHidden, IntrinsicDirty::None,
                   NS_FRAME_IS_DIRTY);
}
