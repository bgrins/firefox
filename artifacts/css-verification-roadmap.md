# CSS and Stylo verification roadmap

Continue finding observable CSS/Stylo bugs, verifying relevant models and code, and preparing independently reviewable local fix-and-test commits. Research precedes production repairs. Keep work local; no push, Try run or external submission.

## Current position — November 10, 2026

The catalogue contains 168 committed browser repair entries, including held #160 and excluding #120. This is not a count of newly discovered upstream issues. The generic ArcSlice library repair is recorded separately. See css-all-work-readout-20261110-v16/README.md for all commits, priorities and qualifications.

Signing resumed successfully. New signed commits are:

| Commit | Content |
| --- | --- |
| b8d134179280 | Animation obligation conservation: 30 checked theorems, eight negative controls and native hint-posting boundaries |
| 191083fb76eb | Typed stateful CSS escape derivation: full-result proof, 18 examples, 12 controls and independent source-only replay |
| 8424404304d6 | Implicit-scope host-context cache repair: one Rust file and two WPT resources (#169) |
| 6f9376f98c47 | Current host-context build and 14-assertion combined comparison |
| 8ffd094be532 | Implicit-scope stylesheet-index cache repair: one Rust file and three WPT resources (#168) |
| 919fcb04ddfe | Current index comparison, Nightly exposure and replayed scope/vector-key proofs |
| aadc64afe8b7 | Frozen-rule derivation benchmark: two checked predicates, held-out consumption refused, independent source-only replay |
| ed8bce6fa5d7 | Preserve stylesheet CSSOM state during moves: five native files and seven WPT resources (#167) |
| b86cd38915d8 | Exact filtered stylesheet-move validation and shared-media interaction controls |
| 0aec45242b12 | Per-entry media applicability repair: three Rust files and five WPT resources (#166) |
| 1635894bbdde | Fresh shared-media comparisons, source review and upstream applicability |
| fac90af04d60 | Source-only shared-media rebase preserving current root-identity and rollback repairs |
| 664b08bcb7ce | Root-animation identity repair: one Rust file and four WPT resources (#165) |
| acece22fa877 | Fresh root-identity build, installed Nightly baseline and 47 passing candidate assertions |
| de2f6ccd1a1a | Independent source-linked CSS Syntax to Lean derivation prototype |
| 935c1e2916dc | Retained root-identity comparison and fresh local baseline |
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

1. Review held #160 as a combined producer-local handoff and dependency-drain repair. The producer-only comparison is already complete: A and B both retained 137 PASS / 27 FAIL; combined C passed 164. The completed causal trace explains the historical broad-handoff timeout; do not repeat either experiment. Full native scheduling refinement and global convergence remain unproved. The new obligation-conservation model separately accounts for queued requests, hints, in-flight work, installation and justified retirement, preserving full pseudo/cascade/generation identity. Its 30 theorems and eight negative controls pass, but native generation/coalescing and failed-post retirement are still explicit mapping obligations. Next, use a finite fixture and the producer-local combined candidate for a request-to-installation ledger, including actual hint-post outcomes; do not repeat the broad-handoff timeout. Root-self identity is now committed separately as #165.
2. Review standalone readiness of the newly committed stylesheet repairs. #166 passes 47 assertions plus a rendering reference test; #167 passes its exact 31-assertion delivery/control selection and preserves eight shared-media checks. Both defect signatures also reproduce in installed Nightly. The move patch needs the recorded context-only upstream adaptation; neither has an isolated upstream native build. Keep canvas substitution pending its compatibility decision.
3. Follow up the committed same-rule fix's dense-case allocation cost and isolated upstream readiness. #164 explicitly requires #163; the five-file source patch is not independently cherry-pickable onto the pre-project ancestor. Dense Rule256 remains 25.27–25.80 microseconds/update versus 10.43–10.94 baseline. Single-trigger256 is 8.61–9.00 versus 8.44–8.85. These are bounded synthetic comparisons, not release-page estimates. Profile many-longhand cases before claiming a general allocation or performance improvement.
4. Continue broader Arc/DST verification: allocation, provenance, cross-language transfer and shared-UA serialization remain separate from the committed empty-allocation fix.
5. Review and extend the separately versioned stateful derivation experiment. The typed escape program now has complete scalar/remainder/EOF-error correspondence, caller-domain conditions, 18 examples and 12 negative controls. Frozen transfer to consume-number was refused at its result interface. Before extending to decimal/exponent parsing, decide whether a first-order expression/statement IR and checked lowering would reduce the present higher-order/manual boundary. Keep numeric semantics explicit; do not add arbitrary loop fuel. See css-spec-stateful-derivation-20261110-v1/REPORT.md. Source interpretation, general translator correctness and native refinement remain unproved.

## Completed rollback evidence

#163 changed the exact A16+B16+D48 roster from 74 PASS / 6 FAIL to 80 PASS, preserving every prior pass. Existing controls retained five passing assertions, two known cycle failures, three OK harness completions and one passing crashtest. Raw-event checks and independent restoration passed. The exact patch passes WPT lint/configured Rustfmt and applies to the retained October pre-project ancestor; no isolated latest-upstream runtime is claimed. See css-rollback-current-comparison-v1 and css-rollback-delivery-v1. The two interacting defects require shared cumulative state; historical partial repairs regress one another.

The held C comparison used #163 on both sides: baseline 162 PASS / 28 FAIL became 190 PASS, preserving every prior pass. Failures comprise twelve held D rows, eight logical/physical rows and eight substituted longhand/shorthand rows; these are manifestations of one existing lead, not 28 bugs. Canvas checks passed both roles. Full regression-control signatures stayed identical. Both builds, integrated raw/BuildID checks, and independent restoration audits passed. Sources, the ArcSlice patch, Git state, 9,378 application entries and three extra files were preserved. Owned process groups are absent and both approximately 1 GB backups were removed. See css-rollback-c-comparison-v1 and css-rollback-c-restoration-audit-v1.

The consumer proof bridges strict representative updates, the longhand bit/map gate and guarded streams to region deletion. The C proof adds the correct fast-bit union invariant and identity gate/update correspondence, retaining flags in normalized priority equality. Root read both proofs and authenticated their inputs. The ownership audit follows nine pinned native/library files through nonempty ThinVec allocation, locks and original-reference preservation. Provider/order/substitution correctness, semantic occurrence identity and native memory safety remain explicit boundaries.

#164 now packages the owner-map dedup implementation selected after the incremental and eager-index alternatives. It preserves all 190 prior correctness and six occurrence passes, with exact five-PASS/two-known-FAIL controls. All six external executions in its fresh comparison closed successfully; the independent restoration audit had no missing process receipts or observation errors. The original C comparison's 28 failures are manifestations of this same-rule lead, not 28 new defects. The native-tested Rust bytes are committed unchanged; one existing WPT help anchor was corrected without changing executable test code. See css-revert-rule-owner-map-dedup-assessment-v1 and css-revert-rule-production-validation-v1/DECISION.md.

Twenty incremental-index axiom audits and twelve owner-map refinement audits passed. The latter erases empty-block visited state and proves owner-map/cursor equivalence across arbitrary finite lookup histories under unique ownership and whole-block indexing. A separate diagnostic build produced 24 complete, uncapped rosters, with twelve nonadjacent same-raw-priority storage-sharing witnesses and twelve independent-control rosters without them. Context attribution is transport-only; universal semantic occurrence identity, provider coverage and native memory behavior remain explicit boundaries. See css-revert-rule-occurrence-diagnostic-assessment-v1 and css-revert-rule-owner-map-dedup-lean-v1.

## ArcSlice and housekeeping

The committed empty-ArcSlice repair has an in-crate regression test, strict Miri comparisons, C++ alignment checks, a kernel-checked layout model and a successful native build. No browser-reachable over-aligned element type is known, so no unrelated WPT was added and the browser-entry count was not increased.

The fresh baseline build in css-rollback-performance-baseline-build-v1 includes both the committed ArcSlice and cumulative rollback repairs at 2d867102694a. The cold-C performance owner restored that exact application and the committed sources; independent restoration audit and the final baseline browser run passed. That restoration was the experiment baseline, not the current installed application. The later committed build in css-same-rule-committed-build-v1 successfully rebuilt Nightly.app from #164 and left the same-rule fix installed at that checkpoint.

All completed native/browser experiments are closed. Signing failures, the early sandbox recovery and formatter incident remain retained historical evidence. Use explicit file selections for commits and scoped formatter paths. Do not run bare mach format on this long research branch. Remove owned build targets, temporary profiles and backups only after their processes close and required evidence is retained. The old D64 probe is preserved in css-rollback-probe-preservation-v1; the committed D48 file is the tested #163 delivery.

The November 10 native build now leaves the #165 root-identity repair installed in the local Nightly.app. The build source and binary hashes, 47 passing assertions, two matched baseline pages and installed Nightly comparison are recorded in css-root-self-resume-20261110-v1. Its build metadata predates the final native commit; exact delivery bytes were verified. The independent spec-derivation replay and shared-media rebase used temporary directories that have been removed.

The later November 10 builds now leave #166 and #167 installed alongside #165. The two native repairs are separate signed commits, each preceded by current validation research. All selected WPT resources are committed. The exact filtered move candidate execution gap is closed; #160 remains held. Temporary upstream/source-only replay directories are removed after successful checks; the active objdir is retained for manual testing.

The subsequent scope-cache builds leave #168 and #169 installed too. The current branch comparison was 10 PASS / 4 FAIL before either repair, 12 PASS / 2 FAIL after index preservation, and 14 PASS after host-context keying, each with four OK harness endings. Installed Nightly reproduces all four scope failures. Each repair has its own native/WPT commit, with no sibling test mixed into it. The 34-theorem abstract key/vector replay and 12 rejected false claims are retained in the preceding index research; complete native cache correctness remains outside that model.

The stateful derivation artifact is committed as 191083fb76eb. Root independently replayed exactly 15 source/manifest files with no generated or compiled inputs; all 18 examples and 12 controls passed and consume-number remained unsupported. Both owned replay directories were removed. The canonical standalone library remains unchanged. Pinned verbatim specification snippets retain their source trailing blank lines; those two artifact whitespace diagnostics were not reformatted.

The obligation-conservation continuation changes research only; #160 stays held and the browser repair catalogue remains at 168 entries. No native build was needed. Successful proof scratch directories are removed. Saved raw Searchfox output and failed-attempt logs retain their original whitespace; authored Lean, Python and markdown pass scoped diff checks.
