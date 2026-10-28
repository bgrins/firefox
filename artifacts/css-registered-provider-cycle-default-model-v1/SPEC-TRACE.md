Question: can a recursive fallback or early registered initial erase an actual property cycle?

Scenario: valid non-universal registrations with `inherits: false`, admitted independent initials, self/mutual `var()` references, and an outside consumer. No contextual units in the cyclic bodies. Numbers 3/7 encode distinct admitted values; the plain mutual example also models distinct writing-mode keywords.

1. [Variables 1, replace a var() function, steps 2 and 4](https://drafts.csswg.org/css-variables-1/): request the referenced computed value; use the second argument only for a guaranteed-invalid result.
2. [Values 5, Substitution, guard definition and steps 1/3](https://drafts.csswg.org/css-values-5/): reentry marks the participating contexts. The post-substitution check returns invalid even if an inner replacement produced tokens. Its decisive condition is “If context is marked as a cyclic substitution context”.
3. [Values 5, Invalid Substitution](https://drafts.csswg.org/css-values-5/): a non-universal registration defaults according to inheritance; our noninheriting scenario selects its own initial. A context outside the marked cycle is not invalidated merely for consuming that computed value.
4. [Properties and Values API 1, sections 2.4 and 2.7](https://drafts.css-houdini.org/css-properties-values-api-1/): apply registered grammar admission at computed-value time and substitute the resulting computed value. A rejected provider therefore supplies its default to an outside consumer, rather than retrying that consumer's var fallback.

Verdict: REACHED for these scenarios. Preserve participant marking through substitution and default publication. Missing-provider fallback, grammar rejection and cycle invalidation are different transitions.

Rejected routes: an inner fallback erases the caller's mark (contradicts final guard check); every dependent is a participant (confuses entry prefix with cycle segment); pending work is guaranteed-invalid (no normative basis); all registrations use initial (universal/inherited registrations are excluded here).

Primary documents were read online 2026-10-27 with the spec-trace/webspec-index workflow's manual-primary fallback: Variables ED 2026-10-09, Values 5 ED 2026-10-27, Properties API ED 2026-08-06. The CLI is unavailable in this session; this is an explicit hand trace, not an exhaustive indexed route enumeration. No old static graph rule that eagerly traverses every unused fallback is assumed.
