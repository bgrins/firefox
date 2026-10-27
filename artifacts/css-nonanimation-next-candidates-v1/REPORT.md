Best next observable experiment: contained quote append invalidation.

This revisits an existing unaccepted prototype, not a new discovery. The current ledger has133 accepted/committed fixes and excludes held120; none of the three fixtures below occurs in its accepted new_queue. The unfinished-v3 snapshot retains all three source/test families. The older worktree reconciliation labels are historical readiness notes, not current acceptance. Six raw logs were independently recounted in RAW-RECOUNT.json; no browser or build was run.

1. Contained quote append — highest priority

Sources: layout/base/nsQuoteList.cpp and nsQuoteList.h; exact three-file patch artifacts/css-quote-scope-append-fix-v1/fix-candidate-v1.patch. Fixture: testing/web-platform/tests/css/css-contain/quote-scoping-append-invalidation.html. Recorded gates: artifacts/css-quote-scope-append-fix-v1/ROOT-NATIVE-WPT-v1.json; original/candidate raw files under css-quote-scope-append-probe-v1.

Actual64-case pair:52PASS/12FAIL →64PASS, one OK harness each. The simplest first-read witness is open-quote, seed0, direct child scope, no trailing quote, inserted before the child: initial40, mutated40, fresh120, afterFresh40, restored40 on original; candidate passes. This isolates stale child quote-depth delivery rather than a font failure or later fresh-construction flush. The patch retains immediate appended-node calculation but requests existing batched recalculation when the list has child scopes; leaf append keeps its fast path. Fifteen existing regression passes and three unchanged expected failures are recorded. Historical build passed; lint reported zero errors but exit1 for an ignored-WPT warning, not a clean exit0 lint claim.

Why unaccepted: independent native review and the promised scope/order/provider/dirty-delivery companion remain pending. No isolated-base build or performance measurement was recorded. The conservative child-presence test may dirty children preceding the append; this needs review, not a per-insertion subtree walk invented for the experiment.

Smallest decisive next experiment: after the current build finishes, review the two native hunks and their current transport, then run the existing single64-case WPT on exact scoped-original/candidate/restored bodies while preserving unrelated prototypes. Require12 calibrated historical repairs,52 identical controls and exact restored results; the fixture already covers all four quote operations, before/after insertion, nested/direct scopes, seed0/1, fresh equivalents and removal. No new fixture or controller architecture is needed. The snapshot already contains the candidate, so do not label a run of the current dirty browser an original baseline. The original phase must actually exclude only these two owned hunks, with matching built binaries. Fresh evidence supports readiness but does not substitute for the outstanding review/proof scope.

2. Named @page selector-list matching — narrow fallback option

Sources: servo/components/style/stylesheets/page_rule.rs::PageRule::match_specificity and stylist.rs::PageRuleMap; patch artifacts/css-page-selector-name-fix-v1/fix-candidate-v1.patch. Main fixtures: css/css-page/page-selector-list-name-applicability-print.html and page-selector-list-name-specificity-print.html, with their exact refs and unnamed-mixed control in that patch. Root evidence is ROOT-NATIVE-WPT-v1.json plus css-page-selector-name-probe-v1/ROOT-BASELINE-v3.json.

Actual18 print-reftest pair:8PASS/10FAIL →18PASS; six existing print tests pass on both builds. The applicability witness @page alpha:first, beta on an alpha document incorrectly moves page2 by96px; the raw report records800 differing pixels. Saved images show the400-pixel square at y96 instead of y0. The specificity witness prevents unmatched beta:first from raising the alpha rule's priority. Candidate filters members by the actual collection bucket name before taking matching specificity. This is observable print layout, not CSSOM parsing. Earlier v2 predictions were corrected; use v3 only.

Why unaccepted: independent name-bucket/specificity review and full collection/sorting/duplicate/important/layer proof scope remain pending. Transport was checked at two old bases but no isolated-base build or physical-printer claim exists. stylist.rs also contains other unaccepted work, so preserve all surrounding bytes.

Smallest decisive next experiment: first run the existing applicability and specificity print tests plus unnamed-mixed control as a three-test original/candidate/restored discriminator, with page2 output retained. Use the existing print runner's exact5x3in,96dpi,scale1/background/no-shrink settings. If proceeding to acceptance, retain all18 prepared cases and six regressions (cheap enough to reuse together) and require exact baseline restoration. Screen-only tests would not answer this question.

3. nowrap chunk publication — useful but more composition risk

Source: dom/base/nsLineBreaker.cpp; patch artifacts/css-nowrap-partitions-fix-v1/fix-candidate-v1.patch. Fixture: testing/web-platform/tests/css/css-text/white-space/nowrap-inline-break-policies.html. Root gates: artifacts/css-nowrap-partitions-fix-v1/ROOT-NATIVE-WPT-v1.json.

Actual169-case pair:133PASS/36FAIL →169PASS;724 regression subtests and17 harnesses pass on each side. A direct break-all/whole/normal-container/no-transform witness wraps into4lines instead of1. The patch affects the suppression helper and two publication sites; its original-source transport does not require the separate language/hyphenation patches. Browser evidence nevertheless used their combined worktree, which is the important limit.

Why unaccepted: independent native review and full sink/publication/invalidation companion remain pending. FORMAL-TARGET-DRAFT explicitly warns that publishing zero break values does not erase previously seeded glyph bits; arbitrary partition equivalence and cache-validity assumptions are not proved. This shared file also holds language and hyphenation candidates.

Smallest decisive next experiment: isolate only the suppression helper/publication hunks on a coherent current source snapshot and rerun the one169-case fixture before/candidate/restored, requiring36 repairs and133 unchanged observations. Follow with the existing724 regression set. If the source review finds mutation admission genuinely uncovered, add one style-toggle/reconstruction paired control for preseeded text runs before claiming dynamic correctness; do not claim a second bug from that unrun hypothesis.

Do not prioritize these alternatives first

The exact-size transport candidate repaired12/38 draft cases but still has numeric-precision and actual-child-output boundaries; the fragment candidate has recorded preservation regressions and shared ancestor arithmetic. They require a larger design decision than the three bounded candidates above. Old flex candidates labeled native-accepted/full-formal-pending are not permission to increase counts. The contextual steps/rounding feature prerequisites, accepted easing fixes and held120 are excluded here, as is the unresolved animated-provider scheduler. No new spec verdict, acceptance, security finding or universal performance claim is made.

All references are local existing evidence. No untouched-source search was needed: this assessment reads the exact modified prototype patches and their archived results. It does not claim current native bytes or newly built binaries were independently verified.
