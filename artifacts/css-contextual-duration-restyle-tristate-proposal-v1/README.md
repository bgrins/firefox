# Isolated tri-state compositor proposal

This uncompiled, unexecuted two-file proposal changes only dom/animation/EffectCompositor.cpp and EffectCompositor.h. Exact restored bases are CPP6ec3a0ca and header5ee05443. It contains no diagnostic logger, matching.rs change, fixture edit or execution authority. A later duration experiment would combine it with matching.rs c3b2ddf2 under a separately reviewed reversible owner. No native file was modified.

Replace the map boolean with byte-sized Throttled, Pending and DispatchAttempted. Pending preserves non-throttled PreTraverse eligibility without claiming a PresShell call occurred. DispatchAttempted means only that the call is about to be made, not that a root was queued or composition completed.

| Operation | Behavior |
| --- | --- |
| Throttled request | Insert Throttled if absent; preserve existing state and request the existing throttled flush. |
| Non-throttled request on Throttled | Upgrade to Pending and try the existing posting path. |
| Non-throttled request on Pending | Retry only outside Servo traversal, PreTraverse and style refresh; otherwise preserve inside-traversal coalescing. |
| Non-throttled request on DispatchAttempted | Coalesce. |
| Forced-throttled posting | Select only Throttled; upgrade to Pending before posting. Skip Pending and DispatchAttempted, just as old true entries were skipped. |
| PostRestyleForAnimation | After target/context early returns and all three guards, mark an existing entry DispatchAttempted immediately before calling PresShell. |
| PreTraverse | Pending and DispatchAttempted are non-throttled eligible; Throttled remains eligible whenever the existing flush-throttled condition is true. |

The extra IsInStyleRefresh guard matters: outside Servo/PreTraverse does not imply outside style refresh. It replaces a debug-only assertion with a deferral that leaves Pending. RequestRestyle's borrowed value and PostRestyleForAnimation's lookup handle end before the PresShell call. Forced-throttled posting no longer stores/writes a value reference after posting; its existing iterator/call assumption remains. Lookup does not insert a missing entry for a direct post call. Existing Layer generation updates are unchanged.

Complete consumer inventory: cycle-collection unlink clears maps; cycle-collection traversal follows keys; RequestRestyle inserts/upgrades; PostRestyleForThrottledAnimations selects throttled entries; HasPendingStyleUpdates checks count; PreTraverse's first pass collects cascade updates and second pass posts hints/prepares effects/removes entries. Its wrong-document, missing-effect and consumed-entry removals and full-document/flush-throttled clear are unchanged. Disconnect only clears the pres-context pointer; no value-type-dependent behavior is introduced there.

The indexed direct PostRestyleForAnimation callers are only RequestRestyle and PostRestyleForThrottledAnimations. PresShell is the sole indexed forced-throttled caller and invokes it for flushAnimations immediately before ProcessPendingRestyles. HasPendingStyleUpdates callers in RestyleManager and nsComputedDOMStyle remain presence checks. CONSUMER-QUERIES.json preserves exact query output. In particular, selecting all unattempted entries in forced-throttled posting would wrongly broaden behavior: it would newly wake deferred non-throttled self-feedback on forced animation flushes/reads. This proposal preserves Throttled-only selection.

Narrow branch diff751af5 established local changes in ServoStyleSet/RestyleManager/PresShell, allowing exact local reads. Six complete scheduling bodies equal full upstream captures (a3e3ca); the forced-flush call context also matches. EffectCompositor.h is unchanged versus origin/main. Scoped git diff -G over dom/animation, layout/style and PresShell found no added/removed queue-field or posting-method occurrences (a25b06). APPLICABILITY.json pins these findings; this is not a global whole-tree proof.

The observed instrumented candidate failed both fixed2000ms override controls and had13 bounded intervals from6 seeds; original had0. This supports investigating the queue state, not a completed causal proof. The logger lacks IsInStyleRefresh and synchronized JS phase markers. The dispatch-attempt Lean model supports abstract pending/attempted separation and three blockers; it does not prove native refinement, forced-throttled behavior, root delivery, composition or reentrancy.

Static904f6a/0 passed exact two-file patch application in owned scratch, base hashes, CPP changes confined to four functions, preserved removal/clear sites and forced-throttled selection. Scratch removed. No Gecko compile/browser execution occurred. Before acceptance, independently review and compile, then measure fixed script/literal controls, seek changes, ordinary/unchanged timings, forced-throttled flushes, restyle counts, inactive reactivation and updateTiming ownership/rejection. No drain loop, exit hook, new frame callback or arbitrary cycle cap is added; no autonomous progress, convergence, new bug ID or acceptance increment is claimed.
