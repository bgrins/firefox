# CSS-ANIMATIONS-2#animation-duration

**The animation-duration property** (heading)

**SHA**: hash:2f3a65bc90db82e56cc0b26890a026af8c02f356e10e4bfd03e024536a243e5c

## Content

| Name:                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| \[ auto [&#124;](https://drafts.csswg.org/css-values-4/#comb-one) [\<time \[0s,∞\]>](https://drafts.csswg.org/css-values-4/#time-value) \][#](https://drafts.csswg.org/css-values-4/#mult-comma) |
| auto                                                                                                                                                                                        |
| [all elements](https://www.w3.org/TR/css-pseudo/#generated-content)                                                                                                                         |
| no                                                                                                                                                                                          |
| N/A                                                                                                                                                                                         |
| list, each item either a time or the keyword [auto](https://drafts.csswg.org/css-animations-2#valdef-animation-duration-auto)                                                               |
| per grammar                                                                                                                                                                                 |
| not animatable                                                                                                                                                                              |

The [animation-duration](https://drafts.csswg.org/css-animations-2#propdef-animation-duration) property specifies the [iteration duration](https://drafts.csswg.org/web-animations-1/#iteration-duration) of the animation’s associated [animation effect](https://drafts.csswg.org/web-animations-1/#animation-effect).

**auto** 

For time-driven animations, equivalent to 0s.For [scroll-driven animations](https://drafts.csswg.org/scroll-animations-1/#scroll-driven-animations), equivalent to the duration necessary to fill the timeline in consideration of [animation-range](https://drafts.csswg.org/scroll-animations-1/#propdef-animation-range), [animation-delay](https://drafts.csswg.org/css-animations-2#propdef-animation-delay), and [animation-iteration-count](https://drafts.csswg.org/css-animations-1/#propdef-animation-iteration-count). See [Scroll-driven Animations § 4.1 Finite Timeline Calculations](https://drafts.csswg.org/scroll-animations-1/#finite-attachment).

**[\<time \[0s,∞\]>](https://drafts.csswg.org/css-values-4/#time-value)** 

For time-driven animations, specifies the length of time that an animation takes to complete one cycle. A negative [\<time>](https://drafts.csswg.org/css-values-4/#time-value) is invalid.For [scroll-driven animations](https://drafts.csswg.org/scroll-animations-1/#scroll-driven-animations), treated as [auto](https://drafts.csswg.org/css-animations-2#valdef-animation-duration-auto).

If the [used](https://drafts.csswg.org/css-cascade-5/#used-value) [animation-duration](https://drafts.csswg.org/css-animations-2#propdef-animation-duration) is 0s, the animation itself still occurs (instantaneously). The animation’s start and end events are still fired. If [animation-fill-mode](https://drafts.csswg.org/css-animations-1/#propdef-animation-fill-mode) is set to backwards or both, the first frame of the animation (as defined by [animation-direction](https://drafts.csswg.org/css-animations-1/#propdef-animation-direction)) will be displayed during the [animation-delay](https://drafts.csswg.org/css-animations-2#propdef-animation-delay); and if animation-fill-mode is set to forwards or both, the last frame of the animation (as defined by animation-direction) will be displayed after the animation-delay. However, if animation-fill-mode is set to [none](https://drafts.csswg.org/css-animations-1/#valdef-animation-fill-mode-none) the keyframes of the animation animation will have no noticeable effect.

For backwards-compatibility with Level 1, when the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of [animation-timeline](https://drafts.csswg.org/css-animations-2#propdef-animation-timeline) is [auto](https://drafts.csswg.org/css-animations-2#valdef-animation-timeline-auto) (i.e. only one list value, and that value being auto), the [resolved value](https://drafts.csswg.org/cssom-1/#resolved-value) of [auto](https://drafts.csswg.org/css-animations-2#valdef-animation-duration-auto) for [animation-duration](https://drafts.csswg.org/css-animations-2#propdef-animation-duration) is 0s whenever its [used value](https://drafts.csswg.org/css-cascade-5/#used-value) would also be 0s.

## Navigation

- Parent: `animation-definition` — Declaring Animations
- Next: `animation-timing-function` — The animation-timing-function property
- Children: 3
  - `propdef-animation-duration` — animation-duration
  - `valdef-animation-duration-auto` — auto
  - `valdef-animation-duration-time-0s` — <time [0s,∞]>

## Outgoing refs (29)

`webspec-index refs CSS-ANIMATIONS-2#animation-duration -d outgoing -l 29`

## Incoming refs (1)

- CSS-ANIMATIONS-2#contents
