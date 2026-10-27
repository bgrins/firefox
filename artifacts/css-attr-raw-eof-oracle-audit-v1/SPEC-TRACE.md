# EOF in a nested attribute function

**Question:** Does data-foo=`attr(data-foo` make `--x: attr(data-foo type(*), abc)` fall back to abc?

**Scenario:** The attribute is present with those exact characters; --x is unregistered. Its outer declaration is syntactically complete.

1. [Values 5 attr substitution, step 6](https://drafts.csswg.org/css-values-5/#attr-substitution) processes the typed attribute contents under the data-foo attribute context.
2. [Syntax grammar parsing](https://drafts.csswg.org/css-syntax-3/#parse-grammar) obtains [component values](https://drafts.csswg.org/css-syntax-3/#parse-list-of-component-values). A function token invokes [consume a function](https://drafts.csswg.org/css-syntax-3/#consume-function). EOF and a closing parenthesis select the same return branch:
   > Discard a token from input. Return function.
   The resulting function has name attr and one identifier argument, data-foo. EOF does not create an unmatched closing token or require rejection. This is parser recovery, not mutation of the DOM attribute.
3. [Arbitrary substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) replaces that function. [Attr step 5](https://drafts.csswg.org/css-values-5/#attr-substitution) handles omitted type:
   > return a CSS <string> whose value is attr value.
   It returns before step 6's recursive typed context. The string's characters are still `attr(data-foo`; no parenthesis is appended inside it.
4. The outer [universal syntax](https://drafts.csswg.org/css-values-5/#parse-with-a-syntax) accepts this CSS string. Its fallback is unused.

**Verdict: REACHED** — the candidate's `"attr(data-foo"` string is specified. This is a third obsolete existing oracle, not evidence of a native regression.

| Rejected explanation | Deciding distinction |
|---|---|
| Missing closing parenthesis always invalidates CSS | Syntax's function consumer returns normally on EOF. |
| The inner read repeats the typed attribute guard | Bare/raw-string replacement returns before typed recursion. |
| Recovery adds a parenthesis to the returned string | The inner read uses the unchanged DOM attribute value. |

Current primary HTML and checked anchor IDs are archived. webspec-index is unavailable; this is a manual positive trace, not an exhaustive graph search. The parse-with-syntax prose uses both raw-parse and values variables; the typed replacement already supplies a resolved string, so that wording does not distinguish outcomes here.
