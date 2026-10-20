# Implementation sketch, not a compiled candidate

Keep the initial reset and transformed/zoom early path unchanged. Enclose the ordinary translation traversal in a local generic lambda with compile-time booleans `TrackWide` and `CommonLayout`. Dispatch once:

```cpp
if (!aAppUnitTranslation) {
  return traverse.operator()<false, false>();
}
if (aFlags.isEmpty() && aViewportType == ViewportType::Layout &&
    aStopAtAncestor.mViewportType == ViewportType::Layout) {
  return traverse.operator()<true, true>();
}
return traverse.operator()<true, false>();
```

Within the shared traversal, use `if constexpr (TrackWide)` for each existing v2 arithmetic branch. Null mode remains the original operations. Only the wide mode declares or uses the signed64 state. Use existing public `mozilla::SafeAdd` from `mozilla/CheckedArithmetic.h`; preserve CheckedInt for the rare narrowing checks if that keeps the patch smaller.

For an addition to the two wide doc coordinates:

```cpp
int64_t nextX, nextY;
if (!SafeAdd(wideDocX, int64_t(position.x), &nextX) ||
    !SafeAdd(wideDocY, int64_t(position.y), &nextY)) {
  return GetTransformMatrix(aViewportType, aStopAtAncestor, aOutAncestor,
                            aFlags);
}
wideDocX = nextX;
wideDocY = nextY;
```

The cross-document addition and addDocOffset offset updates use the same checked pattern. Never execute signed64 `+=` first and check afterward. Preserve the existing scale call on a narrowed nsPoint when APD differs.

Within CommonLayout only, get positions with GetPosition, and simplify shouldStopAt to IsTransformed. Generic mode keeps the entire original stopping expression. The existing target comparison remains outside and before shouldStopAt. Keep canUseAppUnits and all boundary invalidations; CommonLayout is not equivalent to exact eligibility.

The SVG equivalence is:

```cpp
!frame->HasAnyStateBits(NS_FRAME_IS_SVG_TEXT | NS_FRAME_SVG_LAYOUT)
```

No production patch, build, or assembly accompanies this sketch. Source-operation equivalence is explained in REPORT.md. Full compilation may reveal integration issues; optimization may already remove some v2 overhead.
