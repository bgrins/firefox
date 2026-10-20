# View-transition type mutation misses ordinary style invalidation

Status: reproduced correctness defect on the existing shared development binary. No native repair, standalone prerequisite verdict, release-browser result, or formal verification is claimed here.

## Result

The calibrated `v2` loopback probe has **six discrepancies and twelve passing controls**. All eighteen pre-mutation baselines and forced-refresh calibrations pass. Source, generated binding, probe, runner and binary hashes remain unchanged across execution. The browser reports Firefox 160.0 and a visible document. The isolated profile changes no CSS or view-transition preferences.

| Operation on the active transition | Direct membership | Computed root color / descendant width |
|---|---|---|
| Add `alpha` | Correctly becomes true | Remains base color / 17px instead of green / 43px |
| Delete `alpha` | Correctly becomes false | Remains green / 43px instead of base color / 17px |
| Clear nonempty types | Correctly becomes false | Remains green / 43px instead of base color / 17px |

Each discrepancy occurs synchronously after startup and after `ready`. The public type set and active-transition identity are correct. Calls to `getComputedStyle()` do not repair the stale values. Disabling the test stylesheet, flushing, then enabling it recomputes the expected result. Thus this observes computed-style invalidation, separately from the previously repaired initial-duplicate membership disagreement. No initial sequence contains duplicates.

Passing controls: existing-member Add, absent-member Delete, and empty Clear in both phases; three mutations on a completed transition without an active transition; and three mutations on that old transition while a new `beta` transition owns the document. The last three retain the new transition's blue / 61px style and membership. Non-root `matches()` is false throughout. These controls do not prove arbitrary root replacement, adoption, scoped transitions, or cross-document lifecycle behavior.

The first run is preserved as `runtime-v1`. Its attempted calibration inserted a rule affecting only the root and did not reliably refresh descendant selectors, contaminating later baselines. It is diagnostic evidence only. Use `v2/runtime-v1/RUN.json` and `raw.json` for the calibrated result count.

## Independent normative oracle

The current View Transitions 2 draft defines the type set as mutable and selects the document root by its document's **currently active** transition and current type membership. The ordinary `alpha` and `beta` identifiers avoid reserved-name questions. Mutating an already completed transition cannot change the current transition's membership. These requirements imply the stylesheet predicates used by the probe. [Type set](https://drafts.csswg.org/css-view-transitions-2/#viewtransitiontypeset), [type selector](https://drafts.csswg.org/css-view-transitions-2/#the-active-view-transition-type-pseudo).

CSSOM obtains current resolved property values for connected rendered elements; cached results are not an alternative allowed result. The fixture uses fixed color and width declarations, no transitions on these properties, and no font, percentage, interpolation, or image-loading dependency. [getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle), [resolved values](https://drafts.csswg.org/cssom/#resolved-values).

The View Transitions ED dated 31 August 2026 was verified through primary-source browsing during this audit. `spec/css-view-transitions-2.html` and `FETCH.json` preserve the earlier independent review's exact primary acquisition, rather than claiming a fresh byte download. Current CSSOM ED dated 13 October 2026 was also read through primary browsing. A fresh curl acquisition was rejected by automatic approval review's interpretation of the network restriction; it was not retried. Root subsequently clarified that primary research reads are authorized, while behavioral requests must stay on loopback. No test request uses an external collector.

## Actual source chain

1. Generated `ViewTransitionBinding.cpp` invokes `ViewTransitionTypeSet::Add/Delete/Clear`. Successful Add updates the generated backing set and appends an atom. Successful Delete removes the native member. Clear empties both representations. These complete methods have no style notification. `GetTypeList()` is a direct reference accessor without a hidden notification.
2. `Document::StartViewTransition` installs `mActiveViewTransition` and adds `ACTIVE_VIEW_TRANSITION` to the root. `ViewTransition::ClearActiveTransition` removes that state at transition completion. Neither state changes when only the active type list changes.
3. Gecko's `NonTSPseudoClass::ActiveViewTransitionType` requires that state flag and calls `Gecko_HasActiveViewTransitionTypes` on the element's owner document. The bridge reads `GetActiveViewTransition()->GetTypeList()` each time. This explains why fresh `matches()` is correct while already computed style is stale.
4. `selector_parser.rs::state_flag()` maps this pseudo-class to `ACTIVE_VIEW_TRANSITION`. Ordinary state notifications travel through `Document::ElementStateChanged`, `PresShell::ElementStateChanged`, and `RestyleManager::ElementStateChanged`. The latter uses a previous-state snapshot synthesized from current flags XOR changed bits. It has no old type-list snapshot.
5. `ViewTransition::UpdatePseudoElementStyles` separately updates generated group rules and may post a recascade hint for a transition pseudo-element when geometry-related declarations change. That path does not establish ordinary root/descendant invalidation after a type mutation.

`SOURCE-PINS.json` identifies the ten source/generated inputs pinned before and after both runs. `SUPPLEMENTAL-SOURCES.json` records additional exact bridge, restyle, preference and existing-test snapshots read afterward; those files were not part of runtime pins. Source hashes identify inspected inputs, not a reproducible source-to-binary proof. Searchfox discovery preceded the directed local reads.

## Narrow repair recommendation

After a successful mutation that changes the native type list, notify a helper owned by the transition. The helper must check that its document's current active transition is this object and that the relevant root exists. Invalidate selector matching for the active root and its affected subtree, including descendants and transition pseudo-elements. Do not alter the active state bit or the active transition object merely to force a restyle.

An ordinary state-change notification with the unchanged bit is not automatically sufficient: it synthesizes an old inactive state. For Delete, both the fabricated old-state predicate and current now-absent type predicate could be false, even though cached styles came from an earlier true predicate. A dedicated invalidation or explicit subtree restyle avoids depending on a missing old-type snapshot. This is a source-derived caution, not a tested repair comparison. `Document::ElementStateChanged` also requires script blocking; `Element::NotifyStateChange` is not a public mutation API.

Add-existing and Delete-absent already return early; preserve those paths and failed-helper behavior. Empty Clear can avoid redundant notification. Completed-old transitions must not restyle or otherwise mutate the new active transition's ownership. Root's candidate should be independently tested with the existing ownership controls and pseudo-element regressions. No global equality or initial-set changes are needed for this lead.

## Tests, known issues and next obligation

The existing early-mutation reftest can set types before its first useful style computation. The late-mutation reftest targets generated transition pseudo-elements. The mutable-set WPT checks set behavior. None of these is evidence that a warmed ordinary root/descendant style updates on all three mutations. Searchfox found no per-file late-mutation expectation; absence is not asserted to mean a passing run. A bounded public issue search found no authoritative matching report; novelty is not claimed.

`proposed-wpt.html` contains eighteen proposed testharness cases: Add/Delete/Clear and their no-op controls, each synchronous and after `ready`, with public membership, direct matching and root/descendant resolved values, plus six completed/old-during-new ownership controls. It creates a fresh stylesheet and target per case to avoid cross-test stale baselines. This exact WPT has **not** been executed; the calibrated standalone probe supplies the runtime evidence.

A meaningful later formal join would connect successful ordered-set mutation and active-owner identity to invalidation scheduling, then to a delivered selector recomputation under an explicit flush contract. Existing set/selector membership proofs alone cannot establish this cache coherence. Snapshot completeness and descendant/pseudo selector dependencies must be modeled, not supplied as an assumed fresh final style.

Both owned browser processes terminated. Their profiles were removed after retaining user.js, browser logs, raw results and before/after pins. No native files, live WPT files, Git state or build products were changed.
