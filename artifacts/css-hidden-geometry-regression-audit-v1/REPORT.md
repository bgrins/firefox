# Hidden flex geometry: regression isolation audit

## Current recommendation

The strongest source-derived suspect is the **containing-block component added to the flex measuring-cache key**. Test its removal alone first, preserving the padding component and all other native changes. `isolate-containing-block-key.patch` is that two-line diagnostic against the pinned live source. It is not a proposed final repair: removing this key would reopen the table-caption percentage-height defect.

No runtime attribution has been established by this audit. Installed Firefox 158 and the current combined project build are different source/configuration baselines. Their difference alone cannot assign the failure to one local patch or prove an upstream regression. This audit made no native, Git, build or browser mutations.

## Independently reconstructed observation

The supplied probe has 32 configurations and five stages each. Project and release differ in exactly 32 stages: flex subjects, both with/without columns, both initial visibility states, all four query APIs, specifically `append` and `append-again`. Project returns 0×0 for the old target on all three repeated queries; release returns 24×32. Initial/hide/show stages and all block subjects remain controls. `DIFFERENCES.json` retains the exact differing records.

The outer subject query is important: each stage first reads its client-rect count and scroll dimensions, then queries the target. Thus a hidden parent layout can occur before the target's forced-hidden-layout admission. Hidden outer scroll height already drops to zero in both browsers at the hide stage, so this is not merely lack of content-visibility support in the release control.

## Source chain and conditional causal hypothesis

1. `FlexItem::CanMainSizeInfluenceCrossSize` defaults to true for this ordinary, non-stretched row item. An explicit 32px cross size does not by itself bypass the measuring path. `DoFlexLayout` can therefore call `SizeItemInCrossAxis` and `MeasureBSizeForFlexItem` before `ReflowChildren`'s hidden-content return.
2. The strengthened key contains `aRI.mContainingBlockSize`. If the hidden outer layout supplies a different containing-block size than the previous forced visible layout, a formerly valid measurement can now miss even when the old target remains clean. The actual old/new key values still need instrumentation; this is the central unconfirmed runtime premise.
3. The child is an ordinary block. Its `Reflow` returns early when hidden by its in-flow parent and lacking a next continuation. The zero-initialized output is not filled with the normal 24×32 geometry on this branch.
4. `MeasureBSizeForFlexItem` nevertheless calls `FinishReflowChild` with `NoMoveFrame`, then publishes the measuring cache. `FinishReflowChild` still calls `SetSize`, then `DidReflow`. `NoMoveFrame` does not preserve size.
5. `nsIFrame::DidReflow` has a hidden-parent branch that removes only `NS_FRAME_IN_REFLOW`. It **does not clear** an existing dirty bit, but it also does not add one. A target already clean before this measuring miss can therefore become zero-sized and remain clean. This corrects the earlier tentative explanation that hidden `DidReflow` clears dirty state.
6. `PresShell::UpdateHiddenContentInForcedLayout` immediately returns for a clean target. Otherwise it records the hidden ancestors and queues the topmost frame for reflow. Clean zero geometry can therefore defeat the target query's recovery path; repeated queries do not help.

This explains the observed stage asymmetry if the premises hold: hiding can dirty the target and preserve recovery, while appending a sibling can dirty the flex parent without dirtying the existing target. Showing removes the hidden early-return condition and restores ordinary layout. Exact frame identity, dirty state, key change and executed branch must be observed before calling this the cause.

## What was ruled down, not ruled out

`CACHE-METHOD-COMPARISON.json` shows complete `MeasureBSizeForFlexItem`, `NeedsFinalReflow`, and `ReflowFlexItem` bodies byte-identical between the fetched indexed source and the local source. The committed key additions are separate from those bodies. The local uncommitted flex patch has no change to these three methods.

The newly added `NaturalBaselineBOffset` query initially looked suspicious because it can run after hidden child layout is skipped. Inspection of the ordinary block's const natural-baseline getter found line/geometry reads, not a direct size write. It is a lower-priority isolation target, not an established cause. The nearby uncommitted `nsBlockFrame`/`BlockReflowState` changes concern floats, absent from this fixture.

The accepted flex hidden guards remove `!GetNextContinuation()` from two early returns relative to indexed source. This can matter with a continuation, but it does not explain the plain non-column case without evidence of such a continuation. Restoring those conjuncts is a secondary diagnostic if key isolation fails. The tiny fixture also offers no arithmetic-overflow explanation for the pending wide packing changes.

The indexed/local full diff is retained. Symbol-based Searchfox extraction returned incomplete/misaligned excerpts for two flex methods; the equality checks use complete methods extracted from the full downloaded file instead. Full source snapshots and local file hashes are retained, so no symbol excerpt is being used as a complete implementation proof.

## Minimal root-owned experiment

After signing/restoration bookkeeping, apply only `isolate-containing-block-key.patch` reversibly, rebuild, and rerun the exact 160-stage probe. Preserve the original 32 failures and all 128 control-stage outcomes. If removing the key restores these stages, it implicates the cache-miss condition but does not by itself establish each downstream state transition. Keep the key removal out of the final repair.

For decisive instrumentation, restrict receipts to the target/subject frame identities and collect:

- Before/after the outer query: target physical size, `IsSubtreeDirty`, parent hidden-for-layout status, next-continuation pointer.
- At `CachedBAxisMeasurement::IsValidFor`: cached and new containing-block sizes, computed size, border/padding, min/max and available block size, final key comparison. This distinguishes the CB component from another changed input.
- Before child measuring reflow and after `FinishReflowChild`: actual output size, stored frame size, dirty state, hidden-parent guard and same-frame identity.
- At target `UpdateHiddenContentInForcedLayout`: dirty gate result, ancestor insertion and whether a forced layout is queued.

Enabling existing `FlexContainer:5` logs and temporarily disabling the final-reflow optimization preference are useful no-build discriminators. The latter cannot exclude a measuring-cache failure: the hidden parent can return before final reflow is considered. Do not call `NeedsFinalReflow` twice for logging; it can publish cached final metrics.

## Repair boundary remains open

The sibling reviewer has a provisional mark-dirty-on-hidden-cache-miss direction that retains the required containing-block key. It has not been reviewed or accepted here. Any such repair must establish dirty propagation through the actual `FinishReflowChild`/`DidReflow` ordering, preserve forced-hidden queries, avoid repeated hidden-reflow scheduling, and retain cache/continuation/frame-lifetime invariants. Ordinary, initially hidden, show/hide, sibling append, repeated query, columns and the table-caption key regression all belong in the paired gate. A safe repair must not rely on a cached measurement hit to conceal a skipped-layout zero output.

This is a bounded source hypothesis and isolation proposal. No new accepted bug count, cache-lifecycle theorem, source-translation proof or security claim is made.
