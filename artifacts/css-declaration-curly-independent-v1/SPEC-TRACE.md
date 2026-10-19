# Curly declaration fallback: normative trace

Question: may a noncustom declaration retain a top-level curly block alongside other values solely because it contains var(), env(), or attr()?

Scenario: a supported ordinary property, balanced tokens, no !important, and a syntactically valid substitution function. Examples use font-family and inspect parsing/serialization, not computed font selection.

1. CSSOM setProperty parses the supplied property value and returns without replacing the old declaration on failure. cssText parses a declaration block; stylesheet parsing consumes declarations within the rule. These entry paths must retain the same structural declaration restrictions. [CSSOM setProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty), [CSSOM cssText](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-csstext).
2. CSS Syntax consume-declaration first collects component values. Step 8 exempts custom properties, then rejects ordinary values containing a top-level curly simple block plus any other non-whitespace value: “return nothing.” Whole-value curly blocks and curly blocks nested within another component are different cases. [Consume a declaration](https://drafts.csswg.org/css-syntax-3/#consume-declaration).
3. Values 5 defers the property's value grammar when valid arbitrary substitution functions occur. That deferral does not undo the structural rejection in the declaration algorithm. The CSSWG resolution explicitly retained curly-block rejection despite var(). [Substitution](https://drafts.csswg.org/css-values-5/#arbitrary-substitution), [CSSWG issue 9317](https://github.com/w3c/csswg-drafts/issues/9317).
4. CSS.supports(property, value) returns true only when the property/value parses; the rejected ordinary declarations therefore return false. [CSS.supports](https://drafts.csswg.org/css-conditional-3/#dom-css-supports).

Verdict: REACHED — the six tested ordinary font-family values combining top-level curly blocks and other values must be rejected. Existing declarations remain visible through setProperty/cssText/stylesheet parsing, while CSS.supports returns false.

| Alternative | Why it does not change this result |
| --- | --- |
| Substitution makes all grammar acceptable | The separate declaration structural gate precedes contextual validity. |
| A lone curly block is also invalid | It passes this structural gate; the test contains a valid substitution function and checks parse-time retention only. |
| Square blocks should be rejected identically | The special gate names curly blocks. |
| Custom properties should be rejected | Step 8 explicitly takes the custom-property branch instead. |
| Undefined variable should reject at parse time | Missing values are resolved later; this test concerns syntactic acceptance. |

Primary web retrieval on 2026-10-19 read the current CSS Syntax draft dated 16 October 2026, Values 5, CSSOM, Conditional Rules 3, and issue 9317. The stated anchors were present in fetched sections. This is a manual current-primary-source trace: webspec-index is unavailable and Searchfox CLI discovery failed DNS. No exhaustive reference-graph claim or successful CLI lookup is made. Root forbids Mach work for this review, so no bootstrap was attempted.
