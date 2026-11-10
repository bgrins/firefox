# CSS-CASCADE-5#revert-rule-keyword

**Rolling Back Rules: the revert-rule keyword** (heading)

**SHA**: hash:31ebeb508bec4d304d2668da331656cfc59480b3f577404a8bade33f18df37e2

## Content

The **revert-rule** [CSS-wide keyword](https://drafts.csswg.org/css-values-4/#css-wide-keywords) rolls back the cascade similar to [revert](https://drafts.csswg.org/css-cascade-5#valdef-all-revert) and [revert-layer](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-layer), except it works by [style rule](https://drafts.csswg.org/css-syntax-3/#style-rule) rather than [cascade origin](https://drafts.csswg.org/css-cascade-5#origin) or [cascade layer](https://drafts.csswg.org/css-cascade-5#cascade-layers).

If the [cascaded value](https://drafts.csswg.org/css-cascade-5#cascaded-value) of a property is the [revert-rule](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-rule) keyword, the cascaded value is rolled back such that the [specified value](https://drafts.csswg.org/css-cascade-5#specified-value) is calculated as if the current [style rule](https://drafts.csswg.org/css-syntax-3/#style-rule) had not been present at all.

> **Example:** The [revert-rule](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-rule) keyword can be combined with [if()](https://drafts.csswg.org/css-values-5/#funcdef-if) to conditionally ignore a declaration:
>
> ```
> div {
>   border-radius: 5px;
> }
> .apply-sharp {
>   border-radius: if(style(--mode:sharp): 0px; else: revert-rule);
> }
> ```
>
> Given an element `<div class=apply-sharp>`, the above style sets border-radius to `0px` only when the [computed value](https://drafts.csswg.org/css-cascade-5#computed-value) of `--mode` is `sharp`.

The [revert-rule](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-rule) keyword behaves like [revert-layer](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-layer) in the [animation origin](https://drafts.csswg.org/css-cascade-5#cascade-origin-animation).

## Navigation

- Parent: `defaulting-keywords` — Explicit Defaulting
- Prev: `revert-layer` — Rolling Back Cascade Layers: the revert-layer keyword
- Children: 1
  - `valdef-all-revert-rule` — revert-rule

## Outgoing refs (12)

`webspec-index refs CSS-CASCADE-5#revert-rule-keyword -d outgoing -l 12`

## Incoming refs (1)

- CSS-CASCADE-5#contents

### Possible effects

CSS-CASCADE-5#revert-rule-keyword

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-CASCADE-5#revert-rule-keyword" --format markdown`
