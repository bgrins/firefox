# Focused landing validation input plan

Disabled input plan: seven pages, 36 callbacks, two landing targets and 34 strict controls. No browser, build, source overlay, index change or canonical publication is implemented or performed here. The six-case source-cause comparison stays unchanged.

| Page | Callbacks | Role |
|---|---:|---|
| sibling-count-cross-parent-invalidation.html | 2 | Exact landing-v2 width/opacity targets |
| calc-sibling-function.html | 7 | Basic arithmetic, root and pseudo-elements |
| calc-sibling-function-in-shadow-dom.html | 3 | Light tree, slots and shadow children |
| tree-scoped-sibling-function.html | 2 | Resolved outer-part fallback one and normal host counts |
| sibling-function-invalidation.html | 12 | Removal invalidation including four pseudo-elements |
| sibling-function-container-query-invalidation.html | 8 | Size/style query changes after removal |
| css-inline/line-height-tree-counting.html | 2 | Accepted141 contextual integer/inherited line-height preservation |

The five existing css-values pages and accepted141 tree-counting control were captured exactly from signed HEAD19b09cce1a9b03ab19c46addc6fa46242f1544f9 using the previously inspected coverage inventory. The new landing HTML is referenced from its immutable path-only successor. Standard harness resources reuse authenticated existing captures. All applicable metadata parents and per-page records, including explicit absence, are pinned. Tree-counting and typed arithmetic/style-query preferences are present in inherited metadata. The existing nested-pseudo-element subtest has expected: FAIL; no all-green baseline is assumed. The rejected historical outer-part zero hypothesis is not used.

Both phases must run this same full roster. The original must complete every callback and seven test endings without infrastructure/setup errors; the two targets remain observations and should demonstrate the reported defect. The candidate must pass both landing targets and preserve all34 control signatures and seven endings exactly (status, message, expected/intermittent fields and their presence). Historical six-case results cannot substitute for this fresh original. Any changed control needs explicit adjudication, not silent narrowing. The compiled source and actual application metadata must be bound by the root-owned runner; this package intentionally has no execution authority or build binding.

Preparation 03225d→5a6446/0 used the real WPT manifest parser/roundtrip, private-root scoped WPT lint, HTML parsing and inert Node callback registration. Callback bodies were not executed. The two setup-only outer operations in existing pages (shadow attachment and removal) are stubbed solely for enumeration; no browser semantics are inferred. Private scratch was removed. CHECK.json and ROSTER.json record all36 names.

Independent bounded input-plan review: typed_demand_review 9c9aa6/0 clear. This review covered roster/scope, preserved expected failure and fresh/full comparison requirements; it did not execute callbacks or independently authenticate captures. Saved resource/reference authentication ea1230/0 verified11 resources and12 metadata/absence records.
