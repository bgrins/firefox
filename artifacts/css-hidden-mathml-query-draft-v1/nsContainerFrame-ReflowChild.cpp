void nsContainerFrame::ReflowChild(nsIFrame* aKidFrame,
                                   nsPresContext* aPresContext,
                                   ReflowOutput& aDesiredSize,
                                   const ReflowInput& aReflowInput, nscoord aX,
                                   nscoord aY, ReflowChildFlags aFlags,
                                   nsReflowStatus& aStatus,
                                   nsOverflowContinuationTracker* aTracker) {
  MOZ_ASSERT(aReflowInput.mFrame == aKidFrame, "bad reflow input");

  // Position the child frame and its view if requested.
  if (ReflowChildFlags::NoMoveFrame !=
      (aFlags & ReflowChildFlags::NoMoveFrame)) {
    aKidFrame->SetPosition(nsPoint(aX, aY));
  }

  // Reflow the child frame
  aKidFrame->Reflow(aPresContext, aDesiredSize, aReflowInput, aStatus);

  // If the child frame is complete, delete any next-in-flows,
  // but only if the NoDeleteNextInFlowChild flag isn't set.
  if (aStatus.IsFullyComplete() &&
      !(aFlags & ReflowChildFlags::NoDeleteNextInFlowChild)) {
    if (nsIFrame* kidNextInFlow = aKidFrame->GetNextInFlow()) {
      // Remove all of the childs next-in-flows. Make sure that we ask
      // the right parent to do the removal (it's possible that the
      // parent is not this because we are executing pullup code)
      nsOverflowContinuationTracker::AutoFinish fini(aTracker, aKidFrame);
      DestroyContext context(PresShell());
      kidNextInFlow->GetParent()->DeleteNextInFlowChild(context, kidNextInFlow,
                                                        true);
    }
  }
}
