static nscoord ContentContribution(const GridItemInfo& aGridItem,
                                   const GridReflowInput& aGridRI,
                                   LogicalAxis aAxis,
                                   const LogicalSize& aPercentageBasis,
                                   IntrinsicISizeType aConstraint,
                                   nscoord aMinSizeClamp = NS_MAXSIZE,
                                   const StyleSizeOverrides& aOverrides = {}) {
  nsIFrame* child = aGridItem.mFrame;

  const WritingMode gridWM = aGridRI.mWM;
  nscoord extraMargin = 0;
  nsGridContainerFrame::Subgrid* subgrid = nullptr;
  if (child->GetParent() != aGridRI.mFrame) {
    // |child| is a subgrid descendant, so it contributes its subgrids'
    // margin+border+padding for any edge tracks that it spans.
    auto* subgridFrame = child->GetParent();
    subgrid = subgridFrame->GetProperty(Subgrid::Prop());
    const auto itemEdgeBits = aGridItem.mState[aAxis] & ItemState::eEdgeBits;
    if (itemEdgeBits) {
      LogicalMargin mbp = SubgridAccumulatedMarginBorderPadding(
          subgridFrame, subgrid, gridWM, aAxis);
      if (itemEdgeBits & ItemState::eStartEdge) {
        extraMargin += mbp.Start(aAxis, gridWM);
      }
      if (itemEdgeBits & ItemState::eEndEdge) {
        extraMargin += mbp.End(aAxis, gridWM);
      }
    }
    // It also contributes (half of) the subgrid's gap on its edges (if any)
    // subtracted by the non-subgrid ancestor grid container's gap.
    // Note that this can also be negative since it's considered a margin.
    if (itemEdgeBits != ItemState::eEdgeBits) {
      const auto subgridAxis =
          gridWM.ConvertAxisTo(aAxis, subgridFrame->GetWritingMode());
      auto& gapStyle = subgridAxis == LogicalAxis::Block
                           ? subgridFrame->StylePosition()->mRowGap
                           : subgridFrame->StylePosition()->mColumnGap;
      if (!gapStyle.IsNormal()) {
        auto subgridExtent = subgridAxis == LogicalAxis::Block
                                 ? subgrid->mGridRowEnd
                                 : subgrid->mGridColEnd;
        if (subgridExtent > 1) {
          nscoord subgridGap =
              nsLayoutUtils::ResolveGapToLength(gapStyle, NS_UNCONSTRAINEDSIZE);
          const auto& tracks = aGridRI.TracksFor(aAxis);
          auto gapDelta = subgridGap - tracks.mGridGap;
          if (!itemEdgeBits) {
            extraMargin += gapDelta;
          } else {
            extraMargin += gapDelta / 2;
          }
        }
      }
    }
  }

  gfxContext* rc = &aGridRI.mRenderingContext;
  PhysicalAxis axis = gridWM.PhysicalAxis(aAxis);
  auto childWM = child->GetWritingMode();
  const bool isOrthogonal = childWM.IsOrthogonalTo(gridWM);
  auto childAxis = isOrthogonal ? GetOrthogonalAxis(aAxis) : aAxis;

  StyleSizeOverrides overrides = aOverrides;
  if (childAxis == LogicalAxis::Inline && !overrides.mStyleBSize) {
    const bool stretchesInBlockAxis =
        child->StylePosition()
            ->BSize(childWM, AnchorPosResolutionParams::From(child))
            ->IsAuto() &&
        aGridRI.mFrame->GridItemShouldStretch(child, LogicalAxis::Block);
    if (stretchesInBlockAxis) {
      overrides.mStyleBSize.emplace(StyleSize::Stretch());
    }
  }

  nscoord size = nsLayoutUtils::IntrinsicForAxis(
      axis, rc, child, aConstraint, Some(aPercentageBasis),
      nsLayoutUtils::BAIL_IF_REFLOW_NEEDED, aMinSizeClamp, overrides);
  if (size == NS_INTRINSIC_ISIZE_UNKNOWN && childAxis == LogicalAxis::Block) {
    nscoord contentBSize = 0;
    if (aGridRI.mIsGridIntrinsicSizing && aAxis == LogicalAxis::Block &&
        !StaticPrefs::layout_css_grid_intrinsic_sizing_measure_bsize()) {
      // FIXME: Remove this code-path once the stack overflow crashes it causes
      // are figured out.
      size = 0;
    } else {
      // We need to reflow the child to find its BSize contribution.
      nscoord availISize = INFINITE_ISIZE_COORD;
      nscoord availBSize = NS_UNCONSTRAINEDSIZE;
      // The next two variables are MinSizeClamp values in the child's axes.
      nscoord iMinSizeClamp = NS_MAXSIZE;
      nscoord bMinSizeClamp = NS_MAXSIZE;
      LogicalSize cbSize = aPercentageBasis;
      // Below, we try to resolve the child's grid-area size in its inline-axis
      // to use as the CB/Available size in the MeasuringReflow that follows.
      if (child->GetParent() != aGridRI.mFrame) {
        // This item is a child of a subgrid descendant.
        auto* subgridFrame =
            static_cast<nsGridContainerFrame*>(child->GetParent());
        MOZ_ASSERT(subgridFrame->IsGridContainerFrame());
        auto* uts =
            subgridFrame->GetOrCreateDeletableProperty(UsedTrackSizes::Prop());
        // The grid-item's inline-axis as expressed in the subgrid's WM.
        const auto subgridAxis = childWM.ConvertAxisTo(
            LogicalAxis::Inline, subgridFrame->GetWritingMode());
        uts->ResolveTrackSizesForAxis(subgridFrame, subgridAxis, *rc);
        if (uts->mCanResolveLineRangeSize[subgridAxis]) {
          auto* subgrid =
              subgridFrame->GetProperty(nsGridContainerFrame::Subgrid::Prop());
          const GridItemInfo* originalItem = nullptr;
          for (const auto& item : subgrid->mGridItems) {
            if (item.mFrame == child) {
              originalItem = &item;
              break;
            }
          }
          MOZ_ASSERT(originalItem, "huh?");
          const auto& range = originalItem->mArea.LineRangeForAxis(subgridAxis);
          const nscoord sz = range.ToLength(uts->mTrackPlans[subgridAxis]);
          if (childWM.IsOrthogonalTo(subgridFrame->GetWritingMode())) {
            availBSize = sz;
            cbSize.BSize(childWM) = sz;
            if (aGridItem.mState[aAxis] & ItemState::eClampMarginBoxMinSize) {
              bMinSizeClamp = sz;
            }
          } else {
            availISize = sz;
            cbSize.ISize(childWM) = sz;
            if (aGridItem.mState[aAxis] & ItemState::eClampMarginBoxMinSize) {
              iMinSizeClamp = sz;
            }
          }
        }
      } else {
        const LogicalAxis inlineAxisInChildWM =
            isOrthogonal ? LogicalAxis::Block : LogicalAxis::Inline;
        const nscoord colSize = cbSize.Size(inlineAxisInChildWM, childWM);
        if (colSize != NS_UNCONSTRAINEDSIZE) {
          MOZ_ASSERT(aGridRI.mCols.mCanResolveLineRangeSize,
                     "Grid column sizes should be resolvable!");
          if (isOrthogonal) {
            availBSize = colSize;
            if (aGridItem.mState[aAxis] & ItemState::eClampMarginBoxMinSize) {
              bMinSizeClamp = colSize;
            }
          } else {
            availISize = colSize;
            if (aGridItem.mState[aAxis] & ItemState::eClampMarginBoxMinSize) {
              iMinSizeClamp = colSize;
            }
          }
        }
      }
      if (isOrthogonal == (aAxis == LogicalAxis::Inline)) {
        bMinSizeClamp = aMinSizeClamp;
      } else {
        iMinSizeClamp = aMinSizeClamp;
      }
      LogicalSize availableSize(childWM, availISize, availBSize);
      const auto measurement =
          ::MeasuringReflow(child, aGridRI.mReflowInput, rc, availableSize,
                            cbSize, iMinSizeClamp, bMinSizeClamp);
      size = measurement.mBSize;
      contentBSize = measurement.mContentBSize;
      if (aGridRI.mIsGridIntrinsicSizing) {
        MarkDirtyAfterIntrinsicSizingReflow(child);
      }
    }
    size += child->GetLogicalUsedMargin(childWM).BStartEnd(childWM);
    nscoord overflow = size - aMinSizeClamp;
    if (MOZ_UNLIKELY(overflow > 0)) {
      nscoord newContentSize = std::max(nscoord(0), contentBSize - overflow);
      // XXXmats deal with percentages better, see bug 1300369 comment 27.
      size -= contentBSize - newContentSize;
    }
  }
  MOZ_ASSERT(aGridItem.mBaselineOffset[aAxis] >= 0,
             "baseline offset should be non-negative at this point");
  MOZ_ASSERT((aGridItem.mState[aAxis] & ItemState::eIsBaselineAligned) ||
                 aGridItem.mBaselineOffset[aAxis] == nscoord(0),
             "baseline offset should be zero when not baseline-aligned");
  size += aGridItem.mBaselineOffset[aAxis];
  size += extraMargin;
  return std::max(size, 0);
}
