nsGridContainerFrame::Grid::ResolveLineRange(
    const StyleGridLine& aStart, const StyleGridLine& aEnd,
    const LineNameMap& aNameMap, LogicalAxis aAxis, uint32_t aExplicitGridEnd,
    const nsStylePosition* aStyle) {
  LinePair r = ResolveLineRangeHelper(aStart, aEnd, aNameMap, aAxis,
                                      aExplicitGridEnd, aStyle);
  MOZ_ASSERT(r.second != int32_t(kAutoLine));

  if (r.first == int32_t(kAutoLine)) {
    // r.second is a span, clamp it to aNameMap.mClampMaxLine - 1 so that
    // the returned range has a HypotheticalEnd <= aNameMap.mClampMaxLine.
    // https://drafts.csswg.org/css-grid-2/#overlarge-grids
    r.second = std::min(r.second, aNameMap.mClampMaxLine - 1);
  } else {
    // Clamp the lines to be within our limits, per
    // https://drafts.csswg.org/css-grid-2/#overlarge-grids
    // Note that our limits here might come from the [kMinLine, kMaxLine]
    // extremes; or, they might just be the bounds of a subgrid's explicit
    // grid. We use the same clamping approach either way, per
    // https://drafts.csswg.org/css-grid-2/#subgrid-implicit ("using the same
    // procedure as for clamping placement in an overly-large grid").
    //
    // Note that these two clamped assignments might collapse our range to
    // have both edges pointing at the same line (spanning 0 tracks); this
    // might happen here if e.g. r.first were mClampMaxLine, and r.second gets
    // clamped from some higher number down to mClampMaxLine. We'll handle this
    // by shifting the inner line (r.first in this hypothetical) inwards by 1,
    // in the #grid-placement-errors section; that achieves the outcome of
    // the #overlarge-grids clamping spec text that says "its span must be
    // truncated to 1" when clamping an item that was completely outside the
    // limits.
    r.first =
        std::clamp(r.first, aNameMap.mClampMinLine, aNameMap.mClampMaxLine);
    r.second =
        std::clamp(r.second, aNameMap.mClampMinLine, aNameMap.mClampMaxLine);

    // Handle grid placement errors.
    // https://drafts.csswg.org/css-grid-2/#grid-placement-errors
    if (r.first > r.second) {
      std::swap(r.first, r.second);
    } else if (r.first == r.second) {
      // (This is #grid-placement-errors fixup, but it's also where we ensure
      // that any #overlarge-grids fixup that we did above will end up
      // truncating the range to a span of 1 rather than 0 -- i.e. sliding
      // inwards if needed.)
      if (MOZ_UNLIKELY(r.first == aNameMap.mClampMaxLine)) {
        r.first = aNameMap.mClampMaxLine - 1;
      }
      r.second = r.first + 1;
    }
  }
  return LineRange(r.first, r.second);
}
