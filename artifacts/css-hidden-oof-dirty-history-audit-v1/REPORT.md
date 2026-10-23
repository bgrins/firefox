# Absolute fallback dirty-history audit

**Bounded negative finding:** no concrete ordinary non-fragmented position-try caller sequence was found that introduces a dirty absolute root with a clean queried leaf at the candidate's hidden `MarkSubtreeDirty` seam. This is not a universal dirty-subtree invariant or acceptance of the proposed native repair.

## Source and selected repair

`AbsoluteContainingBlock.indexed.cpp` was retrieved through Searchfox after a retained failed sandbox DNS attempt. Complete retained local original/candidate files are copied from the sealed OOF proposal. `SOURCE-JOIN.json` verifies the candidate is exactly that original plus the selected three-line hidden subtree mark, and checks the relevant fallback/Reflow/DidReflow snippets against indexed source. The candidate mark occurs **inside every fallback iteration, before constructing the child's ReflowInput**. Whole indexed and local files are not asserted identical.

The exact controlling methods are `AbsoluteContainingBlock::ReflowAbsoluteFrame`, `AutoFallbackStyleSetter`, `nsIFrame::DidReflow`, `nsIFrame::MarkSubtreeDirty`, `PresShell::FrameNeedsReflow`, and `nsBlockFrame::Reflow`. Complete retrieved or retained source bodies/entry guards accompany this note. Source locations are identified by method names rather than moving line positions.

## Relevant order

Each fallback iteration performs:

1. Apply the attempted style to the **kid** with `SetComputedStyleWithoutNotification`, compute its containing block, and prepare available size.
2. Candidate hidden-parent check and `MarkSubtreeDirty`.
3. Construct ReflowInput; call the virtual kid `Reflow` with a fresh output.
4. Position/commit the resulting rectangle, then call kid `DidReflow`.
5. Test fit, finish, or choose another/finalizing fallback.
6. Only if continuing: `AddStateBits(NS_FRAME_IS_DIRTY)` on the kid, reset status, and start the next iteration.

Every loop exit precedes step6. Exhaustion can schedule one finalizing reflow, or break before the direct dirty publisher. The post-loop fallback rollback restores a position/style record; it does not publish this direct dirty bit. The local loop has no event-loop yield or interrupt exit between step6 and the next iteration. Interrupt handling in the outer `AbsoluteContainingBlock::Reflow` occurs after this method and uses `MarkSubtreeDirty` or `HAS_DIRTY_CHILDREN`, not a new root-only `IS_DIRTY` publisher.

## Cases

| Entry/iteration case | Consequence within the inspected ordinary path |
|---|---|
| Hidden, initially clean ordinary root/subtree | First candidate mark reaches the descendants. `nsBlockFrame::Reflow` with no next continuation returns before laying out descendants. Hidden `DidReflow` removes only `IN_REFLOW`, preserving these dirty bits. A retry's root-only mark therefore does not create a newly clean descendant. |
| Hidden, already dirty from ordinary `FrameNeedsReflow(IS_DIRTY)` | The shell marks descendants using an explicit stack and does not prune at dirty frames. This publisher does not supply the proposed root-dirty/leaf-clean counterexample. |
| Visible or currently forced layout | Candidate hidden predicate is false. A root-only dirty state can exist between fallback iterations after a completed reflow; it is transient. The next iteration reflows it, and ordinary visible `DidReflow` clears root dirty bits before a final exit. |
| Externally supplied dirty root with clean descendant | `MarkSubtreeDirty` really does return immediately. The candidate does not repair this abstract state merely by invoking the helper. No new concrete producer for this state was identified in the inspected ordinary fallback path. |

`FrameNeedsReflow`'s already-dirty ancestor/root bookkeeping does not suppress its descendant-mark traversal. It would be incorrect to replace that method with the pruned helper when reasoning about style-driven invalidation.

The hidden predicate depends on the in-flow parent (the placeholder's parent for OOF frames), that parent's hidden/forced-layout state, and the anonymous-box exception. The fallback style setter changes the kid's style, not its in-flow parent's identity or style. The inspected direct fallback publisher alone therefore does not demonstrate a visible-to-hidden transition between retries.

## Explicit limits and decision

The reasoning assumes a stable in-flow parent/hidden forcing scope during this synchronous invocation, an ordinary non-fragmented block hidden early return, and an initially coherent subtree or the stated ordinary invalidation publisher. It does **not** establish these properties for every virtual frame implementation, arbitrary callback mutation, destruction/reparenting, continuation cleanup, table-column-group pruning, or every direct dirty publisher elsewhere in Gecko. In particular, a block with a next continuation bypasses the quoted hidden early return; its full dirty-history cannot be inferred from this case table.

The existing helper pruning concern remains a source-admission boundary. This investigation did not find the requested concrete fallback-origin failure and supplies no new bug claim, candidate expansion, or browser fixture. Stop this lead here; use the ongoing calibrated runtime and separate provider/continuation reviews for their own scopes. No browser, compiler, Gecko build, native mutation, or Git operation was performed.
