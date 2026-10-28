# Grid shorthand random cache index

Scenario: a supported grid shorthand contains one or two random length tracks before `/ auto-flow`; each reference substitutes explicit UA cache names in the same shorthand and otherwise preserves the entire value.

1. CSS Grid2 [grid shorthand](https://drafts.csswg.org/css-grid-2/#grid-shorthand) admits template rows followed by `/`, auto-flow and optional auto-column tracks. Thus failure of an implementation's tentative grid-template branch does not invalidate this grammar alternative.
2. CSS Values5 [random-key simplification](https://drafts.csswg.org/css-values-5/#random-simplify) and [random caching](https://drafts.csswg.org/css-values-5/#random-caching) assign property-index-scoped keys using the property name and random-function index in the property value, before shorthand expansion. The name is grid, not grid-template-rows. Failed implementation attempts are not additional functions in that value.
3. The explicit ua-grid-1 reference therefore names the first function's cache. Multiple functions use1,2 in parsed-value order. Same-key and same-range computation must agree; no inequality between distinct keys is required.

Verdict: REACHED — successful accepted shorthand functions retain their declared one-based cache indices; source predicts leaked implementation-attempt indices. Browser confirmation remains pending.

Fresh primary sections read2026-10-28 through web tools (Grid2 shorthand grammar and Values5 pre-shorthand-expansion clause). This is a prose grammar/default-key trace, not a parser or native-equivalence proof.
