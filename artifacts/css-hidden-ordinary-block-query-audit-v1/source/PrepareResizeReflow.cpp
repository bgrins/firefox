void nsBlockFrame::PrepareResizeReflow(BlockReflowState& aState) {
  // See if we can try and avoid marking all the lines as dirty
  // FIXME(emilio): This should be writing-mode aware, I guess.
  bool tryAndSkipLines =
      // The left content-edge must be a constant distance from the left
      // border-edge.
      !StylePadding()->mPadding.Get(eSideLeft).HasPercent();

#ifdef DEBUG
  if (gDisableResizeOpt) {
    tryAndSkipLines = false;
  }
  if (gNoisyReflow) {
    if (!tryAndSkipLines) {
      IndentBy(stdout, gNoiseIndent);
      ListTag(stdout);
      printf(": marking all lines dirty: availISize=%d\n",
             aState.mReflowInput.AvailableISize());
    }
  }
#endif

  if (tryAndSkipLines) {
    WritingMode wm = aState.mReflowInput.GetWritingMode();
    nscoord newAvailISize =
        aState.mReflowInput.ComputedLogicalBorderPadding(wm).IStart(wm) +
        aState.mReflowInput.ComputedISize();

#ifdef DEBUG
    if (gNoisyReflow) {
      IndentBy(stdout, gNoiseIndent);
      ListTag(stdout);
      printf(": trying to avoid marking all lines dirty\n");
    }
#endif

    for (LineIterator line = LinesBegin(), line_end = LinesEnd();
         line != line_end; ++line) {
      // We let child blocks make their own decisions the same
      // way we are here.
      bool isLastLine = line == mLines.back() && !GetNextInFlow();
      if (line->IsBlock() || line->HasFloats() ||
          (!isLastLine && !line->HasForcedLineBreakAfter()) ||
          ((isLastLine || !line->IsLineWrapped())) ||
          line->ResizeReflowOptimizationDisabled() ||
          line->IsImpactedByFloat() || (line->IEnd() > newAvailISize)) {
        line->MarkDirty();
      }

#ifdef REALLY_NOISY_REFLOW
      if (!line->IsBlock()) {
        printf("PrepareResizeReflow thinks line %p is %simpacted by floats\n",
               line.get(), line->IsImpactedByFloat() ? "" : "not ");
      }
#endif
#ifdef DEBUG
      if (gNoisyReflow && !line->IsDirty()) {
        IndentBy(stdout, gNoiseIndent + 1);
        printf(
            "skipped: line=%p next=%p %s %s%s%s clearTypeBefore/After=%s/%s "
            "xmost=%d\n",
            static_cast<void*>(line.get()),
            static_cast<void*>(
                (line.next() != LinesEnd() ? line.next().get() : nullptr)),
            line->IsBlock() ? "block" : "inline",
            line->HasForcedLineBreakAfter() ? "has-break-after " : "",
            line->HasFloats() ? "has-floats " : "",
            line->IsImpactedByFloat() ? "impacted " : "",
            line->UsedClearToString(line->FloatClearTypeBefore()),
            line->UsedClearToString(line->FloatClearTypeAfter()), line->IEnd());
      }
#endif
    }
  } else {
    // Mark everything dirty
    for (auto& line : Lines()) {
      line.MarkDirty();
    }
  }
}
