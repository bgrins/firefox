void nsBlockFrame::Reflow(nsPresContext* aPresContext, ReflowOutput& aMetrics,
                          const ReflowInput& aReflowInput,
                          nsReflowStatus& aStatus) {
  if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      !GetNextContinuation()) {
    FinishAndStoreOverflow(&aMetrics, aReflowInput.mStyleDisplay);
    return;
  }

