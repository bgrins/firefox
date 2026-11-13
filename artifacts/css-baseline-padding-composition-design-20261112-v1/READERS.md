# Source map and remaining consumers

Local identities are in INPUTS.json. Locations below describe the frozen containing-block candidate, not current line numbers on upstream. Searchfox files are discovery receipts with their original output; they do not replace the local source authority. Queries are bounded inventories, not a whole-program completeness proof.

| Boundary | Frozen source / receipt | Migration consequence |
| --- | --- | --- |
| Full computed storage, getters, independent setters | ReflowInput.h, `SizeComputationInput`, lines 79–132 | Replace both authorities and operations; promotion after `mComputedBorderPadding - mComputedPadding` is too late. |
| Raw selected padding, baseline additions, border composition, cache | ReflowInput.cpp, `InitOffsets`, lines 2447–2549 | Full reset first; at most one new adjustment per axis; cache must be exact too. |
| Style/table padding provider | ReflowInput.cpp, `ComputePadding`, lines 2869–2902 | Table row/column families zero; dependent style branch floors negative resolved values; full assignment in all branches. Earlier resolution remains open. |
| Computed size plus side helpers and resize predicates | ReflowInput.h, lines 407–411, 847–854 | Bounded side sums do not prove arbitrary content plus sides fits signed128; comparison rearrangements and size construction are different obligations. |
| Used property and virtual access | nsIFrame.h, lines 1447, 1662–1673; nsIFrame.cpp, `GetUsedPadding`, lines 1667–1696 | One exact cache; preserve theme-before-cache, first-reflow/SVG, virtual table behavior, no narrow composition. |
| Restyle reconstruction | RestyleManager.cpp, lines 1033–1036 and 1047–1050 | Both parent and optional containing-block copies must preserve exact padding and border-padding. Subsequent narrow size operations remain open. |
| Reflow-root feedback | pres-shell-source.txt, `PresShell::DoReflow` | Resolved used padding passed back as input override; per-invocation bound is insufficient after widening this edge. |
| Baseline measuring key | grid-other-reader-source.txt | Raw signed32 baseline property is part of key equality, separate from adjusted padding. |

The indexed setter closure lists ten `SetComputedLogicalPadding` matches (including declaration) and five border-padding setter matches. Padding writes in `ComputePadding` and `InitOffsets` plus the two RestyleManager contexts are the immediate migration set. Field searches also identify a direct `mComputedBorderPadding` argument to `nsIFrame::ComputeSize` in ReflowInput; that provider signature must eventually change, not receive a narrow facade.

The logical border-padding reader query has 67 matches across generic block/flex/grid/inline/ruby/line layout, absolute positioning, forms, video, table wrappers, PresShell, RestyleManager and XUL. Their storage copies and size arithmetic are required downstream work. The separate exact computed-size/provider migration remains necessary.

Used-padding readers have terminal CSSOM conversion, ResizeObserver sizing, StickyScrollContainer bounds, flex overflow inflation, background/painting/display-list geometry, and logical helpers. Logical padding adds AbsoluteContainingBlock, nsBlockFrame and nsFloatManager consumers. The getter does not apply skip sides; callers currently decide which sides to skip. An exact replacement must preserve that division of responsibility.

The table overrides in retained indexed source are explicit: ordinary nsTableFrame delegates; collapsed table, nsTableRowFrame and nsTableRowGroupFrame return zero. A shared nonvirtual helper cannot bypass these results.

Source compatibility is not a theorem that all observers should use baseline-adjusted padding under every theme/cache state. Those semantics must remain visible while the arithmetic representation changes. General geometry/transforms, rendering/overflow/sticky, fragmentation and exact provider acquisition remain part of the full objective.
