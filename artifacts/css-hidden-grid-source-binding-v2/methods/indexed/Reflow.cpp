void nsGridContainerFrame::Reflow(nsPresContext* aPresContext,
                                  ReflowOutput& aDesiredSize,
                                  const ReflowInput& aReflowInput,
                                  nsReflowStatus& aStatus) {
  NormalizeChildLists();

  if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      !GetNextContinuation()) {
    return;
  }

  MarkInReflow();
  DO_GLOBAL_REFLOW_COUNT("nsGridContainerFrame");
  MOZ_ASSERT(aStatus.IsEmpty(), "Caller should pass a fresh reflow status!");

  GRID_LOG("Reflow grid container frame %p", this);

  if (IsFrameTreeTooDeep(aReflowInput, aDesiredSize, aStatus)) {
    return;
  }

#ifdef DEBUG
  mDidPushItemsBitMayLie = false;
  SanityCheckChildListsBeforeReflow();
#endif  // DEBUG

  for (auto& perAxisBaseline : mBaseline) {
    for (auto& baseline : perAxisBaseline) {
      baseline = NS_INTRINSIC_ISIZE_UNKNOWN;
    }
  }

  const nsStylePosition* stylePos = aReflowInput.mStylePosition;
  auto prevInFlow = static_cast<nsGridContainerFrame*>(GetPrevInFlow());
  if (MOZ_LIKELY(!prevInFlow)) {
    InitImplicitNamedAreas(stylePos);
  } else {
    MOZ_ASSERT(prevInFlow->HasAnyStateBits(kIsSubgridBits) ==
                   HasAnyStateBits(kIsSubgridBits),
               "continuations should have same kIsSubgridBits");
  }
  GridReflowInput gridRI(this, aReflowInput);
  if (gridRI.mIter.ItemsAreAlreadyInOrder()) {
    AddStateBits(NS_STATE_GRID_NORMAL_FLOW_CHILDREN_IN_CSS_ORDER);
  } else {
    RemoveStateBits(NS_STATE_GRID_NORMAL_FLOW_CHILDREN_IN_CSS_ORDER);
  }
  if (gridRI.mIter.AtEnd() || aReflowInput.mStyleDisplay->IsContainLayout()) {
    // We have no grid items, or we're layout-contained. So, we have no
    // baseline, and our parent should synthesize a baseline if needed.
    AddStateBits(NS_STATE_GRID_SYNTHESIZE_BASELINE);
  } else {
    RemoveStateBits(NS_STATE_GRID_SYNTHESIZE_BASELINE);
  }
  const nscoord computedBSize = aReflowInput.ComputedBSize();
  const nscoord computedISize = aReflowInput.ComputedISize();

  // XXX Technically incorrect: 'contain-intrinsic-block-size: none' is
  // treated as 0, ignoring our row sizes, when really we should use them but
  // *they* should be computed as if we had no children. To be fixed in bug
  // 1488878.
  const Maybe<nscoord> containIntrinsicBSize =
      aReflowInput.mFrame->ContainIntrinsicBSize();
  const WritingMode& wm = gridRI.mWM;

  nscoord consumedBSize = 0;
  nscoord contentBSize = 0;
  if (MOZ_LIKELY(!prevInFlow)) {
    Grid grid;
    if (MOZ_LIKELY(!IsSubgrid())) {
      RepeatTrackSizingInput repeatSizing(aReflowInput.ComputedMinSize(),
                                          aReflowInput.ComputedSize(),
                                          aReflowInput.ComputedMaxSize());
      grid.PlaceGridItems(gridRI, repeatSizing);
    } else {
      auto* subgrid = GetProperty(Subgrid::Prop());
      MOZ_ASSERT(subgrid, "an ancestor forgot to call PlaceGridItems?");
      gridRI.mGridItems = subgrid->mGridItems.Clone();
      gridRI.mAbsPosItems = subgrid->mAbsPosItems.Clone();
      grid.mGridColEnd = subgrid->mGridColEnd;
      grid.mGridRowEnd = subgrid->mGridRowEnd;
    }

    // Resolve the column sizes with the grid container's inline size.
    // 12.1.1: https://drafts.csswg.org/css-grid-2/#algo-grid-sizing
    gridRI.CalculateTrackSizesForAxis(LogicalAxis::Inline, grid, computedISize,
                                      SizingConstraint::NoConstraint);

    nscoord bSizeForResolvingRowSizes = ComputeBSizeForResolvingRowSizes(
        gridRI, computedBSize, containIntrinsicBSize);

    // Resolve the row sizes with the determined bSizeForResolvingRowSizes.
    // 12.1.2: https://drafts.csswg.org/css-grid-2/#algo-grid-sizing
    //
    // If bSizeForResolvingRowSizes is unconstrained, that's fine. It forces
    // percent-valued row sizes to be treated as 'auto', yielding an intrinsic
    // content block-size needed later to *actually* resolve percent-valued row
    // gaps and row sizes.
    gridRI.CalculateTrackSizesForAxis(LogicalAxis::Block, grid,
                                      bSizeForResolvingRowSizes,
                                      SizingConstraint::NoConstraint);

    // Invalidate the column sizes before re-resolving them.
    gridRI.InvalidateTrackSizesForAxis(LogicalAxis::Inline);

    // Re-resolve the column sizes.
    // 12.1.3: https://drafts.csswg.org/css-grid-2/#algo-grid-sizing
    gridRI.CalculateTrackSizesForAxis(LogicalAxis::Inline, grid, computedISize,
                                      SizingConstraint::NoConstraint);

    // If our bSizeForResolvingRowSizes is still indefinite, replace it with
    // the sum of the row sizes we just resolved, then re-resolve the row
    // sizes against that value. We skip this for masonry, which doesn't need
    // two-pass row sizes resolution.
    if (bSizeForResolvingRowSizes == NS_UNCONSTRAINEDSIZE && !IsRowMasonry()) {
      bSizeForResolvingRowSizes =
          std::max(gridRI.mRows.TotalTrackSizeWithoutAlignment(this),
                   gridRI.mReflowInput->ComputedMinBSize());

      NS_ASSERTION(bSizeForResolvingRowSizes != NS_UNCONSTRAINEDSIZE,
                   "The block-size for re-resolving the row sizes should be "
                   "definite in non-masonry layout!");

      // Invalidate the row sizes before re-resolving them.
      gridRI.InvalidateTrackSizesForAxis(LogicalAxis::Block);

      // Re-resolve the row sizes.
      // 12.1.4: https://drafts.csswg.org/css-grid-2/#algo-grid-sizing
      gridRI.CalculateTrackSizesForAxis(LogicalAxis::Block, grid,
                                        bSizeForResolvingRowSizes,
                                        SizingConstraint::NoConstraint);
    }

    if (computedBSize == NS_UNCONSTRAINEDSIZE ||
        aReflowInput.ShouldApplyAutomaticMinimumOnBlockAxis()) {
      // We either have an unconstrained block-size, or we have a definite
      // block-size derived from the inline-size (transferred via aspect-ratio)
      // and need to apply the automatic content-based minimum sizes on the
      // block-axis. In both case, we need to compute the intrinsic
      // content block-size.
      contentBSize = ComputeIntrinsicContentBSize(gridRI, computedBSize,
                                                  bSizeForResolvingRowSizes,
                                                  containIntrinsicBSize);
    }
  } else {
    consumedBSize = CalcAndCacheConsumedBSize();
    gridRI.InitializeForContinuation(this, consumedBSize);
    if (containIntrinsicBSize) {
      contentBSize = *containIntrinsicBSize;
    } else {
      const uint32_t numRows = gridRI.mRows.mSizes.Length();
      contentBSize =
          gridRI.mRows.GridLineEdge(numRows, GridLineSide::AfterGridGap);
    }
  }
  if (computedBSize == NS_UNCONSTRAINEDSIZE) {
    contentBSize = aReflowInput.ApplyMinMaxBSize(contentBSize);
  } else if (aReflowInput.ShouldApplyAutomaticMinimumOnBlockAxis()) {
    contentBSize = aReflowInput.ApplyMinMaxBSize(contentBSize);
    contentBSize = std::max(contentBSize, computedBSize);
  } else {
    contentBSize = computedBSize;
  }
  if (contentBSize != NS_UNCONSTRAINEDSIZE) {
    contentBSize = std::max(contentBSize - consumedBSize, 0);
  }
  auto& bp = gridRI.mBorderPadding;
  LogicalRect contentArea(wm, bp.IStart(wm), bp.BStart(wm), computedISize,
                          contentBSize);

  if (!prevInFlow) {
    const auto& rowSizes = gridRI.mRows.mSizes;
    if (!IsRowSubgrid()) {
      if (!gridRI.mRows.mIsMasonry) {
        // Apply 'align-content' to the grid.
        auto alignment = stylePos->mAlignContent;
        gridRI.mRows.AlignJustifyContent(stylePos, alignment, wm, contentBSize,
                                         false);
      }
    } else {
      if (computedBSize == NS_UNCONSTRAINEDSIZE) {
        contentBSize = gridRI.mRows.GridLineEdge(rowSizes.Length(),
                                                 GridLineSide::BeforeGridGap);
        contentArea.BSize(wm) = std::max(contentBSize, nscoord(0));
      }
    }
    // Save the final row sizes for use by subgrids, if needed.
    if (HasSubgridItems() || IsSubgrid()) {
      StoreUsedTrackSizes(LogicalAxis::Block, rowSizes);
    }
  }

  nsSize containerSize = contentArea.Size(wm).GetPhysicalSize(wm);
  bool repositionChildren = false;
  if (containerSize.width == NS_UNCONSTRAINEDSIZE && wm.IsVerticalRL()) {
    // Note that writing-mode:vertical-rl is the only case where the block
    // logical direction progresses in a negative physical direction, and
    // therefore block-dir coordinate conversion depends on knowing the width
    // of the coordinate space in order to translate between the logical and
    // physical origins.
    //
    // A masonry axis size may be unconstrained, otherwise in a regular grid
    // our intrinsic size is always known by now.  We'll re-position
    // the children below once our size is known.
    repositionChildren = true;
    containerSize.width = 0;
  }
  containerSize.width += bp.LeftRight(wm);
  containerSize.height += bp.TopBottom(wm);

  contentBSize =
      ReflowChildren(gridRI, contentArea, containerSize, aDesiredSize, aStatus);
  if (Style()->GetPseudoType() == PseudoStyleType::MozScrolledContent) {
    // Per spec, the grid area is included in a grid container's scrollable
    // overflow region [1], as well as the padding on the end-edge sides that
    // would satisfy the requirements of 'place-content: end' alignment [2].
    //
    // Note that we include the padding from all sides of the grid area, not
    // just the end sides; this is fine because the grid area is relative to our
    // content-box origin. The inflated bounds won't go beyond our padding-box
    // edges on the start sides.
    //
    // The margin areas of grid item boxes are also included in the scrollable
    // overflow region [2].
    //
    // [1] https://drafts.csswg.org/css-grid-2/#overflow
    // [2] https://drafts.csswg.org/css-overflow-3/#scrollable

    // Synthesize a grid area covering all columns and rows, and compute its
    // rect relative to our border-box.
    //
    // Note: the grid columns and rows exist only if there is an explicit grid;
    // or when an implicit grid is needed to place any grid items. See
    // nsGridContainerFrame::Grid::PlaceGridItems().
    const auto numCols = static_cast<int32_t>(gridRI.mCols.mSizes.Length());
    const auto numRows = static_cast<int32_t>(gridRI.mRows.mSizes.Length());
    if (numCols > 0 && numRows > 0) {
      const GridArea gridArea(LineRange(0, numCols), LineRange(0, numRows));
      const LogicalRect gridAreaRect =
          gridRI.ContainingBlockFor(gridArea) +
          LogicalPoint(wm, bp.IStart(wm), bp.BStart(wm));

      MOZ_ASSERT(bp == aReflowInput.ComputedLogicalPadding(wm),
                 "A scrolled inner frame shouldn't have any border!");
      const LogicalMargin& padding = bp;
      nsRect physicalGridAreaRectWithPadding =
          gridAreaRect.GetPhysicalRect(wm, containerSize);
      physicalGridAreaRectWithPadding.Inflate(padding.GetPhysicalMargin(wm));
      aDesiredSize.mOverflowAreas.UnionAllWith(physicalGridAreaRectWithPadding);
    }

    nsRect gridItemMarginBoxBounds;
    for (const auto& item : gridRI.mGridItems) {
      gridItemMarginBoxBounds =
          gridItemMarginBoxBounds.Union(item.mFrame->GetMarginRect());
    }
    aDesiredSize.mOverflowAreas.UnionAllWith(gridItemMarginBoxBounds);
  }
  ReflowAbsoluteChildren(gridRI, contentArea, contentBSize, aDesiredSize,
                         aStatus);
  contentBSize = std::max(contentBSize - consumedBSize, 0);

  // Skip our block-end border if we're INCOMPLETE.
  if (!aStatus.IsComplete() && !gridRI.mSkipSides.BEnd() &&
      StyleBorder()->mBoxDecorationBreak != StyleBoxDecorationBreak::Clone) {
    bp.BEnd(wm) = nscoord(0);
  }

  LogicalSize desiredSize(wm, computedISize + bp.IStartEnd(wm),
                          contentBSize + bp.BStartEnd(wm));
  aDesiredSize.SetSize(wm, desiredSize);
  nsRect frameRect(0, 0, aDesiredSize.Width(), aDesiredSize.Height());
  aDesiredSize.mOverflowAreas.UnionAllWith(frameRect);

  if (repositionChildren) {
    nsPoint physicalDelta(aDesiredSize.Width() - bp.LeftRight(wm), 0);
    for (const auto& item : gridRI.mGridItems) {
      auto* child = item.mFrame;
      child->MovePositionBy(physicalDelta);
      ConsiderChildOverflow(aDesiredSize.mOverflowAreas, child);
    }
  }

  // TODO: fix align-tracks alignment in fragments
  if ((IsRowMasonry() && !prevInFlow) || IsColMasonry()) {
    gridRI.AlignJustifyTracksInMasonryAxis(contentArea.Size(wm),
                                           aDesiredSize.PhysicalSize());
  }

  // Convert INCOMPLETE -> OVERFLOW_INCOMPLETE and zero bsize if we're an OC.
  if (HasAnyStateBits(NS_FRAME_IS_OVERFLOW_CONTAINER)) {
    if (!aStatus.IsComplete()) {
      aStatus.SetOverflowIncomplete();
      aStatus.SetNextInFlowNeedsReflow();
    }
    contentBSize = 0;
    desiredSize.BSize(wm) = contentBSize + bp.BStartEnd(wm);
    aDesiredSize.SetSize(wm, desiredSize);
  }

  if (!gridRI.mInFragmentainer) {
    MOZ_ASSERT(gridRI.mIter.IsValid());
    auto sz = frameRect.Size();
    CalculateBaselines(BaselineSet::eBoth, &gridRI.mIter, &gridRI.mGridItems,
                       gridRI.mCols, 0, gridRI.mCols.mSizes.Length(), wm, sz,
                       bp.IStart(wm), bp.IEnd(wm), desiredSize.ISize(wm));
    CalculateBaselines(BaselineSet::eBoth, &gridRI.mIter, &gridRI.mGridItems,
                       gridRI.mRows, 0, gridRI.mRows.mSizes.Length(), wm, sz,
                       bp.BStart(wm), bp.BEnd(wm), desiredSize.BSize(wm));
  } else {
    // Only compute 'first baseline' if this fragment contains the first track.
    // XXXmats maybe remove this condition? bug 1306499
    BaselineSet baselines = BaselineSet::eNone;
    if (gridRI.mStartRow == 0 &&
        gridRI.mStartRow != gridRI.mNextFragmentStartRow) {
      baselines = BaselineSet::eFirst;
    }
    // Only compute 'last baseline' if this fragment contains the last track.
    // XXXmats maybe remove this condition? bug 1306499
    uint32_t len = gridRI.mRows.mSizes.Length();
    if (gridRI.mStartRow != len && gridRI.mNextFragmentStartRow == len) {
      baselines = BaselineSet(baselines | BaselineSet::eLast);
    }
    Maybe<CSSOrderAwareFrameIterator> iter;
    Maybe<nsTArray<GridItemInfo>> gridItems;
    if (baselines != BaselineSet::eNone) {
      // We need to create a new iterator and GridItemInfo array because we
      // might have pushed some children at this point.
      // Even if gridRI.mIter is invalid, we can reuse its
      // state about order to optimize initialization of the new iterator.
      // An ordered child list can't become unordered by pushing frames.
      // An unordered list can become ordered in a number of cases, but we
      // ignore that here and guess that the child list is still unordered.
      // XXX this is O(n^2) in the number of items in this fragment: bug 1306705
      using Filter = CSSOrderAwareFrameIterator::ChildFilter;
      using Order = CSSOrderAwareFrameIterator::OrderState;
      bool ordered = gridRI.mIter.ItemsAreAlreadyInOrder();
      auto orderState = ordered ? Order::Ordered : Order::Unordered;
      iter.emplace(this, FrameChildListID::Principal, Filter::SkipPlaceholders,
                   orderState);
      gridItems.emplace();
      for (; !iter->AtEnd(); iter->Next()) {
        auto child = **iter;
        for (const auto& info : gridRI.mGridItems) {
          if (info.mFrame == child) {
            gridItems->AppendElement(info);
          }
        }
      }
    }
    auto sz = frameRect.Size();
    CalculateBaselines(baselines, iter.ptrOr(nullptr), gridItems.ptrOr(nullptr),
                       gridRI.mCols, 0, gridRI.mCols.mSizes.Length(), wm, sz,
                       bp.IStart(wm), bp.IEnd(wm), desiredSize.ISize(wm));
    CalculateBaselines(baselines, iter.ptrOr(nullptr), gridItems.ptrOr(nullptr),
                       gridRI.mRows, gridRI.mStartRow,
                       gridRI.mNextFragmentStartRow, wm, sz, bp.BStart(wm),
                       bp.BEnd(wm), desiredSize.BSize(wm));
  }

  if (HasAnyStateBits(NS_STATE_GRID_COMPUTED_INFO)) {
    // This state bit will never be cleared, since reflow can be called
    // multiple times in fragmented grids, and it's challenging to scope
    // the bit to only that sequence of calls. This is relatively harmless
    // since this bit is only set by accessing a ChromeOnly property, and
    // therefore can't unduly slow down normal web browsing.

    // Clear our GridFragmentInfo property, which might be holding a stale
    // dom::Grid object built from previously-computed info. This will
    // ensure that the next call to GetGridFragments will create a new one.
    if (mozilla::dom::Grid* grid = TakeProperty(GridFragmentInfo())) {
      grid->ForgetFrame();
    }

    // Now that we know column and row sizes and positions, set
    // the ComputedGridTrackInfo and related properties

    const auto* subgrid = GetProperty(Subgrid::Prop());
    const auto* subgridColRange =
        subgrid && IsColSubgrid() ? &subgrid->SubgridCols() : nullptr;

    LineNameMap colLineNameMap(gridRI.mGridStyle, GetImplicitNamedAreas(),
                               gridRI.mColFunctions, nullptr, subgridColRange);
    uint32_t colTrackCount = gridRI.mCols.mSizes.Length();
    nsTArray<nscoord> colTrackPositions(colTrackCount);
    nsTArray<nscoord> colTrackSizes(colTrackCount);
    nsTArray<uint32_t> colTrackStates(colTrackCount);
    nsTArray<bool> colRemovedRepeatTracks(
        gridRI.mColFunctions.mRemovedRepeatTracks.Clone());
    uint32_t col = 0;
    for (const TrackSize& sz : gridRI.mCols.mSizes) {
      colTrackPositions.AppendElement(sz.mPosition);
      colTrackSizes.AppendElement(sz.mBase);
      bool isRepeat = ((col >= gridRI.mColFunctions.mRepeatAutoStart) &&
                       (col < gridRI.mColFunctions.mRepeatAutoEnd));
      colTrackStates.AppendElement(
          isRepeat ? (uint32_t)mozilla::dom::GridTrackState::Repeat
                   : (uint32_t)mozilla::dom::GridTrackState::Static);

      col++;
    }
    // Get the number of explicit tracks first. The order of argument evaluation
    // is implementation-defined. We should be OK here because colTrackSizes is
    // taken by rvalue, but computing the size first prevents any changes in the
    // argument types of the constructor from breaking this.
    const uint32_t numColExplicitTracks =
        IsColSubgrid() ? colTrackSizes.Length()
                       : gridRI.mColFunctions.NumExplicitTracks();
    ComputedGridTrackInfo* colInfo = new ComputedGridTrackInfo(
        gridRI.mColFunctions.mExplicitGridOffset, numColExplicitTracks, 0, col,
        std::move(colTrackPositions), std::move(colTrackSizes),
        std::move(colTrackStates), std::move(colRemovedRepeatTracks),
        gridRI.mColFunctions.mRepeatAutoStart,
        colLineNameMap.GetResolvedLineNamesForComputedGridTrackInfo(),
        IsColSubgrid(), IsColMasonry());
    SetProperty(GridColTrackInfo(), colInfo);

    const auto* subgridRowRange =
        subgrid && IsRowSubgrid() ? &subgrid->SubgridRows() : nullptr;
    LineNameMap rowLineNameMap(gridRI.mGridStyle, GetImplicitNamedAreas(),
                               gridRI.mRowFunctions, nullptr, subgridRowRange);
    uint32_t rowTrackCount = gridRI.mRows.mSizes.Length();
    nsTArray<nscoord> rowTrackPositions(rowTrackCount);
    nsTArray<nscoord> rowTrackSizes(rowTrackCount);
    nsTArray<uint32_t> rowTrackStates(rowTrackCount);
    nsTArray<bool> rowRemovedRepeatTracks(
        gridRI.mRowFunctions.mRemovedRepeatTracks.Clone());
    uint32_t row = 0;
    for (const TrackSize& sz : gridRI.mRows.mSizes) {
      rowTrackPositions.AppendElement(sz.mPosition);
      rowTrackSizes.AppendElement(sz.mBase);
      bool isRepeat = ((row >= gridRI.mRowFunctions.mRepeatAutoStart) &&
                       (row < gridRI.mRowFunctions.mRepeatAutoEnd));
      rowTrackStates.AppendElement(
          isRepeat ? (uint32_t)mozilla::dom::GridTrackState::Repeat
                   : (uint32_t)mozilla::dom::GridTrackState::Static);

      row++;
    }
    // Get the number of explicit tracks first. The order of argument evaluation
    // is implementation-defined. We should be OK here because colTrackSizes is
    // taken by rvalue, but computing the size first prevents any changes in the
    // argument types of the constructor from breaking this.
    const uint32_t numRowExplicitTracks =
        IsRowSubgrid() ? rowTrackSizes.Length()
                       : gridRI.mRowFunctions.NumExplicitTracks();
    // Row info has to accommodate fragmentation of the grid, which may happen
    // in later calls to Reflow. For now, presume that no more fragmentation
    // will occur.
    ComputedGridTrackInfo* rowInfo = new ComputedGridTrackInfo(
        gridRI.mRowFunctions.mExplicitGridOffset, numRowExplicitTracks,
        gridRI.mStartRow, row, std::move(rowTrackPositions),
        std::move(rowTrackSizes), std::move(rowTrackStates),
        std::move(rowRemovedRepeatTracks),
        gridRI.mRowFunctions.mRepeatAutoStart,
        rowLineNameMap.GetResolvedLineNamesForComputedGridTrackInfo(),
        IsRowSubgrid(), IsRowMasonry());
    SetProperty(GridRowTrackInfo(), rowInfo);

    if (prevInFlow) {
      // This frame is fragmenting rows from a previous frame, so patch up
      // the prior GridRowTrackInfo with a new end row.

      // FIXME: This can be streamlined and/or removed when bug 1151204 lands.

      ComputedGridTrackInfo* priorRowInfo =
          prevInFlow->GetProperty(GridRowTrackInfo());

      // Adjust track positions based on the first track in this fragment.
      if (priorRowInfo->mPositions.Length() >
          priorRowInfo->mStartFragmentTrack) {
        nscoord delta =
            priorRowInfo->mPositions[priorRowInfo->mStartFragmentTrack];
        for (nscoord& pos : priorRowInfo->mPositions) {
          pos -= delta;
        }
      }

      ComputedGridTrackInfo* revisedPriorRowInfo = new ComputedGridTrackInfo(
          priorRowInfo->mNumLeadingImplicitTracks,
          priorRowInfo->mNumExplicitTracks, priorRowInfo->mStartFragmentTrack,
          gridRI.mStartRow, std::move(priorRowInfo->mPositions),
          std::move(priorRowInfo->mSizes), std::move(priorRowInfo->mStates),
          std::move(priorRowInfo->mRemovedRepeatTracks),
          priorRowInfo->mRepeatFirstTrack,
          std::move(priorRowInfo->mResolvedLineNames), priorRowInfo->mIsSubgrid,
          priorRowInfo->mIsMasonry);
      prevInFlow->SetProperty(GridRowTrackInfo(), revisedPriorRowInfo);
    }

    // Generate the line info properties. We need to provide the number of
    // repeat tracks produced in the reflow. Only explicit names are assigned
    // to lines here; the mozilla::dom::GridLines class will later extract
    // implicit names from grid areas and assign them to the appropriate lines.

    auto& colFunctions = gridRI.mColFunctions;

    // Generate column lines first.
    uint32_t capacity = gridRI.mCols.mSizes.Length();
    nsTArray<nsTArray<RefPtr<nsAtom>>> columnLineNames(capacity);
    for (col = 0; col <= gridRI.mCols.mSizes.Length(); col++) {
      // Offset col by the explicit grid offset, to get the original names.
      nsTArray<RefPtr<nsAtom>> explicitNames =
          colLineNameMap.GetExplicitLineNamesAtIndex(
              col - colFunctions.mExplicitGridOffset);

      columnLineNames.EmplaceBack(std::move(explicitNames));
    }
    // Get the explicit names that follow a repeat auto declaration.
    nsTArray<RefPtr<nsAtom>> colNamesFollowingRepeat;
    nsTArray<RefPtr<nsAtom>> colBeforeRepeatAuto;
    nsTArray<RefPtr<nsAtom>> colAfterRepeatAuto;
    // Note: the following is only used for a non-subgridded axis.
    if (colLineNameMap.HasRepeatAuto()) {
      MOZ_ASSERT(!colFunctions.mTemplate.IsSubgrid());
      // The line name list after the repeatAutoIndex holds the line names
      // for the first explicit line after the repeat auto declaration.
      uint32_t repeatAutoEnd = colLineNameMap.RepeatAutoStart() + 1;
      for (auto* list : colLineNameMap.ExpandedLineNames()[repeatAutoEnd]) {
        for (auto& name : list->AsSpan()) {
          colNamesFollowingRepeat.AppendElement(name.AsAtom());
        }
      }
      auto names = colLineNameMap.TrackAutoRepeatLineNames();
      for (auto& name : names[0].AsSpan()) {
        colBeforeRepeatAuto.AppendElement(name.AsAtom());
      }
      for (auto& name : names[1].AsSpan()) {
        colAfterRepeatAuto.AppendElement(name.AsAtom());
      }
    }

    ComputedGridLineInfo* columnLineInfo = new ComputedGridLineInfo{
        std::move(columnLineNames), std::move(colBeforeRepeatAuto),
        std::move(colAfterRepeatAuto), std::move(colNamesFollowingRepeat)};
    SetProperty(GridColumnLineInfo(), columnLineInfo);

    // Generate row lines next.
    auto& rowFunctions = gridRI.mRowFunctions;
    capacity = gridRI.mRows.mSizes.Length();
    nsTArray<nsTArray<RefPtr<nsAtom>>> rowLineNames(capacity);
    for (row = 0; row <= gridRI.mRows.mSizes.Length(); row++) {
      // Offset row by the explicit grid offset, to get the original names.
      nsTArray<RefPtr<nsAtom>> explicitNames =
          rowLineNameMap.GetExplicitLineNamesAtIndex(
              row - rowFunctions.mExplicitGridOffset);
      rowLineNames.EmplaceBack(std::move(explicitNames));
    }
    // Get the explicit names that follow a repeat auto declaration.
    nsTArray<RefPtr<nsAtom>> rowNamesFollowingRepeat;
    nsTArray<RefPtr<nsAtom>> rowBeforeRepeatAuto;
    nsTArray<RefPtr<nsAtom>> rowAfterRepeatAuto;
    // Note: the following is only used for a non-subgridded axis.
    if (rowLineNameMap.HasRepeatAuto()) {
      MOZ_ASSERT(!rowFunctions.mTemplate.IsSubgrid());
      // The line name list after the repeatAutoIndex holds the line names
      // for the first explicit line after the repeat auto declaration.
      uint32_t repeatAutoEnd = rowLineNameMap.RepeatAutoStart() + 1;
      for (auto* list : rowLineNameMap.ExpandedLineNames()[repeatAutoEnd]) {
        for (auto& name : list->AsSpan()) {
          rowNamesFollowingRepeat.AppendElement(name.AsAtom());
        }
      }
      auto names = rowLineNameMap.TrackAutoRepeatLineNames();
      for (auto& name : names[0].AsSpan()) {
        rowBeforeRepeatAuto.AppendElement(name.AsAtom());
      }
      for (auto& name : names[1].AsSpan()) {
        rowAfterRepeatAuto.AppendElement(name.AsAtom());
      }
    }

    ComputedGridLineInfo* rowLineInfo = new ComputedGridLineInfo{
        std::move(rowLineNames), std::move(rowBeforeRepeatAuto),
        std::move(rowAfterRepeatAuto), std::move(rowNamesFollowingRepeat)};
    SetProperty(GridRowLineInfo(), rowLineInfo);

    // Generate area info for explicit areas. Implicit areas are handled
    // elsewhere.
    if (!gridRI.mGridStyle->mGridTemplateAreas.IsNone()) {
      auto* areas = new StyleOwnedSlice<NamedArea>(
          gridRI.mGridStyle->mGridTemplateAreas.AsAreas()->areas);
      SetProperty(ExplicitNamedAreasProperty(), areas);
    } else {
      RemoveProperty(ExplicitNamedAreasProperty());
    }
  }

  if (!prevInFlow) {
    if (!aStatus.IsFullyComplete()) {
      SharedGridData* sharedGridData =
          GetOrCreateDeletableProperty(SharedGridData::Prop());
      sharedGridData->mCols.mSizes = std::move(gridRI.mCols.mSizes);
      sharedGridData->mCols.mContentBoxSize = gridRI.mCols.mContentBoxSize;
      sharedGridData->mCols.mBaselineSubtreeAlign =
          gridRI.mCols.mBaselineSubtreeAlign;
      sharedGridData->mCols.mIsMasonry = gridRI.mCols.mIsMasonry;
      sharedGridData->mRows.mSizes = std::move(gridRI.mRows.mSizes);
      // Save the original row grid sizes and gaps so we can restore them later
      // in GridReflowInput::Initialize for the continuations.
      auto& origRowData = sharedGridData->mOriginalRowData;
      origRowData.ClearAndRetainStorage();
      origRowData.SetCapacity(sharedGridData->mRows.mSizes.Length());
      nscoord prevTrackEnd = 0;
      for (auto& sz : sharedGridData->mRows.mSizes) {
        SharedGridData::RowData data = {sz.mBase, sz.mPosition - prevTrackEnd};
        origRowData.AppendElement(data);
        prevTrackEnd = sz.mPosition + sz.mBase;
      }
      sharedGridData->mRows.mContentBoxSize = gridRI.mRows.mContentBoxSize;
      sharedGridData->mRows.mBaselineSubtreeAlign =
          gridRI.mRows.mBaselineSubtreeAlign;
      sharedGridData->mRows.mIsMasonry = gridRI.mRows.mIsMasonry;
      sharedGridData->mGridItems = std::move(gridRI.mGridItems);
      sharedGridData->mAbsPosItems = std::move(gridRI.mAbsPosItems);

      sharedGridData->mGenerateComputedGridInfo =
          HasAnyStateBits(NS_STATE_GRID_COMPUTED_INFO);
    } else if (!GetNextInFlow()) {
      RemoveProperty(SharedGridData::Prop());
    }
  }

  FinishAndStoreOverflow(&aDesiredSize);
}
