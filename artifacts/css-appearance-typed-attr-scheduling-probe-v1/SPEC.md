# Portable typed-attribute expectations

Read 2026-10-30; versions and primary-read references are in PRIMARY.json. This is a manual algorithm trace. The spec-index query and anchor check failed with a readonly database error (ANCHOR-CHECK.log); no exhaustive graph search or successful machine anchor validation is claimed.

Scenario: a registered non-inherited `<length>` has initial `0px` and specified `1em`; the subject font-size is a literal 20px, then 30px. There is no font-size reference back to the registered value. The two controls avoid nested var substitution or omit the attribute.

1. [Properties and Values API computed-value rules](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) convert the registered dimension to canonical units. Its specified em uses the subject font size. This gives 20px then 30px, independently of appearance or font-family metrics.
2. [Values 5 attr replacement, step 6](https://drafts.csswg.org/css-values-5/#attr-substitution) substitutes functions in a present attribute, then parses the requested syntax. Its success branch says: “If that succeeds, return the result”. Thus a resolved length returns the length. Missing attributes take step 3’s failure branch and step 7 substitutes the authored fallback.
3. Values 5 Appendix A, property replacement step 3, parses the substituted result against the consuming property grammar. A failure is invalid at computed-value time, which defaults this non-inherited property to its initial value. It does not retry attr’s fallback after successful typed substitution.
4. [UI appearance](https://drafts.csswg.org/css-ui-4/#appearance-switching) has keyword grammar, initial `none`, and no inheritance. Therefore both present length cases yield `none`; the missing case returns valid `auto`.
5. For the separate family case, the present literal identifier parses as `<custom-ident>`, then [Fonts 4 font-family](https://drafts.csswg.org/css-fonts-4/#font-family-prop) accepts `monospace` as a generic family. Its computed keyword remains monospace; the serif fallback is unused.

**Verdict: REACHED** for these four expected endpoints under the stated setup. This establishes test expectations, not a native execution path. The previous unresolved unused-unit-fallback timing question is absent here: 1em is actually selected and font-size is literal.
