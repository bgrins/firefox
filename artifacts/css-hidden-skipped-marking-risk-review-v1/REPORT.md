# Skipped-child marking: bounded callsite risk review

NO_NEW_RECURSION_BLOCKER_IDENTIFIED. No additional block/Grid correctness gate is justified solely by frame depth from the inspected change. Keep the planned exact landing-file runtime and restoration gates. This is source review, not native acceptance or a general memory-safety proof.

## Stack and synchronous effects

The exact retained nsIFrame::MarkSubtreeDirty uses an explicit AutoTArray<nsIFrame*,32> worklist. It never recursively calls itself for child frames. The32 is inline capacity, not a traversal depth limit. ChildLists supplies immediate lists; indexed nsContainerFrame/nsBlockFrame getters append owned lists and use the fixed class-inheritance chain, not recursive frame descent. Indexed AddStateBits directly ORs mState. MarkPrincipalChildrenDirty is the retained loop calling this same helper for each principal root.

Thus the new Grid call, per-line block calls and selected float-root calls do not introduce recursive stack growth proportional to frame depth. No new synchronous reflow/callback dispatch is present in the changed calls. This conclusion does not depend on an unverified DOM/frame-depth limit or the finite Lean model. All possible virtual GetChildLists overrides and allocator internals were not re-audited; their existing valid-list/lifetime/allocation contracts remain boundaries.

## Repetition and cost

A root already carrying IS_DIRTY returns immediately. An encountered dirty descendant is popped but its children are not enqueued. On a stable frame graph with no intervening bit clearing, repeating the same root marking therefore avoids another full subtree traversal. Block still scans its skipped line's roots; Grid still scans principal roots; float still scans the current Float list and tests pushed bits. None is constant-time in root-list length.

The first mark can visit a large clean owned subtree and allocate worklist storage. Pending work scales with encountered child edges/frontier; it is not bounded by32. This is extra conservative work compared with returning without marking, not evidence of stack overflow or an allocator defect. Existing indexed callers already use the helper from reflow/resize paths (Grid, block, columns, absolute and SVG), but their presence alone does not prove new-callsite performance acceptable.

Between layout passes or trials, real reflow can clear flags or move/reconstruct frames. The stable-graph observation is not a global amortized bound. In particular, the float proposal runs once per ReflowDirtyLines invocation, not once per complete reflow. Retained ReflowDirtyLines retries/interrupt handling are governed by its existing clearance/interrupt branches; the new state-bit helper itself does not set line dirty or directly request another pass. No new self-sustaining retry route was identified, and no universal termination claim is made.

## Actionable gates and existing limits

- Block: current query-cost corpus covers block/td/col with1/32/128 branches. Use its first-recovery and correct hot-loop results for the measured domain; do not infer arbitrary-depth or Grid/float cost from it.
- Grid: the planned isolated eight-case plus50controls tests the new branch. No additional stack-depth gate is required by the iterative helper. A future Grid fanout measurement could quantify first-mark overhead if a cost concern appears; this source review does not require a speculative performance rewrite.
- Float: preserve its separate candidate/runtime gate and pushed/continuation ownership limits. Existing dirty-root/table barriers and external placeholder edges remain correctness coverage issues, not newly discovered recursion hazards. Do not globally follow OOF pointers or remove pruning based on this review.

Searchfox discovery logs are retained separately from exact frozen-source inputs; indexed line numbers/source versions are not used as local source identity. Six sandbox DNS failures are retained, followed by successful read-only network retries. The two complete retained helper bodies and unchanged ReflowDirtyLines control body are copied from authenticated predecessor roles. No browser, compiler/build, production source or Git mutation occurred. Full frame lifetime, callback/provider and allocation F1–F16/F11/F12 obligations remain open.
