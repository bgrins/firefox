LEAN_MUTATIONS = {
    "ExcludeFirstLine": ("if lo ≤ x ∧ x ≤ hi then some x else none", "if lo < x ∧ x ≤ hi then some x else none", "projection_inside"),
    "OmitSwap": ("if a > b then (b, a)", "if a > b then (a, b)", "finish_distinct_identity"),
    "OmitInwardFixup": ("if a = hi then hi - 1 else a", "if a = hi then hi else a", "normalize_bounded"),
    "MapBoundsForAbspos": ("if abs then (ulo,uhi) else (maplo,maphi)", "if abs then (maplo,maphi) else (maplo,maphi)", "abspos_independent_of_map_bounds"),
    "UABoundsForNormal": ("if abs then (ulo,uhi) else (maplo,maphi)", "if abs then (ulo,uhi) else (ulo,uhi)", "normal_flow_unchanged"),
    "WrongPreClampSide": ("| .upperEnd, a, b => (a,min b hi)", "| .upperEnd, a, b => (min a hi,b)", "preclamp_absorption"),
    "SpanIsDefinite": ("| .span _ => (none,none)", "| .span n => (some n,some n)", "span_only_is_auto"),
}

CPP_MUTATIONS = {
    "DropAbsposFlag": ("ResolveAbsPosLineRange-after.inc", ", aStyle, true)", ", aStyle, false)"),
    "RetainHelperLowerMapClamp": ("ResolveLineRangeHelper-after.inc", "std::max(end - span, aClampMinLine)", "std::max(end - span, aNameMap.mClampMinLine)"),
    "RetainHelperUpperMapClamp": ("ResolveLineRangeHelper-after.inc", "std::min(start + nth, aClampMaxLine)", "std::min(start + nth, aNameMap.mClampMaxLine)"),
    "RetainFinalizerMapBounds": ("ResolveLineRange-after.inc", "aIsAbsPos ? kMaxLine : aNameMap.mClampMaxLine", "aIsAbsPos ? aNameMap.mClampMaxLine : aNameMap.mClampMaxLine"),
    "UABoundsForNormal": ("ResolveLineRange-after.inc", "aIsAbsPos ? kMaxLine : aNameMap.mClampMaxLine", "aIsAbsPos ? kMaxLine : kMaxLine"),
    "ExcludeFirstLine": ("AutoIfOutside.inc", "aLine < aMin", "aLine <= aMin"),
    "OmitSwap": ("ResolveLineRange-after.inc", "std::swap(r.first, r.second);", "std::ignore = r.first;"),
    "OmitInwardFixup": ("ResolveLineRange-after.inc", "r.first = clampMaxLine - 1;", "r.first = clampMaxLine;"),
}
