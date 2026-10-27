void nsGridContainerFrame::Tracks::InitializeItemBaselines(
    GridReflowInput& aGridRI, nsTArray<GridItemInfo>& aGridItems) {
  MOZ_ASSERT(!mIsMasonry);
  if (aGridRI.mFrame->IsSubgrid(mAxis)) {
    // A grid container's subgridded axis doesn't have a baseline.
    return;
  }

  nsTArray<ItemBaselineData> firstBaselineItems;
  nsTArray<ItemBaselineData> lastBaselineItems;
  const WritingMode containerWM = aGridRI.mWM;
  ComputedStyle* containerStyle = aGridRI.mFrame->Style();

  for (GridItemInfo& gridItem : aGridItems) {
    if (gridItem.IsSubgrid(mAxis)) {
      // A subgrid itself is never baseline-aligned.
      continue;
    }

    nsIFrame* child = gridItem.mFrame;
    uint32_t baselineTrack = kAutoLine;
    auto state = ItemState(0);
    const auto childWM = child->GetWritingMode();

    const bool isOrthogonal = containerWM.IsOrthogonalTo(childWM);
    const bool isInlineAxis = mAxis == LogicalAxis::Inline;  // i.e. columns
    const bool itemHasBaselineParallelToTrack = isInlineAxis == isOrthogonal;

    // [align|justify]-self:[last ]baseline.
    auto selfAlignment =
        child->StylePosition()->UsedSelfAlignment(mAxis, containerStyle);
    selfAlignment &= ~StyleAlignFlags::FLAG_BITS;
    if (selfAlignment == StyleAlignFlags::BASELINE) {
      state |= ItemState::eFirstBaseline | ItemState::eSelfBaseline;
    } else if (selfAlignment == StyleAlignFlags::LAST_BASELINE) {
      state |= ItemState::eLastBaseline | ItemState::eSelfBaseline;
    }

    // https://drafts.csswg.org/css-align-3/#baseline-align-content
    // Baseline content-alignment can only apply if the align-content axis is
    // parallel with the box’s block axis; otherwise the fallback alignment is
    // used.
    if (!isInlineAxis) {
      // Handle align-content:[last ]baseline (if present)
      auto alignContent = child->StylePosition()->mAlignContent.primary;
      alignContent &= ~StyleAlignFlags::FLAG_BITS;
      if (alignContent == StyleAlignFlags::BASELINE ||
          alignContent == StyleAlignFlags::LAST_BASELINE) {
        const auto selfAlignEdge = alignContent == StyleAlignFlags::BASELINE
                                       ? StyleAlignFlags::SELF_START
                                       : StyleAlignFlags::SELF_END;
        bool validCombo = selfAlignment == StyleAlignFlags::NORMAL ||
                          selfAlignment == StyleAlignFlags::STRETCH ||
                          selfAlignment == selfAlignEdge;
        if (!validCombo) {
          // We're doing alignment in the axis that's orthogonal to mAxis here.
          LogicalAxis alignAxis = GetOrthogonalAxis(mAxis);
          // |sameSide| is true if the container's start side in this axis is
          // the same as the child's start side, in the child's parallel axis.
          bool sameSide =
              containerWM.ParallelAxisStartsOnSameSide(alignAxis, childWM);
          if (selfAlignment == StyleAlignFlags::LEFT) {
            selfAlignment = containerWM.IsBidiLTR() ? StyleAlignFlags::START
                                                    : StyleAlignFlags::END;
          } else if (selfAlignment == StyleAlignFlags::RIGHT) {
            selfAlignment = StyleAlignFlags::START;
          }

          if (selfAlignment == StyleAlignFlags::START ||
              selfAlignment == StyleAlignFlags::FLEX_START) {
            validCombo =
                sameSide == (alignContent == StyleAlignFlags::BASELINE);
          } else if (selfAlignment == StyleAlignFlags::END ||
                     selfAlignment == StyleAlignFlags::FLEX_END) {
            validCombo =
                sameSide == (alignContent == StyleAlignFlags::LAST_BASELINE);
          }
        }
        if (validCombo) {
          const GridArea& area = gridItem.mArea;
          if (alignContent == StyleAlignFlags::BASELINE) {
            state |= ItemState::eFirstBaseline | ItemState::eContentBaseline;
            baselineTrack = area.mRows.mStart;
          } else if (alignContent == StyleAlignFlags::LAST_BASELINE) {
            state |= ItemState::eLastBaseline | ItemState::eContentBaseline;
            baselineTrack = area.mRows.mEnd - 1;
          }
        }
      }
    }

    if (state & ItemState::eIsBaselineAligned) {
      // The item is baseline aligned, so calculate the baseline sharing group.
      // <https://drafts.csswg.org/css-align-3/#baseline-terms>
      bool isFirstBaseline = (state & ItemState::eFirstBaseline) != 0;
      BaselineSharingGroup baselineAlignment = isFirstBaseline
                                                   ? BaselineSharingGroup::First
                                                   : BaselineSharingGroup::Last;
      // Baseline alignment occurs along `mAxis`, but baselines are defined in
      // the orthogonal axis (the axis of the baseline context that defines the
      // baseline sharing group).
      auto baselineWM = WritingMode::DetermineWritingModeForBaselineSynthesis(
          containerWM, childWM, GetOrthogonalAxis(mAxis));

      auto sameSideInBaselineWM =
          containerWM.ParallelAxisStartsOnSameSide(mAxis, baselineWM);
      auto baselineSharingGroup = BaselineSharingGroup::First;
      if (sameSideInBaselineWM != isFirstBaseline) {
        baselineSharingGroup = BaselineSharingGroup::Last;
        state |= ItemState::eLastBaselineSharingGroup;

        baselineTrack = (isInlineAxis ? gridItem.mArea.mCols.mEnd
                                      : gridItem.mArea.mRows.mEnd) -
                        1;
      } else {
        baselineTrack = isInlineAxis ? gridItem.mArea.mCols.mStart
                                     : gridItem.mArea.mRows.mStart;
      }

      // XXXmats if |child| is a descendant of a subgrid then the metrics
      // below needs to account for the accumulated MPB somehow...

      auto* rc = &aGridRI.mRenderingContext;
      // XXX figure out if we can avoid/merge this reflow with the main reflow.
      // XXX (after bug 1174569 is sorted out)
      //
      // XXX How should we handle percentage padding here? (bug 1330866)
      // XXX (see ::ContentContribution and how it deals with percentages)
      // XXX What if the true baseline after line-breaking differs from this
      // XXX hypothetical baseline based on an infinite inline size?
      // XXX Maybe we should just call ::ContentContribution here instead?
      const LogicalSize cbSize = aGridRI.PercentageBasisFor(mAxis, gridItem);
      LogicalSize avail(childWM, INFINITE_ISIZE_COORD, NS_UNCONSTRAINEDSIZE);
      const LogicalAxis inlineAxisInChildWM =
          isOrthogonal ? LogicalAxis::Block : LogicalAxis::Inline;
      const nscoord colSize = cbSize.Size(inlineAxisInChildWM, childWM);
      if (colSize != NS_UNCONSTRAINEDSIZE) {
        avail.Size(inlineAxisInChildWM, childWM) = colSize;
      }
      ::MeasuringReflow(child, aGridRI.mReflowInput, rc, avail, cbSize);

      nsGridContainerFrame* grid = do_QueryFrame(child);
      auto frameSize =
          isInlineAxis ? child->ISize(containerWM) : child->BSize(containerWM);
      auto margin = child->GetLogicalUsedMargin(containerWM);
      auto alignSize =
          frameSize + (isInlineAxis ? margin.IStartEnd(containerWM)
                                    : margin.BStartEnd(containerWM));

      Maybe<nscoord> baseline;
      if (grid) {
        baseline.emplace((isOrthogonal == isInlineAxis)
                             ? grid->GetBBaseline(baselineAlignment)
                             : grid->GetIBaseline(baselineAlignment));
      } else {
        if (itemHasBaselineParallelToTrack) {
          baseline = child->GetNaturalBaselineBOffset(
              childWM, baselineAlignment, BaselineExportContext::Other);
        }

        if (!baseline) {
          // If baseline alignment is specified on a grid item whose size in
          // that axis depends on the size of an intrinsically-sized track, that
          // item does not participate in baseline alignment, and instead uses
          // its fallback alignment as if that were originally specified.
          // https://drafts.csswg.org/css-grid-2/#row-align

          // Check if the item crosses any tracks that are intrinsically sized.
          auto range = gridItem.mArea.LineRangeForAxis(mAxis).Range();
          auto isTrackAutoSize =
              std::find_if(range.begin(), range.end(), [&](auto track) {
                constexpr auto intrinsicSizeFlags =
                    TrackSize::eIntrinsicMinSizing |
                    TrackSize::eIntrinsicMaxSizing |
                    TrackSize::eApplyFitContentClamping |
                    TrackSize::eFlexMaxSizing;
                return (mSizes[track].mState & intrinsicSizeFlags) != 0;
              }) != range.end();

          // If either the track or the item is not auto sized, then the item
          // participates in baseline alignment.
          if (!isTrackAutoSize ||
              !gridItem.IsBSizeDependentOnContainerSize(containerWM)) {
            // We're synthesizing the baseline from the child's border-box
            // (frameSize is the size of the border-box). See:
            // https://drafts.csswg.org/css-align-3/#baseline-export.

            if (containerWM.IsCentralBaseline()) {
              // We want to use the exact same central position within the
              // frame, regardless of which side we're measuring from. To
              // achieve that, we round *up* if we're in the first baseline
              // sharing group, and *down* if we're in the last baseline sharing
              // group.
              const bool isFirstBaselineSharingGroup =
                  baselineSharingGroup == BaselineSharingGroup::First;
              baseline.emplace(frameSize / 2 + (isFirstBaselineSharingGroup
                                                    ? 0
                                                    : frameSize % 2));
            } else {
              // The baseline offset is measured from the block-{start,end} edge
              // of the container, using the block axis of 'baselineWM' (which
              // may differ from the child or container’s writing mode).
              //
              // If we're synthesizing a baseline from the edge nearest to the
              // container's reference side (start for the first baseline group,
              // end for the last), the offset is `0`. Otherwise, it's from the
              // opposite edge, so we use `frameSize`.
              //
              // This logic depends on whether we're in the first or last
              // baseline-sharing group, and whether the line is inverted (e.g.,
              // in vertical-rl mode), which affects which edge is considered
              // the "start" or "end".
              baseline.emplace((isFirstBaseline == baselineWM.IsLineInverted())
                                   ? 0
                                   : frameSize);
            }
          }
        }
      }

      if (baseline) {
        nscoord finalBaseline = *baseline;
        NS_ASSERTION(finalBaseline != NS_INTRINSIC_ISIZE_UNKNOWN,
                     "about to use an unknown baseline");

        nscoord marginAdjust = 0;
        if (baselineSharingGroup == BaselineSharingGroup::First) {
          marginAdjust = isInlineAxis ? margin.IStart(containerWM)
                                      : margin.BStart(containerWM);
        } else {
          marginAdjust = isInlineAxis ? margin.IEnd(containerWM)
                                      : margin.BEnd(containerWM);

          // This flag is used in ::AlignSelf(...) to check whether the item is
          // last baseline aligned, but this flag should go away.
          state |= GridItemInfo::eEndSideBaseline;
        }
        finalBaseline += marginAdjust;

        auto& baselineItems =
            (baselineSharingGroup == BaselineSharingGroup::First)
                ? firstBaselineItems
                : lastBaselineItems;
        baselineItems.AppendElement(ItemBaselineData{
            baselineTrack, finalBaseline, alignSize, &gridItem});
      } else {
        state &= ~ItemState::eAllBaselineBits;
      }

      if (aGridRI.mIsGridIntrinsicSizing) {
        MarkDirtyAfterIntrinsicSizingReflow(child);
      }
    }

    MOZ_ASSERT(
        (state & (ItemState::eFirstBaseline | ItemState::eLastBaseline)) !=
            (ItemState::eFirstBaseline | ItemState::eLastBaseline),
        "first/last baseline bits are mutually exclusive");
    MOZ_ASSERT(
        (state & (ItemState::eSelfBaseline | ItemState::eContentBaseline)) !=
            (ItemState::eSelfBaseline | ItemState::eContentBaseline),
        "*-self and *-content baseline bits are mutually exclusive");
    MOZ_ASSERT(
        !(state & (ItemState::eFirstBaseline | ItemState::eLastBaseline)) ==
            !(state & (ItemState::eSelfBaseline | ItemState::eContentBaseline)),
        "first/last bit requires self/content bit and vice versa");

    gridItem.mState[mAxis] |= state;
    gridItem.mBaselineOffset[mAxis] = nscoord(0);
  }

  if (firstBaselineItems.IsEmpty() && lastBaselineItems.IsEmpty()) {
    return;
  }

  // TODO: CSS Align spec issue - how to align a baseline subtree in a track?
  // https://lists.w3.org/Archives/Public/www-style/2016May/0141.html
  mBaselineSubtreeAlign[BaselineSharingGroup::First] = StyleAlignFlags::START;
  mBaselineSubtreeAlign[BaselineSharingGroup::Last] = StyleAlignFlags::END;

  CalculateItemBaselines(firstBaselineItems, BaselineSharingGroup::First);
  CalculateItemBaselines(lastBaselineItems, BaselineSharingGroup::Last);
}
