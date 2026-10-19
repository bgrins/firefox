# Primary specification check

Checked the current editors' drafts on 19 October 2026:

- [CSS Syntax, consume a string token](https://drafts.csswg.org/css-syntax-3/#consume-string-token): EOF returns the accumulated string token; a backslash immediately before EOF contributes no character. The resulting token is distinct from the bad-string return for an unescaped newline.
- [CSS Variables, replace a var() function](https://drafts.csswg.org/css-variables-1/#replace-a-var-function): a missing custom property with a fallback follows fallback substitution. The regression compares that resulting value with a fully closed literal.

This supports the semantic WPT oracle. It does not specify Stylo's internal
byte offsets or prove the native parser. The independent arithmetic component
and source review cover the offset correction under their stated assumptions.
