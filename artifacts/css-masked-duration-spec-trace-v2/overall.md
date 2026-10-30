# WEB-ANIMATIONS-1#calculating-the-overall-progress

**Calculating the overall progress** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The **overall progress** describes the number of iterations that have completed (including partial iterations) and is defined as follows:

1.  If the [active time](https://drafts.csswg.org/web-animations-1#active-time) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved), return unresolved.

2.  Calculate an initial value for *overall progress* based on the first matching condition below:

    If the [iteration duration](https://drafts.csswg.org/web-animations-1#iteration-duration) is zero,

    If the animation effect is in the [before phase](https://drafts.csswg.org/web-animations-1#animation-effect-before-phase), let *overall progress* be zero; otherwise, let it be equal to the [iteration count](https://drafts.csswg.org/web-animations-1#iteration-count).

    Otherwise,

    Let *overall progress* be the result of calculating [`active time`](https://drafts.csswg.org/web-animations-1#active-time).

3.  Return the result of calculating `*overall progress* + [iteration start](https://drafts.csswg.org/web-animations-1#iteration-start)`.

Tests

*   [overallProgress.html](https://wpt.fyi/results/web-animations/interfaces/Animation/overallProgress.html) [(live test)](http://wpt.live/web-animations/interfaces/Animation/overallProgress.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/interfaces/Animation/overallProgress.html)

## Navigation

- Parent: `core-animation-effect-calculations` — Calculating progress
- Prev: `calculating-the-active-time` — Calculating the active time
- Next: `calculating-the-simple-iteration-progress` — Calculating the simple iteration progress
- Children: 1
  - `overall-progress` — overall progress

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#calculating-the-overall-progress

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-the-overall-progress" --format markdown`
