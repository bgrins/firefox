# Hidden absolute-child geometry: distinct producer review

## Bounded conclusion

Recommend a separate, reversible source/trace experiment. The root reports one unchanged failure in both original and principal-repair variants: `Positioned child: oof-static, one hidden ancestor, hidden`, insertion expected `[104,10,12,8]`, actual `[110,10,0,0]`. This report does not independently replay that runtime. The existing 44-test artifact remains unchanged, and the failure is not dropped.

This is a distinct immediate producer from the skipped principal-child final-layout bug. Both use the hidden-layout dirty/forcing protocol, but absolute children have a separate reflow owner and size-commit path. Keep the principal repair independently reviewable. If the following experiment confirms the source prediction, package the absolute correction separately with its own WPT and control results. No native acceptance, security claim, or generalized lifecycle closure is made here.

## Source-derived chain

1. The retained flex `ReflowChildren` hidden branch returns before principal final reflow/movement and placeholder reflow. Marking principal child subtrees includes placeholders, but a placeholder's out-of-flow link is not a child-list edge to the absolute frame.
2. Flex `Reflow` later calls `FinishReflowWithAbsoluteFrames` regardless of that early return. The containing-block wrapper prepares absolute frames and passes width/height-changed flags. Principal marking therefore does not end all child layout.
3. `AbsoluteContainingBlock::Reflow` can select a clean absolute child: `FrameDependsOnContainer` immediately returns true for `NeedsHypotheticalPositionIfAbsPos`. This fits auto-inset static positioning; fixed offsets need not take that same dependency path. No anchor fallback is needed.
4. `ReflowAbsoluteFrame` constructs a fresh `ReflowOutput` and directly invokes virtual `Reflow`. The retained `nsBlockFrame::Reflow` entry, when hidden by the in-flow parent and without a next continuation, finishes overflow and returns before normal sizing. The in-flow parent of an out-of-flow frame is the first-continuation placeholder's parent, not necessarily the absolute containing block.
5. Absolute layout uses the returned physical size to resolve offsets and calls `SetRect`. With zero width, centering in 200 pixels yields x100 relative to the containing block, hence viewport x110. Width12 would instead yield viewport x104. This numerically matches the reported failure but is not a native trace receipt.
6. `DidReflow` sees the same hidden in-flow parent, removes IN_REFLOW and returns without setting IS_DIRTY. A previously clean frame may remain clean after a zero-size commit. `UpdateHiddenContentInForcedLayout` rejects a clean target before initiating hidden ancestor forcing. The subsequent geometry query can therefore read the installed zero rectangle.

The relevant local full files and narrow retained bodies are included. Searchfox discovery uses the current name `AbsoluteContainingBlock`, not the older ns-prefixed name; unsuccessful lookup/DNS attempts were not treated as evidence. Indexed and local absolute/container full files differ and are retained separately. `SOURCE-PINS.json` binds the actual local proposal inputs. Root must check the exact original hash before application; no live flex source was adopted during its experiment.

## Proposed diagnostic seam

`candidate-v2.patch` adds this before constructing `kidReflowInput` within the existing selected absolute-reflow iteration:

```cpp
if (aKidFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
  aKidFrame->MarkSubtreeDirty();
}
```

This uses actual placeholder/in-flow ownership, including when the absolute containing block is external to the hidden element. It does not reflow clean absolute children that the existing gate would reuse, and visible or explicitly forced calls avoid the subtree walk. The actual callback, status, offset resolution, SetRect, DidReflow, fallback and overflow sequence remains intact. Dirty state can survive a skipped callback and later admit a query that forces real layout. This is the same protocol expectation as principal marking, applied to its independent absolute producer.

`MarkSubtreeDirty` is necessary rather than only AddStateBits: a leaf-first query may otherwise see a clean descendant even when its OOF parent is dirty. It still prunes already-dirty nodes and table column groups. This proposal does **not** establish a universal descendant invariant if earlier publishers made a parent dirty without its descendants. Anchor position-try direct dirty publication is such a distinct audit boundary; the reported failing fixture contains no anchors. The new parent-resize history challenges normal style invalidation without claiming exact native bits from JavaScript.

There is also bounded overmarking: the hidden predicate does not prove every frame class/continuation will skip its virtual callback. Block next-continuation paths and non-block callbacks must retain their existing semantics. Additional dirty work could occur only on an already-selected hidden OOF reflow, but runtime/performance validation is still required. The patch schedules no reflow itself and does not clear caches/properties or change frame ownership. Interruptions, anchor fallbacks, external placeholders, fragment continuations and callback/lifetime effects are not universally proved.

### Preserved provisional version

The initially announced `candidate.patch` and unversioned trace patches marked after RI construction. They are retained as superseded source proposals and were not executed here. `ReflowInput.cpp` reads subtree dirtiness during resize-flag initialization; v2 moves the mark before that construction so non-block/continuation work does not see an input initialized against the earlier dirty state. The original zero-return block example alone would not discriminate these placements. The late version is not recommended for execution.

## Alternatives

- Adding `MarkAllFramesDirty` beside principal marking in the flex hidden branch would cover its current absolute list, but it dirties even otherwise reusable explicit-offset children, does not cover an external absolute owner, and does not make this distinct producer disappear.
- Walking all child lists has similar scope/cost issues and still does not follow arbitrary placeholder links. It is broader than needed for the observed clean-to-zero producer.
- Skipping absolute reflow entirely changes initialization, fallback/status/overflow and fragmentation work. That is not proposed without a separate source contract.
- Marking only IS_DIRTY repeats the descendant-admission pitfall already observed with the partial principal repair.
- Centralizing invalidation in all skipped virtual Reflow entries might be a larger coherent redesign, but auditing one block early return does not justify changing every provider.

## Native trace required before acceptance

`baseline-trace-v2.patch` and `candidate-trace-v2.patch` are applied against the same retained original absolute file, not layered on each other. The latter includes the candidate. They report only calls whose in-flow parent is hidden:

- before marking/reflow: frame identity, dirty state, old dimensions and next-continuation presence;
- after the virtual call: same identity, dirty state and returned dimensions;
- after SetRect/DidReflow: same identity, dirty state and committed rectangle.

Run an isolated failing case first. The predicted baseline receipt is clean + 720×480 appunit old size → returned0×0 → clean committed rectangle centered at6000au. The candidate should retain dirty state across the same temporary zero commit, followed by a forced query returning the calibrated CSS rectangle. Geometry success alone does not prove that this trace happened. Initial nonempty/dirty states, different callbacks, or a next continuation require revising the causal claim. Logs use existing primitive geometry getters and `fprintf`, with an explicit stdio include; no build was done here, and root should verify declarations/format before compiling the diagnostic.

## Added leaf-first tests

`hidden-flex-oof-descendant-query.html` has eight tests: one/two hidden ancestors × static/explicit offsets × append/prepend. The observer is a leaf inside a 12×20 OOF parent, with 50% width, 40% height and margins1/2. It is queried three times before the reference or OOF parent; no direct parent rectangle read can mask clean-leaf admission. After hiding and in-flow insertion, the OOF parent is resized to20×30 before another leaf-first query, then shown.

Independent visible references must calibrate `[105,12,6,8]` and then `[101,12,10,12]` for centered static position, or `[18,21,6,8]` and `[18,21,10,12]` for explicit offsets. The reference checks run before target assertions. These fixtures are unrun; a reference failure is not a repair failure. Preserve the existing eight root-observer tests as well. A follow-up external-containing-block fixture would discriminate the per-OOF seam from marking only the flex owner's absolute list, but is not claimed covered by these eight cases.

## Specification oracle and status

An absolute child does not participate in flex layout; its auto-inset static position uses its sole-item alignment geometry, so an unrelated in-flow insertion does not make its specified 12×8 size disappear. [Flexbox positioned children](https://drafts.csswg.org/css-flexbox-1/#abspos-items). Hidden content suppresses rendering but permits requested geometry; the fixed-size, positioned container keeps the visible reference equivalent. [CSS Containment](https://drafts.csswg.org/css-contain-2/#content-visibility). The observer is border-box geometry. [CSSOM View](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect).

**Verdict: GO for a bounded diagnostic, HOLD native acceptance pending reached trace, all direct/leaf calibration results and regression gates.** No production, browser, build or Git mutation was performed. The candidate is not a proof that every hidden layout path has coherent dirty bits.
