# Ordinary hidden-block residual: skipped line versus frame readiness

**Finding:** a concrete, source-supported producer/query mismatch is plausible beyond the column-provider issue. This is not seven separate bugs and is not yet a validated repair. The report retains a minimal offline experiment patch; no live source, Git, browser, build or compiler was changed/run.

## What the actual eight cases show

I independently recounted the completed baseline and both raw WPT rows from `css-hidden-layout-column-runtime-v1`: the eight exact status/message pairs are identical. Seven fail at the first `change` query after all visible/outer-flush calibrations. Source/test pins are stable within each phase. The enclosing experiment's restoration and final seal are root-owned; this audit records hashes of the completed receipts and raw files rather than treating the whole runtime as independently accepted.

| Mutation | col | colgroup | td | table |
|---|---|---|---|---|
| Outer width 100→50 | stale 50, expected25 | stale100, expected50 | stale50, expected25 | stale100, expected50 |
| Table width100%→50% | stale50, expected25 | stale100, expected50 | stale50, expected25 | PASS50 |

Every observer gets its own fixture, so the passing table query does not flush the failing descendant cases. The mutation path is ordinary block layout: `.outer > .subject(hidden) > .item > table`. The fixture host is absolutely positioned for stable page coordinates, but neither `.item` nor the table is an OOF child, and no flex container exists. The existing principal-flex and OOF repairs therefore do not directly mark these skipped block descendants. This explains why their table/cell controls can recover while these ordinary-block controls still fail.

## Actual producer seam

The retained tested HEAD `nsBlockFrame.cpp` has three distinct states:

1. `TrialReflow` calls `PrepareResizeReflow` for an inline-size resize when the block itself is not directly dirty. `PrepareResizeReflow` marks **line boxes**, including block lines, dirty. It does not mark the line's child frames or their descendants dirty.
2. `ReflowDirtyLines` calls `ReflowLine` for selected dirty lines. `ReflowLine` first calls `aLine->ClearDirty()`, then detects that the first child is hidden by its in-flow parent, and returns without child reflow when the owning block lacks `NS_FRAME_OWNS_ANON_BOXES`. That return also performs no frame/subtree dirty publication.
3. `UpdateHiddenContentInForcedLayout` tests the **queried frame's** `IsSubtreeDirty()` before walking hidden ancestors. It does not inspect a parent's line-box flags. A stale clean descendant can therefore fail the query gate even though resizing its skipped ancestor would change its geometry.

For this DOM, `.subject` owns the line containing `.item`; `IsHiddenByContentVisibilityOfInFlowParentForLayout` consults that immediate in-flow parent and its hidden-layout state. The source branch is plausible for the fixture, but a per-case line-skip→frame-bits→query trace has not yet been captured. The reported column trace supplies aggregate dirty-provider occurrences, not this missing join.

`LazyMarkLinesDirty` is the opposite-direction bridge: when the block has `NS_BLOCK_LOOK_FOR_DIRTY_FRAMES`, it notices dirty child frames and marks their lines. It does not convert line dirtiness into dirty descendants. Preserving the skipped line's dirty flag alone would consequently not open the existing target-frame query gate. It could also leave repeated ordinary layout work without establishing query freshness.

The separate `nsBlockFrame::Reflow` hidden-parent early return precedes `MarkInReflow`, calls `FinishAndStoreOverflow` and returns when there is no next continuation. It is an additional entry seam, not proved to execute in these cases: the earlier parent-line skip can prevent that child call entirely. The offline patch intentionally does not combine those two mechanisms.

## Table primary versus geometry provider

The Searchfox construction chain maps table display to `ConstructTable` via a full-constructor descriptor; that descriptor sets `FCDATA_FUNC_IS_FULL_CTOR`. `ConstructTable` returns the table **wrapper**, with the styled inner table as its principal child. `ConstructFrameFromItemInternal` installs the full constructor's returned frame as the content primary. Thus the table element's initial query readiness is wrapper readiness, while the column/group provider accessors select the **inner table**.

The direct table-width/table PASS is consistent with a direct style invalidation leaving the table primary eligible, so its query forces the enclosing hidden block and recovers geometry. A clean cell or column can still return before that ancestor walk. This is an inference, not a traced assertion that a particular wrapper bit was set: existing table-only tracing may omit the wrapper because it is not `IsTableFrame()`. Add the wrapper explicitly to a discriminating trace.

The earlier column gate proposal only adds clean-col/group access to a dirty inner-table provider. It does not admit a clean `td`, a clean table wrapper, or a clean inner provider merely because an ancestor line was skipped. It therefore cannot be advertised as a complete repair for these seven failures.

## Minimal offline experiment candidate

`skipped-line-candidate.patch` adds only this action inside the existing hidden/!OWNS_ANON_BOXES early return of `ReflowLine`:

```cpp
for (nsIFrame* child : aLine->ChildFrames()) {
  child->MarkSubtreeDirty();
}
```

Marking only the first child would miss later frames on an inline line; use the exact line child range. Marking all block principal children would unnecessarily include other lines not being skipped at this point. The prototype retains `ClearDirty`, the existing hidden test, the anonymous-owner exception, and every other line/placement path. It does not turn line dirtiness into a global native invariant.

The existing helper's barriers remain material: already-directly-dirty roots prune recursion, descendant table-column groups are skipped, and external OOF targets are not followed through placeholders. Thus full descendant coverage needs the existing dirty-subtree producer conditions; it is not guaranteed by calling the helper. The table provider query change could remain complementary for columns after this candidate makes the table/cell path eligible. No expected outcome is relaxed if either candidate fails.

Keep floats/placeholders, inline siblings, anonymous-owned children and fragmentation explicit boundaries. The source comment justifies skipping the whole inline line when its first child is hidden, but does not prove every future DOM/frame family satisfies a new dirty-closure law. The patch is an experiment candidate, not a recommendation to apply globally without tests.

## Next discriminators

1. Keep all eight current cases and exact rectangles. Add a table-first rescue on a separate instance: table-width should recover its subsequent cell/column reads if the wrapper-ready explanation is correct; outer-width need not. Also record selected primary kind and both dirty bits for the wrapper, inner table and cell before forcing.
2. Replace the table subtree with ordinary percentage-width nested blocks and two inline-block siblings. This distinguishes a general skipped-line readiness failure from a table-specific problem, and tests why first-child-only marking is insufficient. Use visible reference, outer-only flush, first/repeat query, restore and show stages unchanged.
3. For the producer patch, trace just the hidden `ReflowLine` return: owning block, first child and exact child range, block/inline line kind, line dirty state before ClearDirty, and each child's two frame dirty bits. Join these identities to the later query and table publisher; do not infer a lifetime join from aggregate pointer counts.
4. Preserve no-mutation/visible controls, a directly dirtied descendant, col-span query, an anonymous-owned parent control and one calibrated fragmentation case. Pair line-only, column-gate-only and combined candidates if needed to separate coverage. No broad ancestor-force policy is proposed.

## Source evidence and scope

Three complete block methods and three explicitly labeled excerpts match both the tested retained HEAD snapshot and fresh Searchfox source exactly once. Their complete file hashes differ in unrelated content; no whole-revision identity is inferred. The constructor/wrapper discovery bodies are kept as Searchfox roles, with full fetched-file hashes where available, not silently promoted to the runtime binary's constructor identity. Full downloaded files are not duplicated here; small relevant bodies/excerpts and exact parent source pointers suffice.

Failed DNS lookups and the incomplete `--define nsBlockFrame::Reflow` response are retained and not treated as complete bindings. The successful full-file fetch supplies the matching block slices. `SOURCE-PINS.json` pins the exact input, offline candidate and patch, and `RUNTIME-SUBSET.json` retains the independent raw recount. No universal hidden-layout, provider, lifetime or CSS-conformance proof is claimed.
