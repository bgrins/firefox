# CSS and Stylo verification roadmap

Continue finding observable CSS/Stylo bugs, verifying relevant models and code, and preparing independently reviewable local fix-and-test commits. Research precedes production repairs. Keep work local; no push, Try run or external submission.

## Current position — November 5, 2026

The catalogue contains 162 committed browser repair entries, including held #160 and excluding #120. This is not a count of newly discovered upstream issues. The generic ArcSlice library repair is recorded separately. See css-all-work-readout-20261104-v12/README.md for all commits, priorities and qualifications.

Signing resumed successfully. New signed commits are:

| Commit | Content |
| --- | --- |
| 92bb75455480 | Recovery audit and roadmap |
| dfddd364baf6 | Empty ArcSlice research and validation |
| 836b5a688284 | Three-file empty ArcSlice repair with in-crate Rust test |
| 407a423cb4e6b | Cumulative rollback research, proofs and browser comparisons |
| e63fc6b1892b | Cumulative rollback repair: two Rust files and three WPTs (#163) |
| 4291dff2735a | Same-rule rollback comparisons, ownership model and pending benchmark |
| 11496220b9fb | Completed cold-C timing comparison, fresh baseline build and restoration evidence |
| 8b26f6a764bf | Indexed C alternative and checked owner-index/list-set equivalence proof |
| 85e24df1f696 | Indexed native build, 190-case correctness, controls and short timing validation |
| 397ba5f922c9 | Completed long-chain and single-trigger A–B–B–A comparisons |

The original Bloom milestones 1–6 remain conditional results at their recorded revisions. The standalone CSS Lean repository remains at 162b20fb7c53a0ab89b20875a965baee98fb66bb. No whole-CSS or whole-Stylo verification is claimed. Historical detailed milestones remain under css-continuation-roadmap-20261104-v278.

## Next work, in order

1. Reduce the indexed same-rule rollback candidate's first-trigger cost and finish identity coverage. The full 190 assertions and exact historical controls pass. Longer A–B–B–A measurements now quantify residual overhead: at 256 Rule-chain entries, indexed medians 24.648–26.016 microseconds/update versus 10.742–10.762 baseline; with one Rule and 256 unrelated payload blocks, 16.504–16.523 versus 8.867–8.965. Controls remain close and all value/report checks and independent restoration audits pass. These are bounded synthetic results, not general Firefox slowdown estimates. See css-revert-rule-indexed-long-cost-comparison-v1 and css-revert-rule-indexed-single-trigger-comparison-v1/ASSESSMENT.md. An incremental source-owner index with a property/full-priority exclusion gate is prepared and source/format checked in css-revert-rule-incremental-index-candidate-v1; native validation is pending. It uses flat full keys plus prefix membership, avoiding an inner-set allocation per longhand. Assess allocation tradeoffs for many longhands too. The occurrence audit confirms cache-cloned sheet wrappers can share declarations but found no differing result. Six occurrence fixtures are prepared in css-revert-rule-occurrence-fixtures-v1 for selector copies, nonadjacent cache clones, mixed importance and mutation coverage without forcing CSSOM uniqueness. They are not yet browser-validated; actual pointer sharing remains a separate diagnostic obligation. Existing fourteen-theorem index/list proof retains unique-entry ownership and coverage assumptions. New implementation and browser results must precede promotion; completed owners are closed and must not be rerun.
2. Prepare the C-only fix atop #163 after performance and remaining identity review. Keep its two Rust files, C/substitution WPTs and D48-to-D64 expansion together. Supporting proofs and diagnostics are committed in the preceding research. Preserve existing probe bytes until their role is resolved.
3. Review the held #160 producer-local handoff and dependency-drain repair with its root-self prerequisite. The completed bounded causal experiment already explains the historical broad-handoff timeout; do not repeat it. Full native scheduling refinement and global convergence remain unproved.
4. Publish completed root-self font animation, CSSOM stylesheet-move, and shared-media/scope-cache repairs in separate fix-and-WPT commits after prerequisite review. Root-self comparison improved 120 PASS / 9 FAIL to 129 PASS. Keep canvas substitution pending its compatibility decision.
5. Continue broader Arc/DST verification: allocation, provenance, cross-language transfer and shared-UA serialization remain separate from the committed empty-allocation fix.
6. Expand the CSS model where it can resolve implementation questions. Preserve spec provenance, assumptions, counterexamples, matched browser comparisons and unresolved specification issues. Do not count a theorem about a model as verified native behavior.

## Completed rollback evidence

#163 changed the exact A16+B16+D48 roster from 74 PASS / 6 FAIL to 80 PASS, preserving every prior pass. Existing controls retained five passing assertions, two known cycle failures, three OK harness completions and one passing crashtest. Raw-event checks and independent restoration passed. The exact patch passes WPT lint/configured Rustfmt and applies to the retained October pre-project ancestor; no isolated latest-upstream runtime is claimed. See css-rollback-current-comparison-v1 and css-rollback-delivery-v1. The two interacting defects require shared cumulative state; historical partial repairs regress one another.

The held C comparison used #163 on both sides: baseline 162 PASS / 28 FAIL became 190 PASS, preserving every prior pass. Failures comprise twelve held D rows, eight logical/physical rows and eight substituted longhand/shorthand rows; these are manifestations of one existing lead, not 28 bugs. Canvas checks passed both roles. Full regression-control signatures stayed identical. Both builds, integrated raw/BuildID checks, and independent restoration audits passed. Sources, the ArcSlice patch, Git state, 9,378 application entries and three extra files were preserved. Owned process groups are absent and both approximately 1 GB backups were removed. See css-rollback-c-comparison-v1 and css-rollback-c-restoration-audit-v1.

The consumer proof bridges strict representative updates, the longhand bit/map gate and guarded streams to region deletion. The C proof adds the correct fast-bit union invariant and identity gate/update correspondence, retaining flags in normalized priority equality. Root read both proofs and authenticated their inputs. The ownership audit follows nine pinned native/library files through nonempty ThinVec allocation, locks and original-reference preservation. Provider/order/substitution correctness, semantic occurrence identity and native memory safety remain explicit boundaries.

## ArcSlice and housekeeping

The committed empty-ArcSlice repair has an in-crate regression test, strict Miri comparisons, C++ alignment checks, a kernel-checked layout model and a successful native build. No browser-reachable over-aligned element type is known, so no unrelated WPT was added and the browser-entry count was not increased.

The fresh baseline build in css-rollback-performance-baseline-build-v1 includes both the committed ArcSlice and cumulative rollback repairs at 2d867102694a. The cold-C performance owner restored that exact application and the committed sources; independent restoration audit and the final baseline browser run passed. Same-rule C remains absent from the restored application.

All completed native/browser experiments are closed. Signing failures, the early sandbox recovery and formatter incident remain retained historical evidence. Use explicit file selections for commits and scoped formatter paths. Do not run bare mach format on this long research branch. Remove owned build targets, temporary profiles and backups only after their processes close and required evidence is retained. The old D64 probe is preserved in css-rollback-probe-preservation-v1; the committed D48 file is the tested #163 delivery.
