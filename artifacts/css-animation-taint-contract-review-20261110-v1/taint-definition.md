# CSS-VARIABLES-2#animation-tainted

**animation-tainted** (definition)

**SHA**: hash:7dd5332310c717489184acb6367fdd28c9fbb4b8d2798c866342f9e9a8b5eb9b

## Content

Notably, they can even be animated, but since the UA has no way to interpret their contents, they always use the "flips at 50%" behavior that is used for any other pair of values that can’t be intelligently interpolated. However, any [custom property](https://drafts.csswg.org/css-variables-2#custom-property) used in a [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) rule becomes **animation-tainted**, which affects how it is treated when referred to via the [var()](https://drafts.csswg.org/css-variables-2#funcdef-var) function in an animation property.

## Navigation

- Parent: `defining-variables` — Defining Custom Properties: the --* family of properties
- Prev: `typedef-custom-property-name` — <custom-property-name>

## Incoming refs (3)

- CSS-VARIABLES-2#defining-variables
- CSS-VARIABLES-2#index-defined-here
- CSS-VARIABLES-2#replace-a-var-function

### Possible effects

CSS-VARIABLES-2#animation-tainted

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VARIABLES-2#animation-tainted" --format markdown`
