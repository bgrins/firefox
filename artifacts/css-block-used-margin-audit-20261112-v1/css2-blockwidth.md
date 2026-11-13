# CSS2#blockwidth

**Block-level, non-replaced elements in normal
flow** (heading)

**SHA**: hash:f7588264f073215501b849ab8172ab4f0d7bf4aa82886ad3e5a89f431743cc42

## Content

The following constraints must hold among the used values of the other properties:

> [margin-left](CSS2#propdef-margin-left) + [border-left-width](CSS2#propdef-border-left-width) + [padding-left](CSS2#propdef-padding-left) + [width](CSS2#propdef-width) + [padding-right](CSS2#propdef-padding-right) + [border-right-width](CSS2#propdef-border-right-width) + [margin-right](CSS2#propdef-margin-right) = width of [containing block](CSS2#containing-block-details)

If [width](CSS2#propdef-width) is not [auto](CSS2#valdef-width-auto) and [border-left-width](CSS2#propdef-border-left-width) + [padding-left](CSS2#propdef-padding-left) + width + [padding-right](CSS2#propdef-padding-right) + [border-right-width](CSS2#propdef-border-right-width) (plus any of [margin-left](CSS2#propdef-margin-left) or [margin-right](CSS2#propdef-margin-right) that are not auto) is larger than the width of the containing block, then any auto values for margin-left or margin-right are, for the following rules, treated as zero.

If all of the above have a computed value other than auto, the values are said to be "over-constrained" and one of the used values will have to be different from its computed value. If the [direction](CSS2#propdef-direction) property of the containing block has the value [ltr](CSS2#valdef-direction-ltr), the specified value of [margin-right](CSS2#propdef-margin-right) is ignored and the value is calculated so as to make the equality true. If the value of direction is [rtl](CSS2#valdef-direction-rtl), this happens to [margin-left](CSS2#propdef-margin-left) instead.

If there is exactly one value specified as auto, its used value follows from the equality.

If [width](CSS2#propdef-width) is set to [auto](CSS2#valdef-width-auto), any other auto values become 0 and width follows from the resulting equality.

If both [margin-left](CSS2#propdef-margin-left) and [margin-right](CSS2#propdef-margin-right) are auto, their used values are equal. This horizontally centers the element with respect to the edges of the containing block.

## Navigation

- Parent: `Computing_widths_and_margins` — Calculating widths and
margins
- Prev: `inline-replaced-width` — Inline, replaced elements
- Next: `block-replaced-width` — Block-level, replaced elements in normal flow

## Outgoing refs (12)

`webspec-index refs CSS2#blockwidth -d outgoing -l 12`

## Incoming refs (11)

`webspec-index refs CSS2#blockwidth -d incoming -l 11`

### Possible effects

CSS2#blockwidth

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS2#blockwidth" --format markdown`
