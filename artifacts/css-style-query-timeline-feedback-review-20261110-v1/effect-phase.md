# WEB-ANIMATIONS-1#animation-effect-phases-and-states

**Animation effect phases and states** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

*This section is non-normative*At a given moment, an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) can be in one of three possible *phases*. If an animation effect has an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [local time](https://drafts.csswg.org/web-animations-1#local-time) it will not be in any phase.

The different phases are illustrated below.

![An example of the different phases and states
used to describe an animation effect.](images/animation-effect-phases-and-states.svg)

An example of the different phases and states used to describe an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect). 

The phases are as follows:

[before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase) 

The [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [local time](https://drafts.csswg.org/web-animations-1#local-time) falls before the effect’s [active interval](https://drafts.csswg.org/web-animations-1#active-interval) and [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time), *or* occurs during the range when a negative [start delay](https://drafts.csswg.org/web-animations-1#start-delay) is in effect.

[active phase](https://drafts.csswg.org/web-animations-1#animation-effect-active-phase) 

The [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [local time](https://drafts.csswg.org/web-animations-1#local-time) falls inside the effect’s [active interval](https://drafts.csswg.org/web-animations-1#active-interval) and outside the range of any negative [start delay](https://drafts.csswg.org/web-animations-1#start-delay) or negative [end delay](https://drafts.csswg.org/web-animations-1#end-delay).

[after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase) 

The [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [local time](https://drafts.csswg.org/web-animations-1#local-time) falls after the effect’s [active interval](https://drafts.csswg.org/web-animations-1#active-interval) or after the [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time) if that comes first (due to a negative [end delay](https://drafts.csswg.org/web-animations-1#end-delay)), but *not* during the range when a negative [start delay](https://drafts.csswg.org/web-animations-1#start-delay) is in effect.

In addition to these phases, an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) can also be described as being in one of several overlapping *states*. These states are only established for the duration of a single [animation frame](https://drafts.csswg.org/web-animations-1#animation-frame) and are primarily a convenience for describing stative parts of the model.

These states and their usage within the model are summarized as follows:

[in play](https://drafts.csswg.org/web-animations-1#in-play) 

Corresponds to an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) whose [active time](https://drafts.csswg.org/web-animations-1#active-time) is changing on each frame.

[current](https://drafts.csswg.org/web-animations-1#current) 

Corresponds to an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) that is either [in play](https://drafts.csswg.org/web-animations-1#in-play) or could become in play in the future based on its [animation](https://drafts.csswg.org/web-animations-1#concept-animation)’s current [playback rate](https://drafts.csswg.org/web-animations-1#playback-rate).

[in effect](https://drafts.csswg.org/web-animations-1#in-effect) 

Corresponds to an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) that has a resolved [active time](https://drafts.csswg.org/web-animations-1#active-time). This occurs when either the animation effect is in its [active phase](https://drafts.csswg.org/web-animations-1#animation-effect-active-phase) or outside the active phase but at a time where the effect’s [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode) (see [§ 4.6.8 Fill behavior and fill modes](https://drafts.csswg.org/web-animations-1#fill-behavior)) causes its active time to be resolved. Only [in effect](https://drafts.csswg.org/web-animations-1#in-effect) animation effects apply a result to their target.

The normative definition of each of these states follows.

The phase of an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) depends on the following definitions:

**animation direction** 

“backwards” if the effect is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation) *and* the associated [animation](https://drafts.csswg.org/web-animations-1#concept-animation)’s [playback rate](https://drafts.csswg.org/web-animations-1#playback-rate) is less than zero; in all other cases, the [animation direction](https://drafts.csswg.org/web-animations-1#animation-direction) is “forward”.

**before-active boundary time** 

`max(min([start delay](https://drafts.csswg.org/web-animations-1#start-delay),
                [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time)), 0)`

**active-after boundary time** 

`max(min([start delay](https://drafts.csswg.org/web-animations-1#start-delay) + [active duration](https://drafts.csswg.org/web-animations-1#active-duration),
                [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time)), 0)`

Furthermore, an **endpoint-inclusive active interval** flag may be specified when determining the phase. If not specified, it is assumed to be false.

An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the **before phase** if the animation effect’s [local time](https://drafts.csswg.org/web-animations-1#local-time) is not [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) and *either* of the following conditions are met:

*   the [local time](https://drafts.csswg.org/web-animations-1#local-time) is less than the [before-active boundary time](https://drafts.csswg.org/web-animations-1#before-active-boundary-time), *or*

*   the [animation direction](https://drafts.csswg.org/web-animations-1#animation-direction) is “backwards”, the [endpoint-inclusive active interval](https://drafts.csswg.org/web-animations-1#endpoint-inclusive-active-interval) flag is false, and the [local time](https://drafts.csswg.org/web-animations-1#local-time) is equal to the [before-active boundary time](https://drafts.csswg.org/web-animations-1#before-active-boundary-time).

An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the **after phase** if the animation effect’s [local time](https://drafts.csswg.org/web-animations-1#local-time) is not [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) and *either* of the following conditions are met:

*   the [local time](https://drafts.csswg.org/web-animations-1#local-time) is greater than the [active-after boundary time](https://drafts.csswg.org/web-animations-1#active-after-boundary-time), *or*

*   the [animation direction](https://drafts.csswg.org/web-animations-1#animation-direction) is “forwards”, the [endpoint-inclusive active interval](https://drafts.csswg.org/web-animations-1#endpoint-inclusive-active-interval) flag is false, and the [local time](https://drafts.csswg.org/web-animations-1#local-time) is equal to the [active-after boundary time](https://drafts.csswg.org/web-animations-1#active-after-boundary-time).

An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the **active phase** if the animation effect’s [local time](https://drafts.csswg.org/web-animations-1#local-time) is not [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) and it is neither in the [before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase) nor in the [after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase).

Furthermore, it is often convenient to refer to the case when an animation effect is in none of the above phases as being in the **idle phase**.

An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is **in play** if *all* of the following conditions are met:

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the [active phase](https://drafts.csswg.org/web-animations-1#animation-effect-active-phase), and

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation) that is not [finished](https://drafts.csswg.org/web-animations-1#play-state-finished).

An [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is **current** if *any* of the following conditions are true:

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is [in play](https://drafts.csswg.org/web-animations-1#in-play), or

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the [before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase) and is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation) with a [playback rate](https://drafts.csswg.org/web-animations-1#playback-rate) > 0, or

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is in the [after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase) and is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation) with a [playback rate](https://drafts.csswg.org/web-animations-1#playback-rate) < 0, or

*   the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation) not in the [idle](https://drafts.csswg.org/web-animations-1#play-state-idle) [play state](https://drafts.csswg.org/web-animations-1#animation-play-state) with a non-null associated [timeline](https://drafts.csswg.org/web-animations-1#timeline) that is not [monotonically increasing](https://drafts.csswg.org/web-animations-1#monotonically-increasing-timeline).

An animation effect is **in effect** if its [active time](https://drafts.csswg.org/web-animations-1#active-time), as calculated according to the procedure in [§ 4.7.2 Calculating the active time](https://drafts.csswg.org/web-animations-1#calculating-the-active-time), is *not* [unresolved](https://drafts.csswg.org/web-animations-1#unresolved).

## Navigation

- Parent: `animation-effects` — Animation effects
- Prev: `the-active-interval` — The active interval
- Next: `relevant-animations-section` — Relevant animations
- Children: 11
  - `animation-direction` — animation direction
  - `before-active-boundary-time` — before-active boundary time
  - `active-after-boundary-time` — active-after boundary time
  - `endpoint-inclusive-active-interval` — endpoint-inclusive active interval
  - `animation-effect-before-phase` — before phase
  - `animation-effect-after-phase` — after phase
  - `animation-effect-active-phase` — active phase
  - `animation-effect-idle-phase` — idle phase
  - `in-play` — in play
  - `current` — current
  - `in-effect` — in effect

## Outgoing refs (31)

`webspec-index refs WEB-ANIMATIONS-1#animation-effect-phases-and-states -d outgoing -l 31`

## Incoming refs (5)

`webspec-index refs WEB-ANIMATIONS-1#animation-effect-phases-and-states -d incoming -l 5`

### Possible effects

WEB-ANIMATIONS-1#animation-effect-phases-and-states

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#animation-effect-phases-and-states" --format markdown`
