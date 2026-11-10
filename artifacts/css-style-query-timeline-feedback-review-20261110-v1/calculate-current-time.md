# WEB-ANIMATIONS-1#the-current-time-of-an-animation

**Calculating the current time of an animation** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

The [current time](https://drafts.csswg.org/web-animations-1#animation-current-time) of an [animation](https://drafts.csswg.org/web-animations-1#concept-animation) is calculated from the first matching condition below:

If the animation’s [hold time](https://drafts.csswg.org/web-animations-1#animation-hold-time) is [resolved](https://drafts.csswg.org/web-animations-1#unresolved), 

The [current time](https://drafts.csswg.org/web-animations-1#animation-current-time) is the animation’s [hold time](https://drafts.csswg.org/web-animations-1#animation-hold-time).

If *any* of the following are true:

*   the animation has no associated [timeline](https://drafts.csswg.org/web-animations-1#timeline), or

*   the associated [timeline](https://drafts.csswg.org/web-animations-1#timeline) is [inactive](https://drafts.csswg.org/web-animations-1#inactive-timeline), or

*   the animation’s [start time](https://drafts.csswg.org/web-animations-1#animation-start-time) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved),

The [current time](https://drafts.csswg.org/web-animations-1#animation-current-time) is an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) time value.

Otherwise, 

> [`current time`](https://drafts.csswg.org/web-animations-1#animation-current-time)

Where *timeline time* is the current [time value](https://drafts.csswg.org/web-animations-1#time-value) of the associated [timeline](https://drafts.csswg.org/web-animations-1#timeline). The [playback rate](https://drafts.csswg.org/web-animations-1#playback-rate) value is defined in [§ 4.5.15 Speed control](https://drafts.csswg.org/web-animations-1#speed-control).

## Navigation

- Parent: `animations` — Animations
- Next: `setting-the-timeline` — Setting the timeline of an animation

## Outgoing refs (10)

`webspec-index refs WEB-ANIMATIONS-1#the-current-time-of-an-animation -d outgoing -l 10`

## Incoming refs (3)

- WEB-ANIMATIONS-1#animations
- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#play-states

### Possible effects

WEB-ANIMATIONS-1#the-current-time-of-an-animation

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#the-current-time-of-an-animation" --format markdown`
