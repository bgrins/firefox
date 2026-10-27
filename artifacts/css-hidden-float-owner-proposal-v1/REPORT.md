# Current-owner float readiness proposal

ARTIFACT_ONLY_CANDIDATE; not built, browser-tested or accepted. Base is the pinned HEAD block source from css-hidden-float-readiness-audit-v1, not a changing runtime worktree.

## Minimal candidate

At entry to ReflowDirtyLines, under `HidesContentForLayout() && !HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES)`, visit the current Float child list and call MarkSubtreeDirty on entries without NS_FRAME_IS_PUSHED_OUT_OF_FLOW. The standalone patch changes only this method. It does not depend syntactically on the separate skipped-line child-marking patch; exact disjoint substitution confirms the changes commute.

The guard intentionally uses HidesContentForLayout, not HidesContent. Its exact implementation subtracts PresShell::IsForcingLayoutForHiddenContent(this), so the pass does not remark during a forced-layout operation admitted for this owner. An unrelated force operation is not assumed to disable this guard. Visible owners and owners with anonymous children take no new traversal or writes. The anonymous-owner exclusion matches the existing line skip's exclusion.

No per-float immediate-parent hidden predicate is added: a placeholder nested in an ordinary inline can have that inline as its in-flow parent even though the containing owner's entire line is skipped. The guard concerns the actual skipped owner. This must still be checked against native owner/placeholder ancestry for accepted runtime families; Float-list membership alone is not a theorem about arbitrary DOM ancestry.

## Ordering and extent

TrialReflow calls DrainOverflowLines, handles overflow containers, then DrainPushedFloats and ReflowPushedFloats, then line dirtying and ReflowDirtyLines. ReflowPushedFloats can remove, reparent or delete float-list storage, so the proposal obtains the Float list after that processing rather than caching it earlier. The subsequent pass calls only the existing bit-marking traversal; it does not relink lists or invoke child reflow.

Pushed entries are explicitly excluded: they already have a separate placement/reflow path, and this proposal does not attempt to repair them. Current non-pushed owner-list roots are the target. Floats remaining in PushedFloats/OverflowFloats, another owner, or another continuation are not claimed covered. Marking after pushed processing also avoids executing stale pointers retained before that processing.

The pass runs once per ReflowDirtyLines invocation, not once per whole Reflow. TrialReflow can run multiple trials; existing markRoot idempotence explains repeated bit marking under a stable projected tree, but neither native structural stability across trials nor zero cost follows from that theorem. It may mark a root even when no individual dirty line is ultimately dispatched; the own-hidden guard limits the work to skipped content. Cost needs measurement after correctness.

## Meaningful reuse of the existing model

PROOF-REFERENCE authenticates the previous closed subtree capsule manifest and the exact source/model inputs used here. Current MarkSubtreeDirty, HidesContentForLayout and IsHiddenByContentVisibilityOfInFlowParentForLayout bodies match that capsule exactly. No duplicate Lean development or new kernel result is claimed.

Manual projection: after pushed-float processing, select the finite current Float-list entries whose PUSHED bit is absent. Project each actual real float subtree into Subtree.Tree; under the owner guard apply markRoot to those roots. This is a new selection of roots, not a claim that native MarkPrincipalChildrenDirty follows placeholders. Existing root_is_dirty/root_is_eligible give direct-root readiness; clear_root_path_marks gives selected nested-leaf readiness under clearRootPath; root_coverage_exact preserves the stronger barrierClosure obligation. selected_query_recovery/completion additionally require the original same-frame query/provider and hidden-ancestor premises.

The original principal-only projection leaves a separately owned float untouched because placeholder.mOutOfFlowFrame is not a ChildLists edge. The candidate changes that root selection explicitly. Already-dirty roots can still hide clean leaves; table-column descendants remain traversal barriers; alias/lifetime/ownership and actual query-provider identities remain admissions. Pua's independent small model instantiation is separate and must not be represented as proving this entire native caller.

## Remaining gates

Wait for the main campaign's actual both outcomes. If float failures persist, compare this candidate with a clean matching baseline using direct float root and leaf-first queries, an inline-nested placeholder and a nested ordinary block owner. Keep visible controls, repeated queries and shown-restoration observations. Include a targeted continuation/pushed control before broadening the claim; current proposal deliberately excludes pushed roots. Check exact caller ownership before concluding all current-list entries are behind the guarded hidden boundary.

This proposal is a bounded route to test, not a final float repair or full hidden-content contract. No changes to production source, index or Git; no browser, build or compiler work.
