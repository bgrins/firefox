# Independent root review of attribute cycle semantics

The root re-read the current CSS Values 5 Editor’s Draft (27 October 2026), including attribute replacement, generic substitution and context guards, independently of the audit author. This is a manual positive algorithm trace; no exhaustive indexed route claim.

## Raw nested reads

Scenario: --x: attr(data-foo type(*), abc), with data-foo containing attr(data-foo), no namespace or dynamic-name complication.

1. Property replacement guards --x and substitutes its value.
2. Outer attribute replacement finds data-foo, reaches the typed case, and invokes generic substitution of its attribute value with the data-foo attribute context.
3. That substitution sees the inner bare attr(data-foo). Attribute replacement finds the same DOM attribute and returns its literal text as one CSS string at step 5. It does not reach the typed substitution in step 6, so no second data-foo context is pushed.
4. The outer typed substitution receives a string token. Fully resolved replacement tokens are not reparsed as a second CSS expression. Parsing with the universal syntax accepts the string. Neither active context became cyclic. The expected serialization is a quoted string containing attr(data-foo).

Verdict: REACHED for the literal-string result in this scenario. The generic explanatory prose mentioning attr(foo) contexts is broader than this specific raw-return branch; it does not add a recursive call before the explicit return. The old WPT expectation is implementation-history evidence, not an override of the algorithm. Existing test changes still require candidate regression evidence and a clear explanation of this oracle correction.

## Used bare/unit fallback cycles

Scenario: --x: attr(data-missing, var(--x, red)); color:var(--x,green), with data-missing absent. Property substitution guards --x. Attribute replacement fails the presence check, reaches FAILURE, and substitutes its fallback. The var(--x) primary repeats the property context, marking that context cyclic. The var fallback cannot rescue the active property: generic substitution rechecks the cycle marker after nested replacement. --x becomes guaranteed-invalid, so the independent color declaration uses green. A present raw attribute returns a string without examining its unused fallback.

Verdict: REACHED for invalid --x / green in this scenario. The same missing-primary argument applies to a failed primitive numeric/unit parse; these cases need their own browser controls.

Sources checked live through the web tool: https://drafts.csswg.org/css-values-5/#attr-substitution ; https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function ; https://drafts.csswg.org/css-values-5/#guarded ; https://drafts.csswg.org/css-values-5/#property-replacement . The audit’s captured source and anchor inventory remain the byte-pinned evidence; this review adds independent judgment, not another source snapshot.

No native proof, browser result, new accepted fix or security impact is claimed by this review.
