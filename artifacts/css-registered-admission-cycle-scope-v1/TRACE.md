# Selected references and simplified numeric trees

Question: does eager simplification alone authorize removing a selected relative-unit dependency from a registered property's cycle graph?

Scenario: a registered property with syntax `<length> | <number>` receives `sign(1em)`, directly or through an unregistered provider, and supplies `font-size`. This is separate from a relative unit occurring only in an unused fallback or a value rejected by the registration grammar.

1. [Properties and Values API, computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) applies the registration grammar. Numeric functions use their function-defined computation rules.
2. [Relative-unit dependency cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) adds dependencies for registrations containing a length or length-percentage component and the specified relative units. The mixed descriptor meets that descriptor condition. The text does not explicitly order its containment test against numeric simplification.
3. [Values 4, simplification](https://drafts.csswg.org/css-values-4/#calc-simplification) permits eager numeric simplification when enough information is available. It also explicitly preserves zero-valued terms in sums when their units differ. Neither fact by itself proves which representation the registered-property graph must inspect.

Verdict: **INCONCLUSIVE**. The inspected sections do not establish that a dependency absent from the simplified AST may be removed from the cycle graph. This is a manual trace, not an exhaustive indexed route search: `webspec-index` is unavailable in this environment. The exact HTML captures, response metadata and validated anchor inventory are retained in this directory. No conformance oracle is assigned to the self-font sign scenario.

The implementation review independently identified `sign(1em)` as a concrete simplification path that can hide a selected unit from the proposed collector. This is a candidate-review finding, not a newly accepted Firefox bug. The revised admission repair will obtain flags from the selected substituted tokens after actual grammar admission. It will retain the existing scheduling prefilter and intersect those selected flags with the accumulated graph mask. This preserves the intended fallback/admission repair while leaving numeric scheduling and graph-policy research active separately.

The isolated collector proof starts with an already retained AST; it does not justify this representation change. The fixed-graph projection proof likewise proves only edge nonexpansion, not preservation of every required dependency or equivalence of dynamic graph construction. Paired browser observations remain required.
