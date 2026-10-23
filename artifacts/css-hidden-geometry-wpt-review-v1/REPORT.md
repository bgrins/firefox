# Hidden flex geometry WPT review and additions

## Recommendation

Ready for root-owned baseline/candidate execution and targeted WPT lint. This is a source/oracle review and test delivery, not runtime acceptance of the proposed repair. `TESTS.json` binds three files and exact per-file rosters: **124 tests = 48 + 32 + 44**. No production files were changed and no browser or Gecko build was run for this artifact.

The retained 48-test file is byte-identical to `css-hidden-geometry-release-key-review-v1/hidden-flex-item-measuring-reflow.html`. Root separately reports its baseline as 40 PASS / 8 FAIL; this artifact does not reclassify those outcomes or independently rerun them.

## Existing 48 tests

The test crosses nested/direct targets, append/prepend, three flex sizing policies, hidden/visible and bounding/offset APIs. It captures warm, visibility, insertion, removal and shown stages before asserting. Each stage takes three target reads before querying a separate visible reference; all reference calibrations are checked before target comparisons. The fixed container and noncollapsing geometry avoid making previous declarations or skipped intrinsic container size the oracle. No source or assertion blocker was found.

## Fixed-size 32 tests

`hidden-flex-fixed-size-query.html` converts the original `css-hidden-geometry-probe-v1` fixture: flex/block, columns/no columns, initially hidden/visible and bounding/client-rect/offset/scroll APIs. Fixed 24 by 32 pixel items are checked through initial, hide, append, second append and show stages, preserving the original outer-flush ordering. Block and visible cases are controls. These cases cover the additional fixed-size failures exposed by the containing-block measuring key; they do not imply that removing that necessary key is a repair.

## New placement and descendant tests

`hidden-flex-skipped-positions.html` contains:

- 16 item/leaf placement cases: append/prepend, one/two hidden ancestors and visible controls. A 40-pixel item centered in 200 pixels starts at 80 relative pixels; inserting a 20-pixel sibling moves it to 70 or 90. Removing the sibling restores 80. Leaf margins add exactly 3 and 4 pixels.
- 16 parent-mutation cases: width, height, margin and padding changes after warming and hiding the leaf. Changes target the parent only, then the outer layout is queried before the leaf. Height changes are observed through the leaf's 40% height. Sibling insertion and showing follow. These are candidate dirty-history challenges, not a claim that JavaScript establishes an already-dirty parent with a provably clean descendant.
- 4 anonymous text-item cases: direct text creates an anonymous flex item. Ahem is explicitly loaded and its availability asserted; a Range observes both text position and 40 by 20 pixel size. Visible controls calibrate font metrics and geometry.
- 8 positioned-child cases: static-position center/end and explicit offsets, with one/two hidden ancestors and visible controls. Positioned children do not participate in flex sizing. The positioned subject fixes the containing block equally in hidden and visible cases. The static child starts at relative x=94 and moves to 188 with end alignment; explicit offsets remain (7,9). In-flow sibling insertion must not change either static center or explicit offsets.

Each stage collects three target observations before the visible reference. Test support and font checks fail explicitly rather than skip. No tolerance hides a position discrepancy. The anonymous Range cases need actual browser calibration before being treated as repair evidence.

## Primary specification basis

Content visibility can skip descendant work, but geometry queries require the relevant geometry. CSS Containment's hidden-measurement discussion and nested forced-query example support testing this distinction; the example itself is illustrative, not a replacement for the CSSOM algorithms. Fixed outer dimensions and an explicit positioned containing block keep the reference equivalent despite hidden containment. [CSS Containment 2](https://drafts.csswg.org/css-contain-2/#content-visibility)

Center/end free-space placement, anonymous text items, and the special static position of absolutely positioned flex children provide the independent numeric oracles. The positioned child is treated as the sole fixed-size item for its main-axis static position. [Flex layout](https://drafts.csswg.org/css-flexbox-1/#justify-content-property), [positioned children](https://drafts.csswg.org/css-flexbox-1/#abspos-items)

The observer is the current border-box geometry returned by client rectangles, with Range geometry used only for text; offset and scrolling dimensions are separately checked in the fixed-size tests. [CSSOM View client rectangles](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), [bounding rectangle](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect)

Primary pages were checked through web access. The local `webspec-index` executable was unavailable; no installation or build was attempted. Searchfox discovery outputs and three representative existing tests are retained. `REGRESSIONS.json` supplies 12 focused existing paths; preserve exact baseline failures and harness outcomes rather than assuming they all pass.

## Native scope and remaining gates

The proposed skipped `ReflowChildren` branch marks principal children. Its helper has an already-dirty early return, so neither the helper name nor these histories proves all descendant dirty bits. Append/prepend tests aim at stale placement even on a valid measuring hit; nested and parent-style tests challenge descendant forcing. These tests do not cover all continuation ownership, external containing-block out-of-flow frames, every child list, callbacks, or frame lifetime. Ordinary anonymous and same-containing-block positioned children provide bounded coverage, not a universal ownership theorem.

`collect-rosters.cjs` parses and executes only registration-level script code with stubbed `test`/`promise_test`; it never invokes their callbacks. It checks exact counts and unique names. The 124 expected PASS entries remain proposed runtime assertions. Root must run the files, distinguish failed reference/support calibration from target failures, lint, and retain per-phase native/source/binary pins before drawing a repair conclusion.
