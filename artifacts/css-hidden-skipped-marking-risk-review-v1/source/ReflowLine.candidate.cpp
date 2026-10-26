bool nsBlockFrame::ReflowLine(BlockReflowState& aState, LineIterator aLine,
                              bool* aKeepReflowGoing) {
  MOZ_ASSERT(aLine->GetChildCount(), "reflowing empty line");

  // Setup the line-layout for the new line
  aState.mCurrentLine = aLine;
  aLine->ClearDirty();
  aLine->InvalidateCachedIsEmpty();
  aLine->ClearHadFloatPushed();
  aLine->ClearTextBoxTrimStartApplied();
  aLine->ClearTextBoxTrimEndApplied();

  // If this line contains a single block that is hidden by `content-visibility`
  // don't reflow the line. If this line contains inlines and the first one is
  // hidden by `content-visibility`, all of them are, so avoid reflow in that
  // case as well.
  // For frames that own anonymous children, even the first child is hidden by
  // `content-visibility`, there could be some anonymous children need reflow,
  // so we don't skip reflow this line.
  nsIFrame* firstChild = aLine->mFirstChild;
  if (firstChild->IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      !HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES)) {
    for (nsIFrame* child : aLine->ChildFrames()) {
      child->MarkSubtreeDirty();
    }
    return false;
  }

  // Now that we know what kind of line we have, reflow it
  bool usedOverflowWrap = false;
  if (aLine->IsBlock()) {
    ReflowBlockFrame(aState, aLine, aKeepReflowGoing);
  } else {
    aLine->SetLineWrapped(false);
    usedOverflowWrap = ReflowInlineFrames(aState, aLine, aKeepReflowGoing);

    // Store the line's float edges for overflow marker analysis if needed.
    aLine->ClearFloatEdges();
    if (aState.mFlags.mCanHaveOverflowMarkers) {
      WritingMode wm = aLine->mWritingMode;
      nsFlowAreaRect r = aState.GetFloatAvailableSpaceForBSize(
          wm, aLine->BStart(), aLine->BSize(), nullptr);
      if (r.HasFloats()) {
        LogicalRect so = aLine->GetOverflowArea(OverflowType::Scrollable, wm,
                                                aLine->mContainerSize);
        nscoord s = r.mRect.IStart(wm);
        nscoord e = r.mRect.IEnd(wm);
        if (so.IEnd(wm) > e || so.IStart(wm) < s) {
          // This line is overlapping a float - store the edges marking the area
          // between the floats for text-overflow analysis.
          aLine->SetFloatEdges(s, e);
        }
      }
    }
  }

  aLine->ClearMovedFragments();

  // If text-box-trim was applied on the start/end side, clear the
  // state flags to prevent checking trim eligibility for later siblings.
  if (aLine->TextBoxTrimStartApplied()) {
    aState.mFlags.mShouldApplyTextBoxTrimStart = false;
  }
  if (aLine->TextBoxTrimEndApplied()) {
    aState.mFlags.mShouldApplyTextBoxTrimAtBlockEnd = false;
    aState.mFlags.mShouldApplyTextBoxTrimAtFragmentEnd = false;
  }

  return usedOverflowWrap;
}
