# EOF closure in the nested raw attribute case

**Question:** Must `--x:attr(data-foo type(*),abc)` use fallback when the DOM attribute data-foo contains exactly `attr(data-foo`, without a closing parenthesis?

**Scenario:** Unregistered --x, present null-namespace data-foo, no competing declarations or other substitutions. The attribute's literal text is unchanged throughout evaluation.

1. Outer property replacement invokes substitution; the outer typed attr reads the attribute and enters the typed attribute-substitution route. [Values 5 attribute replacement, step 6](https://drafts.csswg.org/css-values-5/#attr-substitution).

2. Typed parsing uses CSS component values. Parsing with a syntax explicitly starts by parsing a component-value list; CSS grammar parsing likewise normalizes input, builds component values, then matches the grammar. The string tokenizes as function-token `attr`, ident-token `data-foo`, then EOF. [Syntax normalization](https://drafts.csswg.org/css-syntax-3/#normalize-into-a-token-stream), [component-value list](https://drafts.csswg.org/css-syntax-3/#parse-a-list-of-component-values), [grammar parsing](https://drafts.csswg.org/css-syntax-3/#parse-grammar).

3. Consuming the function appends the ident as its argument. EOF and a closing parenthesis take the same current normative branch:
   > Discard a token from input. Return function.
   There is no EOF-error condition on this branch in the 20 October 2026 ED. The resulting function object has a complete name and valid argument; a missing source delimiter is not retained as an unmatched closing token. [Consume a function](https://drafts.csswg.org/css-syntax-3/#consume-a-function).

4. Substitution recognizes that function as bare attr(data-foo). Its first argument matches the attribute-name grammar and has no type. The present-attribute/raw branch returns a string before typed recursion:
   > return a CSS &lt;string> whose value is attr value.
   Crucially this reads the original DOM text, not a serialization of the recovered function. [Values 5 attribute replacement, steps 2–5](https://drafts.csswg.org/css-values-5/#attr-substitution).

5. The outer typed parse accepts the resulting CSS string under `*`, which is treated as optional declaration-value. There is no second typed attribute guard, no grammar failure, and no fallback selection. [Parsing with a syntax](https://drafts.csswg.org/css-values-5/#parse-with-a-syntax), [declaration-value grammar](https://drafts.csswg.org/css-syntax-3/#typedef-declaration-value).

**Verdict: REACHED** — the expected computed custom-property value is the single CSS string `"attr(data-foo"`, including the original missing parenthesis inside that string. The candidate observation agrees with this route; the existing `abc` expectation requires an explicit third oracle correction.

| Rejected explanation | Deciding rule |
|---|---|
| EOF makes this attr argument invalid | Function consumption returns its function at EOF; argument grammar is complete. |
| Every parse error mandates fallback | This EOF branch is not labeled a parse error in the current ED. Grammar matching occurs on parsed components. |
| Raw self-read is a substitution cycle | Raw return precedes typed attribute recursion. |
| Recovery adds a parenthesis to returned text | Recovery builds a function object; the raw read returns the unchanged DOM attribute text. |
| The old “wrong syntax” comment establishes failure | The comment does not override the parsing algorithm. |

This does not make all malformed strings valid: missing attribute names, invalid argument tokens, bad-string/bad-url tokens and unmatched closing tokens have distinct grammar/error paths. A genuinely typed self-reference recovered at EOF still takes the typed-cycle route. Those are useful separate controls, not outcomes established by this run.

Values 5's parse-with-syntax algorithm names both `raw parse` and `values` somewhat awkwardly. This trace relies on the attr algorithm's explicit substitution of attr value before its final syntax parse; that final input is a CSS string, accepted by either component-value parsing route. No strict-source-parenthesis check is specified there. No normalized Lean theorem is used: its parser assumptions exclude this question.

The initial capsule and its failing comparison remain immutable. Any corrected fixture must visibly document this additional oracle change and be run unchanged against both original and candidate; the earlier failure must not be relabeled a pass.

Sources: CSS Syntax 3 ED 20 October 2026 (fresh HTML captured here), Values 5 ED 27 October 2026 (pinned complete prior capture plus current web check). Every report fragment is verified against HTML ids. This is a manual positive trace, not exhaustive route enumeration: webspec-index was unavailable as recorded in the prior normative trace. No browser, build, native/index/HEAD/ledger edits, or additional formal-coverage credit.
