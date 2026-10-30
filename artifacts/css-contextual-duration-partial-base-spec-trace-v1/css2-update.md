# CSS-ANIMATIONS-2#animations

**Animations** (heading)

**SHA**: hash:2f3a65bc90db82e56cc0b26890a026af8c02f356e10e4bfd03e024536a243e5c

## Content

Changes to any of the animation properties defined in this specification cause the corresponding [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) object and its associated objects to be updated according to the correspondence between these properties and Web Animations concepts defined in [§ 3 Assembling Keyframes](https://drafts.csswg.org/css-animations-2#keyframes).

However, if the author modifies the animation using the Web Animations programming interface, the changes from the programming interface take precedence as follows:

*   After a successful call to [`setKeyframes()`](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes) on the [`KeyframeEffect`](https://drafts.csswg.org/web-animations-1/#keyframeeffect) associated with a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation), any subsequent change to matching [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) rules or the resolved value of the [animation-timing-function](https://drafts.csswg.org/css-animations-1/#propdef-animation-timing-function) property for the target element will not be reflected in that animation.

    However, if the last matching [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) rule is removed the animation must still be canceled.

*   After a successful call to [`updateTiming()`](https://drafts.csswg.org/web-animations-1/#dom-animationeffect-updatetiming) on the [`KeyframeEffect`](https://drafts.csswg.org/web-animations-1/#keyframeeffect) associated with a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation), for each property included in the [`timing`](https://drafts.csswg.org/web-animations-1/#dom-animationeffect-updatetiming-timing-timing) parameter, any subsequent change to a corresponding animation property will not be reflected in that animation.

    For example, calling `cssAnimation.effect.updateTiming({ duration: 1000 })` would cause subsequent changes to [animation-duration](https://drafts.csswg.org/css-animations-2#propdef-animation-duration) to be ignored whilst changes to [animation-delay](https://drafts.csswg.org/css-animations-2#propdef-animation-delay) would still be reflected in the [`KeyframeEffect`](https://drafts.csswg.org/web-animations-1/#keyframeeffect)’s timing.

*   After a successful call to [`play()`](https://drafts.csswg.org/web-animations-1/#dom-animation-play) or [`pause()`](https://drafts.csswg.org/web-animations-1/#dom-animation-pause) on a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation), any subsequent change to the [animation-play-state](https://drafts.csswg.org/css-animations-1/#propdef-animation-play-state) will no longer cause the [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) to be played or paused as defined in [§ 4.5 The animation-play-state property](https://drafts.csswg.org/css-animations-2#animation-play-state).

*   After a successful call to [`reverse()`](https://drafts.csswg.org/web-animations-1/#dom-animation-reverse) on a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) or after successfully setting the [`startTime`](https://drafts.csswg.org/web-animations-2/#dom-animation-starttime) on a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation), if, as a result of that call the [play state](https://drafts.csswg.org/web-animations-1/#animation-play-state) of the [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) changes to or from the [paused](https://drafts.csswg.org/web-animations-1/#play-state-paused) play state, any subsequent change to the [animation-play-state](https://drafts.csswg.org/css-animations-1/#propdef-animation-play-state) will no longer cause the [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) to be played or paused as defined in [§ 4.5 The animation-play-state property](https://drafts.csswg.org/css-animations-2#animation-play-state).

    The requirement for a change to or from the [paused](https://drafts.csswg.org/web-animations-1/#play-state-paused) state ensures that even after calling [`reverse()`](https://drafts.csswg.org/web-animations-1/#dom-animation-reverse) or setting the [`startTime`](https://drafts.csswg.org/web-animations-2/#dom-animation-starttime) on a running animation, the animation continues to observe changes in [animation-play-state](https://drafts.csswg.org/css-animations-1/#propdef-animation-play-state).

*   After successfully setting the [`effect`](https://drafts.csswg.org/web-animations-1/#dom-animation-effect) of a [`CSSAnimation`](https://drafts.csswg.org/css-animations-2#cssanimation) to `null` or some [`AnimationEffect`](https://drafts.csswg.org/web-animations-1/#animationeffect) other than the original [`KeyframeEffect`](https://drafts.csswg.org/web-animations-1/#keyframeeffect), all subsequent changes to animation properties other than [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name), [animation-play-state](https://drafts.csswg.org/css-animations-1/#propdef-animation-play-state), or [animation-timeline](https://drafts.csswg.org/css-animations-2#propdef-animation-timeline) will not be reflected in that animation. Similarly, any change to matching [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) rules will not be reflected in that animation. However, if the last matching @keyframes rule is removed the animation must still be canceled.

> **Note:** Note, the reference to a successful call in the above rules is necessary to ensure that when an exception is thrown by any of these methods, the override behavior is *not* applied.

### Owning element

The **owning element** of an animation refers to the element or pseudo-element to which the [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property was applied that generated the animation.

If the [display](https://drafts.csswg.org/css-display-4/#propdef-display) property of an element is set to [none](https://drafts.csswg.org/css-display-4/#valdef-display-none) and its display value would compute to none when ignoring the Transitions and Animations [cascade origins](https://drafts.csswg.org/css-cascade-6/#origin), then terminate running animations with this [owning element](https://drafts.csswg.org/css-animations-2#owning-element). If an element has a display of none and its display value had computed to none when ignoring the Transitions and Animations cascade origins, updating display to a value other than none will start all animations applied to the element by the [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property.

> **Note:** Note: In practice, this means that an animation to a [display](https://drafts.csswg.org/css-display-4/#propdef-display) value of [none](https://drafts.csswg.org/css-display-4/#valdef-display-none) will not terminate running animations unless the style also computes to none without the effect of the animations.

If an animation generated using the markup defined in this specification is later disassociated from that markup by an update to the computed value of the [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property on the [owning element](https://drafts.csswg.org/css-animations-2#owning-element), the animation is disassociated from its owning element (that is, it has no owning element from that point forwards).

> **Note:** In the example below, `animation`’s initial [owning element](https://drafts.csswg.org/css-animations-2#owning-element) is `elem`. `animation` is disassociated from `element` through an update to the computed value of `elem`’s [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property.
>
> ```
> elem.style.animation = 'spin 1s';
> let animation = elem.getAnimations()[0]; // animation's owning element is elem
> elem.style.animation = ""; // animation no longer has an owning element
> ```
>
> Note that although the [owning element](https://drafts.csswg.org/css-animations-2#owning-element) is often equal to the [target element](https://drafts.csswg.org/web-animations-1/#effect-target-target-element) of an animation’s [associated effect](https://drafts.csswg.org/web-animations-1/#animation-associated-effect), this is not always the case. The following example demonstrates some of the situations where these two elements may differ.
>
> ```
> elem.style.animation = 'move 1s';
> let animation = elem.getAnimations()[0];
> // animation.effect.target == elem == animation's owning element
>
> animation.effect.target = elem2;
> // animation.effect.target == elem2 != animation's owning element
>
> animation.effect = null;
> // animation.effect?.target is undefined != animation's owning element
> ```

### Animation composite order

[Animations](https://drafts.csswg.org/web-animations-1/#concept-animation) generated from the markup defined in this specification have an [animation class](https://drafts.csswg.org/web-animations-1/#animation-class) of ‘CSS Animation’.

CSS Animations *with* an [owning element](https://drafts.csswg.org/css-animations-2#owning-element) have a *later* composite order than CSS Transitions but an *earlier* composite order than animations without a specific [animation class](https://drafts.csswg.org/web-animations-1/#animation-class).

Within the set of CSS Animations *with* an [owning element](https://drafts.csswg.org/css-animations-2#owning-element), two animations *A* and *B* are sorted in composite order (first to last) as follows:

1.  If the [owning element](https://drafts.csswg.org/css-animations-2#owning-element) of *A* and *B* differs, sort *A* and *B* by [tree order](https://dom.spec.whatwg.org/#concept-tree-order) of their corresponding owning elements. With regard to pseudo-elements, the sort order is as follows:

    *   element

    *   ::marker

    *   ::before

    *   any other pseudo-elements not mentioned specifically in this list, sorted in ascending order by the Unicode codepoints that make up each selector

    *   ::after

    *   element children
2.  Otherwise, sort *A* and *B* based on their position in the computed value of the [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property of the (common) [owning element](https://drafts.csswg.org/css-animations-2#owning-element).

When determining the composite order in order to sort [animation events](https://drafts.csswg.org/css-animations-2#events) where either or both of the events is an [`animationcancel`](https://drafts.csswg.org/css-animations-1/#eventdef-globaleventhandlers-animationcancel) event, treat the CSS Animation(s) for which the [`animationcancel`](https://drafts.csswg.org/css-animations-1/#eventdef-globaleventhandlers-animationcancel) event was generated as having an [owning element](https://drafts.csswg.org/css-animations-2#owning-element) corresponding to the owning element in use at the moment when the CSS Animation was cancelled. Furthermore, use the position of the animation in the [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) property in effect at the time when the CSS Animation was cancelled sorting such that positions of cancelled animations sort before positions of animations that have not been cancelled.

The composite order of CSS Animations *without* an [owning element](https://drafts.csswg.org/css-animations-2#owning-element) is based on their position in the [global animation list](https://drafts.csswg.org/web-animations-1/#global-animation-list).

> **Issue:** This differs from the behavior defined for transitions. We should probably sort transitions first, then animation, then use the global animation list. The reason being that when developer tools etc. hang on to orphaned animations and transitions in order to replay them, they should maintain roughly the same composite order.

CSS Animations generated using the markup defined in this specification are *not* added to the [global animation list](https://drafts.csswg.org/web-animations-1/#global-animation-list) when they are created. Instead, these animations are appended to the global animation list at the first moment when they transition out of the [idle](https://drafts.csswg.org/web-animations-1/#play-state-idle) play state after being disassociated from their [owning element](https://drafts.csswg.org/css-animations-2#owning-element). CSS Animations that have been disassociated from their owning element but are still idle do not have a defined composite order.

> **Note:** Note, this behavior relies on the fact that disassociating an animation from its [owning element](https://drafts.csswg.org/css-animations-2#owning-element) always causes it to enter (or remain) in the [idle](https://drafts.csswg.org/web-animations-1/#play-state-idle) play state.

## Navigation

- Prev: `delta` — Delta specification
- Next: `keyframes` — Assembling Keyframes
- Children: 2
  - `owning-element-section` — Owning element
  - `animation-composite-order` — Animation composite order

## Outgoing refs (22)

`webspec-index refs CSS-ANIMATIONS-2#animations -d outgoing -l 22`

## Incoming refs (2)

- CSS-ANIMATIONS-2#animation-play-state
- CSS-ANIMATIONS-2#contents
