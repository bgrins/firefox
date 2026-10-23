# Optional hidden flex descendant fragmentation diagnostic

## Decision and scenario

Ready for a separate root-owned calibration run; **not a new accepted bug or final WPT**. The current 124-test suite is untouched. `hidden-flex-fragment-query.html` registers four tests: flex/block outer container, natural/forced internal column break. No browser, native build, Git or production mutation occurred here.

The topology is fixed 220×40 outer container → fixed 220×40 two-column child → ordinary column-direction flex container → target flex item → two block chunks. Columns have width100 and gap20. The entire fragmentation context is below the element whose content visibility changes. The outer flex container itself is unfragmented, and its principal multicol child contains the fragmented descendant. The block outer variant controls the flex-specific skipped-layout branch.

The target is intentionally larger than one column: two40px chunks initially, then40px+20px with width changed100→80. It has no flex shrink, border, padding, margin or transforms. A forced-break variant additionally places break-before:column on the second chunk. A separate visible tree receives identical content/style mutations. The proposed exact calibration lists are:

- Initial: `(10,10,100,40)`, `(130,10,100,40)`.
- Changed: `(10,10,80,40)`, `(130,10,80,20)`.

Every stage asserts the visible target actually has more than one fragment and checks every rectangle against that list. Then all three reads of the hidden test target are compared. Stages are visible warm → hidden query → hidden descendant size change/query → shown query. Only the outer element is flushed before each target observation; the visible reference is queried afterward. A failed visible calibration is a fixture/fragmentation result, not evidence that the skipped-layout repair failed. These are exact diagnostic calibration conditions, not a claim that Flexbox defines every fragmented layout detail.

## Normative trace

1. Setting hidden enables containment including size containment; size containment boxes are monolithic. Consequently a flex container directly inside external columns cannot be expected to preserve the visible fragmented layout merely because its descendants are queried. This rejected topology would conflate containment semantics with stale continuations. [CSS Containment size containment](https://drafts.csswg.org/css-contain-2/#containment-size), [content visibility](https://drafts.csswg.org/css-contain-2/#content-visibility).
2. The chosen topology instead places every column inside the same fixed-size outer boundary. It does not cross that boundary, and hiding does not change the multicol child's explicit dimensions. Layout containment's fragmentation-boundary restriction therefore does not split this internal context. [Layout containment](https://drafts.csswg.org/css-contain-2/#containment-layout).
3. Flexbox allows breaks inside flex items and applies its fragmentation rules to columns. Its exact fragmented layout is not completely specified; the sample algorithm is informative. This is why the visible exact calibration is a separate prerequisite, not an inferred universal flex-fragment count. [Flex fragmentation](https://drafts.csswg.org/css-flexbox-1/#pagination).
4. getClientRects observes each box fragment in content order, including zero-sized fragments. The diagnostic does not discard extra or empty rectangles, sort them, or reduce them to a bounding box. [CSSOM View](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects).

**Verdict: INCONCLUSIVE pending visible calibration/runtime.** Equivalent internal layout is the intended relational oracle; no observed fragment list or native continuation reachability is asserted before execution. Passing all four tests would support this bounded descendant-continuation case, not a universal claim about skipped container continuations.

## Source connection and limits

Searchfox `nsIFrame::HidesContentForLayout` checks the element's hidden state and the pres-shell forced-layout override. The indexed `nsFlexContainerFrame::ReflowChildren` guard additionally excludes an existing next continuation. The local repair's retained source is separately bound by `css-hidden-geometry-skipped-layout-review-v1`; indexed versus local guard differences must not be silently merged. This fixture keeps the skipped outer container unfragmented, avoiding dependence on that guard difference, while arranging continuation-bearing descendants under its principal child.

The principal-child marking proposal may traverse descendants; the actual continuation tree and dirty propagation remain source/runtime questions. A multi-rectangle visible calibration establishes observable fragmentation, not a proof of the precise frame-tree dirty-bit transitions. Fresh reflow can replace continuations after hiding, so preservation of old frame identity is not an oracle. This test does not cover cross-parent continuation reparenting, fragmented hidden flex containers themselves, external out-of-flow frames, or all fragmentainers.

`existing-contain-size-multicol-004.html` is retained from Searchfox as the relevant monolithic size-containment control. For source audit, `HidesContentForLayout.txt` and `flex-hidden-search.txt` retain the narrow discovery results. Initial sandbox DNS attempts failed; authorized read-only retries succeeded. The primary specifications were verified through web access (local webspec-index was unavailable in the preceding review).

## Execution recommendation

Run these four cases independently before adding them to a final suite. Preserve exact test names, every failing assertion, and whether failure occurred in visible calibration versus target comparison. The block controls and shown stage must pass. If a geometry calibration fails, retain the result and inspect real fragments rather than dropping the >1-fragment assertion or accepting an arbitrary list. No runtime is needed to establish the warning against the rejected external-columns topology.
