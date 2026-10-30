# WEB-ANIMATIONS-1#calculating-the-directed-progress

**Calculating the directed progress** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The **directed progress** is calculated from the [simple iteration progress](https://drafts.csswg.org/web-animations-1#simple-iteration-progress) using the following steps:

1.  If the [simple iteration progress](https://drafts.csswg.org/web-animations-1#simple-iteration-progress) is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved), return unresolved.

2.  Calculate the *current direction* using the first matching condition from the following list:

    If [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) is [normal](https://drafts.csswg.org/web-animations-1#playback-direction-normal),

    Let the *current direction* be forwards.

    If [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) is [reverse](https://drafts.csswg.org/web-animations-1#playback-direction-reverse),

    Let the *current direction* be reverse.

    Otherwise (the [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) is [alternate](https://drafts.csswg.org/web-animations-1#playback-direction-alternate) or [alternate-reverse](https://drafts.csswg.org/web-animations-1#playback-direction-alternate-reverse))p,

    1.  Let *d* be the [current iteration index](https://drafts.csswg.org/web-animations-1#current-iteration-index).

    2.  If [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) is [alternate-reverse](https://drafts.csswg.org/web-animations-1#playback-direction-alternate-reverse) increment *d* by 1.

    3.  If `*d* % 2 == 0`, let the *current direction* be forwards; otherwise let the *current direction* be reverse. If *d* is infinity, let the *current direction* be forwards.

3.  If the *current direction* is forwards then return the [simple iteration progress](https://drafts.csswg.org/web-animations-1#simple-iteration-progress).

    Otherwise, return `1.0 − [simple iteration progress](https://drafts.csswg.org/web-animations-1#simple-iteration-progress)`.

## Navigation

- Parent: `core-animation-effect-calculations` — Calculating progress
- Prev: `calculating-the-current-iteration` — Calculating the current iteration index
- Next: `calculating-the-transformed-progress` — Calculating the transformed progress
- Children: 1
  - `directed-progress` — directed progress

## Incoming refs (3)

- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#direction-control
- WEB-ANIMATIONS-1#transformed-progress

### Possible effects

WEB-ANIMATIONS-1#calculating-the-directed-progress

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#calculating-the-directed-progress" --format markdown`
