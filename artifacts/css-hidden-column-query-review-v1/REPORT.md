# Hidden column geometry: independent source audit

Status: **source-supported conditional failure path; no browser bug or repair established**. This is separate from the running principal/OOF experiment. No native edits, compiler, build, browser or Git operations were performed.

## Query target and geometry owner differ

Both `Element::GetBoundingClientRect` and `GetClientRects` request `GetPrimaryFrame(FlushType::Layout)`. The implementation is `nsIContent::GetPrimaryFrame` in Element.cpp. It first performs the ordinary document flush, obtains that element's primary frame, passes the same frame to `EnsureReflowIfFrameHasHiddenContent`, and reacquires the primary frame afterward. This reacquisition is important if forcing changes frame ownership.

`EnsureReflowIfFrameHasHiddenContent` calls `UpdateHiddenContentInForcedLayout` then the pending hidden-content reflow. Update's first test is `!aFrame || !aFrame->IsSubtreeDirty()`. A clean selected column/group is rejected before walking any in-flow ancestors. No column-to-table promotion occurs on this inspected path. The initial ordinary document flush can still make geometry current, so the source alone does not prove a stale observation.

`nsTableFrame::SetColumnDimensions` supplies the observable group/column rectangles. It derives block extent from table size, border/padding and row spacing; widths come from the first-in-flow table's column widths. It calls SetRect for the group, then each column relative to that group. Table Reflow invokes it after its main size calculation. Column/group geometry is therefore not supplied by their ordinary zero-size Reflow return values.

## Why the pruning matters

`MarkSubtreeDirty` marks its root, but its descendant worklist skips any table-column-group before marking or descending into it. Consequently a formerly clean group and its columns may remain clean while the table that supplies their geometry is dirty. This is exactly the conditional barrier retained in the earlier proof, not a proof that the browser fixture reaches it.

The table child-reflow loop explains the convention: column groups do not care about dimensions or reflow inputs; reflow is mostly needed for dynamic style changes involving border collapse. Only subtree-dirty groups are reflowed there, with dummy sizes/position. Group Reflow visits its columns using dummy sizes; column Reflow clears its output size and checks visibility-collapse; group Reflow also clears its own output. The table later installs their real rectangles.

This is evidence for avoiding unnecessary column reflows, not a historical explanation of the original pruning change. Dirtying groups is not intrinsically prohibited: the existing loop explicitly supports dirty groups, style changes propagate border-collapse damage to the table, and ordinary broad FrameNeedsReflow dirtying does not use this pruning. Removing the exclusion would nevertheless add zero-size reflow/finish work and dirty-lifetime effects. Neither its safety nor its cost is established by the abstract coverage counterexample.

## Existing provider to investigate if the diagnostic fails

There is a concrete typed route:

- Column `GetTableFrame()` calls `GetTableColGroupFrame()->GetTableFrame()`.
- Group `GetTableFrame()` returns its parent table and asserts that the parent is a first-in-flow table.
- `SetColumnDimensions` explicitly consults that first-in-flow table for widths.

If a clean column query is stale while querying its dirty table repairs it, consulting the table's readiness before the forcing guard is an implementation avenue. It is **not a patch recommendation yet**. A solution must preserve the original geometry target, reacquire it after a potentially reconstructing flush, and account for spans, anonymous groups, collapsed columns, and table fragmentation. The relevant provider may itself be clean while an ancestor has pending geometry; the typed accessor alone is not a complete freshness predicate.

## Diagnostic and next evidence

Authenticated peer capsule `css-hidden-table-column-query-v1`, FILES `4d4f7acc9f167e841aaf2ca691a7bd7479caa84af1e11134b530582fd5667518`, supplies eight unrun cases: principal shrink and absolute-position routes, each with independent col/colgroup versus cell/table controls. Keep visible calibration and repeated reads; querying a table control first in the same instance could repair the candidate and erase discrimination.

A useful positive result needs calibrated column-only discrepancies, source/binary identities, and evidence that the selected primary frame is clean while its table/provider is pending. A useful negative result is that this exact sequence stays correct; it would not disprove every abstract dirty barrier. No expected geometry was relaxed and no fixture changed by this review.

## Source identities and limits

Searchfox was used for discovery. Three initial sandbox network failures and the mistaken `Element::GetPrimaryFrame` symbol lookup are retained. The correct implementation was located with `nsIContent::GetPrimaryFrame`; an initial local comparison against nsIContent.cpp was corrected to Element.cpp and recorded.

Nine relevant complete discovered bodies match the local source exactly once, recorded in SOURCE-COMPARISON.json. Complete fetched nsTableFrame.cpp differs from the local file in unrelated allocation/background-constructor contexts, retained in TABLE-SOURCE-DIFFERENCE.patch; no whole-revision equality is claimed. Source snapshots/receipts are pinned by this artifact, not asserted to identify the running binary. The current root experiment owns source changes and all runtime work.

This review resolves the narrow source ownership/query question. It does not settle normative CSS column geometry, frame reconstruction, every table provider, or full hidden-layout correctness. No Lean model was added merely to restate the unresolved native predicate.
