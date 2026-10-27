void nsMathMLContainerFrame::ReflowChild(nsIFrame* aChildFrame,
                                         nsPresContext* aPresContext,
                                         ReflowOutput& aDesiredSize,
                                         const ReflowInput& aReflowInput,
                                         nsReflowStatus& aStatus) {
  // Having foreign/hybrid children, e.g., from html markups, is not defined by
  // the MathML spec. But it can happen in practice, e.g., <html:img> allows us
  // to do some cool demos... or we may have a child that is an nsInlineFrame
  // from a generated content such as :before { content: open-quote } or
  // :after { content: close-quote }. Unfortunately, the other frames out-there
  // may expect their own invariants that are not met when we mix things.
  // Hence we do not claim their support, but we will nevertheless attempt to
  // keep them in the flow, if we can get their desired size. We observed that
  // most frames may be reflowed generically, but nsInlineFrames need extra
  // care.

  NS_ASSERTION(!aChildFrame->IsInlineFrameOrSubclass(),
               "Inline frames should be wrapped in blocks");

  nsContainerFrame::ReflowChild(aChildFrame, aPresContext, aDesiredSize,
                                aReflowInput, 0, 0,
                                ReflowChildFlags::NoMoveFrame, aStatus);

  if (aDesiredSize.BlockStartAscent() == ReflowOutput::ASK_FOR_BASELINE) {
    // This will be suitable for inline frames, which are wrapped in a block.
    nscoord ascent;
    WritingMode wm = aDesiredSize.GetWritingMode();
    if (!nsLayoutUtils::GetLastLineBaseline(wm, aChildFrame, &ascent)) {
      // We don't expect any other block children so just place the frame on
      // the baseline instead of going through DidReflow() and
      // GetBaseline().  This is what nsIFrame::GetBaseline() will do anyway.
      aDesiredSize.SetBlockStartAscent(aDesiredSize.BSize(wm));
    } else {
      aDesiredSize.SetBlockStartAscent(ascent);
    }
  }
  if (IsForeignChild(aChildFrame)) {
    // use ComputeTightBounds API as aDesiredSize.mBoundingMetrics is not set.
    nsRect r = aChildFrame->ComputeTightBounds(
        aReflowInput.mRenderingContext->GetDrawTarget());
    aDesiredSize.mBoundingMetrics.leftBearing = r.x;
    aDesiredSize.mBoundingMetrics.rightBearing = r.XMost();
    aDesiredSize.mBoundingMetrics.ascent =
        aDesiredSize.BlockStartAscent() - r.y;
    aDesiredSize.mBoundingMetrics.descent =
        r.YMost() - aDesiredSize.BlockStartAscent();
    aDesiredSize.mBoundingMetrics.width = aDesiredSize.Width();
  }
}
