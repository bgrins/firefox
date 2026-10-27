# Current attribute replacement trace

Version: [CSS Values 5 Editor's Draft, 27 October 2026](https://drafts.csswg.org/css-values-5/), rechecked live during this review. Complete pinned HTML and the independent root review are referenced by REFERENCES.json. No spread syntax, dynamic names, registration or animation applies to these two oracle scenarios.

1. [Property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) starts substitution under the custom-property context.
2. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) guards that context and dispatches the outer attr().
3. [Attribute replacement](https://drafts.csswg.org/css-values-5/#attr-substitution), step 6, recursively substitutes each typed attribute under its attribute context.
4. The terminal bare/raw-string calls return literal strings at step 5, before step 6. Primitive reads similarly return or select fallback at step 4.
5. Consequently, [guarding](https://drafts.csswg.org/css-values-5/#guarded) never repeats an attribute context for these raw reads. String contents remain data during subsequent syntax parsing.
6. Universal syntax accepts the resulting strings; no context is poisoned. Missing or invalid non-type primaries instead evaluate their supplied fallback, preserving actual typed/property cycles.

**Verdict: REACHED** — the two literal outcomes in ORACLE-ADJUDICATION.md follow. This is a manual positive trace, not an exhaustive indexed-route claim. webspec-index remains unavailable; the linked anchors exist in the pinned primary HTML.
