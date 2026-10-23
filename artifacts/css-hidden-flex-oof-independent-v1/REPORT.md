# Independent review: hidden absolute-child invalidation

## Verdict

**GO for a reversible diagnostic using `candidate-v2.patch`; HOLD native acceptance pending runtime and regression evidence.** The selected three-line addition marks a hidden absolute child's subtree before constructing its reflow input. The older `candidate.patch` marks after input construction and is superseded. No mathematical or source blocker was found for the proposed bounded experiment. This report does not claim that all hidden descendants, continuation graphs, or callback histories are repaired.

The producer's 31 payloads are captured under `producer/`. FILES is `4571c5fd5131906fb0bb34a1c5a40c981d40d1ab926edbfaa4be488224cb0d24`; selected patch is `d5f61ccd4db2871e17e96e5d84cc30dcb59ad92ac3574878d3169cc1999acdf3`. `V2-PROPOSAL.json` ambiguously names its `candidate_sha256`: that value authenticates the selected **C++ snapshot**, not the patch. Both identities are independently checked here.

## Source review

| Obligation | Finding |
| --- | --- |
| Correct hidden owner | `GetInFlowParent()` follows the first continuation's placeholder for an out-of-flow frame. The new condition tests that in-flow parent's layout suppression, not the absolute containing block's visibility. An external visible containing block therefore does not inherently defeat the condition. |
| Preserved selection | The new code is inside the existing selected absolute-reflow iteration. It does not select otherwise reused absolute children or change containing-block ownership, status, offsets, positioning, overflow, or fallback statements. Dirty state can influence the callback and its input; those effects are intentional, not byte-for-byte output equivalence. |
| Input ordering | `InitResizeFlags` reads IS_DIRTY and subtree dirtiness. V2 marks before constructing `kidReflowInput`, so initialization sees the updated state. The late original proposal did not provide that guarantee. |
| Geometry publication | A hidden block callback without a next continuation can return before ordinary sizing. Existing absolute layout still commits the returned rectangle. Hidden `DidReflow` removes IN_REFLOW but preserves dirty state. Marking therefore admits a later forcing query; it does not prevent the temporary zero-size commit. |
| Direct query | `UpdateHiddenContentInForcedLayout` first checks the queried frame's subtree dirtiness, then follows in-flow ancestors and schedules the topmost hidden ancestor. A freshly marked absolute root meets the first gate; actual geometry recovery still requires the forcing and layout providers. |
| Nested leaf | `MarkSubtreeDirty` walks actual child lists, but prunes an already IS_DIRTY node and table-column groups. A clean leaf below an already-dirty barrier is not universally repaired. HAS_DIRTY_CHILDREN is distinct from IS_DIRTY. The previously sealed subtree model establishes conditional closure, not this entire native history. |
| Placeholder and continuation edges | The predicate follows the originating placeholder. The marking walk does not follow arbitrary placeholder links or next-continuation edges. Neither property implies all continuations or externally owned descendants are marked. |
| Non-skipping callbacks | The condition is broader than block/grid/flex hidden early returns that also require no next continuation. Such hidden selected calls can perform additional dirty work. Moving the mark before input construction makes the input consistent, but does not prove all virtual frame implementations preserve geometry or cost. |
| Visible cost | A false condition avoids subtree traversal. It still adds `GetInFlowParent`, first-continuation/property lookup for OOF frames, and hidden-state checks per selected iteration. A long continuation chain need not have constant lookup cost. No timing claim is made. |
| Anchor retries | The existing position-try loop can directly set IS_DIRTY. Its descendant closure is not established by this patch. No anchor behavior is represented by the eight proposed tests. |

The complete local absolute source and exact source excerpts are preserved in the producer capture. Additional Searchfox discovery receipts retain `GetInFlowParent` and the hidden-entry call sites. Indexed discovery is not falsely identified as the local source revision.

## Standalone source applicability

Private apply/reverse checks succeeded with zero fuzz on both:

- Local HEAD `209dc941c40a5e0b34724bdac38b607b1f67dda6`, whose absolute source exactly matches the producer baseline.
- Upstream `5d41bc07dec206ad511c2689f4b01ab74516c308`, retaining its unrelated source differences.

In each case the sole delta is the selected conditional marking block, and reversal restores every byte. No principal-child repair or flex source edit is required for source application. **Applicability does not establish isolated runtime independence:** run the OOF-only patch and its relevant tests without the principal repair before calling it independently landable.

## Eight-test oracle

The test contains two hidden-ancestor choices, two offset choices, and two insertion choices: eight tests, each with five stages and three target reads. Ancestor queries occur before the leaf reads, but no direct OOF-parent rectangle query occurs first. Thus “leaf-first” is accurate relative to the OOF parent, not to every ancestor or layout flush.

The visible-reference calibration is independent of the hidden target. For static positioning, the absolute parent is centered as a sole item: host x10 plus `(200−12)/2`, followed by leaf margin1, gives x105. Resizing to20 gives x101. Its top10 plus margin2 gives y12. Percentage dimensions give6×8 and10×12. Explicit offsets give x18,y21. These are small exact coordinates. An unrelated in-flow sibling does not enter the absolute child's sole-item static-position computation. This follows [Flexbox §4.1](https://drafts.csswg.org/css-flexbox-1/#abspos-items). The rectangle observes border geometry under [CSSOM View](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects). The geometry-query example in [CSS Containment](https://drafts.csswg.org/css-contain-2/#cv-examples) corroborates forcing hidden layout; it is an example, not a substitute for the observer algorithm.

All visible stages are checked before target assertions. Repeated reads, parent resizing, and showing again are useful controls. The test does not cover an external containing block, continuation callbacks, non-flex in-flow owners, anchor retries, or an arbitrary preexisting dirty barrier. No browser or test execution is claimed by this review.

## Concrete next gates

1. Run the selected v2 trace and paired tests. Verify clean hidden overwrite, retained dirty state, and actual forced recovery, rather than inferring locals from green geometry.
2. Run the OOF-only patch without the principal repair, preserving both direct-root and leaf tests and all calibrated controls.
3. Add a bounded external-containing-block discriminator: keep the positioned outer host, remove positioning from the hidden flex subject, preserve explicit host-relative and static-position references, and establish calibration first.
4. Include an actual hidden OOF continuation/non-skipping callback control and existing absolute fragmentation/position-try regressions. The candidate is a shared absolute-layout change, not a flex-only call site.

Already-dirty clean descendants, arbitrary placeholder ownership, callback lifetime, and complete forced-layout provider semantics remain explicit broader obligations. They are not evidence of an introduced regression. No production, browser, build, compiler, index, or Git mutation was performed; only read-only Git snapshots and private patch operations were used.

## Reproduction

`python3 -I -S verify.py --manifest-sha <this artifact FILES hash>` authenticates both closed rosters, validates selected source roles and the exact insertion, reconstructs the eight-test roster, and repeats private zero-fuzz apply/reverse checks on retained bases. It does not rerun browsers or prove the prose source analysis.
