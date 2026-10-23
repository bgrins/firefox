# Column residual: proposed trace and independent trigger

## Evidence boundary

Root reports principal-only results in the active compact experiment: principal table/cell observers recover, while column/group observers retain50/100px instead of25/50px after insertion. This is an observable residual of that tested principal candidate. Its final immutable runtime receipt is not yet incorporated here. Baseline also fails the table/cell controls, so baseline results alone did not isolate a column-specific issue.

No claim is made that this third issue is independently reachable on upstream without the principal/OOF repair. No native repair is proposed in this artifact. All contents are uncompiled/unrun diagnostics; the current root experiment remains untouched.

## Two-file trace-only proposal

`trace-only.patch` modifies offline snapshots of PresShell.cpp and nsTableFrame.cpp. Each original and trace full-file hash is in SOURCE-PINS.json. These two files are outside the active experiment's21 source variants. Root must still authenticate live bytes and restore/rebuild after any separately authorized trace phase.

- Immediately before `UpdateHiddenContentInForcedLayout`'s clean guard, log column/group/table target pointer and direct/HAS_DIRTY_CHILDREN bits, the typed-parent-chain table pointer, whether it is actually a table, and its two dirty bits. The table pointer is only read; query routing is not changed.
- Immediately after the two real SetRect operations in `SetColumnDimensions`, log table pointer, target pointer/type and local rectangle. These are publication observations, not a claim about global CSSOM coordinates.

The `CV_COLUMN_QUERY` and `CV_COLUMN_PUBLISH` tags permit matching a clean column query to its provider and the most recent size publication. Table control queries are included. There is no whole-layout trace, extra reflow, style change or timing measurement. Pointers are process-local diagnostic identities only and can be reused after fixture destruction.

Expected discriminating trace for the principal residual: after outer insertion, column/group target is clean, provider table is dirty, and its stored publication still has the prior width. The query then returns without a new publication. A separately constructed table/cell control forces recovery and publishes the new widths. If provider bits are also clean, the proposed provider-dirty predicate from the preceding source memo is insufficient and must not be implemented on that premise.

Use the existing eight-case probe for the candidate comparison, preferably one independently created test at a time if correlating pointer lifetimes is ambiguous. Do not query a parent table in the failing fixture before the column observation. Instrumented observations cannot be combined with uninstrumented performance counters.

## Independent upstream-oriented trigger

`hidden-column-independent-trigger.html` contains eight additive testharness cases with no flex layout, out-of-flow child or measurement-cache-key dependency:

1. Change an ordinary outer block width100→50→100 while a nested100%-width table is under a hidden ordinary block. This changes the containing width without directly styling the column/table subtree.
2. Change the table width100%→50%→100% under the same hidden block. This is also a direct-invalidation control: style-driven recursive dirtying may already mark columns and make the query work. It must not be assumed to trigger the pruning path.

Each route has separate col, colgroup, cell and table fixtures, an independent visible peer, warm/hide/change/restore/show stages, and repeat selected queries. Only the outer box is read before the selected target. All visible and outer calibrations are asserted before target equality. No numeric expectations are relaxed. The full40 stage records are retained in `window.columnIndependentResults` for a root-owned loopback collector.

The visible width oracle is explicit: table100/50, equal columns50/25, row height32, position10,10. These values remain subject to the visible calibration, rather than assuming every nominal table width is used. Native table wrapper Reflow does not contain the block's same early hidden branch; its retained definition is evidence that this route differs from the flex skip, not proof of a failure.

Possible outcomes: a calibrated column-only failure on release establishes an independent trigger to investigate; a clean result is a bounded negative; failure of all targets indicates a broader forcing path needing separation. Either result preserves the already observed candidate residual. Do not make independent-landability claims until the relevant original-source/browser route is actually tested.

## Use and limits

The patch is an offline textual diagnostic only. It has not been compiled, formatted, applied to a native tree or run. The HTML has not been executed. Source and fixture inspection used the existing frontend skill and retained layout instructions. Root owns the next browser/build window and final source identity.
