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

