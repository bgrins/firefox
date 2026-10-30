# CSS-ANIMATIONS-2#animation-duration

**The animation-duration property** (heading)

**SHA**: hash:2f3a65bc90db82e56cc0b26890a026af8c02f356e10e4bfd03e024536a243e5c

## Content

| Name:                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| \[ auto [&#124;](CSS-VALUES-4#comb-one) [\<time \[0s,∞\]>](CSS-VALUES-4#time-value) \][#](CSS-VALUES-4#mult-comma) |
| auto                                                                                                                                                                                        |
| [all elements](CSS-PSEUDO#generated-content)                                                                                                                         |
| no                                                                                                                                                                                          |
| N/A                                                                                                                                                                                         |
| list, each item either a time or the keyword [auto](CSS-ANIMATIONS-2#valdef-animation-duration-auto)                                                               |
| per grammar                                                                                                                                                                                 |
| not animatable                                                                                                                                                                              |

The [animation-duration](CSS-ANIMATIONS-2#propdef-animation-duration) property specifies the [iteration duration](WEB-ANIMATIONS-1#iteration-duration) of the animation’s associated [animation effect](WEB-ANIMATIONS-1#animation-effect).

**auto** 

For time-driven animations, equivalent to 0s.For [scroll-driven animations](SCROLL-ANIMATIONS-1#scroll-driven-animations), equivalent to the duration necessary to fill the timeline in consideration of [animation-range](SCROLL-ANIMATIONS-1#propdef-animation-range), [animation-delay](CSS-ANIMATIONS-2#propdef-animation-delay), and [animation-iteration-count](CSS-ANIMATIONS-1#propdef-animation-iteration-count). See [Scroll-driven Animations § 4.1 Finite Timeline Calculations](SCROLL-ANIMATIONS-1#finite-attachment).

**[\<time \[0s,∞\]>](CSS-VALUES-4#time-value)** 

For time-driven animations, specifies the length of time that an animation takes to complete one cycle. A negative [\<time>](CSS-VALUES-4#time-value) is invalid.For [scroll-driven animations](SCROLL-ANIMATIONS-1#scroll-driven-animations), treated as [auto](CSS-ANIMATIONS-2#valdef-animation-duration-auto).

If the [used](CSS-CASCADE-5#used-value) [animation-duration](CSS-ANIMATIONS-2#propdef-animation-duration) is 0s, the animation itself still occurs (instantaneously). The animation’s start and end events are still fired. If [animation-fill-mode](CSS-ANIMATIONS-1#propdef-animation-fill-mode) is set to backwards or both, the first frame of the animation (as defined by [animation-direction](CSS-ANIMATIONS-1#propdef-animation-direction)) will be displayed during the [animation-delay](CSS-ANIMATIONS-2#propdef-animation-delay); and if animation-fill-mode is set to forwards or both, the last frame of the animation (as defined by animation-direction) will be displayed after the animation-delay. However, if animation-fill-mode is set to [none](CSS-ANIMATIONS-1#valdef-animation-fill-mode-none) the keyframes of the animation animation will have no noticeable effect.

For backwards-compatibility with Level 1, when the [computed value](CSS-CASCADE-5#computed-value) of [animation-timeline](CSS-ANIMATIONS-2#propdef-animation-timeline) is [auto](CSS-ANIMATIONS-2#valdef-animation-timeline-auto) (i.e. only one list value, and that value being auto), the [resolved value](CSSOM-1#resolved-value) of [auto](CSS-ANIMATIONS-2#valdef-animation-duration-auto) for [animation-duration](CSS-ANIMATIONS-2#propdef-animation-duration) is 0s whenever its [used value](CSS-CASCADE-5#used-value) would also be 0s.

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

### Possible effects

CSS-ANIMATIONS-2#animation-duration

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-ANIMATIONS-2#animation-duration" --format markdown`
