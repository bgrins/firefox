# WEB-ANIMATIONS-1#calculating-computed-keyframes

**Calculating computed keyframes** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

Before calculating the [effect value](WEB-ANIMATIONS-1#effect-value) of a [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect), the property values on its [keyframes](WEB-ANIMATIONS-1#keyframe) are [computed](WEB-ANIMATIONS-1#computing-property-values), and the offset to use for any keyframes with a null [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) is computed. The result of resolving these values is a set of **computed keyframes**.

The calculated [keyframe offsets](WEB-ANIMATIONS-1#keyframe-offset) of a set of [keyframe](WEB-ANIMATIONS-1#keyframe) that includes suitable values for each null keyframe offset are referred to as the **computed keyframe offsets**.

To produce [computed keyframe offsets](WEB-ANIMATIONS-1#computed-keyframe-offsets), we define a procedure to **compute missing keyframe offsets** that takes a sequence of [keyframes](WEB-ANIMATIONS-1#keyframe), *keyframes*, and has the following steps:

1.  For each [keyframe](WEB-ANIMATIONS-1#keyframe) in *keyframes*, let the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of the keyframe be equal to its [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) value.

2.  If *keyframes* contains more than one [keyframe](WEB-ANIMATIONS-1#keyframe) and the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of the first keyframe in *keyframes* is null, set the computed keyframe offset of the first keyframe to 0.

3.  If the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of the last [keyframe](WEB-ANIMATIONS-1#keyframe) in *keyframes* is null, set its computed keyframe offset to 1.

4.  For each pair of [keyframes](WEB-ANIMATIONS-1#keyframe) *A* and *B* where:

    *   *A* appears before *B* in *keyframes*, and

    *   *A* and *B* have a [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) that is not null, and

    *   all [keyframes](WEB-ANIMATIONS-1#keyframe) between *A* and *B* have a null [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets),
    calculate the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of each [keyframe](WEB-ANIMATIONS-1#keyframe) between *A* and *B* as follows:

    1.  Let **offset*k*** be the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of a [keyframe](WEB-ANIMATIONS-1#keyframe) *k*.

    2.  Let *n* be the number of keyframes *between* and including *A* and *B* minus 1.

    3.  Let *index* refer to the position of *keyframe* in the sequence of keyframes between *A* and *B* such that the first keyframe after *A* has an *index* of 1.

    4.  Set the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of *keyframe* to [offset](WEB-ANIMATIONS-1#offsetk)*A* + (offset*B* − offset*A*) × *index* / *n*.

Tests

*   [background-shorthand.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/background-shorthand.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/background-shorthand.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/background-shorthand.html)
*   [computed-keyframes-shorthands.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/computed-keyframes-shorthands.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/computed-keyframes-shorthands.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/computed-keyframes-shorthands.html)
*   [effect-value-context-filling.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-context-filling.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-context-filling.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-context-filling.html)
*   [effect-value-context.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-context.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-context.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-context.html)

[Computed keyframes](WEB-ANIMATIONS-1#computed-keyframes) are produced using the following procedure. Note that this procedure is only performed on a [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) having an [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target) for which computed property values can be calculated.

1.  Let *computed keyframes* be an empty list of [keyframes](WEB-ANIMATIONS-1#keyframe).

2.  For each *keyframe* in the list of [keyframes](WEB-ANIMATIONS-1#keyframe) specified on this [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect), perform the following steps:

    1.  Add a new empty [keyframe](WEB-ANIMATIONS-1#keyframe), *computed keyframe*, to *computed keyframes*.

    2.  For each property specified in *keyframe*:

        *   [Compute a property value](WEB-ANIMATIONS-1#compute-a-property-value) using the value specified on *keyframe* as the value, and the [target element](WEB-ANIMATIONS-1#effect-target-target-element) as the element; then add the property and resulting value to *computed keyframe*.

        *   For shorthand properties, add the equivalent longhand properties.

        *   For logical properties \[CSS-LOGICAL-1\], add the [equivalent physical properties](CSS-WRITING-MODES-4#logical-to-physical) \[CSS-WRITING-MODES-4\] based on the computed value of [writing-mode](CSS-WRITING-MODES-4#propdef-writing-mode) and/or [direction](CSS-WRITING-MODES-3#propdef-direction) for the [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target).
        For example, if *keyframe* has a value of 12pt for the [border-width](CSS-BACKGROUNDS-3#propdef-border-width) [shorthand property](CSS-CASCADE-5#shorthand-property), the user agent will [compute a property value](WEB-ANIMATIONS-1#compute-a-property-value) of 16px for each of the [longhand properties](CSS-CASCADE-5#longhand): [border-bottom-width](CSS-BACKGROUNDS-3#propdef-border-bottom-width), [border-left-width](CSS-BACKGROUNDS-3#propdef-border-left-width), [border-right-width](CSS-BACKGROUNDS-3#propdef-border-right-width), and [border-top-width](CSS-BACKGROUNDS-3#propdef-border-top-width). As a result, *computed keyframe* would *not* have a value for the border-width property, but would instead include each of the longhand properties, each with the value 16px.

        If conflicts arise when expanding shorthand properties or replacing logical properties with physical properties, apply the following rules in order until the conflict is resolved:

        1.  Longhand properties override shorthand properties (e.g. [border-top-color](CSS-BACKGROUNDS-3#propdef-border-top-color) overrides [border-top](CSS-BACKGROUNDS-3#propdef-border-top)).

        2.  Shorthand properties with fewer longhand components override those with more longhand components (e.g. [border-top](CSS-BACKGROUNDS-3#propdef-border-top) overrides [border-color](CSS-BACKGROUNDS-3#propdef-border-color)).

        3.  Physical properties override logical properties.

        4.  For shorthand properties with an equal number of longhand components, properties whose IDL name (see the [CSS property to IDL attribute](CSSOM#css-property-to-idl-attribute) algorithm \[CSSOM\]) appears earlier when sorted in ascending order by the Unicode codepoints that make up each IDL name, override those who appear later.
3.  Apply the procedure to [compute missing keyframe offsets](WEB-ANIMATIONS-1#compute-missing-keyframe-offsets) to *computed keyframes*.

4.  Return *computed keyframes*.

## Navigation

- Parent: `keyframe-effects` — Keyframe effects
- Prev: `computing-property-values` — Computing property values
- Next: `the-effect-value-of-a-keyframe-animation-effect` — The effect value of a keyframe effect
- Children: 3
  - `computed-keyframes` — computed keyframes
  - `computed-keyframe-offsets` — computed keyframe offsets
  - `compute-missing-keyframe-offsets` — compute missing keyframe offsets

## Outgoing refs (25)

`webspec-index refs WEB-ANIMATIONS-1#calculating-computed-keyframes -d outgoing -l 25`

## Incoming refs (4)

- CSS-ANIMATIONS-2#issues-index
- CSS-ANIMATIONS-2#keyframe-processing
- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect

### Possible effects

WEB-ANIMATIONS-1#calculating-computed-keyframes

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-computed-keyframes" --format markdown`
