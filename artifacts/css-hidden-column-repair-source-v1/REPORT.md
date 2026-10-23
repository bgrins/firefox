# Conditional column-query provider repair

Status: **conditional source proposal, not a confirmed bug or accepted patch**. Runtime is root-owned and pending. This artifact changes no native code and performs no build, browser, compiler or Git work.

## Smallest candidate to evaluate after a positive probe

Keep column/group geometry queries associated with their original primary frame. In `PresShell::UpdateHiddenContentInForcedLayout`, before the clean-frame early return, separately identify the frame supplying column geometry:

```text
if queried frame is absent: return
provider = queried frame
if queried frame is a table column:
    provider = column.GetTableFrame()
else if queried frame is a table column group:
    provider = group.GetTableFrame()
if neither queried frame nor provider is subtree-dirty: return
continue the existing in-flow-ancestor walk from queried frame
```

This is uncompiled pseudocode, not a ready native patch. Using the existing typed accessors would require the corresponding table declarations/includes; a narrowly checked parent traversal expresses the same documented structure without adding a public API. Ordinary frame behavior remains the existing predicate. Keeping the queried-frame alternative also preserves existing handling of dirty columns/groups whose table flag alone is insufficient.

**Do not simply replace `aFrame` with its table for the remainder of the method.** The existing walk starts at `aFrame->GetInFlowParent()`. Retaining the original target preserves every intermediate hidden ancestor, including any hidden geometry provider itself. Substituting the table and then starting at its parent could skip that provider. This warning is about preserving the existing traversal semantics, not an assertion that every such hidden-table combination is reachable.

The method queues forcing; its caller performs the flush. `nsIContent::GetPrimaryFrame(Layout)` reacquires the original element's primary frame afterward. Do not return the table as the element's geometry frame, or retain a column/provider pointer across that flush. No new pointer is needed after the existing scheduling call.

## Why consult the table instead of dirtying columns

The accepted source audit established that table layout writes column/group rectangles through `SetColumnDimensions`; their own Reflow routines return dummy zero dimensions. The table child loop reflows dirty column groups mainly for dynamic style/border-collapse work. Removing `MarkSubtreeDirty`'s exclusion would expand that work for all callers, including unrelated layout paths, and change dirty-bit lifetime. It is a much wider response to a query-readiness problem.

The proposed predicate instead recognizes a known geometry dependency at the hidden-query gate. It does not prove that a dirty table always changes a column's rectangle; it conservatively requests current geometry when that provider is pending. Conversely, if both target and table are clean while a higher ancestor's pending placement makes the observation stale, this predicate does **not** solve the case. That possibility must be distinguished by the runtime/source trace, not hidden by an assumed provider-dirty premise.

## Continuation and caller handling

`nsTableColFrame::GetTableFrame` routes through its column group. `nsTableColGroupFrame::GetTableFrame` asserts a table parent with no previous in-flow. Column span construction creates additional same-parent columns and links them as nonfluid continuations. Thus the primary column and its span-generated continuations use the same table owner; no new continuation traversal or first-continuation coercion is justified for this lookup.

Do not generalize this fact to all fragmented table geometry. The first-in-flow table supplies column widths, but table layout may separately handle fragment block extents and collapsed rows/columns. Hidden fragmented-table behavior and span box-union observations remain test obligations. The proposed lookup does not alter the geometry collector's existing continuation handling.

Searchfox identifies two callers of Update: `EnsureReflowIfFrameHasHiddenContent` and the `ScrollContentIntoView` path that makes content-visibility:auto ancestors temporarily visible. Changing the shared predicate affects both. Keep the existing scroll path's ancestor/visibility sequencing and test it; alternatively placing the special case only in Ensure would intentionally leave that other caller unchanged and needs an explicit narrower scope. No reason to change ordinary scrolling behavior was established here.

## Evidence required before implementation/acceptance

1. The prepared eight-case probe must pass its visible calibration. Preserve col/group failures separately from cell/table controls and repeat reads.
2. For an actual failure, observe the selected primary-frame type and direct/HAS_DIRTY_CHILDREN bits, the table-provider bits, and whether the table's rectangle publisher ran. A dirty provider is essential to this minimal predicate's claimed repair.
3. Preserve original target geometry after forcing. Exercise both col and group, a `col span` case, visible/no-hidden controls and a no-mutation repeat. Include a separated fragmented-table check rather than asserting global continuation coverage.
4. Recheck hidden principal and OOF cases independently. If the failure needs the pending principal/OOF repair to make its table dirty, that prerequisite must be reported; this artifact does not establish independent upstream landability.

Do not force every column query unconditionally merely because a hidden ancestor exists. That could request repeated full layout even when the table has already completed; the current cost investigation makes that an important separate behavior to measure.

## Source identity

The prior source audit is authenticated under FILES `50d6ccb33f1d49f5c823b0ea9cb3dcb65a99b928946f3eecdba82e96bb762b15`. Four newly inspected complete bodies match local source exactly once (SOURCE-PINS.json). Searchfox fetches are retained as discovery snapshots; overload/name lookups returning no complete definition are preserved but not used as complete bindings. The fetched complete PresShell file supplies the actual scrolling caller context. No whole Searchfox/local/browser revision identity is inferred during the running experiment.
