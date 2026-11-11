# WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect

**The effect value of a keyframe effect** (heading)

**SHA**: hash:07b283f9ef260b80742e247ba6ed8cee8f0d3013c60bdaf43a7b2c536f52fc38

## Content

> **Issue:** The implicit keyframe generation steps in Web Animations Level 1 need to be reconciled with the behavior defined for [named timeline range keyframe selectors](https://www.w3.org/TR/scroll-animations-1/#named-range-keyframes) in Scroll Animations. Scroll Animations currently overrides those steps but that overridden behavior should be incorporated directly in this algorithm. See [issue 14309](https://github.com/w3c/csswg-drafts/issues/14309).

The procedure for computing the [effect value](https://drafts.csswg.org/web-animations-1/#effect-value) of a single property referenced by a [keyframe effect](https://drafts.csswg.org/web-animations-1/#keyframe-effect) as one of its [target properties](https://drafts.csswg.org/web-animations-1/#target-property), for a given *iteration progress*, *current iteration* and *underlying value* is amended by inserting the following step after the step to apply the keyframe effect composite mode.

12.  For each *keyframe* in *interval endpoints*:

     1.  (As in web-animations-1).

     2.  If this [keyframe effect](https://drafts.csswg.org/web-animations-1/#keyframe-effect) has an [iteration composite operation](https://drafts.csswg.org/web-animations-2#iteration-composite-operation) of [accumulate](https://drafts.csswg.org/web-animations-2#iteration-composite-operation-accumulate), apply the following step *current iteration* times:

         *   replace the property value of *target property* on *keyframe* with the result of combining the property value on the final keyframe in *property-specific keyframes* (*V*a) with the property value on *keyframe* (*V*b) using the [accumulation procedure](https://www.w3.org/TR/css-values-4/#accumulation) defined for *target property*.

         > **Note:** Note: The order of arguments here is important. In the case where the animation type of the target property does not define a procedure for accumulation or addition, the default definition for these procedures result in *V*b being returned. When performing iteration composition on properties that do not support accumulation, the result should be the initial property value of *target property* on *keyframe*, hence we make this *V*b in the above step.

## Navigation

- Parent: `keyframe-effects` — Keyframe Effects

## Outgoing refs (7)

`webspec-index refs WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect -d outgoing -l 7`

## Incoming refs (2)

- WEB-ANIMATIONS-2#contents
- WEB-ANIMATIONS-2#effect-accumulation-section

### Possible effects

WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-2#the-effect-value-of-a-keyframe-animation-effect" --format markdown`
