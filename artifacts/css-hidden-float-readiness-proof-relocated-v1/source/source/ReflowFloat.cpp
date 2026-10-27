void nsBlockFrame::ReflowFloat(BlockReflowState& aState, ReflowInput& aFloatRI,
                               nsIFrame* aFloat,
                               nsReflowStatus& aReflowStatus) {
  MOZ_ASSERT(aReflowStatus.IsEmpty(),
             "Caller should pass a fresh reflow status!");
  MOZ_ASSERT(aFloat->HasAnyStateBits(NS_FRAME_OUT_OF_FLOW),
             "aFloat must be an out-of-flow frame");

  WritingMode wm = aState.mReflowInput.GetWritingMode();

  // Setup a block reflow context to reflow the float.
  nsBlockReflowContext brc(aState.mPresContext, aState.mReflowInput);

  nsIFrame* clearanceFrame = nullptr;
  do {
    CollapsingMargin margin;
    bool mayNeedRetry = false;
    aFloatRI.mDiscoveredClearance = nullptr;
    // Only first in flow gets a block-start margin.
    if (!aFloat->GetPrevInFlow()) {
      brc.ComputeCollapsedBStartMargin(aFloatRI, &margin, clearanceFrame,
                                       &mayNeedRetry);

      if (mayNeedRetry && !clearanceFrame) {
        aFloatRI.mDiscoveredClearance = &clearanceFrame;
        // We don't need to push the float manager state because the the block
        // has its own float manager that will be destroyed and recreated
      }
    }

    // When reflowing a float, aSpace argument doesn't matter because we pass
    // nullptr to aLine and we don't call nsBlockReflowContext::PlaceBlock()
    // later.
    brc.ReflowBlock(LogicalRect(wm), true, margin, 0, nullptr, aFloatRI,
                    aReflowStatus, aState);
  } while (clearanceFrame);

  if (aFloat->IsLetterFrame()) {
    // We never split floating first letters; an incomplete status for such
    // frames simply means that there is more content to be reflowed on the
    // line.
    if (aReflowStatus.IsIncomplete()) {
      aReflowStatus.Reset();
    }
  }

  NS_ASSERTION(aReflowStatus.IsFullyComplete() ||
                   aFloatRI.AvailableBSize() != NS_UNCONSTRAINEDSIZE,
               "The status can only be incomplete or overflow-incomplete if "
               "the available block-size is constrained!");

  if (aReflowStatus.NextInFlowNeedsReflow()) {
    aState.mReflowStatus.SetNextInFlowNeedsReflow();
  }

  const ReflowOutput& metrics = brc.GetMetrics();

  // Set the rect, make sure the view is properly sized and positioned,
  // and tell the frame we're done reflowing it
  // XXXldb This seems like the wrong place to be doing this -- shouldn't
  // we be doing this in BlockReflowState::FlowAndPlaceFloat after
  // we've positioned the float, and shouldn't we be doing the equivalent
  // of |PlaceFrameView| here?
  WritingMode metricsWM = metrics.GetWritingMode();
  aFloat->SetSize(metricsWM, metrics.Size(metricsWM));
  aFloat->DidReflow(aState.mPresContext, &aFloatRI);
}
