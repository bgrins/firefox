nsGridContainerFrame::Grid::ResolveAbsPosLineRange(
    const StyleGridLine& aStart, const StyleGridLine& aEnd,
    const LineNameMap& aNameMap, LogicalAxis aAxis, uint32_t aExplicitGridEnd,
    int32_t aGridStart, int32_t aGridEnd, const nsStylePosition* aStyle) {
  if (aStart.IsAuto()) {
    if (aEnd.IsAuto()) {
      return LineRange(kAutoLine, kAutoLine);
    }
    uint32_t from = aEnd.line_num < 0 ? aExplicitGridEnd + 1 : 0;
    int32_t end = ResolveLine(aEnd, aEnd.line_num, from, aNameMap,
                              MakeLogicalSide(aAxis, LogicalEdge::End),
                              aExplicitGridEnd, aStyle);
    if (aEnd.is_span) {
      ++end;
    }
    // A line outside the existing grid is treated as 'auto' for abs.pos (10.1).
    end = AutoIfOutside(end, aGridStart, aGridEnd);
    return LineRange(kAutoLine, end);
  }

  if (aEnd.IsAuto()) {
    uint32_t from = aStart.line_num < 0 ? aExplicitGridEnd + 1 : 0;
    int32_t start = ResolveLine(aStart, aStart.line_num, from, aNameMap,
                                MakeLogicalSide(aAxis, LogicalEdge::Start),
                                aExplicitGridEnd, aStyle);
    if (aStart.is_span) {
      start = std::max(aGridEnd - start, aGridStart);
    }
    start = AutoIfOutside(start, aGridStart, aGridEnd);
    return LineRange(start, kAutoLine);
  }

  LineRange r = ResolveLineRange(aStart, aEnd, aNameMap, aAxis,
                                 aExplicitGridEnd, aStyle, true);
  if (r.IsAuto()) {
    MOZ_ASSERT(aStart.is_span && aEnd.is_span,
               "span / span is the only case "
               "leading to IsAuto here -- we dealt with the other cases above");
    // The second span was ignored per 9.2.1.  For abs.pos., 10.1 says that this
    // case should result in "auto / auto" unlike normal flow grid items.
    return LineRange(kAutoLine, kAutoLine);
  }

  return LineRange(AutoIfOutside(r.mUntranslatedStart, aGridStart, aGridEnd),
                   AutoIfOutside(r.mUntranslatedEnd, aGridStart, aGridEnd));
}
