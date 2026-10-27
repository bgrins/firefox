# Grid own-content skip: local source binding and minimal proposal

Outcome: PROPOSED_NOT_ACCEPTED. No browser reproduction or native execution here.

## Actual source identities

At HEAD90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e, working nsGridContainerFrame.cpp exactly equals the committed file (SHA613bab7d4c495c54b04df8801e188224f1cc70362c64a2f31342cb9acf0d5531). The same equality holds for nsContainerFrame.cpp (SHA1c89576b44909a4773901aeb00121a04b420e7152e360a21a8b6067ee552ae6a). Full snapshots and source/method hash receipts are retained. HEAD was unchanged across capture. Other experiment-owned files are not a source baseline for this audit.

The earlier indexed Grid fetch differs. In particular, indexed ReflowChildren and Reflow have `&& !GetNextContinuation()`; actual HEAD has neither continuation condition. The proposed patch preserves HEAD's predicates exactly. Full indexed-to-HEAD diff also retains unrelated line-clamping/allocation differences, which are not part of the proposal. Complete NormalizeChildLists differs only in the AutoFrameListPtr constructor's explicit PresContext argument. The indexed --define output and raw fetched file do not even have identical formatting/version at that point; authoritative local method bodies avoid conflating them.

Read-only blame attributes the current own-content skip to d6b19e86ff729 (2022) and the in-flow-parent return to the retained 2022 lines; this is provenance, not runtime reachability or an attribution of a new regression. No history search beyond those narrow ranges.

## One-call proposal

candidate.patch adds `MarkPrincipalChildrenDirty();` inside the existing `HidesContentForLayout()` early return of ReflowChildren. No condition, sizing result, continuation policy, normal-visible child algorithm, or intrinsic-measurement caller changes. Candidate full file is included. This is an experiment proposal, not an instruction to apply it while the current campaign runs.

The intended effect is to preserve query readiness for existing principal grid items skipped after ordinary track sizing. The helper independently visits each principal child even if the grid itself is already dirty. Existing Reflow returns early under a hidden in-flow parent before reaching this helper; that separate entry skip remains unchanged. Do not claim this call repairs every hidden Grid entry route.

## Exact source joins and important exception

METHOD-BINDINGS compares complete local/indexed ReflowChildren, Reflow, NormalizeChildLists, MeasuringReflow, ContentContribution, InitializeItemBaselines, ComputeIntrinsicISize and MarkDirtyAfterIntrinsicSizingReflow. All five measurement/intrinsic methods match exactly. The normal GridReflowInput constructor uses the actual ReflowInput and leaves mIsGridIntrinsicSizing false; ComputeIntrinsicISize sets it true. ContentContribution and baseline measurement call MarkDirtyAfterIntrinsicSizingReflow only under that flag. Thus intrinsic protection already exists and is preserved. Fixed explicit-track normal layout is a useful discriminator; real track-sizing execution and dirtiness still require runtime evidence.

Own-content ReflowChildren returns before overflow-container handling and principal iteration. Reflow continues after that call, including absolute-child processing and output work. Marking principal roots is not a proof that separate overflow lists, absolute-owned frames, placeholders' external targets, other continuations, or all query providers are marked. NormalizeChildLists can change membership before the call. Under ordinary no-continuation/no-overflow fixtures these moving-list branches are inactive; arbitrary continuation membership remains an obligation.

## Reuse existing proof rather than duplicate it

Authenticated the closed css-hidden-subtree-proof-v1/capsule FILES e93989395671b1edb1b9586d77a9898596c526ef4a8b1f0a18df12ccbaf25452 and all its payload hashes. Exact complete current MarkPrincipalChildrenDirty and MarkSubtreeDirty bodies equal that capsule's source bodies. PROOF-REUSE records this equality. No new Lean proof or replay is claimed.

Existing theorem premises remain essential: direct IS_DIRTY roots prune traversal; table-column-group descendants are excluded; eligibility also involves HAS_DIRTY_CHILDREN; queried provider/path identity and stable graph/lifetime are manually projected. A directly dirty item with a clean nested queried leaf is not automatically repaired. Path-local readiness can suffice without allDirty, but the Grid caller's history must establish the relevant path condition. A clean principal root is marked and its admitted descendant paths are traversed; this is conditional source/model reuse, not native caller closure.

## Gates before acceptance

1. Execute the tiny explicit-track diagnostic and WPT conversion with visible calibration, parent-only flush, leaf-first/repeated queries, and showing restoration. No outcome is assumed.
2. Pair candidate against its actual local baseline and inspect any still-failing nested/provider case rather than weaken the oracle.
3. Assess continuation/overflow/subgrid and dirty-barrier histories separately. Current actual predicate is broader than indexed source, so a no-continuation fixture does not validate all changed calls.
4. Check visible controls and hidden-query cost: new dirty marking adds traversal and can make a previously skipped query do layout. No no-regression/cost claim from a one-line patch.

No production, index, Git, browser, build or compiler mutation. All proposal writes are within this new artifact. Existing sealed lead/proof/diagnostic artifacts remain unchanged.
