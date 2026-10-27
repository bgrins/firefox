void nsBlockFrame::CheckFloats(BlockReflowState& aState) {
#ifdef DEBUG
  // If any line is still dirty, that must mean we're going to reflow this
  // block again soon (e.g. because we bailed out after noticing that
  // clearance was imposed), so don't worry if the floats are out of sync.
  bool anyLineDirty = false;

  // Check that the float list is what we would have built
  AutoTArray<nsIFrame*, 8> lineFloats;
  for (auto& line : Lines()) {
    if (line.HasFloats()) {
      lineFloats.AppendElements(line.Floats());
    }
    if (line.IsDirty()) {
      anyLineDirty = true;
    }
  }

  AutoTArray<nsIFrame*, 8> storedFloats;
  bool equal = true;
  bool hasHiddenFloats = false;
  uint32_t i = 0;
  for (nsIFrame* f : GetChildList(FrameChildListID::Float)) {
    if (f->HasAnyStateBits(NS_FRAME_IS_PUSHED_OUT_OF_FLOW)) {
      continue;
    }
    // There are chances that the float children won't be added to lines,
    // because in nsBlockFrame::ReflowLine, it skips reflow line if the first
    // child of the line is IsHiddenByContentVisibilityOfInFlowParentForLayout.
    // There are also chances that the floats in line are out of date, for
    // instance, lines could reflow if
    // PresShell::IsForcingLayoutForHiddenContent, and after forcingLayout is
    // off, the reflow of lines could be skipped, but the floats are still in
    // there. Here we can't know whether the floats hidden by c-v are included
    // in the lines or not. So we use hasHiddenFloats to skip the float length
    // checking.
    if (!hasHiddenFloats &&
        f->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
      hasHiddenFloats = true;
    }
    storedFloats.AppendElement(f);
    if (i < lineFloats.Length() && lineFloats.ElementAt(i) != f) {
      equal = false;
    }
    ++i;
  }

  if ((!equal || lineFloats.Length() != storedFloats.Length()) &&
      !anyLineDirty && !hasHiddenFloats) {
    NS_ERROR(
        "nsBlockFrame::CheckFloats: Explicit float list is out of sync with "
        "float cache");
  }
#endif

  const nsFrameList* oofs = GetOverflowFloats();
  if (oofs && oofs->NotEmpty()) {
    // Floats that were pushed should be removed from our float
    // manager.  Otherwise the float manager's YMost or XMost might
    // be larger than necessary, causing this block to get an
    // incorrect desired height (or width).  Some of these floats
    // may not actually have been added to the float manager because
    // they weren't reflowed before being pushed; that's OK,
    // RemoveRegions will ignore them. It is safe to do this here
    // because we know from here on the float manager will only be
    // used for its XMost and YMost, not to place new floats and
    // lines.
    aState.FloatManager()->RemoveTrailingRegions(oofs->FirstChild());
  }
}
