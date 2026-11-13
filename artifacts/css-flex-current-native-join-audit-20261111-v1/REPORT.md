# Current native join audit

No new browser defect was established. A concrete **initial clamp-diagnostic candidate** was found, together with a high-value **entry-specific line producer invariant** and positional diagnostic-array join. This is independent of the stored-prefix weight producer now assigned to root/design. No native code, browser, build, compiler, Git, canonical package, or frozen proof was changed.

## Exact version

The audited current `nsFlexContainerFrame.cpp` is SHA256 `210a38a494eba5ebc666ad6409c4b4f5b6651668c8bc6f9ef5b02834d578e733`. Against the accepted wide-caller design's source snapshot, the whole-file difference is exactly `GetWeight` returning double and promoting `mFlexShrink` before multiplication. `DESIGN-TO-CURRENT.patch` preserves that delta. All resolver correction, clamp, report, selection, and count control flow is byte-identical to the approved snapshot. Finite-weight arithmetic evidence must bind this new version explicitly; it is not silently covered by the old source provider.

The accepted twelve-part Lean theorem remains unchanged. Its generic semantic input is positional acquired deltas; its representation theorem requires the correlated budget. It does not establish the native provider or native initial seed acquisition. The root acceptance inventory is independently authenticated by `check.py`; this audit does not repeat its compiler replay.

## Initial clamp-diagnostic candidate

`GenerateFlexItemForChild` saves local `flexBaseSize`, `mainMinSize`, and `mainMaxSize` from `childRI`. It later calls `ResolveFlexBaseSizeFromAspectRatio`, freezes grow=shrink=0 records, and classifies their min/max clamp using those earlier locals. Only afterward does `ResolveAutoFlexBasisAndMinSize` resolve an unconstrained block-axis base by measurement, calling `SetFlexBaseSizeAndMainSize`. That setter changes base/current but does not recompute frozen clamp flags. `UpdateFlexLineAndItemInfo` exposes those flags as `clampState`.

The minimal candidate is a column container with one `flex:0 0 auto; min-height:0; max-height:100px` item containing a 20px child. If the initial block-axis base is unconstrained, the early comparison marks max-clamped; measurement then gives base/current 20px without actual max clamping, but the report can retain max-clamped. This is a concrete source-path hypothesis, not a browser reproduction. Aspect-ratio base replacement creates a second stale-local route whose input acquisition still needs testing.

Searchfox's existing `test_flex_item_clamp.html` covers 14 default-row cases, including inflexible min/max clamps, but no column content-measurement case. It therefore does not settle this candidate. `PROBE-DESIGN.md` gives a small chrome API matrix with genuine clamp and explicit-base controls. No test was installed or executed. The accepted caller target permits initially frozen clamp metadata as input and proves its preservation; it does not certify the meaning of those acquired flags. A confirmed diagnostic mismatch would require fixing/reviewing that producer, not changing the accepted preservation theorem.

## Concrete producer finding

A global claim that every native `FlexLine` satisfies frozen-count agreement would be false. `GenerateFlexLayoutResult` creates a fresh line (count starts at zero), then appends `CloneFor` copies of cached items without `AddLastItemToMainSizeTotals`. Copies retain frozen state. A one-item frozen continuation therefore has one frozen record with zero cached count. This is a source-derived counterexample to an overbroad invariant, **not a native bug**: the `Reflow` continuation branch bypasses `DoFlexLayout` and `ResolveFlexibleLengths` and reuses earlier positions.

The actual resolver entry has a different producer chain:

1. `DoFlexLayout` starts a fresh result and calls `GenerateFlexLines`.
2. Each new record is appended but still pending bookkeeping. If wrapping, `PopLastElement` transfers that pending record to a fresh line before any accounting. Thus the previous line needs no frozen-count decrement. Existing lines and record order survive transfer.
3. `AddLastItemToMainSizeTotals` runs once on the final owning line; its `IsFrozen` test counts already frozen normal items and struts as well as active items.
4. Collapse restart clears the old lines and calls `DoFlexLayout` again; it does not reuse resolver-mutated counts.
5. Only the resulting fresh lines reach the sole local `ResolveFlexibleLengths` call.

The proof boundary should be the fresh-layout producer path, not the `FlexLine` class invariant. A proof of arbitrary append lists alone would miss the pending transfer and the intentionally different continuation constructor.

## Positional reports and native/model schedule

`CreateFlexLineAndFlexItemInfo` appends exactly one report line per layout line and one report slot per item. A missing content node does not omit its slot. `DoFlexLayout` constructs these arrays before its indexed resolver walk; collapse restart clears stale report lines before reconstruction. The resolver initializes every slot, including frozen items, and uses the original reverse item index after decrementing it before the frozen skip. No record insertion/removal occurs in the resolver. These facts provide a concrete source route to `ReportsValid`, rather than assuming an arbitrary report array is long enough. Ownership, allocation success, re-entrancy and compiled memory access remain unproved.

Current source matches the accepted schedule: reset active bases; forward weight/share preparation; optional factor adjustment; reverse active correction and report updates; forward clamp contributions; sign selection and survivor flag clearing. Frozen weight/share fields can be arbitrary because both preparation and reverse consumption skip them. The active-count early stop needs the entry invariant and accepted monotone count/history proof. Root's separate stored-prefix work is the appropriate implementation of that next arithmetic producer layer.

`origAvailableFreeSpace` is captured on the first nonzero pass before factor adjustment. `entryFree` versus adjusted `free`, finite/native floating operations, and the relationship between original and per-pass free space are still external to the accepted caller model. No later-zero interpretation is resolved here.

## Acquisition findings and exclusions

`GenerateFlexItemForChild` obtains min/max from `ReflowInput` and asserts their order. The constructor then uses `SetFlexBaseSizeAndMainSize`; auto-min resolution may update the min/current before line accounting. These are concrete acquisition providers, not proofs that all CSS inputs satisfy `SeedsValid`. Content-measured bases can exceed the preferred half-range; do not restore a base<=preferred-limit premise. Nonnegative active shrinking bases should be derived through early-freeze/history, as the accepted helper does, rather than imposed on frozen entries or all acquired bases.

The existing individual MBP/OuterMainSize overflow warning, narrow `SumOfGaps`, full main-positioning cancellation, and original-free/later-zero ambiguity are known separate work. This audit does not count them as new findings. Finite-weight evidence does not by itself cover all nonfinite CSS/computed factors. No reachable NaN/infinity defect was established, and no speculative failure is promoted to a browser bug.

## Recommended next target

First run the small diagnostic candidate under a separately coordinated chrome test. In parallel or if it is not reproduced, prepare an isolated source-shaped producer target with a committed line prefix and at most one unaccounted appended record. Prove commit and optional transfer preserve flattened item identity/order and restore exact frozen count, with a count increment only at final commit. Include ordinary, initially frozen, strut, oversized/wrapped, and collapse-restart cases. Explicitly model continuation cloning as a separate result that is not admitted to the resolver. For the report layer, derive equal lengths and index correspondence by the actual nested append traversal; preserve nullable nodes and optional reporting.

This target supplies the missing native-entry realization for the already accepted `initialLine` append fold, without duplicating root's stored-prefix provider or claiming scalar acquisition, C++ object semantics, ABI or whole native execution. A future browser/DevTools probe would combine wrapping, collapsed struts, optional computed-info capture and fragmentation; no such probe was run here. Root review should precede implementation.

## Evidence method and limits

Read layout instructions, LayoutOverview and reviewer checklist; used specmap and webspec-index instructions. Searchfox discovery is pinned to revision `33abb900fc1646fef2e5ffed2d6b22e806ae10c1`; its definition and references are retained. Local changed source is the authority for the pending patches. The source excerpts are convenient views of the fully pinned file, not independent parser output.

`webspec-index` failed with a read-only cache error and announced an update; neither tool nor cache was modified. Primary [Flexbox §9.7](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths) was consulted directly: free-space calculation precedes distribution, clamping then supplies the sign-based freeze selection. This source audit does not close the explicit reset/later-zero interpretation boundary. The initial sandbox Searchfox DNS refusal and subsequent successful escalated public read are preserved.

`check.py` authenticates source and accepted proof inventory and checks the exact version delta. PASS means those byte checks succeeded, not that a native refinement theorem or new browser test passed. No new Lean/Coq proof, browser execution or native compilation was performed.
