void nsMathMLContainerFrame::Reflow(nsPresContext* aPresContext,
                                    ReflowOutput& aDesiredSize,
                                    const ReflowInput& aReflowInput,
                                    nsReflowStatus& aStatus) {
  if (IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
    return;
  }

  MarkInReflow();
  MOZ_ASSERT(aStatus.IsEmpty(), "Caller should pass a fresh reflow status!");

  aDesiredSize.Width() = aDesiredSize.Height() = 0;
  aDesiredSize.SetBlockStartAscent(0);
  aDesiredSize.mBoundingMetrics = nsBoundingMetrics();

  /////////////
  // Reflow children
  // Asking each child to cache its bounding metrics

  nsReflowStatus childStatus;
  nsIFrame* childFrame = mFrames.FirstChild();
  while (childFrame) {
    ReflowOutput childDesiredSize(aReflowInput);
    WritingMode wm = childFrame->GetWritingMode();
    LogicalSize availSize = aReflowInput.ComputedSize(wm);
    availSize.BSize(wm) = NS_UNCONSTRAINEDSIZE;
    ReflowInput childReflowInput(aPresContext, aReflowInput, childFrame,
                                 availSize);
    ReflowChild(childFrame, aPresContext, childDesiredSize, childReflowInput,
                childStatus);
    // NS_ASSERTION(childStatus.IsComplete(), "bad status");
    SaveReflowAndBoundingMetricsFor(childFrame, childDesiredSize,
                                    childDesiredSize.mBoundingMetrics);
    childFrame = childFrame->GetNextSibling();
  }

  /////////////
  // If we are a container which is entitled to stretch its children, then we
  // ask our stretchy children to stretch themselves

  // The stretching of siblings of an embellished child is _deferred_ until
  // after finishing the stretching of the embellished child - bug 117652

  DrawTarget* drawTarget = aReflowInput.mRenderingContext->GetDrawTarget();

  if (!mEmbellishData.flags.contains(
          MathMLEmbellishFlag::EmbellishedOperator) &&
      (mPresentationData.flags.contains(
           MathMLPresentationFlag::StretchAllChildrenVertically) ||
       mPresentationData.flags.contains(
           MathMLPresentationFlag::StretchAllChildrenHorizontally))) {
    // get the stretchy direction
    StretchDirection stretchDir =
        mPresentationData.flags.contains(
            MathMLPresentationFlag::StretchAllChildrenVertically)
            ? StretchDirection::Vertical
            : StretchDirection::Horizontal;

    // what size should we use to stretch our stretchy children
    // We don't use PreferredStretchSizeMode::Embellishments -- because
    // we don't want to include them in the caculations of the size of stretchy
    // elements
    nsBoundingMetrics containerSize;
    GetPreferredStretchSize(
        drawTarget,
        PreferredStretchSizeMode::EmbellishmentsIfSameStretchDirection,
        stretchDir, containerSize);

    // fire the stretch on each child
    childFrame = mFrames.FirstChild();
    while (childFrame) {
      nsIMathMLFrame* mathMLFrame = do_QueryFrame(childFrame);
      if (mathMLFrame) {
        // retrieve the metrics that was stored at the previous pass
        ReflowOutput childDesiredSize(aReflowInput);
        GetReflowAndBoundingMetricsFor(childFrame, childDesiredSize,
                                       childDesiredSize.mBoundingMetrics);

        mathMLFrame->Stretch(drawTarget, stretchDir, containerSize,
                             childDesiredSize);
        // store the updated metrics
        SaveReflowAndBoundingMetricsFor(childFrame, childDesiredSize,
                                        childDesiredSize.mBoundingMetrics);
      }
      childFrame = childFrame->GetNextSibling();
    }
  }

  /////////////
  // Place children now by re-adjusting the origins to align the baselines
  FinalizeReflow(drawTarget, aDesiredSize);
}
