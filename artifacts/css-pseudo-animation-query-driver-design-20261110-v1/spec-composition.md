# WEB-ANIMATIONS-1#applying-the-composited-result

**Applying the composited result** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

Applying a [composited value](WEB-ANIMATIONS-1#composited-value) to a [target property](WEB-ANIMATIONS-1#target-property) is achieved by adding a specified value to the CSS cascade.

The level of the cascade to which this specified value is added depends on the [class](WEB-ANIMATIONS-1#animation-class) of the [animation](WEB-ANIMATIONS-1#concept-animation) [associated with](WEB-ANIMATIONS-1#animation-effect-associated-animation) the effect with the highest composite order in the [effect stack](WEB-ANIMATIONS-1#effect-stack) for a given property. By default, the specified value is added to the [Animation Origin](CSS-CASCADE-5#cascade-origin-animation) of the cascade. \[CSS-CASCADE-3\]

Tests

*   [applying-the-composited-result.html](https://wpt.fyi/results/web-animations/animation-model/combining-effects/applying-the-composited-result.html) [(live test)](http://wpt.live/web-animations/animation-model/combining-effects/applying-the-composited-result.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/combining-effects/applying-the-composited-result.html)

> **Example:** For example, if the effect with the highest composite order is associated with a “CSS transition”-class animation, the [composited value](WEB-ANIMATIONS-1#composited-value) will be added to the [Transition Origin](CSS-CASCADE-5#cascade-origin-transition) of the cascade.

The [composited value](WEB-ANIMATIONS-1#composited-value) calculated for a CSS [target property](WEB-ANIMATIONS-1#target-property) is applied using the following process:

1.  Calculate the *base value* of the property as the value generated for that property by finding the [computed value](CSS-CASCADE-5#computed-value) for that property in the absence of animations.

2.  Establish the [effect stack](WEB-ANIMATIONS-1#effect-stack) for the property (see [§ 5.4.2 The effect stack](WEB-ANIMATIONS-1#the-effect-stack)).

3.  Calculate the [composited value](WEB-ANIMATIONS-1#composited-value) of the [effect stack](WEB-ANIMATIONS-1#effect-stack) passing in the *base value* of the property as the initial [underlying value](WEB-ANIMATIONS-1#underlying-value) (see [§ 5.4.3 Calculating the result of an effect stack](WEB-ANIMATIONS-1#calculating-the-result-of-an-effect-stack)).

4.  Insert the [composited value](WEB-ANIMATIONS-1#composited-value) into the CSS cascade at the level defined for the [class](WEB-ANIMATIONS-1#animation-class) of the [animation](WEB-ANIMATIONS-1#concept-animation) [associated with](WEB-ANIMATIONS-1#animation-effect-associated-animation) the effect at the top of the [effect stack](WEB-ANIMATIONS-1#effect-stack) established for the [target property](WEB-ANIMATIONS-1#target-property).

## Navigation

- Parent: `combining-effects` — Combining effects
- Prev: `effect-composition` — Effect composition

## Outgoing refs (12)

`webspec-index refs WEB-ANIMATIONS-1#applying-the-composited-result -d outgoing -l 12`

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#applying-the-composited-result

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#applying-the-composited-result" --format markdown`
