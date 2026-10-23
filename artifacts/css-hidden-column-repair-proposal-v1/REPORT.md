# Hidden column queries: minimal provider-readiness candidate

Status: **uncompiled source proposal, pending runtime provider trace and independent review**. No production source, browser, compiler, build or Git operation was performed. The full retained pre-instrumentation PresShell source is the input, not the changing live source of the root experiment.

## Change

`native.patch` modifies only the entry predicate of `PresShell::UpdateHiddenContentInForcedLayout`. Null still returns. An already-subtree-dirty frame immediately follows the original path without any provider lookup. For a clean frame, checked immediate parents recognize exactly column → column group → table or column group → table; only a subtree-dirty table permits proceeding. Other clean frames and clean columns/groups with clean providers return as before.

The original `aFrame` is never replaced. Its complete `GetInFlowParent` walk, hidden-content set updates, and reflow scheduling body are byte-identical. The geometry query still returns the original element's primary frame after the existing post-flush reacquisition. No includes, public APIs, new state, column dirtying or unconditional forcing are introduced. Checked parent links avoid adding table-type header dependencies and fail closed for a malformed/unrecognized chain; such a chain is not claimed reachable.

The new behavior is conservatively broader only at the readiness predicate. It is not a proof that arbitrary extra reflow is observationally inert, nor that all stale geometry is detected.

## Source joins

The authenticated retained accessors give the exact structural relation: `nsTableColFrame::GetTableColGroupFrame` asserts its parent is a column group; its `GetTableFrame` delegates to that group. `nsTableColGroupFrame::GetTableFrame` asserts a table parent with no previous in-flow. The candidate expresses those immediate-parent checks without casts. It does not search arbitrary ancestors or substitute a table wrapper.

`nsTableFrame::SetColumnDimensions` publishes both group and column rectangles. The separate col/group reflow routines do not independently provide those final dimensions. `MarkSubtreeDirty` intentionally skips column-group descendants. Consulting the table therefore follows an actual geometry dependency instead of changing that general dirtying convention.

The before snapshot contains the full changed method and both calling paths. `EnsureReflowIfFrameHasHiddenContent` calls Update and then `ReflowForHiddenContentIfNeeded`; `nsIContent::GetPrimaryFrame(Layout)` reacquires its original primary frame after Ensure. The local provider variable is read only before scheduling and is neither stored nor used after a flush. The scrolling path sets auto-visibility flags, calls Update, updates relevancy, then flushes; its sequencing remains unchanged, but the broader clean-column predicate affects that caller too.

Retained column construction creates span columns with the same parent and nonfluid continuation links. The proposal does not change geometry collection across those links. Broader fragmented-table publication, collapsed columns and continuation-specific block extents remain separate tests/obligations. No first-continuation coercion is added.

## Evidence and next gate

Root reports principal-only runtime repairs the table/cell controls but leaves clean column/group append observations at 50/100 instead of 25/50; OOF-only likewise repairs table/cell controls while column/group x remains 110 instead of 60. These are parent-reported ongoing experiment results, not authenticated runtime evidence inside this source capsule. They support the focused investigation, but do not establish that the table provider is dirty at the query gate.

The decisive trace must join the queried primary pointer/kind and bits, the checked table pointer and bits, and `SetColumnDimensions` publication. If the provider is also clean while some other pending placement makes the column observation stale, this candidate is insufficient. No such case is excluded by assumption here.

After that trace, root can test the candidate on both prerequisite configurations and on the separate ordinary-block width/table-width trigger in `css-hidden-column-diagnostic-v1`. A release/upstream-independent trigger is still needed before claiming independent upstream runtime repair. The patch is source-local and contains neither principal nor OOF repair, but semantic runtime independence is not established by textual separation.

Retain existing exact rectangle assertions. Additional bounded gates: col/group plus cell/table controls; clean repeat query; visible and no-mutation control; direct dirty column; col span and group span; content-visibility:auto scrolling; and a separately calibrated fragmented-table case. Keep first-query recovery cost separate from subsequent unchanged-state queries.

## Validation and limits

All payloads of three externally pinned predecessor source capsules were authenticated before copying selected evidence. The candidate was generated by one exact replacement; the remainder of the full file is identical, including the entire ancestor/scheduling suffix. `SOURCE-PINS.json` records before/candidate/patch identities and a corrected development manifest-format mismatch. Existing source comparison records are historical body joins, not claims that Searchfox and the running browser share a whole revision.

No C++ syntax/type/format gate, apply/reverse on current HEAD/upstream, browser pair, scheduler completion, universal table provider-readiness proof or native acceptance is claimed. `OBLIGATIONS.md` states the precise proposed proof boundary.
