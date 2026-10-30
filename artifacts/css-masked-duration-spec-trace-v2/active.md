# WEB-ANIMATIONS-1#calculating-the-active-time

**Calculating the active time** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The **active time** is based on the [local time](https://drafts.csswg.org/web-animations-1#local-time) and [start delay](https://drafts.csswg.org/web-animations-1#start-delay). However, it is only defined when the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) should produce an output and hence depends on its [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode) and phase as follows:

If the animation effect is in the [before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase), 

The result depends on the first matching condition from the following:

If the [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode) is [backwards](https://drafts.csswg.org/web-animations-1#fill-mode-backwards) or [both](https://drafts.csswg.org/web-animations-1#fill-mode-both), 

Return the result of evaluating `max([local time](https://drafts.csswg.org/web-animations-1#local-time) − [start delay](https://drafts.csswg.org/web-animations-1#start-delay), 0)`.

Otherwise, 

Return an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [time value](https://drafts.csswg.org/web-animations-1#time-value).

If the animation effect is in the [active phase](https://drafts.csswg.org/web-animations-1#animation-effect-active-phase), 

Return the result of evaluating [`local time`](https://drafts.csswg.org/web-animations-1#local-time).

If the animation effect is in the [after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase), 

The result depends on the first matching condition from the following:

If the [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode) is [forwards](https://drafts.csswg.org/web-animations-1#fill-mode-forwards) or [both](https://drafts.csswg.org/web-animations-1#fill-mode-both), 

Return the result of evaluating `max(min([local time](https://drafts.csswg.org/web-animations-1#local-time) − [start delay](https://drafts.csswg.org/web-animations-1#start-delay),
                [active duration](https://drafts.csswg.org/web-animations-1#active-duration)),
            0)`.

Otherwise, 

Return an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [time value](https://drafts.csswg.org/web-animations-1#time-value).

Otherwise (the [local time](https://drafts.csswg.org/web-animations-1#local-time) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved)), 

Return an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [time value](https://drafts.csswg.org/web-animations-1#time-value).

## Navigation

- Parent: `core-animation-effect-calculations` — Calculating progress
- Prev: `animation-effect-calculations-overview` — Overview
- Next: `calculating-the-overall-progress` — Calculating the overall progress
- Children: 1
  - `active-time` — active time

## Incoming refs (4)

- WEB-ANIMATIONS-1#animation-effect-phases-and-states
- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#effect-time-spaces
- WEB-ANIMATIONS-1#fill-behavior

### Possible effects

WEB-ANIMATIONS-1#calculating-the-active-time

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-the-active-time" --format markdown`
