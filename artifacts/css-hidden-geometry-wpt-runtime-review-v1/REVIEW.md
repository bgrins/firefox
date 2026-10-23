# Independent four-phase hidden-flex runtime review

**ACCEPT_RUNTIME_EVIDENCE_WITH_EXPLICIT_RESIDUAL_FAILURE.** The four WPT phases and terminal restoration were independently checked against the frozen runtime package (FILES `0a542591b868f0ecb2444e4c399bbddc5b4a8501d8730541d31fb17d5eb57c02`, 297 authenticated payloads). No browser or build was invoked by this review. This validates the bounded experiment and does not constitute complete native acceptance.

| Phase | PASS | FAIL | Harness OK | Reftest PASS |
|---|---:|---:|---:|---:|
| Exact branch HEAD | 621 | 35 | 14 | 1 |
| HEAD plus hidden-return subtree mark | 655 | 1 | 14 | 1 |
| HEAD minus padding/containing-block key fields | 629 | 27 | 14 | 1 |
| Original key plus hidden-return subtree mark | 647 | 9 | 14 | 1 |

All phases have the same 656 unique subtest identities and all 15 expected test-end identities, with one suite_end. The three new test rosters contain exactly 48, 32 and 44 subtests. All four WPT processes exit 1 because failures remain; all four preceding builds exit 0. This is not an all-pass report.

The first pair fixes 34 failures and preserves 622 exact status/message pairs. The original-key pair fixes 18 failures and preserves 638 exact pairs. No PASS→FAIL or diagnostic-only change occurs within either pair. New-key removal leaves four percentage-padding and four table-caption tests failing identically before/after the marking repair; these are the intentionally removed independent cache-key repairs.

The eight original-field measuring tests fixed by both pairs include four direct item zero-size failures and four clean descendant stale-size failures. The ten additional position tests cover item/leaf insertion, parent margin/padding/width/height changes and anonymous-text insertion. Sixteen fixed-size tests additionally improve with the committed newer key. Keeping the original-key phases distinguishes the preexisting marking defect from failures exposed only by the new key.

One unchanged residual test fails in every phase: `Positioned child: oof-static, one hidden ancestor, hidden`. At in-flow insertion it expects `[104, 10, 12, 8]` and observes `[110, 10, 0, 0]`. The exact assertion message is retained in every raw row. Explicit-position and two-hidden-ancestor cases pass, but that does not waive this assertion. The remaining out-of-flow path needs separate source/runtime adjudication; the selected principal-subtree proof does not cover it.

## Source and evidence checks

Each phase's 70 pre/post pins are identical. All retained nonbinary input snapshots were independently hashed and deduplicated into `blobs/`; absent metadata stays explicitly absent. Across either repair pair, only nsFlexContainerFrame.cpp and the two recorded binary hashes differ. Each source pair differs by exactly the single `MarkPrincipalChildrenDirty();` call after the hidden-layout guard. Removing the two newer key fields deletes only their declarations and initializer entries; `KEY-REMOVAL.diff` preserves the exact delta.

Twenty dirty native files containing pending prototypes were temporarily replaced by branch HEAD in the root-owned driver. The original-key phase changes two fields on that branch, not every source file to upstream. Accordingly, this is evidence that the original four-field key reproduces the issue and that the one-line repair works without fixes 98/101 in this branch environment. It is not an isolated full-upstream runtime result.

The independent driver review and standalone source-application review remain separate frozen packages. This review copies actual raw results, phase commands, input receipts and input bytes; it does not retrospectively prove browser/compiler correctness. Binary bytes themselves are not retained here, only their stable root-run hash receipts. SDK/build configuration and arbitrary transitive resource behavior remain ordinary runtime trust boundaries.

`recount.py` reconstructs the result from copied raw events, verifies exact new names and cross-phase full roster, checks statuses/messages and pins, and verifies the one-line source deltas. `RECOUNT.json` is its retained result. The retained BEFORE and FINAL receipts are identical for historical HEAD `209dc941c40a5e0b34724bdac38b607b1f67dda6`, index digest and all 25 native source pins. STATE is terminal, restored=true, restoration build exit 0, and recovery_errors is empty. On October 22 this review additionally read and hashed all 25 live sources and confirmed all three temporary test paths absent. No current Git commands were run; HEAD/index equality is authenticated historical driver evidence. Restored binaries are not claimed byte-identical. WPT lint exited zero. The restoration was completed before the runtime seal; no later source/runtime mutation is included here.

## Recheck

Run `python3 -I -S verify.py --manifest-sha <external review FILES hash>` from the sealed review copy. It authenticates the closed review roster, binds copied evidence to the external runtime manifest, and reruns the raw recount. All original failure rows and messages remain retained; there is no rewritten expected status. No compiler output was generated by this runtime review.
