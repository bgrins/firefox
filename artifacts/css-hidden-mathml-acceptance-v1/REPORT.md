# Hidden MathML query repair accepted

Root accepts fix110: mark the skipped MathML subtree dirty before the existing hidden-parent reflow return. Clean row and leaf frames otherwise retain stale query state after zero metrics are published.

The standalone patch contains one native line and the four-case WPT. On normalized committed source, two failures become passes and the two visible controls remain passing. Broader integration passes all299 subtests across18 files:79 existing hidden-query controls,8 MathML diagnostic cases and212 ordinary MathML cases. Sources, temporary tests, all925 staged payloads and rebuilt binaries were verified after restoration. Independent native and result review found no blocker. The existing build monitor KeyError remains in the logs alongside successful build exits.

The outer-block diagnostic cases remain integration controls, not part of the independently landable WPT. The Lean extension distinguishes equal-size/different-position rectangles and observes the provider's returned state; it does not prove Gecko's coordinate or lifetime implementation. Dirty-root pruning histories and performance bounds remain open. No security impact is established.

Research precedes the two-path native/WPT commit. Signing remains pending. The candidate is absent from the live tree at this acceptance checkpoint; a separate combined installation will record any subsequent change. Nothing was pushed.
