# Adjacent numeric reset-rule-cache audit

No additional omission was established in this bounded audit. The independently investigated sibling-count omission remains the concrete lead; this package does not claim another defect, family closure, browser reproduction, or new formal coverage. Sources are from immutable signed HEAD `182db9b1c69b7dc890498f7c6264da768cb3d956`, before the proposed sibling-count correction. Live source, app, index and epoch were not inspected or changed.

| Input | Reset-cache protection or retained input | Conclusion |
| --- | --- | --- |
| sibling-index | `query_sibling_index` marks uncacheable | Different from the known sibling-count omission. |
| element-scoped random | `random_base_value` marks uncacheable before hashing the element identity; sharing separately rejects element-scoped random | No matching omission found. Named non-element-scoped samples deliberately share a document/key base. |
| container units | `container_relative_to_computed_value` marks non-inherited computation uncacheable before querying size | Cross-container resolved reset values cannot enter this cache through this route. |
| em / lh | Current-style reset computation records font size / computed line height; `CachedConditions::matches` compares them | Explicit cache inputs, rather than unconditional exclusion. |
| ex / ch / cap / ic | `query_font_metrics` marks reset computation uncacheable and publishes font-metric flags | No matching omission found. |
| vi / vb | Records writing mode; physical viewport input comes from the device | No element-specific input omission demonstrated. |
| rem / root metrics / physical viewport | Document/device inputs; `traverse_dom` creates scoped thread-local contexts containing fresh `RuleCache` instances | This is not a persistent cross-traversal cache. This audit does not prove device/root update scheduling or every non-traversal caller. |
| anchor / anchor-size | Calc mapping retains anchor nodes and maps their side/fallback children; `resolve_anchor` clones and resolves against supplied layout parameters later | A missing immediate uncacheable flag alone does not show stale resolved geometry. Anchor target tree-scope binding and all layout invalidation paths were not proved here. |

These are distinct caches. The reset rule cache copies reset structs and dependency flags after a rule-node/condition hit; the style-sharing cache has separate element eligibility checks; tree-counting caches key index by element and count by parent. A flag copied with stale reset values cannot itself repair the known sibling-count omission. Conversely, a sharing exclusion is not sufficient evidence that the reset cache is safe. Existing authenticated traces are referenced rather than copied.

Specified calc conversion maps contextual leaves through `Leaf::to_computed_value`. The special line-height mapper in this signed branch also delegates its remaining leaves to that operation and propagates failure: accepted fix 141 already changed this path. Searchfox still exposes an older mapper, so treating that upstream snapshot as the local implementation would duplicate an accepted defect. This audit does not reclassify pending contextual-easing representation or keyframe lifecycle work as a new cache bug.

`PROBES.json` proposes four small preservation diagnostics, not predicted failures or an executable roster. Each requires ordinary syntax admission, positive independent controls, full collection before assertions, and root-owned browser execution. There is no reason from this audit alone to delay validation of the one-line sibling-count repair or expand its landing WPT.

Discovery used Searchfox for unchanged paths (`random_base_value`, `resolve_anchor`, `RuleCache`, specified length conversion, scoped thread-local traversal). Exact branch evidence is in SOURCE.json. Relevant read receipts: cf995e, 02f8d2, 056f34, 60188c, 719c3b, 5682f2, 745362, a345d5, 2ed9ae, 234851. No claim of exhaustive grammar, custom-property provider readiness, anchor scoping, or invalidation verification is made.
