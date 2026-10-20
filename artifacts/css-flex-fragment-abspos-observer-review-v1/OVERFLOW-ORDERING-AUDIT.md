# Overflow-container reflow ordering audit

Status: provisional native proposal; dirty/skip branch behavior is an explicit open gate. The root reports336 paired candidate WPT passes versus224 baseline passes/112 failures. No independent build/browser run was made here.

## Exact source roles

`standalone-overflow-proposal/SOURCE.json` pins the retained Git-base flex source and one-operation reordering candidate. `OVERFLOW-PROVIDERS.json` authenticates complete external providers against that same retained revision. The existing nsContainerFrame.cpp, ReflowInput.cpp/.h, nsIFrame.h and block sources are byte-identical to that base; the two added base headers preserve the actual tracker declarations and inheritance. Indexed search receipts corroborate the float-containing-block override set, without replacing retained-source identity.

## Reordered dependencies

1. NormalizeChildLists still runs at Reflow entry. Both original and proposed code construct the fragment's FlexLayoutResult before OC reflow; GenerateFlexLayoutResult enumerates the principal list only. The candidate does not move layout generation across OC mutation.
2. The original OC phase drains previous excess OCs, then its tracker chooses the next parent's OC list or current excess list. The candidate creates this tracker only after ordinary reflow/PushIncompleteChildren, so it does not leave a tracker or pointer into those lists live across ordinary mutations.
3. Ordinary ReflowChild can delete an item's NIF chain when it becomes fully complete. PushIncompleteChildren can create NIFs; steal/reparent an existing OC NIF when an item becomes normally incomplete; convert normal NIFs to OCs when only overflow remains; and move pushed ordinary children. These mutations occur before the candidate OC tracker is constructed.
4. A newly created current normal item's NIF has its PIF parent equal to the current flex fragment. PushIncompleteChildren either inserts it directly into the next parent's existing OC list or keeps it in current excess. Late Drain leaves current excess entries whose PIF parent is this intact. It does not reflow that newly created NIF prematurely as a current OC.
5. Drain does move previous-parent excess entries into current OC, and own excess entries whose PIF parent differs from this. The helper then explicitly skips a current-list entry unless its PIF parent equals the previous flex fragment. It preserves overflow-incomplete status when a next parent exists, preventing deletion of displaced nonempty continuations. This same gate remains in the candidate.
6. Current OC chains and current normal principal-item chains must obey the existing normalized continuation/list invariants. Under those invariants, normal item completion can remove future continuations of its own chain, while a valid current OC belongs to a chain rooted in a previous fragment. The candidate observes the updated live lists rather than stale OC iteration pointers. This is a source-level lifecycle argument, not a mechanized proof of every frame constructor/destructor invariant; no arbitrary frame graph is admitted.
7. OC ReflowChild still supplies the helper's tracker to AutoFinish around next-in-flow deletion. BeginFinish/EndFinish clear or repair sentry/list pointers after deletion, and Insert maintains continuation ordering and marks NIFs dirty when necessary. Reordering does not bypass these operations.
8. PopulateReflowOutput reads principal-item/line geometry and statuses and computes desired size/baselines. It has no frame-list mutation. It never reads ocBounds/ocStatus. The first-fragment avoid-break early return is outside the prevInFlow-only OC phase in both versions. Parent status is merged with OC status after Populate in both versions, before FinishReflowWithAbsoluteFrames and data-property retention/removal decisions.
9. Parent overflow reset and union remain after OC reflow. The candidate accumulates OC overflow in final physical coordinates directly; it does not move a frame after accumulating stale physical ocBounds. Ordinary line-item correction also precedes that union.

## Float-manager dependency

RecoverFloatsFor acts only for a block whose BlockNeedsFloatManager is false. The latter predicate is true whenever its parent is not a float-containing block. nsFlexContainerFrame inherits the false IsFloatContainingBlock predicate through nsContainerFrame/nsSplittableFrame; the indexed override roster contains only nsBlockFrame's true override. Thus a direct block OC under flex owns a separate float manager, so skipped RecoverFloatsFor does not import its floats into the parent. Non-block OC children do not enter RecoverFloatsFor either. A flex item's independent formatting context is consistent with this actual native predicate; the claim does not rely only on the spec name.

## Remaining skipped-placement obligation

The helper's skip branch calls tracker.Skip, optional RecoverFloatsFor, then ConsiderChildOverflow. It does not reposition the child. Supplying the final container size therefore only directly changes the reflow branch. For an existing OC whose prior normal physical position is W-S-B, unchanged physical position under a new final width F observes B+F-W. Logical B is preserved exactly iff F=W (holding actual child size fixed). This is proved in OverflowCoordinates.lean; it is not evidence that such a skip occurs for F != W in a browser.

ShouldReflowAllKids is parent DIRTY, inline resize, block resize plus CONTAINS_RELATIVE_BSIZE, or final column balancing. The other helper gates are child subtree dirty and old scrollable overflow exceeding available B. Incremental test success could be explained by any of these forcing reflow. Diagnostic source logs must record each term, old parent size, supplied final size, child normal/used position and actual selected branch. Detached-PIF early skips are a separate branch.

Do not force reflow speculatively. If a clean same-parent OC is observed skipping while F differs from its old physical container width, a narrowly scoped movement or dirtying correction needs its own source/relative-position/overflow-union audit. Newly drained/reparented OCs may have another previous coordinate frame, so blindly translating every current OC by F minus the old parent width is not justified.

## Numerical scope

OverflowCoordinates.lean proves the reversed block-coordinate placement equation and exact old-size/new-size adjustment. The bounded result explicitly requires finite nonnegative temporary/final widths below Q and child sizes in[0,Q], and proves each modeled subtraction/addition fits signed32. It excludes Q as the physical container sentinel and does not prove general callback, relative/sticky, orthogonal or extreme geometry safety. The standalone candidate introduces no wide arithmetic; the broader fragment prototype's complete physical/availability obligations remain separate.

## Required validation before native acceptance

- Explain and exercise actual skip behavior, including changed versus unchanged final fragment width.
- Validate item removal/reinsertion, resize, completion-to-overflow and overflow-to-normal transitions without stale/deleted-list access; retain the source invariant dependency rather than treating test counts as proof.
- Preserve ordinary writing-mode/direction/row/column controls and inspect relative positioning/border-padding as needed for the exact helper contract.
- Keep extreme cumulative/packing/absolute-continuation defects separate; a bounded overflow-position repair does not close them.

## Actual initial incremental trace

The selected parent diagnostic is retained under external-observations. Twelve OC visits all select reflow, with parent DIRTY=1 and childdirty=1. BResize=1 but CONTAINS_RELATIVE_BSIZE=0, so BResize is not the explanation; parentDIRTY is sufficient. The overflow-exceeds predicate was not evaluated (logged−1 due short-circuit). Initial parent widths0 become160/80px; the last parent's subsequent80→81→80px changes are correctly reflected. No skipped placement is observed.

A concrete upstream dirtying path exists in nsColumnSetFrame::ReflowColumns: reflowNext records the preceding column's NextInFlowNeedsReflow; when true, it calls child->MarkSubtreeDirty before creating the next column's ReflowInput. This dirties the flex descendant and its OCs recursively. ReflowDirtyLines can set NextInFlowNeedsReflow when pull processing remains incomplete, and flex child status propagates through block reflow. This is a source route consistent with the actual trace, not a logged attribution of the dirty flag's writer. The clean skipPull/skip-column branches prevent generalizing it to every reflow.

The helper's child writing mode also matters. A horizontal-rtl child's predecessor IStart is C-prevX-prevWidth, then placement is C-childWidth-IStart, so C cancels. A vertical-rl child's B0 placement is C-childWidth. The added kernel results retain that distinction and the exact scalar relative-offset translation identity; no universal parent-width delta is proposed.

## Other fragmentation entry routes and scope conclusion

Standard pagination: nsPageSequenceFrame::Reflow returns without descendant reflow when FIRST_REFLOW is absent. Its optional unfragmented measuring pass is followed by MarkPrincipalChildrenDirty before normal pagination. nsPageFrame/ContentFrame pass reflow through to canvas. This excludes an ordinary incremental page-sequence route to a clean surviving OC with changed width; it is not a proof about arbitrary direct calls to individual page frames or every pagination retry.

Nested multicolumn layout: child ReflowInput copies parent flags, retaining mIsInLastColumnBalancingReflow; the constructor resets mIsColumnBalancing separately. A final balancing flag therefore forces ShouldReflowAllKids down nested descendants. Earlier balancing passes and clean skipPull status paths are not universally closed by that flag. The executed external-sizing trace now confirms column reflowNext marking for24 visits (including18 previously clean column children), with exact OC parent identity joins, but cannot be extrapolated to all nested retries.

Table special block-size reflow: the ReflowInput constructor asserts frames carrying mSpecialBSizeReflow are clean, so it was investigated as a genuine alternative source entry. nsTableCellFrame clears that special flag before its child reflow and forces BResize. nsTableFrame's measuring/final pass and status-complete condition do not by themselves establish that any already fragmented flex OC survives clean into the changed-width pass. This route remains a caller-domain boundary, not a browser counterexample.

For native retiming, unchanged skipped text alone is insufficient. The relevant source preservation argument is that, under existing normalized continuation/list invariants, an eligible current OC belongs to a previous-fragment chain, disjoint from current principal normal-item continuation chains. Ordinary reflow can create/delete/reclassify future NIFs of current normal items but should not change the surviving eligible OC's dirty state, stored position or old-parent-size-based overflow predicate. Populate writes desired output rather than committing the parent's current GetSize. The tracker is constructed after ordinary mutations and the final bounds union remains after both phases. This supports bounded repair review; it is not a universal proof of skipped placement, arbitrary frame graph integrity, or cross-subtree layout callback independence.

No immediate introduced regression has been demonstrated. Relative/child-writing-mode probes are separately proposed because container-size dependence is determined by child writing mode and callbacks may observe early positioning. General numeric/fragment-model obligations from the previous proof contract remain open. A hypothetical stale skipped child would need reachability and old-versus-new attribution before being labeled an introduced defect or an additional independently packaged repair.
