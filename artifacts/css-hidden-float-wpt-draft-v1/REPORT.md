# Float owner query WPT draft

UNEXECUTED_DRAFT. No native/browser/build/Git action. Wait for the current main campaign's both outcome before considering any float candidate runtime.

## Main bounded file:12 tests

hidden-float-owner-queries.html covers direct float, placeholder nested through two ordinary inline spans, and float in a nested ordinary block owner; root and leaf queries; visible and hidden subject. Each independently starts at100px containing width, then narrows to50px. Float width50% gives50→25px; leaf width100% has the same width, with heights16px/8px. Positions stay10px,10px under fixed horizontal LTR, no fonts/borders/margins.

The only fixed-positioning device is the visible absolute host, to isolate document flow; the selected subject/float uses no absolute positioning. The subject itself is the hidden block. Inline-nested markup changes placeholder ancestry without introducing another block owner. Nested-block markup deliberately introduces a different Float-list owner.

Each test collects warm, hide, change, show, restore stages. A visible outer-only query flushes first; then the selected target's first and repeated reads occur before constructing/querying a fresh visible peer. Leaf tests never query the float root first. The show stage retains the narrowed width, so shown restoration checks25px rather than accidentally passing with the old50px geometry. The final restore returns width100 while visible.

All60 stage rows are collected before assertions in window.floatOwnerQueryResults. Every fresh peer and outer rectangle is calibrated; initial and shown target geometry are checked before selected-query assertions. Do not infer later assertion outcomes solely from the first WPT failure; capture raw rows where needed.

Nested-block cases are ownership/dependency controls: the float-only owner-list proposal may not execute inside an already skipped clean nested block. The separate skipped-line candidate can mark that block root and traverse its owned Float list. No expectation that float-only repairs all12 is asserted by this artifact. Tests state desired browser geometry, not a candidate-specific success quota.

## Separate visible-only calibration:4 tests

visible-float-push-calibration.html is NOT a gate for the main file. A40px column contains a0px or30px prelude and a10px or20px float with break-inside:avoid. The prefilled20px case hypothesizes pushing to the next column; three fit controls distinguish the size/column setup. Raw float fragment lists and computed breakInside are collected before assertions in window.visibleFloatPushResults.

This has not run. A matching rectangle does not prove NS_FRAME_IS_PUSHED_OUT_OF_FLOW was set, nor that a particular continuation remains in the owner's list. Failed hypothesis checks are calibration evidence, not an accepted float bug. A genuine pushed/continuation source trace or independently calibrated fixture remains required before claiming that branch covered. Do not add this speculative geometry to the all-tests-must-calibrate native campaign.

## Verification and provenance

Node parsed scripts and independently enumerated12+4 test registrations without executing any test callback, DOM, layout or browser. The first registration attempt lacked a window facade and failed with ReferenceError; it is retained as development failure, followed by corrected static-js-v2 output with explicit empty window facade. Syntax/roster checks are not browser calibration.

Source reasoning: css-hidden-float-readiness-audit-v1 FILES554db971a56f7ed21c776854c51260bf3633b5b40fd1c42ebe432674f2f6aba1; candidate css-hidden-float-owner-proposal-v1 FILESb9ce433cc0dfccda50b9ef602aca0a94f1b6c1e85395306bc827720a4d05a04c. Neither is broadened by this draft. No existing sealed fixture/assertion is edited.
