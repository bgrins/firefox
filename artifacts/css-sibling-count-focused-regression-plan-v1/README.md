# Focused sibling-count regression coverage proposal

This is a later-validation proposal only. The current ordinary-property baseline
remains exactly six callbacks: two target cases and four strict controls. No
fixture or active execution policy is changed by this inventory.

| Proposed coverage | Existing test |
|---|---|
| Basic arithmetic, root and pseudo-elements | tree-counting/calc-sibling-function.html |
| Light DOM, slots, shadow children and shadow root | tree-counting/calc-sibling-function-in-shadow-dom.html |
| Tree scope, current outer-part fallback of one, host counts | tree-counting/tree-scoped-sibling-function.html |
| Removal invalidation for elements and before/after/first-letter/first-line | tree-counting/sibling-function-invalidation.html |
| Optional container size/style query invalidation | tree-counting/sibling-function-container-query-invalidation.html |
| Accepted 141 preservation | css-inline/line-height-tree-counting.html and css-values/line-height-contextual-number.tentative.html |

The first five files were inspected through Searchfox; SOURCE-COVERAGE.json also
pins all seven exact current signed HEAD bodies without copying them. Tree-
counting paths are relative to testing/web-platform/tests/css/css-values.
The accepted line-height paths are known local accepted changes. The current
outer ::part expectation is one; the rejected historical zero proposal must not
be substituted. The parsing-only page exists but is lower priority for this
one-line computation-cache change.

Before any expanded pair, capture the selected HEAD bodies and metadata, generate
a genuine WPT manifest and exact callback roster, and run a fresh original
comparison for that same expansion. Preserve complete original/candidate
signatures, including existing expected failures; do not assume an all-green
baseline or import historical statuses. Existing metadata feature preferences
must remain explicit. No browser/native execution, callback enumeration, new
acceptance or coverage credit is claimed here.
