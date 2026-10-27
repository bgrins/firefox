# MathML hidden-return contract and candidate review

**Recommend a controlled experiment with proposal v2's single MarkSubtreeDirty call at the existing hidden-parent return. No source-level blocker found for that experiment; the native candidate remains untested and unaccepted.** Use its four internal-mrow cases for the standalone landing test. This review did not author the fixture, run a browser/build, or modify production/index state.

## Actual trace join

Independent parsing of the pinned raw JSON reproduces all 2,210 native events, 256 phase records, eight copied results, six PASS/two FAIL, and one OK harness end. TRACE-JOIN.json retains the selected events and exact raw indices. Joins use process, case, document phase, primary-frame identity, row/leaf/owner pointers, and event order. Addresses are reused between cases; no cross-case lifetime identity is inferred.

| Case | Before / after input | Hidden return | Row publish-after | First / repeated clean reject |
|---|---|---|---|---|
| c1, row-first | 641 / 642 | 644 | 652 | 702 / 705 |
| c3, leaf-first | 1354 / 1355 | 1357 | 1365 | 1415 / 1418 |

In both histories, row DIRTY/HAS_DIRTY_CHILDREN/IsSubtreeDirty and its sole mspace child's dirty/subtree flags are zero before input construction, after construction, at the hidden return, and through publication/DidReflow. The row's hidden-parent predicate is true and no forced layout is active. Thus input construction does **not** create an already-dirty-root barrier in these two histories.

The row returns without layout, zero size/ascent is cached, and its local rectangle changes from `[3600,0,2400,960]` to `[3600,0,0,0]` in native app units. The matching hidden DidReflow branch leaves the still-clean flags unchanged. The selected primary row in c1 and selected primary leaf in c3 are then rejected as clean on both first and repeated queries. Copied CSS rectangles are respectively `[70,25,0,0]` and `[70,25,40,16]`, versus visible `[30,10,40,16]`. The leaf retains its own size while inheriting incorrect placement. This localizes the observed admission failure; it does not prove a repair works.

## Placement and remaining contract

Marking the skipped row at this return is the smallest source-shaped change supported by the trace. The helper marks the clean root and ordinary descendants, so it can make both queried frames eligible. It traverses owned child lists and sets bits without reflowing or relinking frames. No new flush, frame destruction, or retained pointer is introduced. The existing hidden-parent branch of DidReflow preserves dirty bits; the same predicate's forced-layout exemption should allow a later admitted query to execute normal MathML reflow.

Owner-side child marking before ReflowInput construction is justified only if another demonstrated history turns a clean row dirty during input setup while leaving its leaf clean. That did not happen here. Marking the owner itself is not a substitute: an already-dirty owner can prune. A row already dirty before input would defeat both placements using the same helper. Do not remove global pruning or broaden traversal without a separate history and review.

The one-line change still leaves the skipped callback's output unfilled, and its caller can cache/publish interim metrics. It repairs query eligibility, not the validity of those interim metrics. The candidate must demonstrate actual provider completion and correct root-first, leaf-first, repeated, and shown/restored geometry in an uninstrumented run. Already-dirty and table-column barriers, specialized MathML overrides, continuations, lifetime correspondence, and query/provider identity remain broader limits. Generic child reflow's existing complete-status continuation deletion is unchanged and not verified here.

## Independent landing partition

Checked proposal v2 manifest `88f80c45dbcc0e3828d42be9958a277661fdb315988e795bafdfbaaf17919918`. Native bytes add only the proposed helper call. The final WPT removes unused global recording and selects exactly the four internal-mrow cases; fixture code, geometry reads, and assertions are unchanged.

The four original root-block cases remain research/integration controls. nsBlockFrame can skip their children before the MathML return runs, so their observed success with accepted block handling does not establish standalone independence. Their outcome without that repair is **unmeasured**, not a claimed failure. Keeping them outside this fix's landing WPT avoids assuming that separate repair. The planned HEAD-only comparison predicts two visible passes/two hidden failures becoming four passes; those are expectations, not results.

Runtime v3 was restoring when this task arrived. This artifact authenticates the named raw trace and proposal only; it makes no restoration or later-live-state claim. A separate uninstrumented candidate comparison and independent results review remain required before native acceptance.
