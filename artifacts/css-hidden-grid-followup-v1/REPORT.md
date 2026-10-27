# Grid hidden-layout readiness source checkpoint

Outcome: SOURCE_LEAD_ONLY. No browser reproduction, native repair, or accepted bug claim.

## Indexed source roles

The successful `indexed-nsGridContainerFrame-v2.cpp` and `indexed-nsContainerFrame.cpp` are exact retained Searchfox fetches. They have not been tied to local HEAD, a release binary, or an independently authenticated indexed revision. Initial empty `indexed-nsGridContainerFrame.cpp` and failed `fetch.stderr` are retained. Symbol output can be truncated or carry different line numbers; complete fetched files are authoritative for this inspection.

## Relevant branches

* `nsGridContainerFrame::ReflowChildren` returns its content block size when `HidesContentForLayout() && !GetNextContinuation()`. It does so before overflow-container reflow and before its ordinary principal-child iterator; there is no descendant dirty-mark call in this branch.
* `nsGridContainerFrame::Reflow` first normalizes child lists, then returns under `IsHiddenByContentVisibilityOfInFlowParentForLayout() && !GetNextContinuation()`, before `MarkInReflow`, GridReflowInput construction, and output sizing. A clean-zero publication requires a concrete caller/output/DidReflow path; this return alone does not prove it.
* Complete `nsContainerFrame::NormalizeChildLists` handles continuations, overflow lists, reparenting, and sorting. It is not an unconditional subtree-dirty operation. In the intended no-continuation/no-overflow fixture its list-moving branches are inactive. This does not prove arbitrary moved-frame histories safe.
* Own-content skipping does not skip all of Reflow: track sizing precedes ReflowChildren, while absolute children, desired output sizing and other work follow it. Do not infer an OOF omission from the principal skip.

## Existing protection that limits the hypothesis

`MarkDirtyAfterIntrinsicSizingReflow` calls the measured child's `MarkSubtreeDirty`, then propagates ChildIsDirty to ancestors until a dirty/in-reflow parent. Both measuring contribution and baseline callers invoke it when `mIsGridIntrinsicSizing`. `ComputeIntrinsicISize` sets that flag; normal Reflow does not. The default is false and its normal constructor supplies the actual ReflowInput. MeasuringReflow itself caches/reuses measurements and performs ReflowChild/FinishReflowChild; it is not an unconditional dirty-mark wrapper.

Consequently, an assertion that all Grid measurement paths leave clean children would be wrong. The smaller lead is normal, explicit-track own-content skipping with previously clean existing descendants. Track sizing, parent resize propagation, and forced-query history still determine whether that state is reachable.

## Next discriminator (not executed)

Use an ordinary visible block parent and a subject that itself has `display:grid`, fixed height, `grid-template-columns:minmax(0,1fr)`, and an explicit fixed row. A grid item contains a percentage-width leaf. Calibrate visible geometry, hide the grid, query once to establish a clean hidden descendant, change only the visible parent's width, flush only the visible parent, then query the leaf first, repeat, and restore visibility. Run a visible-grid control and direct-item-first variant separately. The explicit grid tracks avoid relying on intrinsic measurement protection; the hidden element is the grid itself, so its parent's block line does not hide the grid due to a hidden in-flow ancestor. Actual branch execution remains untraced.

Do not infer a missing dirty bit from a geometry discrepancy without checking the queried frame/provider identity and prior dirty propagation. A possible future MarkPrincipalChildrenDirty proposal also inherits dirty-root barriers, table-column exclusions, and external frame-list boundaries from existing subtree models.

## Scope

Source-only review. No changes outside this artifact; no browser, build, compiler, Git, or production-source mutation. No universal Grid, fragmentation, ownership, lifetime, query-provider, or CSS correctness claim.
