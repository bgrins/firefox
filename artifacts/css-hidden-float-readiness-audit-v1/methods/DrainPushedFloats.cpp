void nsBlockFrame::DrainPushedFloats() {
  DrainSelfPushedFloats();

  // After our prev-in-flow has completed reflow, it may have a pushed
  // floats list, containing floats that we need to own.  Take these.
  nsBlockFrame* prevBlock = static_cast<nsBlockFrame*>(GetPrevInFlow());
  if (prevBlock) {
    AutoFrameListPtr list(PresContext(), prevBlock->StealPushedFloats());
    if (list && list->NotEmpty()) {
      EnsureFloats()->InsertFrames(this, nullptr, std::move(*list));
    }
  }
}
