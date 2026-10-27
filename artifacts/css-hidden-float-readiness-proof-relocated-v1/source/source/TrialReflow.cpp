nsReflowStatus nsBlockFrame::TrialReflow(nsPresContext* aPresContext,
                                         ReflowOutput& aMetrics,
                                         const ReflowInput& aReflowInput,
                                         TrialReflowState& aTrialState) {
#ifdef DEBUG
  // Between when we drain pushed floats and when we complete reflow,
  // we're allowed to have multiple continuations of the same float on
  // our floats list, since a first-in-flow might get pushed to a later
  // continuation of its containing block.  But it's not permitted
  // outside that time.
  nsLayoutUtils::AssertNoDuplicateContinuations(
      this, GetChildList(FrameChildListID::Float));
#endif

  // ALWAYS drain overflow. We never want to leave the previnflow's
  // overflow lines hanging around; block reflow depends on the
  // overflow line lists being cleared out between reflow passes.
  DrainOverflowLines();

  // Clear any existing -webkit-line-clamp ellipsis if we're reflowing the
  // line-clamp root. We are also setting our max-height to be referenced by
  // descendants when applying line-clamp.
  if (IsLineClampRoot(this)) {
    ClearLineClampEllipsis();
    nscoord rootMaxBSize =
        aReflowInput.ApplyMinMaxBSize(aReflowInput.ComputedBSize());
    SetLineClampRootMaxHeight(rootMaxBSize +
                              GetLogicalUsedBorderAndPadding(GetWritingMode())
                                  .BStartEnd(GetWritingMode()));
  }

  bool blockStartMarginRoot, blockEndMarginRoot;
  IsMarginRoot(&blockStartMarginRoot, &blockEndMarginRoot);

  BlockReflowState state(aReflowInput, aPresContext, this, blockStartMarginRoot,
                         blockEndMarginRoot, aTrialState.mNeedFloatManager,
                         aTrialState.mConsumedBSize,
                         aTrialState.mEffectiveContentBoxBSize,
                         aTrialState.mInset);

  // Handle paginated overflow (see nsContainerFrame.h)
  nsReflowStatus ocStatus;
  if (GetPrevInFlow()) {
    ReflowOverflowContainerChildren(
        aPresContext, aReflowInput, aTrialState.mOcBounds,
        ReflowChildFlags::Default, ocStatus, DefaultChildFrameMerge,
        Some(state.ContainerSize()));
  }

  // Now that we're done cleaning up our overflow container lists, we can
  // give |state| its nsOverflowContinuationTracker.
  nsOverflowContinuationTracker tracker(this, false);
  state.mOverflowTracker = &tracker;

  // Drain & handle pushed floats
  DrainPushedFloats();
  ReflowPushedFloats(state, aTrialState.mFcBounds);

  // If we're not dirty (which means we'll mark everything dirty later)
  // and our inline-size has changed, mark the lines dirty that we need to
  // mark dirty for a resize reflow.
  if (!HasAnyStateBits(NS_FRAME_IS_DIRTY) && aReflowInput.IsIResize()) {
    PrepareResizeReflow(state);
  }

  // The same for percentage text-indent, except conditioned on the
  // parent resizing.
  if (!HasAnyStateBits(NS_FRAME_IS_DIRTY) && aReflowInput.mCBReflowInput &&
      aReflowInput.mCBReflowInput->IsIResize() &&
      StyleText()->mTextIndent.length.HasPercent() && !mLines.empty()) {
    mLines.front()->MarkDirty();
  }

  // For text-wrap:balance trials, we need to reflow all the inline lines even
  // if they're not all "dirty", but we don't need to reflow any block lines.
  if (aTrialState.mBalancing) {
    MarkAllInlineLinesDirty(this);
  } else {
    LazyMarkLinesDirty();
  }

  // Now reflow...
  aTrialState.mUsedOverflowWrap = ReflowDirtyLines(state);

  // If we have a next-in-flow, and that next-in-flow has pushed floats from
  // this frame from a previous iteration of reflow, then we should not return
  // a status with IsFullyComplete() equals to true, since we actually have
  // overflow, it's just already been handled.

  // NOTE: This really shouldn't happen, since we _should_ pull back our floats
  // and reflow them, but just in case it does, this is a safety precaution so
  // we don't end up with a placeholder pointing to frames that have already
  // been deleted as part of removing our next-in-flow.
  if (state.mReflowStatus.IsFullyComplete()) {
    nsBlockFrame* nif = static_cast<nsBlockFrame*>(GetNextInFlow());
    while (nif) {
      if (nif->HasPushedFloatsFromPrevContinuation()) {
        if (nif->HasAnyStateBits(NS_FRAME_IS_OVERFLOW_CONTAINER)) {
          state.mReflowStatus.SetOverflowIncomplete();
        } else {
          state.mReflowStatus.SetIncomplete();
        }
        break;
      }

      nif = static_cast<nsBlockFrame*>(nif->GetNextInFlow());
    }
  }

  state.mReflowStatus.MergeCompletionStatusFrom(ocStatus);

  // If we end in a BR with clear and affected floats continue,
  // we need to continue, too.
  if (NS_UNCONSTRAINEDSIZE != aReflowInput.AvailableBSize() &&
      state.mReflowStatus.IsComplete() &&
      state.FloatManager()->ClearContinues(FindTrailingClear())) {
    state.mReflowStatus.SetIncomplete();
  }

  if (!state.mReflowStatus.IsFullyComplete()) {
    if (HasOverflowLines() || HasPushedFloats()) {
      state.mReflowStatus.SetNextInFlowNeedsReflow();
    }
  }

  // Place the ::marker's frame if it is placed next to a block child.
  //
  // According to the CSS2 spec, section 12.6.1, the ::marker's box
  // participates in the height calculation of the list-item box's
  // first line box.
  //
  // There are exactly two places a ::marker can be placed: near the
  // first or second line. It's only placed on the second line in a
  // rare case: an empty first line followed by a second line that
  // contains a block (example: <LI>\n<P>... ). This is where
  // the second case can happen.
  nsIFrame* outsideMarker = GetOutsideMarker();
  if (outsideMarker && !mLines.empty() &&
      (mLines.front()->IsBlock() ||
       (0 == mLines.front()->BSize() && mLines.front() != mLines.back() &&
        mLines.begin().next()->IsBlock()))) {
    // Reflow the ::marker's frame.
    ReflowOutput reflowOutput(aReflowInput);
    // XXX Use the entire line when we fix bug 25888.
    nsLayoutUtils::LinePosition position;
    WritingMode wm = aReflowInput.GetWritingMode();
    bool havePosition =
        nsLayoutUtils::GetFirstLinePosition(wm, this, &position);
    nscoord lineBStart =
        havePosition ? position.mBStart
                     : aReflowInput.ComputedLogicalBorderPadding(wm).BStart(wm);
    ReflowOutsideMarker(outsideMarker, state, reflowOutput, lineBStart);
    NS_ASSERTION(!MarkerIsEmpty(outsideMarker) || reflowOutput.BSize(wm) == 0,
                 "empty ::marker frame took up space");

    if (havePosition && !MarkerIsEmpty(outsideMarker)) {
      // We have some lines to align the ::marker with.

      // Doing the alignment using the baseline will also cater for
      // ::markers that are placed next to a child block (bug 92896)

      // Tall ::markers won't look particularly nice here...
      LogicalRect bbox =
          outsideMarker->GetLogicalRect(wm, reflowOutput.PhysicalSize());
      const auto baselineGroup = BaselineSharingGroup::First;
      Maybe<nscoord> result;
      if (MOZ_LIKELY(!wm.IsOrthogonalTo(outsideMarker->GetWritingMode()))) {
        result = outsideMarker->GetNaturalBaselineBOffset(
            wm, baselineGroup, BaselineExportContext::LineLayout);
      }
      const auto markerBaseline =
          result.valueOrFrom([bbox, wm, outsideMarker]() {
            return bbox.BSize(wm) +
                   outsideMarker->GetLogicalUsedMargin(wm).BEnd(wm);
          });
      bbox.BStart(wm) = position.mBaseline - markerBaseline;
      outsideMarker->SetRect(wm, bbox, reflowOutput.PhysicalSize());
    }
    // Otherwise just leave the ::marker where it is, up against our
    // block-start padding.
  }

  CheckFloats(state);

  // If this block frame indicated that it needs to be reflowed to apply
  // text-box-trim on the trim-end side, propagate that signal up to the parent.
  aMetrics.mNeedsTextBoxTrimAtFragmentEndRetry =
      state.mNeedsTextBoxTrimAtFragmentEndRetry;

  // Compute our final size (for this trial layout)
  aTrialState.mBlockEndEdgeOfChildren =
      ComputeFinalSize(aReflowInput, state, aMetrics);
  aTrialState.mContainerWidth = state.ContainerSize().width;

  // Align content
  AlignContent(state, aMetrics, aTrialState.mBlockEndEdgeOfChildren);

  return state.mReflowStatus;
}
