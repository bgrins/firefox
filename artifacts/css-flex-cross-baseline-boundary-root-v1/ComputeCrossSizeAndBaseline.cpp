void FlexLine::ComputeCrossSizeAndBaseline(
    const FlexboxAxisTracker& aAxisTracker) {
  // NOTE: in these "cross{Start,End}ToFurthest{First,Last}Baseline" variables,
  // the "first/last" term is referring to the flex *line's* baseline-sharing
  // groups, which may or may not match any flex *item's* exact align-self
  // value. See the code that sets FlexItem::mBaselineSharingGroup for more
  // details.
  nscoord crossStartToFurthestFirstBaseline = nscoord_MIN;
  nscoord crossEndToFurthestFirstBaseline = nscoord_MIN;
  nscoord crossStartToFurthestLastBaseline = nscoord_MIN;
  nscoord crossEndToFurthestLastBaseline = nscoord_MIN;

  nscoord largestOuterCrossSize = 0;
  for (const FlexItem& item : Items()) {
    nscoord curOuterCrossSize = item.OuterCrossSize();

    if ((item.AlignSelf() == StyleAlignFlags::BASELINE ||
         item.AlignSelf() == StyleAlignFlags::LAST_BASELINE) &&
        item.NumAutoMarginsInCrossAxis() == 0) {
      const bool usingItemFirstBaseline =
          (item.AlignSelf() == StyleAlignFlags::BASELINE);

      // Find distance from our item's cross-start and cross-end margin-box
      // edges to its baseline.
      //
      // Here's a diagram of a flex-item that we might be doing this on.
      // "mmm" is the margin-box, "bbb" is the border-box. The bottom of
      // the text "BASE" is the baseline.
      //
      // ---(cross-start)---
      //                ___              ___            ___
      //   mmmmmmmmmmmm  |                |margin-start  |
      //   m          m  |               _|_   ___       |
      //   m bbbbbbbb m  |curOuterCrossSize     |        |crossStartToBaseline
      //   m b      b m  |                      |ascent  |
      //   m b BASE b m  |                     _|_      _|_
      //   m b      b m  |                               |
      //   m bbbbbbbb m  |                               |crossEndToBaseline
      //   m          m  |                               |
      //   mmmmmmmmmmmm _|_                             _|_
      //
      // ---(cross-end)---
      //
      // We already have the curOuterCrossSize, margin-start, and the ascent.
      // * We can get crossStartToBaseline by adding margin-start + ascent.
      // * If we subtract that from the curOuterCrossSize, we get
      //   crossEndToBaseline.

      nscoord crossStartToBaseline = item.BaselineOffsetFromOuterCrossEdge(
          aAxisTracker.CrossAxisPhysicalStartSide(), usingItemFirstBaseline);
      nscoord crossEndToBaseline = curOuterCrossSize - crossStartToBaseline;

      // Now, update our "largest" values for these (across all the flex items
      // in this flex line), so we can use them in computing the line's cross
      // size below:
      if (item.ItemBaselineSharingGroup() == BaselineSharingGroup::First) {
        crossStartToFurthestFirstBaseline =
            std::max(crossStartToFurthestFirstBaseline, crossStartToBaseline);
        crossEndToFurthestFirstBaseline =
            std::max(crossEndToFurthestFirstBaseline, crossEndToBaseline);
      } else {
        crossStartToFurthestLastBaseline =
            std::max(crossStartToFurthestLastBaseline, crossStartToBaseline);
        crossEndToFurthestLastBaseline =
            std::max(crossEndToFurthestLastBaseline, crossEndToBaseline);
      }
    } else {
      largestOuterCrossSize =
          std::max(largestOuterCrossSize, curOuterCrossSize);
    }
  }

  // The line's baseline offset is the distance from the line's edge to the
  // furthest item-baseline. The item(s) with that baseline will be exactly
  // aligned with the line's edge.
  mFirstBaselineOffset = crossStartToFurthestFirstBaseline;
  mLastBaselineOffset = crossEndToFurthestLastBaseline;

  // The line's cross-size is the larger of:
  //  (a) [largest cross-start-to-baseline + largest baseline-to-cross-end] of
  //      all baseline-aligned items with no cross-axis auto margins...
  // and
  //  (b) [largest cross-start-to-baseline + largest baseline-to-cross-end] of
  //      all last baseline-aligned items with no cross-axis auto margins...
  // and
  //  (c) largest cross-size of all other children.
  mLineCrossSize = std::max(
      std::max(
          crossStartToFurthestFirstBaseline + crossEndToFurthestFirstBaseline,
          crossStartToFurthestLastBaseline + crossEndToFurthestLastBaseline),
      largestOuterCrossSize);
}
