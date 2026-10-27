# Used non-type attribute fallback cycle trace

**Question:** Can a fallback inside a missing bare/raw attr() or invalid numeric attr() rescue a custom property's self-reference?

```css
--x: attr(data-missing, var(--x, red));
color: var(--x, green);
```

Scenario: an unregistered property, no matching attribute, no animation, competing declarations, spread syntax or shadow boundaries. The body has black text. Numeric variants use `number` or `px` and either a missing attribute or `data-foo="nope"`.

Version: [CSS Values 5 Editor's Draft, 27 October 2026](https://drafts.csswg.org/css-values-5/) and [CSS Variables 1 Editor's Draft, 9 October 2026](https://drafts.csswg.org/css-variables-1/). REFERENCES.json pins complete previously captured primary HTML.

1. [Property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes --x under its property context.
2. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) guards that context and dispatches attr().
3. [Attribute replacement](https://drafts.csswg.org/css-values-5/#attr-substitution), step 3 for a missing attribute or step 4 for a failed numeric parse, reaches FAILURE. Its third clause substitutes the supplied fallback.
4. [Variable replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function), step 2, asks for --x's computed value, invoking property replacement again. The matching active [guard](https://drafts.csswg.org/css-values-5/#guarded) marks the cycle participants.
5. A var() fallback cannot erase that mark. The enclosing generic substitution returns guaranteed-invalid for the cyclic --x context. Mutual variants likewise invalidate both participating properties.
6. The later color consumer observes an invalid provider and selects its own green fallback.

**Verdict: REACHED** — --x is invalid and color is green. This prediction is separate from the browser result below.

A present raw attribute or valid numeric value returns before the attr fallback. Those unused fallback references do not cause a cycle. Missing attributes with acyclic fallbacks remain valid. These distinctions are tested by controls.

`webspec-index` was unavailable; bootstrap/install was deferred while the parent built. This is a manual positive trace through complete algorithms, not an exhaustive graph traversal or a NOT REACHED verdict. The linked anchors were verified in the pinned HTML. No existing WPT oracle was changed.
