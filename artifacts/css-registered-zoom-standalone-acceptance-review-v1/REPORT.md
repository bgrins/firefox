# Standalone zoom acceptance review

The seven-file proposal is not yet an accepted standalone fix. The current clean-HEAD/zoom-only comparison must finish before attributing its results independently of the admission overlay. The preceding nine-file experiment supports the implementation direction but cannot substitute for that comparison. Count remains137. This is bounded source/test review, not fresh browser execution or a proof of the native implementation.

## What the existing70 assertions establish

The56 assertions across four pages comprise26 scalar length/defaulting/inheritance cases,18 compound/list/transform/image cases,8 em/lh/rem/rlh cases and4 length style-range cases. The additional14 are6 paused-animation/commitStyles cases and8 number/angle/time/resolution style-range cases. Together they exercise direct versus substituted production, cross-zoom inheritance, selected fallbacks, invalid values, mixed percentages, root/font mutation, consumer CSSOM/layout and direct numeric query operands. The font-relative fixture already varies target zoom1/2/.5 with ancestorzoom2; that coverage is not missing. Animation additionally includes1.5.

The source boundary is coherent on the paths inspected: Value<Component> enters a nested/restored registered scope for computation; canonical length leaves avoid double scaling; custom-property CSSOM skips the ordinary unzoom step; style-range operands enter the same scope. Compound length leaves pass through the shared conversion rather than a blind numeric scaling of matrix coefficients. No concrete new defect was found in these seven files during this pass. This is not clearance of every image/animation/font-context producer.

All focused tests use six pages and cover70 named assertions, not70 distinct independent engine paths. The broad original/candidate comparison must still preserve its exact held-B messages and regression signatures. An assertion failure known to exist in both phases must remain visible; do not relabel the baseline as all-pass. Clean transport, appropriate lint and a standalone native-plus-WPT commit remain normal finishing work, not reasons for another broad verification project.

## Container source zoom remains an explicit decision

The container_rule change stores each physical dimension together with its selected source container's effective zoom, then divides by that zoom inside registered computation. cqmin/cqmax now operate on the individually normalized floating-point dimensions. Ordinary computation keeps the prior raw coordinate values. The124 diagnostic observations support this implementation: physical cases match the proposed per-source predictions, mutation results return to their starting values, and ordinary controls stayed unchanged. They do not establish the normative cross-zoom coordinate convention.

The captured official trace remains INCONCLUSIVE. Conditional5 supplies per-axis selection and content-box dimensions, and Viewport supplies element-relative unscaled output rules. The published chain does not explicitly identify the source coordinate conversion at the query-size read. Issue10268's resolution and proposed unscaled-bounds edit support the implementation inference; ordinary Firefox parity is not an oracle because of bug1894104. The Lean provenance model assumes the source dimension/zoom contract and exact scaling; the quantization model separately shows cancellation is not an exact native fact. Neither closes this missing specification step.

Before including this behavior in a landable seven-file fix, obtain an explicit CSS/layout review accepting the intended source-coordinate interpretation, or scope a different proposal that preserves a consistent representation without asserting that rule. This does not require waiting for verification of all CSS or necessarily for a published spec edit. The review description and tests must honestly identify the inference. Simply dropping container_rule.rs from this patch is not a safe mechanical split: specified/length.rs changes depend on its f64 return API, and the global registered CSSOM convention still affects container-derived values. A split requires source and behavior review, not removal of one filename.

## Small decisive additions with bounded oracles

These are focused WPT candidates, not extra gates on unrelated features. Their expected values avoid the disputed non-unit source zoom and the separate writing-mode scheduling lead.

1. Physical container units, source effective zoom1: a fixed200x120px size container, no ancestor zoom, child zoom1→2→.5→1, registered100cqw/100cqh. Expect canonical custom values and consuming widths200/120px; physical widths scale only with the child. Include direct and ready-substituted values in the same small test. Mutating the source width200→300→200 adds a cache/invalidation check with a clear oracle.
2. Per-axis merge and min/max with both source zooms1: horizontal outer size-container320x180, horizontal inner inline-size-container200x120, target explicitly horizontal. Width comes from the inner200px; height comes from the outer180px. Assert cqw/cqh=200/180 and cqmin/cqmax=180/200 while changing only target zoom. The sources have identical coordinate scaling, so this tests pairing/selection and the changed min/max path without deciding cross-zoom source normalization.
3. No eligible container: a fixed320x180 iframe, no size containers, physical100cqw/100cqh and independent100svw/100svh controls. Registered values should be320/180px across child zoom. This directly tests the canonical fallback path; avoid cqi/cqb to keep writing-mode readiness outside scope.

The first two do not exercise division by a non-unit source zoom. No additional number of these tests can settle that disputed rule; retain the existing cross-zoom observations separately until the interpretation is reviewed.

One cheap precision control is also useful before polishing a broad normalization claim: registered0.13px and -0.13px under fractional zoom1.5, read canonical CSSOM and consume through a negative-capable property such as margin-left. Do not derive layout equality from the formal exact-cancellation model; use the appropriate layout tolerance. This probes the bypassed scaling/serialization boundary, not an assertion that all quantized font-relative conversions are exact.

## Remove incidental churn

Two added semicolons in the anchor-positioning parse branches of specified/length.rs are unrelated formatting. The one-line reflow of to_computed_value_for_math in computed/length_percentage.rs is also unrelated. Remove these when preparing the final reviewed patch unless the repository formatter requires them; document formatter necessity if so. The container return-type/min/max edits and numeric style-range arms are semantic, not formatting-only.

The separate logical-unit scheduling defect and disputed genuine-cycle policy should remain separate work; passing a zoom patch does not fix them. This review does not request adding the new provider-readiness16 to the current frozen comparison or changing current metadata.

Read evidence: native patch21e3f2/0; rosters/spec trace31f488/0; actual relative/animation bodiesda66df/0; query/compound callchaind6d319/0; pinned primary clause reread143346/0. No live source/index/epoch/Git mutation, browser, build, fresh web fetch or acceptance change.
