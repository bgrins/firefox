# WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect

**The effect value of a keyframe effect** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

The [effect value](https://drafts.csswg.org/web-animations-1#effect-value) of a single property referenced by a [keyframe effect](https://drafts.csswg.org/web-animations-1#keyframe-effect) as one of its [target properties](https://drafts.csswg.org/web-animations-1#target-property), for a given *iteration progress*, *iteration index* and *underlying value* is calculated as follows.

1.  If *iteration progress* is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) abort this procedure.

2.  Let *target property* be the [longhand property](https://drafts.csswg.org/css-cascade-5/#longhand) for which the [effect value](https://drafts.csswg.org/web-animations-1#effect-value) is to be calculated.

3.  If [animation type](https://drafts.csswg.org/web-animations-1#animation-type) of the *target property* is [not animatable](https://drafts.csswg.org/web-animations-1#not-animatable) abort this procedure since the effect cannot be applied.

4.  If the [keyframe effect](https://drafts.csswg.org/web-animations-1#keyframe-effect) does not have an [effect target](https://drafts.csswg.org/web-animations-1#keyframe-effect-effect-target), or if the effect target cannot have computed property values calculated, abort this procedure.

5.  Let *property-specific keyframes* be the result of getting the set of [computed keyframes](https://drafts.csswg.org/web-animations-1#computed-keyframes) for this [keyframe effect](https://drafts.csswg.org/web-animations-1#keyframe-effect).

6.  Remove any [keyframes](https://drafts.csswg.org/web-animations-1#keyframe) from *property-specific keyframes* that do not have a property value for *target property*.

7.  If *property-specific keyframes* is empty, return *underlying value*.

8.  If there is no [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* with a [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of 0, create a new keyframe with a computed keyframe offset of 0, a property value set to *underlying value*, a [keyframe-specific composite operation](https://drafts.csswg.org/web-animations-1#keyframe-specific-composite-operation) of [replace](https://drafts.csswg.org/web-animations-1#composite-operation-replace), and a [keyframe-specific easing function](https://drafts.csswg.org/web-animations-1#keyframe-specific-easing-function) of the [linear easing function](https://drafts.csswg.org/css-easing-2/#linear-easing-function), and prepend it to the beginning of *property-specific keyframes*.

9.  Similarly, if there is no [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* with a [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of 1, create a new keyframe with a computed keyframe offset of 1, a property value set to *underlying value*, a [keyframe-specific composite operation](https://drafts.csswg.org/web-animations-1#keyframe-specific-composite-operation) of [replace](https://drafts.csswg.org/web-animations-1#composite-operation-replace), and a [keyframe-specific easing function](https://drafts.csswg.org/web-animations-1#keyframe-specific-easing-function) of the [linear easing function](https://drafts.csswg.org/css-easing-2/#linear-easing-function), and append it to the end of *property-specific keyframes*.

> **Note:** Other specifications may override the implicit keyframe generation behavior in the preceding two steps. For example, the [named timeline range keyframe selectors](https://drafts.csswg.org/scroll-animations-1/#named-range-keyframes) defined by Scroll Animations can cause these implicit keyframes not to be generated.
>
> A future level of this specification should incorporate the overridden behavior directly into this algorithm.

1.  Let *interval endpoints* be an empty sequence of keyframes.

2.  Populate *interval endpoints* by following the steps from the first matching condition below:

    If *iteration progress* < 0 and there is more than one [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* with a [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of 0,

    Add the first [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* to *interval endpoints*.

    If *iteration progress* ≥ 1 and there is more than one [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* with a [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of 1,

    Add the last [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* to *interval endpoints*.

    Otherwise,

    1.  Append to *interval endpoints* the last [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* whose [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) is less than or equal to *iteration progress* and less than 1. If there is no such keyframe (because, for example, the [iteration progress](https://drafts.csswg.org/web-animations-1#iteration-progress) is negative), add the last keyframe whose computed keyframe offset is 0.

    2.  Append to *interval endpoints* the next [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) in *property-specific keyframes* after the one added in the previous step.

3.  For each *keyframe* in *interval endpoints*:

    1.  If *keyframe* has a [composite operation](https://drafts.csswg.org/web-animations-1#composite-operation) that is *not* [replace](https://drafts.csswg.org/web-animations-1#composite-operation-replace), or *keyframe* has no composite operation and the composite operation of this [keyframe effect](https://drafts.csswg.org/web-animations-1#keyframe-effect) is *not* replace, then perform the following steps:

        1.  Let *composite operation to use* be the [composite operation](https://drafts.csswg.org/web-animations-1#composite-operation) of *keyframe*, or if it has none, the composite operation of this [keyframe effect](https://drafts.csswg.org/web-animations-1#keyframe-effect).

        2.  Let *value to combine* be the property value of *target property* specified on *keyframe*.

        3.  Replace the property value of *target property* on *keyframe* with the result of combining *underlying value* (*V*a) and *value to combine* (*V*b) using the procedure for the *composite operation to use* corresponding to the *target property*’s [animation type](https://drafts.csswg.org/web-animations-1#animation-type).
4.  If there is only one keyframe in *interval endpoints* return the property value of *target property* on that keyframe.

5.  Let *start offset* be the [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of the first keyframe in *interval endpoints*.

6.  Let *end offset* be the [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) of last keyframe in *interval endpoints*.

7.  Let *interval distance* be the result of evaluating `(*iteration progress* − *start offset*)
            / (*end offset* − *start offset*)`.

8.  Let *transformed distance* be the result of evaluating the [easing function](https://drafts.csswg.org/css-easing-2/#easing-function) associated with the first keyframe in *interval endpoints* passing *interval distance* as the input progress.

9.  Return the result of applying the [interpolation procedure](https://drafts.csswg.org/css-values-4/#interpolation) defined by the [animation type](https://drafts.csswg.org/web-animations-1#animation-type) of the *target property* to the values of the *target property* specified on the two keyframes in *interval endpoints*, taking the first such value as *V*start and the second as *V*end and using *transformed distance* as the interpolation parameter *p*.

Tests

*   [effect-value-interval-distance.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-interval-distance.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-interval-distance.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-interval-distance.html)
*   [effect-value-iteration-composite-operation.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-iteration-composite-operation.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-iteration-composite-operation.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-iteration-composite-operation.html)
*   [effect-value-opacity-replaced-effect-in-shadow-root.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect-in-shadow-root.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect-in-shadow-root.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect-in-shadow-root.html)
*   [effect-value-opacity-replaced-effect.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-opacity-replaced-effect.html)
*   [effect-value-overlapping-keyframes.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-overlapping-keyframes.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-overlapping-keyframes.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-overlapping-keyframes.html)
*   [effect-value-replaced-animations.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-replaced-animations.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-replaced-animations.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-replaced-animations.html)
*   [effect-value-transformed-distance.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-value-transformed-distance.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-value-transformed-distance.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-value-transformed-distance.html)

> **Note:** Note that this procedure assumes the following about the list of [keyframes](https://drafts.csswg.org/web-animations-1#keyframe) specified on the effect:
>
> *   Each [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) has a specified [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets) in the range \[0, 1\].
>
> *   The list of [keyframes](https://drafts.csswg.org/web-animations-1#keyframe) is sorted in ascending order by [computed keyframe offset](https://drafts.csswg.org/web-animations-1#computed-keyframe-offsets).
>
> *   For a given property, there is at most one specified property value on each keyframe.
>
> It is the responsibility of the user of the model (for example, a declarative markup or programming interface) to ensure these conditions are met.
>
> For example, for the [programming interface](https://drafts.csswg.org/web-animations-1#programming-interface) defined by this specification, these conditions are met by the procedure to produce the [computed keyframes](https://drafts.csswg.org/web-animations-1#computed-keyframes) that become the input to this procedure.

> **Note:** Note: this procedure permits overlapping [keyframes](https://drafts.csswg.org/web-animations-1#keyframe). The behavior is that at the point of overlap the output value jumps to the value of the last defined keyframe at that offset. For overlapping keyframes at 0 or 1, the output value for [iteration progress](https://drafts.csswg.org/web-animations-1#iteration-progress) values less than 0 or greater than or equal to 1 is the value of the first keyframe or the last keyframe in *keyframes* respectively.

> **Note:** Note that [computed keyframes](https://drafts.csswg.org/web-animations-1#computed-keyframes) are “live”: user-agents behave as if they are recreated every time the [effect value](https://drafts.csswg.org/web-animations-1#effect-value) is calculated.For example, if there is an ongoing transition on the [font-size](https://drafts.csswg.org/css-fonts-4/#propdef-font-size) property from `10px` to `20px`, a property value specified as `1em` in a [keyframe](https://drafts.csswg.org/web-animations-1#keyframe) would during [keyframe computation](https://drafts.csswg.org/web-animations-1#calculating-computed-keyframes) resolve against the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) in the range \[`10px`, `20px`\] produced by the transition on font-size.

## Navigation

- Parent: `keyframe-effects` — Keyframe effects
- Prev: `calculating-computed-keyframes` — Calculating computed keyframes

## Outgoing refs (24)

`webspec-index refs WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect -d outgoing -l 24`

## Incoming refs (4)

- CSS-ANIMATIONS-2#issues-index
- CSS-ANIMATIONS-2#keyframe-processing
- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#keyframes-section

### Possible effects

WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#the-effect-value-of-a-keyframe-animation-effect" --format markdown`
