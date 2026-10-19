nsGridContainerFrame::Grid::ResolveLineRangeHelper(
    const StyleGridLine& aStart, const StyleGridLine& aEnd,
    const LineNameMap& aNameMap, LogicalAxis aAxis, uint32_t aExplicitGridEnd,
    const nsStylePosition* aStyle) {
  MOZ_ASSERT(int32_t(kAutoLine) > kMaxLine);
  auto startNum = std::clamp(aStart.line_num, kMinLine, kMaxLine);
  auto endNum = std::clamp(aEnd.line_num, kMinLine, kMaxLine);

  if (aStart.is_span) {
    if (aEnd.is_span || aEnd.IsAuto()) {
      // https://drafts.csswg.org/css-grid-2/#grid-placement-errors
      if (aStart.LineName()->IsEmpty()) {
        // span <integer> / span *
        // span <integer> / auto
        return LinePair(kAutoLine, startNum);
      }
      // span <custom-ident> / span *
      // span <custom-ident> / auto
      return LinePair(kAutoLine, 1);  // XXX subgrid explicit size instead of 1?
    }

    uint32_t from = endNum < 0 ? aExplicitGridEnd + 1 : 0;
    auto end = ResolveLine(aEnd, endNum, from, aNameMap,
                           MakeLogicalSide(aAxis, LogicalEdge::End),
                           aExplicitGridEnd, aStyle);
    int32_t span = startNum == 0 ? 1 : startNum;
    if (end <= 1) {
      // The end is at or before the first explicit line, thus all lines before
      // it match <custom-ident> since they're implicit.
      int32_t start = std::max(end - span, aNameMap.mClampMinLine);
      return LinePair(start, end);
    }
    auto start = ResolveLine(aStart, -span, end, aNameMap,
                             MakeLogicalSide(aAxis, LogicalEdge::Start),
                             aExplicitGridEnd, aStyle);
    return LinePair(start, end);
  }

  int32_t start = kAutoLine;
  if (aStart.IsAuto()) {
    if (aEnd.IsAuto()) {
      // auto / auto
      return LinePair(start, 1);  // XXX subgrid explicit size instead of 1?
    }
    if (aEnd.is_span) {
      if (aEnd.LineName()->IsEmpty()) {
        // auto / span <integer>
        MOZ_ASSERT(endNum != 0);
        return LinePair(start, endNum);
      }
      // https://drafts.csswg.org/css-grid-2/#grid-placement-errors
      // auto / span <custom-ident>
      return LinePair(start, 1);  // XXX subgrid explicit size instead of 1?
    }
  } else {
    uint32_t from = startNum < 0 ? aExplicitGridEnd + 1 : 0;
    start = ResolveLine(aStart, startNum, from, aNameMap,
                        MakeLogicalSide(aAxis, LogicalEdge::Start),
                        aExplicitGridEnd, aStyle);
    if (aEnd.IsAuto()) {
      // A "definite line / auto" should resolve the auto to 'span 1'.
      // The error handling in ResolveLineRange will make that happen and also
      // clamp the end line correctly if we return "start / start".
      return LinePair(start, start);
    }
  }

  uint32_t from;
  int32_t nth = endNum == 0 ? 1 : endNum;
  if (aEnd.is_span) {
    if (MOZ_UNLIKELY(start < 0)) {
      if (aEnd.LineName()->IsEmpty()) {
        return LinePair(start, start + nth);
      }
      from = 0;
    } else {
      if (start >= int32_t(aExplicitGridEnd)) {
        // The start is at or after the last explicit line, thus all lines
        // after it match <custom-ident> since they're implicit.
        return LinePair(start, std::min(start + nth, aNameMap.mClampMaxLine));
      }
      from = start;
    }
  } else {
    from = endNum < 0 ? aExplicitGridEnd + 1 : 0;
  }
  auto end = ResolveLine(aEnd, nth, from, aNameMap,
                         MakeLogicalSide(aAxis, LogicalEdge::End),
                         aExplicitGridEnd, aStyle);
  if (start == int32_t(kAutoLine)) {
    // auto / definite line
    start = std::max(aNameMap.mClampMinLine, end - 1);
  }
  return LinePair(start, end);
}
