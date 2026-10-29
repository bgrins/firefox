# Notification coverage obligation

Let M be the moved element, O the old parent's remaining element children, and N the destination's children after insertion. For distinct parents, O and N are disjoint. Recomputing M and notifying only N cannot establish fresh values for count-dependent members of O. The required coverage is the dependency-bearing members of O union N, plus the moved subtree where its inherited/context inputs change. Same-parent reorder collapses the two parent domains and cannot by itself demonstrate source-side notification.

The implementation obligations are independent:

1. Preserve the moved root's style/restyle state needed by the previously scheduled reframe.
2. Run old-container removal invalidation while the old parent and siblings are still discoverable.
3. Retain destination insertion invalidation.
4. Consume scheduled restyles after the DOM operation, using the new topology; notification does not mean sampling the old count immediately.

The proposed true parameter preserves(1) while enabling the existing route for(2); destination logic(3) is unchanged. Existing scheduler behavior and actual paired tests must establish(4). Public API failure paths, frame reconstruction corner cases, shadow/anonymous nodes, descendant state, and all selectors are not proved by this set argument. No Lean/native refinement or coverage increment is claimed.
