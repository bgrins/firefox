# Hidden flex skipped-layout source review

## Recommendation

Retain the one-line `MarkPrincipalChildrenDirty()` candidate at the hidden `nsFlexContainerFrame::ReflowChildren` return for a reversible diagnostic. It is a better common seam than measurement-miss-only dirtying, because the same branch skips final placement after both a cache hit and a cache miss. This is not native acceptance or a complete hidden-layout contract. No native edit, build, browser run or Git mutation was performed here.

The candidate is against the exact retained original `dd8bf533…`, not the temporarily changed live source. `candidate.patch` and `CANDIDATE.json` bind it. Root's four-phase trace extension is independently approved in `DRIVER-V2-REVIEW.json`: 38 payload pins authenticate; the driver changes only its two phase lists; all earlier phase inputs and validators remain identical. The fourth candidate is baseline tracing plus this operation, without the miss-only direct dirty flag.

## Source chain and operation

`Reflow` performs `DoFlexLayout` (or continuation layout reconstruction) before `ReflowChildren`. Measuring reflow can already have committed a temporary size. The hidden return then skips both final child reflow and `MoveFlexItemToFinalPosition`; it also skips `ReflowPlaceholders`. Thus a valid measurement cache hit does not establish that current stored positions or descendant geometry reflect the new flex layout.

`PresShell::UpdateHiddenContentInForcedLayout` starts by testing the particular requested frame's `IsSubtreeDirty()`. A clean target can fail that admission even if an ancestor's child layout was skipped. Once admitted, the helper records hidden ancestors and schedules the topmost one; the forcing set makes their `HidesContentForLayout()` false during the forced pass. Marking the affected descendants preserves that existing admission mechanism rather than changing cache equality or pretending a temporary measurement is final geometry.

`MarkPrincipalChildrenDirty` iterates the actual principal child list and calls `MarkSubtreeDirty`. The latter sets the root bit and visits all its child lists, skipping already-dirty subtrees and table-column-group frames. It neither schedules reflow nor clears frame properties or intrinsic caches. Subsequent dirty-sensitive cache gates reject stale measured/final reuse. The retained cache objects remain allocated; their eventual refresh and callbacks still follow the ordinary source path.

## Comparison

| Placement of dirty operation | What it addresses | Remaining gap |
|---|---|---|
| Direct AddStateBits on measurement miss | Queried item admission after destructive skipped measurement | Clean descendant, valid hit, changed placement and non-measuring routes |
| MarkSubtreeDirty on measurement miss | Miss plus descendants reached by subtree traversal | Still no valid-hit or non-measuring coverage |
| MarkPrincipalChildrenDirty at skipped child layout | Principal children regardless of measurement decision, including skipped placement and descendant queries | Existing dirty-subtree invariant, nonprincipal/external frames, later mutations and fragmentation |

Do not combine the direct-bit miss variant with the branch helper as if their effects necessarily compose: `MarkSubtreeDirty` immediately returns when its root already has `NS_FRAME_IS_DIRTY`. Directly setting only that bit beforehand can prevent traversal of still-clean descendants. The diagnostic branch candidate replaces the miss-only mutation.

## Eligibility and boundaries

- **Actual principal list:** This includes anonymous flex-item wrappers and placeholder frames. It corresponds to the normal children whose final work this branch skips. `GenerateFlexLines` separates placeholders from ordinary items; `ReflowChildren` normally handles both. Iterating only `aFlr.mLines` would omit the placeholders and bind dirtying to a transient layout representation unnecessarily.
- **Out-of-flow frames:** Subtree traversal visits frames actually in a visited frame's child lists. It does not follow a placeholder to an out-of-flow frame parented elsewhere, nor does it mark the flex container's separate absolute list. `FinishReflowWithAbsoluteFrames` still runs later. No complete absolute/fixed-position or containing-block admission is claimed.
- **Continuations:** This marks current principal children and their descendant lists, including continuation frames present there; it does not walk another container fragment's principal list or arbitrary next-continuation links. Earlier `NormalizeChildLists` and the current fragment's layout reconstruction remain source prerequisites. The local retained hidden guard lacks the indexed source's `!GetNextContinuation()` condition; the proposal preserves each source's existing predicate rather than silently importing that upstream difference. Runtime multi-column controls remain necessary.
- **Nested hidden content:** Marking actual descendant frames can admit the initial query. The forcing walk records hidden ancestors. A separately hidden descendant not on the query's ancestor chain may remain legitimately skipped. This does not establish every nested visibility or anonymous-box exception; the existing `IsHiddenByContentVisibilityOfInFlowParentForLayout` uses in-flow parent identity and an owned-anonymous-box exception.
- **Already dirty:** The native state-bit comment says the frame and all descendants need reflow; that is a work obligation, not proof that every descendant bit is physically set. The traversal shortcut assumes a sufficient existing dirty state. It is therefore not an unconditional guarantee that every queried leaf is marked. Freshly created frames, preexisting direct-bit publishers and partially completed child reflow require source/history scrutiny if the diagnostic leaves residuals.
- **Later work:** After `ReflowChildren` returns, container output/overflow processing, vertical-rl position adjustment, overflow-container handling and absolute-frame finishing can still execute. This source proposal does not prove their callbacks or mutations preserve all marked geometry and identities.

## Existing patterns and cost

Primary source discovery used Searchfox identifier searches, followed by complete files fetched through its CLI. `nsColumnSetFrame` calls `MarkPrincipalChildrenDirty` before repeated column layout and after a measuring pass. `nsGridContainerFrame::MarkDirtyAfterIntrinsicSizingReflow` marks a measured child's subtree and propagates dirtiness to a parent already dirty or in reflow. These support dirtying provisional layout, but neither proves this new flex hidden branch correct. ReflowInput's font-inflation path also distinguishes dirty-subtree marking from separately invalidating intrinsic sizes.

This operation is linear in newly traversed descendant frames, with an explicit stack; already-dirty roots/subtrees short-circuit. It can turn later hidden measurement cache hits into misses and cause more work on repeated outer queries. It does not itself enqueue another reflow, so there is no direct self-scheduling loop. Forced visible completion ordinarily clears dirtiness, while hidden completion preserves it. Termination across arbitrary callbacks/repeated external queries and a performance bound are not proved here. Do not mark the container itself via MarkSubtreeDirty: it is already in reflow/possibly dirty, so the same early-return issue can skip the intended descendants, and its own DidReflow can clear its flags.

## Next evidence

The approved four-phase experiment isolates full-key baseline, key omitted, miss-only dirty, and skipped-children subtree marking on both retained matrices. In addition to zero sizes, compare shrink descendants, repeated queries and visible controls. Position correctness needs a position/offset-from-container observer for prepend/reorder (the current shrink validator measures sizes). Subsequent focused controls should cover nested hidden parents, anonymous items, principal placeholders with external positioned targets, continuation queries, already-dirty parent/clean-leaf histories, show/hide cycles and repeated query cost. A passing finite matrix is not a full lifetime or cache freshness theorem.

The installed release's separate 48-case fixture already has failures; consequently exposure by the strengthened key and a preexisting skipped-layout defect must remain distinct. The new diagnostic should explain which route actually executes rather than assign cause solely from source proximity.

## Source provenance

Complete source copies and their hashes are retained. Source lookup URLs are `https://searchfox.org/mozilla-central/source/layout/generic/nsIFrame.cpp`, `nsFlexContainerFrame.cpp`, `nsGridContainerFrame.cpp`, `nsColumnSetFrame.cpp`, `ReflowInput.cpp`, and `https://searchfox.org/mozilla-central/source/layout/base/PresShell.cpp`. The CLI full-file provider fetched current raw main; these are retained byte snapshots, not invented revision permalinks. Initial sandbox DNS failures are recorded; authorized read-only retries succeeded. Layout overview and reviewer checklist were read, especially frame lifetime, continuation ownership and reflow dirty-state guidance.
