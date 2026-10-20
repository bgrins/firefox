# Active view-transition type invalidation: independent source review

## Verdict and narrow repair

Confirmed rendering invalidation defect, distinct from initial duplicate-type normalization. No initial type list in the calibrated fixture contains duplicates. Successful Add/Delete/Clear change selector membership but do not invalidate already computed root/descendant style. The retained diagnostic has 18 rows: six stale-style failures, twelve controls; all pre-mutation and stylesheet-refresh calibrations pass. The independent checker reconstructs expected memberships/styles rather than trusting the reported failure count. This review ran no browser or build.

Recommend a `ViewTransition::NotifyTypesChanged()` helper, called only after a successful native-list change. It should return unless `mDocument->GetActiveViewTransition() == this`, obtain `mDocument->GetRootElement()`, and, if present, call:

```cpp
nsLayoutUtils::PostRestyleEvent(root, RestyleHint::RestyleSubtree(),
                               nsChangeHint(0));
```

ViewTransition.cpp already uses nsLayoutUtils and restyle hints. Declare the helper where ViewTransitionTypeSet can call it. No state-bit toggling, new Document API, global matching change, or pseudo-tree rebuild is needed. This is an implementation recommendation; candidate source/build/runtime acceptance remains separate.

| Mutation branch | Notification decision |
|---|---|
| Add existing or Has failure | Existing early return; none |
| Add helper failure | Existing early return; none |
| Add success | Append native atom, then notify |
| Delete absent or helper failure | Existing false return; none |
| Delete success | Remove native atom, then notify |
| Clear helper failure | Existing early return; none |
| Clear success, native list empty | None; preserve public helper invocation/return semantics |
| Clear success, native list nonempty | Clear native list, then notify |
| Completed/old/replaced transition | Its set still mutates normally; helper identity guard suppresses document restyle |

For Clear, test native-list emptiness after the successful SetlikeHelpers::Clear and before clearing the native list. This preserves all original helper/failure behavior. Calling before a native update risks observing the old list; calling after failure invents a change. String argument conversion can execute author code before entering the native method, so use current owner identity at notification time, not a captured prior active transition.

## Normative trace: REACHED

The `types` getter returns the transition's active type set; ViewTransitionTypeSet is a mutable string set. The type pseudo-class matches the document root from the document's currently active transition and its current membership. The ordinary alpha/beta names avoid reserved-name ambiguity. Thus changing the active set changes matching; an old object's set is irrelevant to a new active transition. [View Transitions 2 type set](https://drafts.csswg.org/css-view-transitions-2/#viewtransitiontypeset), [types getter](https://drafts.csswg.org/css-view-transitions-2/#dom-viewtransition-types), [type selector](https://drafts.csswg.org/css-view-transitions-2/#the-active-view-transition-type-pseudo).

Web IDL defines Add's return object, Delete's membership Boolean, and Clear's undefined result while preserving the set object. The proposed helper leaves those semantics intact. [Add](https://webidl.spec.whatwg.org/#es-set-add), [Delete](https://webidl.spec.whatwg.org/#es-set-delete), [Clear](https://webidl.spec.whatwg.org/#es-set-clear).

CSSOM obtains resolved values from applicable document rules for connected rendered elements. The fixture's fixed colors and pixel widths have no interpolation/resource ambiguity. A cache retaining the old matching result is not an allowed alternate result. [getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle).

Primary sources were freshly fetched with HTTP 200 and hashed in spec/FETCH.json. Anchors are checked against those bytes. Current ED also contains scoped Element transitions; this recommendation covers this branch's document-root implementation, not unimplemented scoped-transition behavior. The webspec-index executable is unavailable; direct primary acquisition follows the prescribed fallback.

## Complete source chain and rejected API

Generated binding calls reach the complete retained ViewTransitionTypeSet Add/Delete/Clear methods. They update SetlikeHelpers and the native atom list with failure checks but no notification. Types() lazy initialization uses generated helpers directly; it does not call the public native Add and should not trigger notifications merely for exposing the set.

Document::StartViewTransition installs the active object and sets ACTIVE_VIEW_TRANSITION on the root. ClearActiveTransition removes the bit and clears ownership. Mutating types leaves the bit unchanged. Gecko wrapper matching requires this bit and Gecko_HasActiveViewTransitionTypes reads the active object's current native type list. GetTypeList is a reference accessor, without a hidden hook.

Do **not** simulate ElementStateChanged(ACTIVE_VIEW_TRANSITION): RestyleManager constructs previousState by XOR with current state, while the old match still reads the current type list. After Delete the synthetic old state is inactive and the new list lacks the type, so both predicates can be false despite previously true cached style. State setters also suppress notifications when the bit does not change. Element's direct notification methods are private. This is a source-derived counterargument, not an executed synthetic-state candidate.

Explicit RestyleSubtree means RESTYLE_SELF | RESTYLE_DESCENDANTS. The propagation method returns the same hint for children. PostRestyleEvent increments undisplayed-style generation, tracks non-animation work, and passes explicit hints to Servo. nsLayoutUtils posts only when a composed document and presentation context exist; no new synchronous style flush is introduced.

Gecko traversal_children selects StyleChildrenIterator when anonymous children exist. That iterator uses AllChildrenIterator, including ::before/::after and native-anonymous children. nsContentUtils::AppendNativeAnonymousChildren explicitly appends the active transition's snapshot containing block for the document root. SetupTransitionPseudoElements binds that wrapper to the root, with the transition pseudo tree beneath it. Thus the existing subtree mechanism supplies the intended propagation, rather than relying on geometry-driven UpdatePseudoElementStyles recascades. The separately authenticated pseudo baseline now reproduces stale root::before, child::before and group(root) opacity for all three successful mutations, with three passing no-op controls. All before/forced-refresh gates pass. Its group animation runs for 100s, while the retained BuildGroupKeyframes contains no opacity entry, supporting a deterministic opacity oracle. Candidate pseudo controls remain required; this source argument is not a full traversal proof.

## Source versions, limits, and remaining gates

Complete source snapshots are retained. Searchfox discovered the APIs; six additional indexed files are retained separately. Three differ from the local checkout outside the relevant methods; exact diffs are included. The source conclusions use local snapshots. Runtime source/binary pins cover the original diagnostic inputs, not every supplemental file; source-to-binary identity is not inferred from source hashes.

The proposed mutation fix does not depend on initial-duplicate normalization for these unique-set cases. It also does not repair that earlier representation defect on its own: if a native list contains duplicate entries, Delete may leave a stale member despite rematching. Preserve independent unique-input WPTs and separate packaging of the two fixes.

Before final native acceptance: compile the exact candidate; run the calibrated mutation/no-op/old-object WPT; add warmed root::before, descendant::before and ready-phase ::view-transition-group(root) checks with deterministic values and animations controlled. Filter agent owns those pseudo diagnostics. Check baseline/candidate source and binary pairing. OOM/helper failure is reviewed from branch structure, not fault-injected. Cross-document lifecycle, arbitrary root replacement and future scoped transitions are not established by these cases.

No production sources, WPTs, Git state, browser profiles or build outputs were changed by this review.
