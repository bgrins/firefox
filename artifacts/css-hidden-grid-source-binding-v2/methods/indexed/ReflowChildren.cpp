nscoord nsGridContainerFrame::ReflowChildren(GridReflowInput& aGridRI,
                                             const LogicalRect& aContentArea,
                                             const nsSize& aContainerSize,
                                             ReflowOutput& aDesiredSize,
                                             nsReflowStatus& aStatus) {
  WritingMode wm = aGridRI.mReflowInput->GetWritingMode();
  nscoord bSize = aContentArea.BSize(wm);
  MOZ_ASSERT(aGridRI.mReflowInput);
  MOZ_ASSERT(aStatus.IsEmpty(), "Caller should pass a fresh reflow status!");
  if (HidesContentForLayout() && !GetNextContinuation()) {
    return bSize;
  }

  OverflowAreas ocBounds;
  nsReflowStatus ocStatus;
  if (GetPrevInFlow()) {
    ReflowOverflowContainerChildren(PresContext(), *aGridRI.mReflowInput,
                                    ocBounds, ReflowChildFlags::Default,
                                    ocStatus, MergeSortedFrameListsFor);
  }

  Maybe<Fragmentainer> fragmentainer = GetNearestFragmentainer(aGridRI);
  // MasonryLayout() can only handle fragmentation in the masonry-axis,
  // so we let ReflowInFragmentainer() deal with grid-axis fragmentation
  // in the else-clause below.
  if (IsMasonry() && !(IsColMasonry() && fragmentainer.isSome())) {
    aGridRI.mInFragmentainer = fragmentainer.isSome();
    nscoord sz = MasonryLayout(
        aGridRI, aContentArea, SizingConstraint::NoConstraint, aDesiredSize,
        aStatus, fragmentainer.ptrOr(nullptr), aContainerSize);
    if (IsRowMasonry()) {
      bSize = aGridRI.mReflowInput->ComputedBSize();
      if (bSize == NS_UNCONSTRAINEDSIZE) {
        bSize = aGridRI.mReflowInput->ApplyMinMaxBSize(sz);
      }
    }
  } else if (MOZ_UNLIKELY(fragmentainer.isSome())) {
    if (IsColMasonry() && !GetPrevInFlow()) {
      // First we do an unconstrained reflow to resolve the item placement
      // which is then kept as-is in the constrained reflow below.
      MasonryLayout(aGridRI, aContentArea, SizingConstraint::NoConstraint,
                    aDesiredSize, aStatus, nullptr, aContainerSize);
    }
    aGridRI.mInFragmentainer = true;
    bSize = ReflowInFragmentainer(aGridRI, aContentArea, aDesiredSize, aStatus,
                                  *fragmentainer, aContainerSize);
  } else {
    aGridRI.mIter.Reset(CSSOrderAwareFrameIterator::ChildFilter::IncludeAll);
    for (; !aGridRI.mIter.AtEnd(); aGridRI.mIter.Next()) {
      nsIFrame* child = *aGridRI.mIter;
      const GridItemInfo* info = nullptr;
      if (!child->IsPlaceholderFrame()) {
        info = &aGridRI.mGridItems[aGridRI.mIter.ItemIndex()];
      }
      nsReflowStatus childStatus;
      ReflowInFlowChild(child, info, aContainerSize, Nothing(), nullptr,
                        aGridRI, aContentArea, aDesiredSize, childStatus);
      MOZ_ASSERT(childStatus.IsComplete(),
                 "child should be complete in unconstrained reflow");
      aStatus.MergeCompletionStatusFrom(childStatus);
    }
  }

  // Merge overflow container bounds and status.
  aDesiredSize.mOverflowAreas.UnionWith(ocBounds);
  aStatus.MergeCompletionStatusFrom(ocStatus);

  return bSize;
}
