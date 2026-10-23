void nsBlockFrame::LazyMarkLinesDirty() {
  if (HasAnyStateBits(NS_BLOCK_LOOK_FOR_DIRTY_FRAMES)) {
    for (LineIterator line = LinesBegin(), line_end = LinesEnd();
         line != line_end; ++line) {
      for (nsIFrame* lineFrame : line->ChildFrames()) {
        if (lineFrame->IsSubtreeDirty()) {
          // NOTE:  MarkLineDirty does more than just marking the line dirty.
          MarkLineDirty(line, &mLines);
          break;
        }
      }
    }
    RemoveStateBits(NS_BLOCK_LOOK_FOR_DIRTY_FRAMES);
  }
}
