# CSS-CASCADE-5#revert-layer

**Rolling Back Cascade Layers: the revert-layer keyword** (heading)

**SHA**: hash:31ebeb508bec4d304d2668da331656cfc59480b3f577404a8bade33f18df37e2

## Content

The **revert-layer** [CSS-wide keyword](https://drafts.csswg.org/css-values-4/#css-wide-keywords) rolls back the cascade similar to [revert](https://drafts.csswg.org/css-cascade-5#valdef-all-revert), except it works by [cascade layer](https://drafts.csswg.org/css-cascade-5#cascade-layers) rather than by [cascade origin](https://drafts.csswg.org/css-cascade-5#origin).

If the [cascaded value](https://drafts.csswg.org/css-cascade-5#cascaded-value) of a property is the [revert-layer](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-layer) keyword, the cascaded value is rolled back to the earlier [layer](https://drafts.csswg.org/css-cascade-5#cascade-layers), so that the [specified value](https://drafts.csswg.org/css-cascade-5#specified-value) is calculated as if no rules were specified in the current cascade layer—​or between its [normal](https://drafts.csswg.org/css-cascade-5#normal) and [important](https://drafts.csswg.org/css-cascade-5#important) levels in the [cascade](https://drafts.csswg.org/css-cascade-5#cascade)—​for this property on this element. For revert-layer in important [element-attached styles](https://drafts.csswg.org/css-cascade-5#style-attr), however, it only reverts the [element-attached styles](https://drafts.csswg.org/css-cascade-5#style-attr) and the intervening [animation origin](https://drafts.csswg.org/css-cascade-5#cascade-origin-animation), and not any of the intervening [author-origin](https://drafts.csswg.org/css-cascade-5#cascade-origin-author) important rules.

> **Example:** For example, applying [revert-layer](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-layer) to the [height](https://drafts.csswg.org/css-sizing-3/#propdef-height) in layer `two`, reverts the height property to the value defined in layer `one`, yielding a height of `100px`.
>
> ```
> @layer one {
>   div { height: 100px }
> }
>
> @layer two {
>   div { height: 200px }
>   div { height: revert-layer }
> }
> ```
>
> Note that since [height](https://drafts.csswg.org/css-sizing-3/#propdef-height) and [block-size](https://drafts.csswg.org/css-logical-1/#propdef-block-size) are paired properties in a [logical property group](https://drafts.csswg.org/css-logical-1/#logical-property-group), the following layer `two` declaration would also revert to the height defined in layer `one`.
>
> ```
> @layer two {
>   div { height: 200px }
>   div { block-size: revert-layer }
> }
> ```

> **Note:** Note: If there are no lower-precedence [declarations](https://drafts.csswg.org/cssom-1/#cssstyledeclaration-declarations) in the same [cascade origin](https://drafts.csswg.org/css-cascade-5#origin) as the [revert-layer](https://drafts.csswg.org/css-cascade-5#valdef-all-revert-layer) value, the [cascaded value](https://drafts.csswg.org/css-cascade-5#cascaded-value) will roll back to the previous origin.

> **Note:** Note: The [animation origin](https://drafts.csswg.org/css-cascade-5#cascade-origin-animation) is not collapsed with the [author origin](https://drafts.csswg.org/css-cascade-5#cascade-origin-author) for this purpose as it is for [revert](https://drafts.csswg.org/css-cascade-5#valdef-all-revert), and thus effectively forms its own [cascade layer](https://drafts.csswg.org/css-cascade-5#cascade-layers).

## Navigation

- Parent: `defaulting-keywords` — Explicit Defaulting
- Prev: `default` — Rolling Back Cascade Origins: the revert keyword
- Next: `revert-rule-keyword` — Rolling Back Rules: the revert-rule keyword
- Children: 1
  - `valdef-all-revert-layer` — revert-layer

## Outgoing refs (17)

`webspec-index refs CSS-CASCADE-5#revert-layer -d outgoing -l 17`

## Incoming refs (1)

- CSS-CASCADE-5#contents

### Possible effects

CSS-CASCADE-5#revert-layer

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-CASCADE-5#revert-layer" --format markdown`
