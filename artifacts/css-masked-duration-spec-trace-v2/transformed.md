# WEB-ANIMATIONS-1#calculating-the-transformed-progress

**Calculating the transformed progress** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The **transformed progress** is calculated from the [directed progress](https://drafts.csswg.org/web-animations-1#directed-progress) using the following steps:

1.  If the [directed progress](https://drafts.csswg.org/web-animations-1#directed-progress) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved), return unresolved.

2.  Calculate the value of the *before flag* as follows:

    1.  Determine the *current direction* using the procedure defined in [§ 4.7.6 Calculating the directed progress](https://drafts.csswg.org/web-animations-1#calculating-the-directed-progress).

    2.  If the *current direction* is forwards, let *going forwards* be true; otherwise it is false.

    3.  The *before flag* is set if the animation effect is in the [before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase) and *going forwards* is true; or if the animation effect is in the [after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase) and *going forwards* is false.
3.  Return the result of evaluating the [effect easing function](https://drafts.csswg.org/web-animations-1#animation-effect-effect-easing-function) passing [directed progress](https://drafts.csswg.org/web-animations-1#directed-progress) as the [input progress value](https://drafts.csswg.org/css-easing-2/#easing-function-input-progress-value) and *before flag* as the [before flag](https://drafts.csswg.org/css-easing-2/#easing-function-before-flag).

## Navigation

- Parent: `core-animation-effect-calculations` — Calculating progress
- Prev: `calculating-the-directed-progress` — Calculating the directed progress
- Next: `the-iteration-progress` — Yielding the iteration progress
- Children: 1
  - `transformed-progress` — transformed progress

## Incoming refs (2)

- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#time-transformations

### Possible effects

WEB-ANIMATIONS-1#calculating-the-transformed-progress

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-the-transformed-progress" --format markdown`
