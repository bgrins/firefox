# CSS-VARIABLES-1#animation-tainted

**animation-tainted** (definition)

**SHA**: hash:72c4b00afaa33f30ded58f4b1e4595c7155bb410d01e0d24b8157cdbdf101e40

## Content

Notably, they can even be animated, but since the UA has no way to interpret their contents, they always use the "flips at 50%" behavior that is used for any other pair of values that can’t be intelligently interpolated. However, any [custom property](CSS-VARIABLES-1#custom-property) used in a [@keyframes](CSS-ANIMATIONS-1#at-ruledef-keyframes) rule becomes **animation-tainted**, which affects how it is treated when referred to via the [var()](CSS-VARIABLES-1#funcdef-var) function in an animation property.

## Navigation

- Parent: `defining-variables` — Defining Custom Properties: the --* family of properties
- Prev: `typedef-custom-property-name` — <custom-property-name>

## Incoming refs (4)

- CSS-2023#terms
- CSS-VARIABLES-1#defining-variables
- CSS-VARIABLES-1#index-defined-here
- CSS-VARIABLES-1#replace-a-var-function

### Possible effects

CSS-VARIABLES-1#animation-tainted

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VARIABLES-1#animation-tainted" --format markdown`
