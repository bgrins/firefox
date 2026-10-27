# Nested raw attribute cycle trace

**Question:** Does the disputed WPT input produce `abc`, or two literal strings?

**Scenario:** One unregistered `--x`, no competing declarations, all attributes present, no spread syntax:

```text
--x: attr(data-foo type(*), abc)
data-foo = attr(data-bar type(*), fallback)
data-bar = attr(data-foo) attr(data-bar)
```

**Version:** [CSS Values 5 Editor's Draft, 27 October 2026](https://drafts.csswg.org/css-values-5/), captured in `values-current.html`.

1. [Property replacement, step 1](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes `--x` under its property context.
2. [Generic substitution, steps 1–2](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) guards that context and invokes the outer function's replacement. No early substitution applies.
3. [Attribute replacement, steps 1–6](https://drafts.csswg.org/css-values-5/#attr-substitution) reads `data-foo`; `type(*)` enters its attribute context. Repeating this route for `data-bar` enters a different context.
4. Both inner calls take step 5:
   > If syntax is null or the keyword raw-string, return a CSS <string> whose value is attr value.
5. These calls return before step 6. [Guarding](https://drafts.csswg.org/css-values-5/#guarded) therefore never re-enters either attribute context.
6. [Syntax parsing](https://drafts.csswg.org/css-values-5/#parse-with-a-syntax) accepts the resulting string tokens. Their contents are not function tokens. Generic substitution's final cycle check succeeds; neither fallback is selected.

**Verdict: REACHED** — the literal-string result follows the captured current algorithms:

```css
"attr(data-bar type(*), fallback)" "attr(data-foo) attr(data-bar)"
```

| Alternative route | Why this scenario rejects it |
|---|---|
| Bare reference enters another attribute guard | Its replacement returns earlier. |
| Missing/invalid primary selects fallback | Both attributes exist; raw values cannot fail parsing. |
| Generated strings recursively invoke their contents | String contents remain data. |
| An unrelated explanatory example makes every attr() guarded | The normative raw return determines this branch. |

Tool limitation: `webspec-index` is unavailable in this environment. No installation or bootstrap was performed during the parent's build. This is a manually followed **positive** route from complete captured algorithms, not an exhaustive graph search or a NOT REACHED verdict. Every linked anchor was checked directly in the fetched HTML. The existing WPT's obsolete `#attr-notations` help anchor is absent; current `#attr-notation` exists. No WPT was changed.
