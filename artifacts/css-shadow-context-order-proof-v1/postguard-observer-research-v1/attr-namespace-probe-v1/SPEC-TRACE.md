# Typed attribute namespace identity

Question: Must `width: attr(a|x type(<length>), 5px)` and `height: attr(b|x type(<length>), 7px)` independently read `a:x="13px"` and `b:x="37px"`?

Scenario: The stylesheet binds `a` and `b` to distinct namespace URIs. Both attributes exist on the same element; their values are absolute lengths and contain no substitution functions. There are no competing width/height declarations, animations, or container queries.

1. [CSS Values 5, attr arguments](https://drafts.csswg.org/css-values-5/#attr-notation) defines an attribute name with an optional namespace prefix. The named attribute belongs to the styled element.
2. [Substitution, step 2](https://drafts.csswg.org/css-values-5/#attr-substitution) parses each function's name and type.
3. Step 3 obtains the value of that attribute on the element. The different qualified names select different attributes.
4. Step 6 substitutes functions in that value and parses it using the requested syntax. These literal lengths have no further references and both parse successfully. Neither fallback applies.

**Verdict: REACHED** — the values are independently 13px and 37px, regardless of declaration order. This is a spec inference; browser execution is pending.

The fresh HTTP 200 primary snapshot and hash are in FETCH.json. Both cited anchors were verified in that snapshot. `webspec-index` is unavailable on PATH; this direct numbered algorithm trace replaces its graph navigation. Mach/bootstrap is forbidden in this agent's scope. No claim of exhaustive unrelated algorithm traversal is made.
