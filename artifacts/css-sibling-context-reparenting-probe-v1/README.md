# Reparenting sibling-dependent ordinary values

Unexecuted follow-up diagnostic, separate from the active 36-case landing comparison. Run after the sibling-count cache repair if the goal is to distinguish an independent invalidation defect from the already identified reset-cache omission. No new defect or acceptance is claimed.

Six callbacks cover width, opacity and inherited font-weight, each with sibling-count and sibling-index. One already-styled target moves by `right.append(target)` and then returns by `left.append(target)`. Stationary targets remain in both parents. No declarations are replaced and no unrelated style is changed during those phases. The same target objects are retained throughout. The initial snapshot forces ordinary computation before the move.

| Role order: left stationary / moved / right stationary | Initial | Moved | Restored |
| --- | --- | --- | --- |
| Parent | left / left / right | left / right / right | left / left / right |
| Count | 2 / 2 / 2 | 1 / 3 / 3 | 2 / 2 / 2 |
| Index | 1 / 2 / 1 | 1 / 3 / 1 | 1 / 2 / 1 |

The stationary index controls stay unchanged while their counts change. Reset width/opacity and inherited font-weight provide a separate cache-class contrast. Expected values are count/index times10px, divided by10, or times100 respectively; independent precreated literals cover inputs1–3. Width includes geometry. All parent computed properties must remain equal; empty block children keep used heights zero. The observer retains topology, parent identity, support, declaration serialization, stable repeated reads, literal admission and values, and absence of active animations.

A visible 400×200 iframe avoids the earlier offscreen scheduling setup. The outer document has an explicit body before callbacks. A single lazy promise collects all six cases, eighteen snapshots and54 target records before any callback asserts. Every callback failure includes its entire case JSON. The iframe is removed in finally. The wrapper stores observations on the window and in a hidden pre; ordinary WPT raw logs retain six callback results, not a separately exported54-record corpus. A runner can optionally call the saved observer directly to retain the full JSON.

The same-tree oracle follows [CSS Values5 tree counting](https://drafts.csswg.org/css-values-5/#tree-counting): element children in the DOM parent determine count and index. No shadow fallback, nested pseudo, contextual easing, Round, random or custom-property syntax appears here. The rejected draft-zero hypothesis is irrelevant to this page.

Fresh Searchfox discovery found RestyleManager under `layout/style`, not its older `layout/base` path. `ContentWillBeRemoved` clears the removed element's subtree Servo data; it also posts tree-counting recascades on flagged remaining container children. `ContentInserted` forwards to insertion/change handling, and append and insertion paths also invoke the tree-counting recascade routine. That routine checks element/pseudo usage and posts RECASCADE_SELF. These are positive source routes, not evidence that a missing route exists. The probe tests their composition with parent changes and fresh style computation; it does not prove which cache path ran. `SOURCE-TRACE.json` records exact excerpts plus the fetched full-source hash; the CLI did not provide a revision identifier.

Preparation `313aca/0` passed real WPT manifest generation, scoped lint, explicit-body HTML parsing and inert registration of all six names. Callbacks did not execute, and no source overlay, browser, build, index or epoch operation occurred. `OBSERVER-DELTA.patch` records the bounded change from the earlier six-case cross-parent observer. Existing standard resources and metadata are referenced by hash rather than copied. Source discovery receipts: f092a6/e8fa40/0764a3/327d06.
