# Repeated cyclic attribute substitution

Scenario: an unregistered custom property contains two `attr(x type(*), …)` functions. The element has `x="attr(x type(*))"`; no custom-property cycle involves the outer property.

1. [attr substitution, step 6](https://drafts.csswg.org/css-values-5/#attr-substitution) substitutes the attribute value under the attribute's context before parsing the requested type.
2. The nested reference re-enters that same context. [Guarding](https://drafts.csswg.org/css-values-5/#guarded) marks the repeated attribute context cyclic.
3. [Substitution steps 1 and 3](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) return the guaranteed-invalid value for that cyclic context. The outer property context is outside the self-cycle.
4. The outer attr's FAILURE branch substitutes its fallback. Each sibling invocation independently reaches its own fallback; `type(*)` cannot exempt the preceding substitution step.
5. [Replacement](https://drafts.csswg.org/css-values-5/#substitution) requires fully resolved output, so an unresolved attr/var function cannot be a successful replacement here.

**Verdict: REACHED** — outer fallbacks 13px and 37px yield custom-property text `13px 37px`, with matching two-value margins. An absent `--missing` similarly makes the attribute value invalid. A literal 19px yields two 19px values. Separate custom declarations each use their own fallback.

Primary snapshot is fresh HTTP200 in FETCH.json, retrieved 2026-10-19. All linked anchors were verified in it. webspec-index remains unavailable; this is a direct algorithm trace. Browser execution is pending.
