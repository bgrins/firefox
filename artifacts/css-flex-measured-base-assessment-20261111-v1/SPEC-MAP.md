# Flex shrink cancellation: specification and implementation

Scenario: one unfrozen item with shrink factor1, a content-derived positive flex base, no margins/border/padding/gaps, min-block-size0 and a definite1000px container block size.

The current [flexible-length algorithm](https://drafts.csswg.org/css-flexbox/#resolve-flexible-lengths) chooses shrinking. The item's positive factor and base at least its hypothetical size do not trigger early freezing. With one item, its scaled shrink factor has ratio1. Step5.3 subtracts all negative remaining free space from the base, producing the container size; step5.4 does not change that positive size under these constraints. The zero violation then freezes the item, and step6 installs its used size. Expected result:1000px.

The retrieved spec section is retained in spec-section.md with its reported source hash. The anchor check exited0. Searchfox located the corresponding native distribution expression in FlexLine::ResolveFlexibleLengths and AuCoordImpl::ToMinMaxClamped. The local source differs from indexed upstream by the existing pending fixes; BEFORE-INPUTS.json pins the actual tested source.

| Source | Responsibility | Result |
| --- | --- | --- |
| FlexItem::SetFlexBaseSizeAndMainSize | Retain measured base and compute hypothetical size | The setter does not enforce the conditional Lean base<=preferredMax premise. |
| FlexLine::ResolveFlexibleLengths | Reset base, distribute sizeDelta, then clamp min/max | Narrowing sizeDelta before base cancellation explains the reproduced mismatch. |
| AuCoordImpl::ToMinMaxClamped | Clamp to preferred app-unit endpoints | The clamp applies to the adjustment independently of the base. |
| flex-shrink-large-content-base.html | Three writing modes, both column directions, four content sizes | Actual local run:18 FAIL,6 PASS. |

The initial broad Searchfox test lookup found ordinary flex shrink/wrapping tests but did not establish exhaustive coverage. No absence-of-metadata claim substitutes for runtime evidence. The planned repair will need the new WPT and neighboring sizing/overflow regressions.

Verdict: the specification requires the small target size in this scenario; the retained local test contradicts that result. The exact native integer trace and repair remain unfinished.
