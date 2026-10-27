nscoord nsGridContainerFrame::ComputeIntrinsicISize(
    const IntrinsicSizeInput& aInput, IntrinsicISizeType aType) {
  GRID_LOG("Compute %s isize for grid container frame %p",
           aType == IntrinsicISizeType::MinISize ? "min" : "pref", this);

  if (Maybe<nscoord> containISize = ContainIntrinsicISize()) {
    return *containISize;
  }

  // Calculate the sum of column sizes under intrinsic sizing.
  // https://drafts.csswg.org/css-grid-2/#intrinsic-sizes
  NormalizeChildLists();
  GridReflowInput gridRI(this, *aInput.mContext);
  // Ensure we do not measure flex tracks against unconstrained bounds.
  gridRI.mIsGridIntrinsicSizing = true;
  InitImplicitNamedAreas(gridRI.mGridStyle);  // XXX optimize

  // The min/sz/max sizes are the input to the "repeat-to-fill" algorithm:
  // https://drafts.csswg.org/css-grid-2/#auto-repeat
  // They're only used for auto-repeat so we skip computing them otherwise.
  RepeatTrackSizingInput repeatSizing(gridRI.mWM);
  if (!IsColSubgrid() && gridRI.mColFunctions.mHasRepeatAuto) {
    repeatSizing.InitFromStyle(
        LogicalAxis::Inline, gridRI.mWM, gridRI.mFrame, gridRI.mFrame->Style(),
        gridRI.mFrame->GetAspectRatio(), aInput.mContainingBlockSize);
  }
  if ((!IsRowSubgrid() && gridRI.mRowFunctions.mHasRepeatAuto &&
       !(gridRI.mGridStyle->mGridAutoFlow & StyleGridAutoFlow::ROW)) ||
      IsColMasonry()) {
    // Only 'grid-auto-flow:column' can create new implicit columns, so that's
    // the only case where our block-size can affect the number of columns.
    // Masonry layout always depends on how many rows we have though.
    repeatSizing.InitFromStyle(
        LogicalAxis::Block, gridRI.mWM, gridRI.mFrame, gridRI.mFrame->Style(),
        gridRI.mFrame->GetAspectRatio(), aInput.mContainingBlockSize);
  }

  Grid grid;
  if (MOZ_LIKELY(!IsSubgrid())) {
    grid.PlaceGridItems(gridRI, repeatSizing);  // XXX optimize
  } else {
    auto* subgrid = GetProperty(Subgrid::Prop());
    gridRI.mGridItems = subgrid->mGridItems.Clone();
    gridRI.mAbsPosItems = subgrid->mAbsPosItems.Clone();
    grid.mGridColEnd = subgrid->mGridColEnd;
    grid.mGridRowEnd = subgrid->mGridRowEnd;
  }

  auto constraint = aType == IntrinsicISizeType::MinISize
                        ? SizingConstraint::MinContent
                        : SizingConstraint::MaxContent;
  if (IsColMasonry()) {
    ReflowOutput desiredSize(gridRI.mWM);
    nsSize containerSize;
    LogicalRect contentArea(gridRI.mWM);
    nsReflowStatus status;
    gridRI.mRows.mSizes.SetLength(grid.mGridRowEnd);
    gridRI.CalculateTrackSizesForAxis(LogicalAxis::Inline, grid,
                                      NS_UNCONSTRAINEDSIZE, constraint);
    return MasonryLayout(gridRI, contentArea, constraint, desiredSize, status,
                         nullptr, containerSize);
  }

  if (grid.mGridColEnd == 0) {
    return nscoord(0);
  }

  gridRI.CalculateTrackSizesForAxis(LogicalAxis::Inline, grid,
                                    NS_UNCONSTRAINEDSIZE, constraint);

  const nscoord contentBoxBSize =
      aInput.mPercentageBasisForChildren
          ? aInput.mPercentageBasisForChildren->BSize(gridRI.mWM)
          : NS_UNCONSTRAINEDSIZE;

  if (IsRowSubgrid() && contentBoxBSize == NS_UNCONSTRAINEDSIZE) {
    // Our rows are the parent grid's rows, and IntrinsicISize() gave us their
    // size as our percentage basis. If it's indefinite, the parent hasn't
    // resolved them yet: we're being measured as part of its column sizing,
    // and resolving the rows here would recurse back into it.
    return gridRI.mCols.TotalTrackSizeWithoutAlignment(this);
  }

  // Resolve row sizes so that when we re-resolve the column sizes, grid items
  // with percent-valued block-sizes (and aspect ratios) have definite row
  // sizes as the percentage basis. Their resolved block-size can then
  // transfer to the inline-axis, contributing correctly to the grid
  // container's intrinsic inline-size.
  gridRI.CalculateTrackSizesForAxis(LogicalAxis::Block, grid, contentBoxBSize,
                                    SizingConstraint::NoConstraint);

  // Invalidate the column sizes before re-resolving them.
  gridRI.InvalidateTrackSizesForAxis(LogicalAxis::Inline);

  // Re-resolve the column sizes, using the resolved row sizes established
  // above. See 12.1.3 of the Grid Sizing Algorithm for more scenarios where
  // re-resolving the column sizes is necessary:
  // https://drafts.csswg.org/css-grid-2/#algo-grid-sizing
  gridRI.CalculateTrackSizesForAxis(LogicalAxis::Inline, grid,
                                    NS_UNCONSTRAINEDSIZE, constraint);

  return gridRI.mCols.TotalTrackSizeWithoutAlignment(this);
}
