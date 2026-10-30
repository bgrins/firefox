# WEB-ANIMATIONS-1#calculating-the-simple-iteration-progress

**Calculating the simple iteration progress** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The **simple iteration progress** is a fraction of the progress through the current iteration that ignores transformations to the time introduced by the [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) or [easing functions](https://drafts.csswg.org/css-easing-2/#easing-function) applied to the effect, and is calculated as follows:

1.  If the [overall progress](https://drafts.csswg.org/web-animations-1#overall-progress) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved), return unresolved.

2.  If [overall progress](https://drafts.csswg.org/web-animations-1#overall-progress) is infinity, let the *simple iteration progress* be [`iteration start`](https://drafts.csswg.org/web-animations-1#iteration-start); otherwise, let the *simple iteration progress* be [`overall progress`](https://drafts.csswg.org/web-animations-1#overall-progress).

3.  If *all* of the following conditions are true:

    *   the *simple iteration progress* calculated above is zero, *and*

    *   the animation effect is in the [active phase](https://drafts.csswg.org/web-animations-1#animation-effect-active-phase) *or* the [after phase](https://drafts.csswg.org/web-animations-1#animation-effect-after-phase), *and*

    *   the [active time](https://drafts.csswg.org/web-animations-1#active-time) is equal to the [active duration](https://drafts.csswg.org/web-animations-1#active-duration), *and*

    *   the [iteration count](https://drafts.csswg.org/web-animations-1#iteration-count) is *not* equal to zero.
    Let the *simple iteration progress* be 1.0.

    > **Note:** The above step implements the behavior that when an animation’s active interval ends precisely at the end of an iteration, it fills by holding the endpoint of the final iteration rather than the start of the next iteration.
    >
    > The final condition prevents this from applying when we never played any iterations of the animation to begin with because the [iteration count](https://drafts.csswg.org/web-animations-1#iteration-count) was zero.

4.  Return *simple iteration progress*.

## Navigation

- Parent: `core-animation-effect-calculations` — Calculating progress
- Prev: `calculating-the-overall-progress` — Calculating the overall progress
- Next: `calculating-the-current-iteration` — Calculating the current iteration index
- Children: 1
  - `simple-iteration-progress` — simple iteration progress

## Incoming refs (2)

- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#interval-timing

### Possible effects

WEB-ANIMATIONS-1#calculating-the-simple-iteration-progress

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-the-simple-iteration-progress" --format markdown`
