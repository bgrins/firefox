    // Now repair the line and update |aState.mBCoord| by calling
    // |ReflowLine| or |SlideLine|.
    // If we're going to reflow everything again, then no need to reflow
    // the dirty line ... unless the line has floats, in which case we'd
    // better reflow it now to refresh its float cache, which may contain
    // dangling frame pointers! Ugh! This reflow of the line may be
    // incorrect because we skipped reflowing previous lines (e.g., floats
    // may be placed incorrectly), but that's OK because we'll mark the
    // line dirty below under "if (aState.mReflowInput.mDiscoveredClearance..."
    if (line->IsDirty() && (line->HasFloats() || !willReflowAgain)) {
      lastLineMovedUp = true;

      bool maybeReflowingForFirstTime =
          line->IStart() == 0 && line->BStart() == 0 && line->ISize() == 0 &&
          line->BSize() == 0;

      // Compute the dirty lines "before" BEnd, after factoring in
      // the running deltaBCoord value - the running value is implicit in
      // aState.mBCoord.
      nscoord oldB = line->BStart();
      nscoord oldBMost = line->BEnd();

      NS_ASSERTION(!willReflowAgain || !line->IsBlock(),
                   "Don't reflow blocks while willReflowAgain is true, reflow "
                   "of block abs-pos children depends on this");

      if (shouldBreakForPageName) {
        // Immediately fragment for page-name. It is possible we could break
        // out of the loop right here, but this should make it more similar to
        // what happens when reflow causes fragmentation.
        // Set the page name, so that PushTruncatedLine does not need to
        // recalculate the new page name.
        PresShell()->FrameConstructor()->SetNextPageContentFramePageName(
            nextPageName ? nextPageName : GetAutoPageValue());
        PushTruncatedLine(aState, line, &keepGoing,
                          ComputeNewPageNameIfNeeded::No);
      } else {
        // Reflow the dirty line. If it's an incremental reflow, then force
        // it to invalidate the dirty area if necessary
        usedOverflowWrap |= ReflowLine(aState, line, &keepGoing);
      }

