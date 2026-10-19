  LinePair ResolveLineRangeHelper(const StyleGridLine& aStart,
                                  const StyleGridLine& aEnd,
                                  const LineNameMap& aNameMap,
                                  LogicalAxis aAxis, uint32_t aExplicitGridEnd,
                                  const nsStylePosition* aStyle,
                                  int32_t aClampMinLine, int32_t aClampMaxLine);

  LineRange ResolveLineRange(const StyleGridLine& aStart,
                             const StyleGridLine& aEnd,
                             const LineNameMap& aNameMap, LogicalAxis aAxis,
                             uint32_t aExplicitGridEnd,
                             const nsStylePosition* aStyle,
                             bool aIsAbsPos = false);
