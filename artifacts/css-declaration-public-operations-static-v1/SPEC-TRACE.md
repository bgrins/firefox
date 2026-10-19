# Primary specification trace

Read current drafts on 2026-10-19. Selected paraphrases below are the relevant obligations, not a complete spec snapshot.

* [CSSOM specified order](https://drafts.csswg.org/cssom/#concept-declarations-specified-order): expand shorthands; represent only the greatest-cascade occurrence of a repeated property, retaining its relative source position. [Cascade importance](https://drafts.csswg.org/css-cascade-5/#importance) gives important declarations precedence over normal ones. This supports push's priority-aware replacement-and-append semantics.
* [CSSOM set a declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration): requested value and importance replace the target while satisfying uniqueness and mapping-order constraints. This is an assignment, so it can lower importance; push is not interchangeable with it.
* [CSSOM removeProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-removeproperty): capture the old serialized value, remove all represented target longhands (or the named custom/longhand declaration), update the style attribute only if something was removed, return the captured value. Earliest-match plus suffix filtering implements this under unique valid storage and an unchanged target roster.
* [CSSOM cssText](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-csstext): replace the declaration list by the parsed specified-order result and update the style attribute. Native clear's mapped-attribute use is a separate internal interface.

Verdict: REACHED for these operation-specific normative contracts; NOT REACHED for a new implementation defect in the inspected admitted callers. Raw malformed-state/stale-index calls are not browser reproducers.
