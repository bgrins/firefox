# WEB-ANIMATIONS-1#animating-properties

**Animating properties** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

Unless otherwise specified, all CSS properties are **animatable**. How property values combine is defined by the **Animation type** line in each property’s property definition table:

**not animatable** 

The property is not animatable. It is not processed when listed in an animation keyframe, and is not affected by transitions.

> **Note:** Note: Properties are typically excluded from animation because animating them would create excessive complications. For example, properties defining animation parameters are [not animatable](https://drafts.csswg.org/web-animations-1#not-animatable) since doing so would create complex recursive behavior.

> **Note:** Note: An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) that targets only properties that are [not animatable](https://drafts.csswg.org/web-animations-1#not-animatable) will still exhibit the usual behavior for an animation effect such as firing events and delaying the fulfillment of the [animation](https://drafts.csswg.org/web-animations-1#concept-animation)’s [current finished promise](https://drafts.csswg.org/web-animations-1#current-finished-promise).

**discrete** 

The property’s values cannot be meaningfully combined, thus it is [not additive](https://drafts.csswg.org/css-values-4/#not-additive). [Interpolation](https://drafts.csswg.org/css-values-4/#interpolation) swaps from *Va* to *Vb* at 50% (*p=0.5*), i.e.

 Vresult\= Vstart if p <0.5 Vend if p ≥0.5

**by computed value** 

Corresponding individual components of the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) are combined (interpolated, added, or accumulated) using the indicated procedure for that value type (see [CSS Values 4 § 3 Combining Values: Interpolation, Addition, and Accumulation](https://drafts.csswg.org/css-values-4/#combining-values)). If the number of components or the types of corresponding components do not match, or if any component value uses [discrete](https://drafts.csswg.org/web-animations-1#discrete) animation and the two corresponding values do not match, then the property values combine as discrete.

**repeatable list** 

Same as [by computed value](https://drafts.csswg.org/web-animations-1#by-computed-value) except that if the two lists have differing numbers of items, they are first repeated to the least common multiple number of items. Each item is then combined by computed value. If a pair of values cannot be combined or if any component value uses [discrete](https://drafts.csswg.org/web-animations-1#discrete) animation, then the property values combine as discrete.

> **Note:** Note: The repeatable list concept ensures that a list that is conceptually repeated to a certain length (as [background-origin](https://drafts.csswg.org/css-backgrounds-3/#propdef-background-origin) is repeated to the length of the [background-image](https://drafts.csswg.org/css-backgrounds-3/#propdef-background-image) list) or repeated infinitely will smoothly transition between any values, and so that the computed value will properly represent the result (and potentially be inherited correctly).

(See prose) 

Some properties have specific interpolation behavior not covered by the above cases; in this case the animation behavior will be specified explicitly for that property.The [animation type](https://drafts.csswg.org/web-animations-1#animation-type) of properties that do not yet include an Animation type line in their property definition, is defined in [Appendix A: Animation types of existing properties](https://drafts.csswg.org/web-animations-1#animation-types).

#### Custom Properties

For [custom properties](https://drafts.csswg.org/css-variables-2/#custom-property) registered using the [`registerProperty()`](https://drafts.css-houdini.org/css-properties-values-api-1/#dom-css-registerproperty) method for the [current global object](https://html.spec.whatwg.org/multipage/webappapis.html#current-global-object), the [animation type](https://drafts.csswg.org/web-animations-1#animation-type) is [by computed value](https://drafts.csswg.org/web-animations-1#by-computed-value), derived from the type used in the property’s [syntax definition](https://drafts.css-houdini.org/css-properties-values-api-1/#syntax-definition). Where there is no [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) type that corresponds to the property’s specified syntax (e.g. when the syntax is the [universal syntax definition](https://drafts.css-houdini.org/css-properties-values-api-1/#universal-syntax-definition)) or when the custom property is not registered, the animation type is [discrete](https://drafts.csswg.org/web-animations-1#discrete).

## Navigation

- Parent: `animation-model` — Animation model
- Prev: `introduction-to-the-animation-model` — Introduction
- Next: `keyframe-effects` — Keyframe effects
- Children: 7
  - `concept-animatable` — animatable
  - `animation-type` — Animation type
  - `not-animatable` — not animatable
  - `discrete` — discrete
  - `by-computed-value` — by computed value
  - `repeatable-list` — repeatable list
  - `custom-properties` — Custom Properties

## Outgoing refs (14)

`webspec-index refs WEB-ANIMATIONS-1#animating-properties -d outgoing -l 14`

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#animating-properties

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#animating-properties" --format markdown`
