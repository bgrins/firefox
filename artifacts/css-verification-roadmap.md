# CSS and Stylo verification roadmap

Continue finding observable CSS/Stylo bugs, verifying relevant models and code, and preparing independently reviewable local fix-and-test commits. Research precedes production repairs. Keep work local; no push, Try run or external submission.

## Current position — November 5, 2026

The catalogue contains 163 committed browser repair entries, including held #160 and excluding #120. This is not a count of newly discovered upstream issues. The generic ArcSlice library repair is recorded separately. See css-all-work-readout-20261105-v13/README.md for all commits, priorities and qualifications.

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
| 1af64611c836 | Incremental candidate and occurrence fixture preparation |
| 3c2e1969bcc7 | Incremental Lean proof, occurrence diagnostic and delivery prerequisites |
| dd570d6fbecc | Incremental native validation, fresh cost comparisons and restoration |
| 92f6b0e80e36 | Actual repeated-source diagnostic and owner-map dedup refinement |
| c1209aa91006 | Final same-rule native validation, comparisons, lint and delivery decision |
| 0f18d294fbac | Same-rule rollback fix: two Rust files and three WPT changes (#164) |

The original Bloom milestones 1–6 remain conditional results at their recorded revisions. The standalone CSS Lean repository remains at 162b20fb7c53a0ab89b20875a965baee98fb66bb. No whole-CSS or whole-Stylo verification is claimed. Historical detailed milestones remain under css-continuation-roadmap-20261104-v278.

## Next work, in order

1. Review held #160's producer-local handoff and dependency-drain repair with its root-self prerequisite. The completed bounded causal experiment already explains the historical broad-handoff timeout; do not repeat it. Full native scheduling refinement and global convergence remain unproved.
2. Publish completed root-self font animation, CSSOM stylesheet-move, and shared-media/scope-cache repairs in separate fix-and-WPT commits after prerequisite review. Root-self comparison improved 120 PASS / 9 FAIL to 129 PASS. Keep canvas substitution pending its compatibility decision.
3. Follow up the committed same-rule fix's dense-case allocation cost and isolated upstream readiness. #164 explicitly requires #163; the five-file source patch is not independently cherry-pickable onto the pre-project ancestor. Dense Rule256 remains 25.27–25.80 microseconds/update versus 10.43–10.94 baseline. Single-trigger256 is 8.61–9.00 versus 8.44–8.85. These are bounded synthetic comparisons, not release-page estimates. Profile many-longhand cases before claiming a general allocation or performance improvement.
4. Continue broader Arc/DST verification: allocation, provenance, cross-language transfer and shared-UA serialization remain separate from the committed empty-allocation fix.
5. Expand the CSS model where it resolves implementation questions. Preserve spec provenance, assumptions, counterexamples, matched browser comparisons and unresolved specification issues. A theorem about a model does not establish whole-native correctness.

## Completed rollback evidence

#163 changed the exact A16+B16+D48 roster from 74 PASS / 6 FAIL to 80 PASS, preserving every prior pass. Existing controls retained five passing assertions, two known cycle failures, three OK harness completions and one passing crashtest. Raw-event checks and independent restoration passed. The exact patch passes WPT lint/configured Rustfmt and applies to the retained October pre-project ancestor; no isolated latest-upstream runtime is claimed. See css-rollback-current-comparison-v1 and css-rollback-delivery-v1. The two interacting defects require shared cumulative state; historical partial repairs regress one another.

The held C comparison used #163 on both sides: baseline 162 PASS / 28 FAIL became 190 PASS, preserving every prior pass. Failures comprise twelve held D rows, eight logical/physical rows and eight substituted longhand/shorthand rows; these are manifestations of one existing lead, not 28 bugs. Canvas checks passed both roles. Full regression-control signatures stayed identical. Both builds, integrated raw/BuildID checks, and independent restoration audits passed. Sources, the ArcSlice patch, Git state, 9,378 application entries and three extra files were preserved. Owned process groups are absent and both approximately 1 GB backups were removed. See css-rollback-c-comparison-v1 and css-rollback-c-restoration-audit-v1.

The consumer proof bridges strict representative updates, the longhand bit/map gate and guarded streams to region deletion. The C proof adds the correct fast-bit union invariant and identity gate/update correspondence, retaining flags in normalized priority equality. Root read both proofs and authenticated their inputs. The ownership audit follows nine pinned native/library files through nonempty ThinVec allocation, locks and original-reference preservation. Provider/order/substitution correctness, semantic occurrence identity and native memory safety remain explicit boundaries.

#164 now packages the owner-map dedup implementation selected after the incremental and eager-index alternatives. It preserves all 190 prior correctness and six occurrence passes, with exact five-PASS/two-known-FAIL controls. All six external executions in its fresh comparison closed successfully; the independent restoration audit had no missing process receipts or observation errors. The original C comparison's 28 failures are manifestations of this same-rule lead, not 28 new defects. The native-tested Rust bytes are committed unchanged; one existing WPT help anchor was corrected without changing executable test code. See css-revert-rule-owner-map-dedup-assessment-v1 and css-revert-rule-production-validation-v1/DECISION.md.

Twenty incremental-index axiom audits and twelve owner-map refinement audits passed. The latter erases empty-block visited state and proves owner-map/cursor equivalence across arbitrary finite lookup histories under unique ownership and whole-block indexing. A separate diagnostic build produced 24 complete, uncapped rosters, with twelve nonadjacent same-raw-priority storage-sharing witnesses and twelve independent-control rosters without them. Context attribution is transport-only; universal semantic occurrence identity, provider coverage and native memory behavior remain explicit boundaries. See css-revert-rule-occurrence-diagnostic-assessment-v1 and css-revert-rule-owner-map-dedup-lean-v1.

## ArcSlice and housekeeping

The committed empty-ArcSlice repair has an in-crate regression test, strict Miri comparisons, C++ alignment checks, a kernel-checked layout model and a successful native build. No browser-reachable over-aligned element type is known, so no unrelated WPT was added and the browser-entry count was not increased.

The fresh baseline build in css-rollback-performance-baseline-build-v1 includes both the committed ArcSlice and cumulative rollback repairs at 2d867102694a. The cold-C performance owner restored that exact application and the committed sources; independent restoration audit and the final baseline browser run passed. That restoration was the experiment baseline, not the current installed application. The later committed build in css-same-rule-committed-build-v1 successfully rebuilt Nightly.app from #164 and intentionally leaves the same-rule fix installed for manual testing.

All completed native/browser experiments are closed. Signing failures, the early sandbox recovery and formatter incident remain retained historical evidence. Use explicit file selections for commits and scoped formatter paths. Do not run bare mach format on this long research branch. Remove owned build targets, temporary profiles and backups only after their processes close and required evidence is retained. The old D64 probe is preserved in css-rollback-probe-preservation-v1; the committed D48 file is the tested #163 delivery.
