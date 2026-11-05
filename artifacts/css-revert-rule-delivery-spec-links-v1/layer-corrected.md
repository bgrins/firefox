# CSS-CASCADE-5#revert-layer

**Rolling Back Cascade Layers: the revert-layer keyword** (heading)

**SHA**: hash:575c0863887c6666041262b19564c52e9f00771d1de1f9498fcefae85c4dbff4

## Content

The **revert-layer** [CSS-wide keyword](CSS-VALUES-4#css-wide-keywords) rolls back the cascade similar to [revert](CSS-CASCADE-5#valdef-all-revert), except it works by [cascade layer](CSS-CASCADE-5#cascade-layers) rather than by [cascade origin](CSS-CASCADE-5#origin).

If the [cascaded value](CSS-CASCADE-5#cascaded-value) of a property is the [revert-layer](CSS-CASCADE-5#valdef-all-revert-layer) keyword, the cascaded value is rolled back to the earlier [layer](CSS-CASCADE-5#cascade-layers), so that the [specified value](CSS-CASCADE-5#specified-value) is calculated as if no rules were specified in the current cascade layer—​or between its [normal](CSS-CASCADE-5#normal) and [important](CSS-CASCADE-5#important) levels in the [cascade](CSS-CASCADE-5#cascade)—​for this property on this element. For revert-layer in important [element-attached styles](CSS-CASCADE-5#style-attr), however, it only reverts the [element-attached styles](CSS-CASCADE-5#style-attr) and the intervening [animation origin](CSS-CASCADE-5#cascade-origin-animation), and not any of the intervening [author-origin](CSS-CASCADE-5#cascade-origin-author) important rules.

> **Example:** For example, applying [revert-layer](CSS-CASCADE-5#valdef-all-revert-layer) to the [height](CSS-SIZING-3#propdef-height) in layer `two`, reverts the height property to the value defined in layer `one`, yielding a height of `100px`.
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
> Note that since [height](CSS-SIZING-3#propdef-height) and [block-size](CSS-LOGICAL-1#propdef-block-size) are paired properties in a [logical property group](CSS-LOGICAL-1#logical-property-group), the following layer `two` declaration would also revert to the height defined in layer `one`.
>
> ```
> @layer two {
>   div { height: 200px }
>   div { block-size: revert-layer }
> }
> ```

> **Note:** Note: If there are no lower-precedence [declarations](CSSOM-1#cssstyledeclaration-declarations) in the same [cascade origin](CSS-CASCADE-5#origin) as the [revert-layer](CSS-CASCADE-5#valdef-all-revert-layer) value, the [cascaded value](CSS-CASCADE-5#cascaded-value) will roll back to the previous origin.

> **Note:** Note: The [animation origin](CSS-CASCADE-5#cascade-origin-animation) is not collapsed with the [author origin](CSS-CASCADE-5#cascade-origin-author) for this purpose as it is for [revert](CSS-CASCADE-5#valdef-all-revert), and thus effectively forms its own [cascade layer](CSS-CASCADE-5#cascade-layers).

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
