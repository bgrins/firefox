# Hidden table column observer: source-derived diagnostic

Status: concrete source-path hypothesis and eight unrun diagnostic tests. No browser failure or accepted bug is claimed. This is separate from the sealed ordinary fallback negative finding and from the current four-variant runtime inputs.

## Why the pruning exception may be observable

`nsIFrame::MarkSubtreeDirty` skips a `TableColGroup` frame before marking that frame, and consequently does not visit its column children. Ordinary `PresShell::FrameNeedsReflow(IS_DIRTY)` does not have that pruning, so a broad dirty style update is a poor distinguishing fixture.

`Element::GetBoundingClientRect` and `GetClientRects` both obtain the selected element's primary frame with `FlushType::Layout`. `nsIContent::GetPrimaryFrame` first performs an ordinary document flush, then passes that **same primary frame** to `EnsureReflowIfFrameHasHiddenContent`. That method calls `UpdateHiddenContentInForcedLayout`, whose first guard rejects a frame that is not subtree-dirty. The inspected admission path does not promote a column-group target to its dirty table ancestor before testing dirtiness.

Meanwhile `nsTableFrame::SetColumnDimensions` writes actual column-group and column rectangles from table row height and column widths. Column/group `Init` bodies do not mark them nondisplay. `nsTableColGroupFrame::Reflow` reflows columns with dummy zero sizes; the later table-owned dimension update matters. These facts make a direct column query materially different from a query on a dirty table/cell, even though all rectangles are ultimately supplied by the table layout.

The attempted symbol lookups in `frame-bounding.txt` and `all-rects.txt` returned unrelated internal contexts. They are retained as discovery failures and are **not** used as complete method bindings. The actual no-promotion conclusion concerns the complete Element/GetPrimaryFrame/PresShell chain retained separately; it does not require a claim about every later geometry collector branch.

## Eight-case fixture

`hidden-table-column-queries.html` has two routes and four independently created targets:

- Principal: a 100px-wide flex container contains a shrinking 100px item with a fixed-layout 100%-width table. Appending an equal sibling changes item/table width to50px; each of two columns becomes25px. Removing restores100/50. This changes the actual table geometry without directly styling the column or table subtree.
- Absolute: a 100px-wide absolute item is centered at x60 in a 200px flex container at x10. In-flow sibling insertion should not change its100px width or static center. A skipped absolute reflow that commits zero size can shift its stored position; querying a clean column frame may fail to trigger the dirty ancestor's recovery.
- Targets `col` and `colgroup` exercise the pruned frames. Separate `td` and `table` tests are dirty-target controls. They use separate fixture instances so the controls cannot recover the column tests first.

Each test records warm, hide/query, append, remove, and show. The hide/query stage intentionally provides an opportunity to establish clean queried frames before sibling mutation. Only the outer flex container is queried before the selected target; no parent table/item query rescues it first. Two repeated target reads are retained. Every stage has an independent visible peer and explicit integer geometry. All visible calibrations are asserted before target failures, so wrong column-box assumptions are distinguishable.

The fixed-layout table has no borders, spacing, padding, caption, or text; its two columns split available width equally and its single row is32px high. The absolute case checks position as well as size; merely comparing old column widths would miss an erroneous zero-size parent centered elsewhere. Initial dirty bits, whether this exact sequence reaches a clean column group, and native frame selection remain runtime questions.

## Normative observation boundary

The current [CSSOM View getClientRects algorithm](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), verified22October2026 (ED8October2026), describes associated box-fragment border geometry and its table/caption special handling. The [bounding-rectangle algorithm](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect) derives its result from those rectangles. The test additionally calibrates that these table column boxes actually have the assumed observable geometry. Hidden layout queries must be assessed with the existing content-visibility forcing oracle; this note does not infer a new exception from a Gecko dirty-bit name.

Recommendation: run this separate eight-test diagnostic only after the active experiment is restored, preferably both repaired and baseline variants. A column-only failure with passing visible, cell, and table controls would justify tracing target dirty bits and `SetColumnDimensions` execution. If all pass, record a bounded negative; do not change the helper solely because an abstract pruning countermodel exists. No native patch is proposed here.

JavaScript parsing and callback registration were checked with Node; exactly eight names were produced. No test callback, Firefox process, Gecko build, Git operation, or production mutation was executed.
