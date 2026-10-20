# DOMRect edge precision repair

Accept the two-file native/WPT repair after separate baseline, DOM-only,
integer-only and combined browser builds. DOMRect::SetLayoutRect already
calculates doubles, then narrows them through SetRect(float...). Direct double
setters preserve the existing endpoint rounding without that second loss.

The four-case WPT covers both axes and small/large identity-transformed boxes,
with host, marker, size and both rectangle API checks. Baseline has two failures;
DOM-only passes all four. The 66 existing regression subtests retain 64 passes
and two expected failures, and the reftest passes. Full raw records are retained.
The exact patch applies and reverses against both our branch and its upstream
base; source applicability does not imply an upstream runtime test.

The independent integer-translation repair is held: the six-run local benchmark
shows a deep transform-near-root cost of550ns/call versus400ns in all four
baseline runs. These are directional headless measurements with coarse timers,
not a CI performance result. The DOMRect fix does not add that traversal.

The formal companion proves selected numeric/grid relationships and exercises
complete extracted helpers. Native frame routing, universal IEEE behavior,
whole CSSOM semantics and the original full safe-origin obligations remain open.
DOM-only changes ResizeObserver.contentRect and can expose remaining graphics
rounding errors more directly; it does not improve every erroneous edge.

Research/evidence precede the standalone native/WPT commit. Nothing is pushed.
