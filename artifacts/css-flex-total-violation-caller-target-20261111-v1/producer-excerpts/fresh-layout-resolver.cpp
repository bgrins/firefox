nsFlexContainerFrame::FlexLayoutResult nsFlexContainerFrame::DoFlexLayout(
    const ReflowInput& aReflowInput, const nscoord aTentativeContentBoxMainSize,
    const nscoord aTentativeContentBoxCrossSize,
    const FlexboxAxisTracker& aAxisTracker, nscoord aMainGapSize,
    nscoord aCrossGapSize, nsTArray<StrutInfo>& aStruts,
    ComputedFlexContainerInfo* const aContainerInfo) {
  FlexLayoutResult flr;

  GenerateFlexLines(aReflowInput, aTentativeContentBoxMainSize,
                    aTentativeContentBoxCrossSize, aStruts, aAxisTracker,
                    aMainGapSize, flr.mPlaceholders, flr.mLines,
                    flr.mHasCollapsedItems);

  if ((flr.mLines.Length() == 1 && flr.mLines[0].IsEmpty()) ||
      aReflowInput.mStyleDisplay->IsContainLayout()) {
    // We have no flex items, or we're layout-contained. So, we have no
    // baseline, and our parent should synthesize a baseline if needed.
    AddStateBits(NS_STATE_FLEX_SYNTHESIZE_BASELINE);
  } else {
    RemoveStateBits(NS_STATE_FLEX_SYNTHESIZE_BASELINE);
  }

  // Construct our computed info if we've been asked to do so. This is
  // necessary to do now so we can capture some computed values for
  // FlexItems during layout that would not otherwise be saved (like
  // size adjustments). We'll later fix up the line properties,
  // because the correct values aren't available yet.
  if (aContainerInfo) {
    MOZ_ASSERT(HasAnyStateBits(NS_STATE_FLEX_COMPUTED_INFO),
               "We should only have the info struct if we should generate it");

    if (!aStruts.IsEmpty()) {
      // We restarted DoFlexLayout, and may have stale mLines to clear:
      aContainerInfo->mLines.Clear();
    } else {
      MOZ_ASSERT(aContainerInfo->mLines.IsEmpty(), "Shouldn't have lines yet.");
    }

    CreateFlexLineAndFlexItemInfo(*aContainerInfo, flr.mLines);
    ComputeFlexDirections(*aContainerInfo, aAxisTracker);
  }

  flr.mContentBoxMainSize = ComputeMainSize(
      aReflowInput, aAxisTracker, aTentativeContentBoxMainSize, flr.mLines);

  uint32_t lineIndex = 0;
  for (FlexLine& line : flr.mLines) {
    ComputedFlexLineInfo* lineInfo =
        aContainerInfo ? &aContainerInfo->mLines[lineIndex] : nullptr;
    line.ResolveFlexibleLengths(flr.mContentBoxMainSize, lineInfo);
    ++lineIndex;
  }
