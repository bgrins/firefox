bool nsIFrame::HidesContentForLayout() const {
  return HidesContent() && !PresShell()->IsForcingLayoutForHiddenContent(this);
}
