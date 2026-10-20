# Provisional hidden measuring repair: independent source review

**GO for a reversible root-owned experiment; HOLD for native acceptance.** Reviewed patch SHA256 `8b2cf5e8ade97bb525ad8e4f7b69b62b00fa351456e8c7999b484cf19249ab78`. No browser, compiler, build, native source or Git mutation was performed here. The key-removal causal isolation is separate and remains root-owned.

## Exact operation

After a measuring-cache miss and before constructing/reflowing the child output, the patch checks `IsHiddenByContentVisibilityOfInFlowParentForLayout()` and adds `NS_FRAME_IS_DIRTY` to that flex item's frame. Valid cached-measurement hits still return before this operation. It keeps the containing-block and padding key components.

The dirty operation is a direct state-bit addition. It does not schedule a reflow, walk ancestors, clear a cache property, invoke a callback, or touch the retained `cachedData` pointer. Consequently it does not introduce an immediate property-lifetime gap at this point. Subsequent virtual reflow, continuation deletion and callbacks retain their existing source/lifetime obligations; a changed dirty state can affect which work those routines perform. This is not a proof that all callback histories are unchanged.

## Why the direct-item recovery is plausible

The ordinary hidden block's reflow can return with default zero output. `FinishReflowChild` installs that size even for `NoMoveFrame`. Its ensuing `DidReflow` preserves dirty bits when the parent is hidden for layout, clearing only `NS_FRAME_IN_REFLOW`. The new bit should therefore survive that skipped measurement.

The measuring cache still receives the skipped output. This is not automatically a valid reusable measurement: `MeasureBSizeForFlexItem` requires both a clean frame and a matching key. A dirty item rejects that zero result when a subsequent geometry request forces the hidden ancestors. `PresShell::UpdateHiddenContentInForcedLayout` also checks the queried frame's dirty state before recording hidden ancestors. These two gates are the intended consumers of the new bit.

During that forced flush, `HidesContentForLayout` is false for every recorded hidden ancestor. The ordinary child can perform real reflow; normal `DidReflow` clears the dirty bit, and the replacement cache should describe that completed result. The patch does not itself request another flush, and `ReflowForHiddenContentIfNeeded` performs one flush then clears its forcing set. This supports a finite direct-query path, not a universal termination proof for arbitrary callbacks.

Repeated outer hidden layouts can still remeasure a persistently dirty item. That is work caused by later callers/mutations, not a new self-scheduling loop demonstrated by this patch. A paired run must confirm that repeated target queries after the first successful forced reflow do not keep reflowing.

## Important remaining boundaries

### Queried descendants versus marked item

The patch marks only the flex item. `UpdateHiddenContentInForcedLayout` checks the actual queried frame, not whether any ancestor is dirty. An already-clean descendant can remain outside the forcing gate even though its item was resized to zero or its pending flex position changed. This is a concrete source admission gap; it is not yet a browser failure of the proposed repair.

`descendant-query-diagnostic.html` has eight cases: direct item/inner child, append/prepend, one/two nested hidden ancestors. Each uses a separate visible fresh peer and measures relative to its host. It preserves three repeated reads and a final show control. Prepend is important because it changes the old item's expected position, rather than testing only dimensions unaffected by sibling append. The fixture is unrun; its geometry reads may themselves expose an older baseline deficiency. Compare original, key-removal and proposed-repair results before assigning a regression.

`alternative-subtree-vs-provisional.patch` replaces the one bit-add with `MarkSubtreeDirty`, only as an alternative for review. The complete implementation recursively marks ordinary descendant child lists, skipping already-dirty and table-colgroup frames; it does not clear the measuring property or directly queue reflow. This would strengthen descendant eligibility but costs a subtree walk on a clean hidden miss and changes more reflow input state. It does not automatically cover continuation chains or prove all queried-frame ancestry. Do not adopt it merely because it is stronger.

### Nested hidden parents

For a dirty directly queried item, the forcing routine walks in-flow ancestors and records all hidden ancestors, then schedules the topmost one. The repair's predicate uses the actual immediate in-flow parent, including its anonymous-box exception. It does not test arbitrary DOM ancestors. A nested flex item's own skipped contents and anonymous wrapper ownership can therefore select a different path from the empty ordinary-block fixture. The diagnostic covers one simple nested case, not all such providers.

### Continuations

The ordinary block early return is conditional on no next continuation in the retained source. With a continuation it can execute actual layout despite the hidden-parent predicate; the new bit then conservatively requests more work. `ReflowChild` may delete next-in-flows before `FinishReflowChild`. Neither the provisional flag nor the subtree alternative proves continuation lifetime safety or that a query of one fragment reaches every required fragment. Keep the existing fragmentation controls and use actual branch/identity receipts if this path is hit.

### Propagation and cached state

Adding the bit alone deliberately does not set all ancestor dirty-child bits. Recovery depends on the explicit CSSOM forcing entry requesting reflow of the topmost hidden ancestor. That is appropriate to test for this layout-skipping path; it is not interchangeable with a general `FrameNeedsReflow` call. Scheduling ancestors while already inside layout could introduce re-entrancy or extra passes, so it is not a preferred unreviewed alternative.

The cache can temporarily hold zero/skipped metrics only while the relevant dirty/forcing mechanism prevents treating them as final current geometry. A future cache-hit optimization must preserve this condition. Current pointer/cache freshness and arbitrary frame mutation proofs remain separate open work.

## Required experiment evidence

1. Establish whether the containing-block-key-only removal eliminates the 32 known stages, while preserving all controls. This is a diagnostic, never the final repair.
2. With the key retained and provisional flag applied, rerun the exact original sequence and proposed 24-subtest WPT. Record old target identity, key comparison, hidden predicate, dirty state, output/frame size and forced-layout admission across the failing stage.
3. Exercise the eight descendant-query cases. If only direct-item queries recover, evaluate subtree marking or a source-specific skipped-result publication repair; do not claim the direct-item flag solves the whole query family.
4. Verify repeated target reads settle after one recovery, and showing restores normal clean/cache behavior. Rerun table-caption containing-block and percentage-padding key regressions, plus the existing nested forced-layout WPT and continuation controls.

No final repair choice, observable-regression attribution, full lifetime theorem or security claim follows from this source-only review.
