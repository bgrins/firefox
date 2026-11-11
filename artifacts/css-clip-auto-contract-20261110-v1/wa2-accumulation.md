# WEB-ANIMATIONS-2#effect-accumulation-section

**Effect accumulation** (heading)

**SHA**: hash:07b283f9ef260b80742e247ba6ed8cee8f0d3013c60bdaf43a7b2c536f52fc38

## Content

Similar to the compositing performed between [effect values](https://drafts.csswg.org/web-animations-1/#effect-value) (see [Web Animations § 5.4.4 Effect composition](https://www.w3.org/TR/web-animations-1/#effect-composition)), the **iteration composite operation** determines how values are combined between successive iterations of the same [keyframe effect](https://drafts.csswg.org/web-animations-1/#keyframe-effect).

This specification defines two [iteration composite operations](https://drafts.csswg.org/web-animations-2#iteration-composite-operation) as follows:

**replace** 

Each successive iteration is calculated independently of previous iterations.

**accumulate** 

Successive iterations of the animation are [accumulated](https://www.w3.org/TR/css-values-4/#accumulation) with the final value of the previous iteration.

The application of the [iteration composite operation](https://drafts.csswg.org/web-animations-2#iteration-composite-operation) is incorporated in the calculation of the [effect value](https://drafts.csswg.org/web-animations-1/#effect-value) in [§ 3.2.1 The effect value of a keyframe effect](https://drafts.csswg.org/web-animations-2#the-effect-value-of-a-keyframe-animation-effect).

### Custom effects

(This section is added.)

> **Issue:** This whole feature needs to be revisited. The current thinking is that rather than having custom effects, we should simply have an `onupdate` callback on each [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect). That would allow, for example, augmenting an existing effect with a function that performs logging or triggers additional actions at certain times. With the current arrangement, doing this would require adding a parent group just to achieve this.

*This section is non-normative*In some situations the [animation effects](https://drafts.csswg.org/web-animations-1/#animation-effect) provided by Web Animations may be insufficient. For example, the animation effects defined here are only able to target certain CSS properties. They are unable, therefore, to modify the [`currentScale`](https://www.w3.org/TR/SVG11/struct.html#__svg__SVGSVGElement__currentScale) property of an SVG element to smoothly zoom the viewport without affecting the document content.

In such cases, where the provided [animation effects](https://drafts.csswg.org/web-animations-1/#animation-effect) do not provide needed functionality, an effect defined by script may be used. Such [custom effects](https://drafts.csswg.org/web-animations-2#custom-effect) receive an [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) and [current iteration](https://drafts.csswg.org/web-animations-1/#current-iteration-index) from the timing model and are responsible for producing an effect corresponding to the specified time.

Using an effect defined in script it is possible to animate not only otherwise un-animatable attributes and properties, but potentially anything that is accessible via script, including even producing audio or creating vibrations.

For example, using a [custom effect](https://drafts.csswg.org/web-animations-2#custom-effect) that draws to a [`canvas`](https://html.spec.whatwg.org/multipage/canvas.html#canvas) element, it is possible to produce a complex animated effect featuring patterns that may be difficult to create using CSS or SVG. Compared to using [Timing control for script-based animations](https://www.w3.org/TR/animation-timing/), this approach ensures the animation is frame-rate independent and can be paused, reversed, eased with timing effects, accelerated, synchronized with other animations, and be controlled in the same manner as any other Web Animations animation without any additional programming.

A **custom effect** is an author-defined programming callback that is passed timing information as part of the [update animations and send events](https://drafts.csswg.org/web-animations-1/#update-animations-and-send-events) procedure.

> **Issue:** It needs to be called whenever timing properties are updated too, right?

#### Sampling custom effects

[Custom effects](https://drafts.csswg.org/web-animations-2#custom-effect) are called for each referencing [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect) when the [update animations and send events](https://drafts.csswg.org/web-animations-1/#update-animations-and-send-events) procedure is performed (henceforth referred to simple as an *update*) based on the following criteria.

1.  If, on the previous update, the [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect) referencing the [custom effect](https://drafts.csswg.org/web-animations-2#custom-effect):

    *   was [in effect](https://drafts.csswg.org/web-animations-1/#in-effect), and

    *   referenced this same [custom effect](https://drafts.csswg.org/web-animations-2#custom-effect), and

    *   had a different [target element](https://www.w3.org/TR/web-animations-1/#effect-target-target-element)
    Call the callback passing an [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved) [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) and the [target element](https://www.w3.org/TR/web-animations-1/#effect-target-target-element) from the previous update as parameters to the callback.

2.  Call the callback for the current [target element](https://www.w3.org/TR/web-animations-1/#effect-target-target-element) based on the first matching condition from the following:

    If the [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect) referencing the custom effect is not [in effect](https://drafts.csswg.org/web-animations-1/#in-effect) but was in effect in the previous update,

    Call the callback passing an [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved) [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) and the current [target element](https://www.w3.org/TR/web-animations-1/#effect-target-target-element) as parameters to the callback.

    Otherwise, if the [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect) referencing the custom effect:

    *   **is [in effect](https://drafts.csswg.org/web-animations-1/#in-effect), and**

    *   **was not [in effect](https://drafts.csswg.org/web-animations-1/#in-effect) in the previous update, or was in effect but with a different [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) or [current iteration](https://drafts.csswg.org/web-animations-1/#current-iteration-index),**

    Call the callback passing with the referencing [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect)’s current [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) and [target element](https://www.w3.org/TR/web-animations-1/#effect-target-target-element) as parameters to the callback.

> **Issue:** There may be use cases where an action needs to be triggered at a specific point in an animation tree. In many cases this can be achieved by inserting a custom effect with a step-start easing that spans the period during which the action should be triggered. However, this can impose additional layout requirements on the content which might be cumbersome to accommodate.Some alternatives under consideration:
>
> *   Additional calling conditions could be defined to accommodate zero-width custom effects. For example, it could be required that the callback be called if (given infinite precision) there was a time between the previous and current update times that aligned with the custom effect.
>
> *   Instead of adding special calling conditions to custom effects, a new type of animation effect, Trigger, could be introduced. The trigger would only ever act as a zero-width custom effect as described above, its constructor would take a callback function, but not require a target or timing. It could also specify other calling conventions, for example whether it should only trigger in a specific playback direction.

#### Execution order of custom effects

Since [custom effects](https://drafts.csswg.org/web-animations-2#custom-effect), unlike [animation effects](https://drafts.csswg.org/web-animations-1/#animation-effect), are not limited to a single [target property](https://drafts.csswg.org/web-animations-1/#target-property), the steps for assessing their order of execution differs from animation effects.f

[Custom effects](https://drafts.csswg.org/web-animations-2#custom-effect) are executed after all [animation effects](https://drafts.csswg.org/web-animations-1/#animation-effect) have completed and applied their result to their targets (see Applying the composited result).

> **Issue:** Need to define this more precisely. Are styles flushed? Presumably they are. Can we suspend reflow for the duration of executing the script-based animation effects and just do it once afterwards?

Within the set of [custom effects](https://drafts.csswg.org/web-animations-2#custom-effect), the order of execution is the same as that defined for [animation effects](https://drafts.csswg.org/web-animations-1/#animation-effect) in [§ 3.3.1 The effect stack](https://drafts.csswg.org/web-animations-2#the-effect-stack). Items sorted earlier are executed before those sorted later.

## Navigation

- Parent: `animation-model` — Animation model
- Prev: `combining-effects` — Combining effects
- Next: `custom-effects` — Custom effects
- Children: 3
  - `iteration-composite-operation` — iteration composite operation
  - `iteration-composite-operation-replace` — replace
  - `iteration-composite-operation-accumulate` — accumulate

## Outgoing refs (6)

`webspec-index refs WEB-ANIMATIONS-2#effect-accumulation-section -d outgoing -l 6`

## Incoming refs (1)

- WEB-ANIMATIONS-2#contents

### Possible effects

WEB-ANIMATIONS-2#effect-accumulation-section

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-2#effect-accumulation-section" --format markdown`
