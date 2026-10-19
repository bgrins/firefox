nsGridContainerFrame::Grid::ResolveLine(
    const StyleGridLine& aLine, int32_t aNth, uint32_t aFromIndex,
    const LineNameMap& aNameMap, LogicalSide aSide, uint32_t aExplicitGridEnd,
    const nsStylePosition* aStyle) {
  MOZ_ASSERT(!aLine.IsAuto());
  aNth = std::clamp(aNth, kMinLine, kMaxLine);
  int32_t line = 0;
  if (aLine.LineName()->IsEmpty()) {
    MOZ_ASSERT(aNth != 0, "css-grid 9.2: <integer> must not be zero.");
    line = int32_t(aFromIndex) + aNth;
  } else {
    if (aNth == 0) {
      // <integer> was omitted; treat it as 1.
      aNth = 1;
    }
    bool isNameOnly = !aLine.is_span && aLine.line_num == 0;
    if (isNameOnly) {
      AutoTArray<uint32_t, 16> implicitLines;
      aNameMap.FindNamedAreas(aLine.ident.AsAtom(), aSide, implicitLines);
      if (!implicitLines.IsEmpty() ||
          aNameMap.HasImplicitNamedArea(aLine.LineName())) {
        // aName is a named area - look for explicit lines named
        // <name>-start/-end depending on which side we're resolving.
        // https://drafts.csswg.org/css-grid-2/#grid-placement-slot
        nsAutoString lineName(nsDependentAtomString(aLine.LineName()));
        if (IsStart(aSide)) {
          lineName.AppendLiteral("-start");
        } else {
          lineName.AppendLiteral("-end");
        }
        RefPtr<nsAtom> name = NS_Atomize(lineName);
        line = aNameMap.FindNamedLine(name, &aNth, aFromIndex, implicitLines);
      }
    }

    if (line == 0) {
      // If LineName() ends in -start/-end, try the prefix as a named area.
      AutoTArray<uint32_t, 16> implicitLines;
      uint32_t index;
      bool useStart = IsNameWithStartSuffix(aLine.LineName(), &index);
      if (useStart || IsNameWithEndSuffix(aLine.LineName(), &index)) {
        auto side = MakeLogicalSide(
            GetAxis(aSide), useStart ? LogicalEdge::Start : LogicalEdge::End);
        RefPtr<nsAtom> name = NS_Atomize(nsDependentSubstring(
            nsDependentAtomString(aLine.LineName()), 0, index));
        aNameMap.FindNamedAreas(name, side, implicitLines);
      }
      line = aNameMap.FindNamedLine(aLine.LineName(), &aNth, aFromIndex,
                                    implicitLines);
    }

    if (line == 0) {
      MOZ_ASSERT(aNth != 0, "we found all N named lines but 'line' is zero!");
      int32_t edgeLine;
      if (aLine.is_span) {
        // https://drafts.csswg.org/css-grid-2/#grid-placement-span-int
        // 'span <custom-ident> N'
        edgeLine = IsStart(aSide) ? 1 : aExplicitGridEnd;
      } else {
        // https://drafts.csswg.org/css-grid-2/#grid-placement-int
        // '<custom-ident> N'
        edgeLine = aNth < 0 ? 1 : aExplicitGridEnd;
      }
      // "If not enough lines with that name exist, all lines in the implicit
      // grid are assumed to have that name..."
      line = edgeLine + aNth;
    }
  }
  // Note: at this point, 'line' might be outside of aNameMap's allowed range,
  // [mClampMinLin, mClampMaxLine]. This is fine; we'll clamp once we've
  // resolved *both* the start and end line -- in particular, we clamp in
  // ResolveLineRange(). If we clamped here, it'd be premature -- if one line
  // is definite and the other is specified as a span to some named line
  // (i.e. we need to perform a name-search that starts from the definite
  // line), then it matters whether we clamp the definite line before or after
  // that search. See https://bugzilla.mozilla.org/show_bug.cgi?id=1800566#c6
  // for more.
  return line;
}
